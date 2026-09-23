"""Converte os formatos FEIMA observados em SN_00040/PROJ1 para TXT.

Usa somente a biblioteca padrao. Consulte docs/formato_feima.md para o mapa
binario e as limitacoes, especialmente a ausencia de quaternions na IMU.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
from pathlib import Path
import struct
import sys
from typing import BinaryIO, TextIO


HEADER_SIZE = 1024
WEEK_NS = 604800 * 1_000_000_000
EXTENSIONS = {".fmraster", ".fmimr", ".fmimu"}
RASTER_COLUMNS = "SAMPTIME DIR INC ANGLE NUM".split()
IMU_COLUMNS = "SAMPTIME ACCX ACCY ACCZ GYRX GYRY GYRZ Q0 Q1 Q2 Q3".split()
TIME = struct.Struct("<4BI")
RASTER = struct.Struct("<BHI")
IMU = struct.Struct("<7h")


class FormatError(ValueError):
    """Arquivo desconhecido, truncado ou inconsistente."""


@dataclass(frozen=True)
class Header:
    kind: str
    record_size: int
    message_type: int
    ticks_per_turn: int = 0
    gyro_scale: float = 0.0
    accel_scale: float = 0.0


@dataclass
class Summary:
    source: Path
    header: Header
    records: int = 0
    first_ns: int = 0
    last_ns: int = 0
    week_rollovers: int = 0
    sequence_gaps: int = 0
    auxiliary_min: int | None = None
    auxiliary_max: int | None = None
    output: Path | None = None

    @property
    def duration(self) -> float:
        return (self.last_ns - self.first_ns + self.week_rollovers * WEEK_NS) / 1e9


def read_header(stream: BinaryIO) -> Header:
    data = stream.read(HEADER_SIZE)
    if len(data) != HEADER_SIZE:
        raise FormatError("Cabecalho incompleto: esperados 1024 bytes.")
    signature = data[:50].split(b"\0", 1)[0]
    descriptor = data[50:150].split(b"\0", 1)[0]
    markers = struct.unpack_from("<4I", data, 200)
    # Os marcadores limitam o suporte a variante efetivamente investigada.
    if markers[:3] != (1467, 1, 6):
        raise FormatError(f"Variante de cabecalho nao suportada: {markers}.")
    if (signature, descriptor, markers[3]) == (
        b"feimarobotics-slam-raster", b"feima-raster-1", 100
    ):
        ticks = struct.unpack_from("<I", data, 232)[0]
        if not 1 <= ticks <= 65536:
            raise FormatError(f"Resolucao do encoder invalida: {ticks}.")
        return Header("raster", 21, 0x3B, ticks_per_turn=ticks)
    if (signature, descriptor, markers[3]) == (
        b"feimarobotics-slam-imu", b"fmimu", 81
    ):
        gyro, accel = struct.unpack_from("<2d", data, 248)
        if not all(math.isfinite(x) and x > 0 for x in (gyro, accel)):
            raise FormatError("Fatores de escala da IMU invalidos.")
        return Header("imu", 28, 0x3A, gyro_scale=gyro, accel_scale=accel)
    raise FormatError(
        f"Formato nao suportado: {signature!r}, {descriptor!r}, tipo {markers[3]}."
    )


def format_time(timestamp_ns: int) -> str:
    seconds, nanoseconds = divmod(timestamp_ns, 1_000_000_000)
    return f"{seconds}.{nanoseconds:09d}"


def process_records(
    stream: BinaryIO, summary: Summary, output: TextIO | None, imu_layout: str
) -> None:
    header = summary.header
    previous_sequence = None
    previous_day = None
    while True:
        record = stream.read(header.record_size)
        if not record:
            break
        offset = HEADER_SIZE + summary.records * header.record_size
        location = f"Registro {summary.records + 1}, byte {offset}"
        if len(record) != header.record_size:
            raise FormatError(f"{location}: registro truncado ({len(record)} bytes).")
        if record[:2] != b"FM" or record[3:5] != bytes(
            (header.message_type, header.record_size - 6)
        ):
            raise FormatError(f"{location}: assinatura, tipo ou tamanho invalido.")
        if sum(record[:-1]) % 256 != record[-1]:
            raise FormatError(f"{location}: checksum invalido.")
        day, hour, minute, second, ns = TIME.unpack_from(record, 5)
        if not (day < 7 and hour < 24 and minute < 60 and second < 60 and ns < 1_000_000_000):
            raise FormatError(f"{location}: horario invalido.")
        whole_seconds = ((day * 24 + hour) * 60 + minute) * 60 + second
        timestamp = whole_seconds * 1_000_000_000 + ns
        if summary.records and timestamp <= summary.last_ns:
            if previous_day == 6 and day == 0:
                summary.week_rollovers += 1
            else:
                raise FormatError(f"{location}: horario repetido ou fora de ordem.")
        if previous_sequence is not None and record[2] != (previous_sequence + 1) % 256:
            summary.sequence_gaps += 1
        previous_sequence, previous_day = record[2], day
        if not summary.records:
            summary.first_ns = timestamp
        summary.last_ns = timestamp
        if header.kind == "raster":
            direction, increment, turns = RASTER.unpack_from(record, 13)
            if direction not in (0, 1) or increment >= header.ticks_per_turn:
                raise FormatError(f"{location}: direcao ou incremento invalido.")
            if output is not None:
                angle = increment * 360.0 / header.ticks_per_turn
                output.write(
                    f"{format_time(timestamp)},{direction},{increment},{angle:.6f},{turns}\n"
                )
        else:
            gx, gy, gz, ax, ay, az, auxiliary = IMU.unpack_from(record, 13)
            if summary.auxiliary_min is None:
                summary.auxiliary_min = summary.auxiliary_max = auxiliary
            else:
                summary.auxiliary_min = min(summary.auxiliary_min, auxiliary)
                summary.auxiliary_max = max(summary.auxiliary_max, auxiliary)
            if output is not None:
                values = (ax * header.accel_scale, ay * header.accel_scale,
                          az * header.accel_scale, gx * header.gyro_scale,
                          gy * header.gyro_scale, gz * header.gyro_scale)
                suffix = "NaN,NaN,NaN,NaN" if imu_layout == "legacy" else str(auxiliary)
                sensors = ",".join(f"{x:.6f}" for x in values)
                output.write(f"{format_time(timestamp)},{sensors},{suffix}\n")
        summary.records += 1
    if not summary.records:
        raise FormatError("Arquivo sem registros.")


def output_path(source: Path) -> Path:
    target = source
    while target.suffix.lower() in EXTENSIONS:
        target = target.with_suffix("")
    return target.with_name(target.name + ".txt")


def convert_file(
    source: str | Path, *, check_only: bool = False, imu_layout: str = "legacy"
) -> Summary:
    """Valida/converte um arquivo; recusa sobrescrita e remove saida incompleta.

    legacy: mesmas 11 colunas da IMU antiga, com Q0..Q3 = NaN.
    measured: sete colunas de tempo/sensores, seguidas de AUX_RAW (sem escala).
    """
    if imu_layout not in ("legacy", "measured"):
        raise ValueError("imu_layout deve ser legacy ou measured.")
    source = Path(source)
    target = output_path(source)
    with source.open("rb") as stream:
        header = read_header(stream)
        summary = Summary(source, header)
        if check_only:
            process_records(stream, summary, None, imu_layout)
            return summary
        if target.resolve() == source.resolve():
            raise ValueError("Entrada e saida nao podem ser o mesmo arquivo.")
        # Modo x protege arquivos existentes, inclusive contra criacao concorrente.
        output = target.open("x", encoding="ascii", newline="\n")
        try:
            with output:
                if header.kind == "raster":
                    columns = RASTER_COLUMNS
                else:
                    columns = (
                        IMU_COLUMNS if imu_layout == "legacy"
                        else IMU_COLUMNS[:7] + ["AUX_RAW"]
                    )
                output.write(",".join(columns) + "\n")
                process_records(stream, summary, output, imu_layout)
        except BaseException:
            target.unlink()
            raise
        summary.output = target
        return summary


def discover(paths: list[Path]) -> list[Path]:
    files = []
    for path in paths:
        if path.is_dir():
            matches = sorted(
                p for p in path.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS
            )
            if not matches:
                raise ValueError(f"Nenhum .fmraster, .fmimr ou .fmimu em {path}.")
            files.extend(matches)
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(f"Caminho inexistente: {path}")
    unique = {p.resolve(): p for p in files}
    return list(unique.values())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Converte binarios FEIMA para TXT ao lado do original, sem sobrescrever.")
    parser.add_argument("paths", nargs="+", type=Path, help="Arquivos ou pastas PROJ1 (sem recursao).")
    parser.add_argument("--check", action="store_true", help="Valida todos os registros sem gravar TXT.")
    parser.add_argument("--imu-layout", choices=("legacy", "measured"), default="legacy",
                        help="legacy: 11 colunas, Q0..Q3=NaN; measured: sensores e AUX_RAW.")
    args = parser.parse_args(argv)
    try:
        sources = discover(args.paths)
    except (OSError, ValueError) as error:
        print(f"ERRO: {error}", file=sys.stderr)
        return 1
    status = 0
    for source in sources:
        try:
            result = convert_file(source, check_only=args.check, imu_layout=args.imu_layout)
        except (OSError, ValueError) as error:
            print(f"ERRO [{source.name}]: {error}", file=sys.stderr)
            status = 1
            continue
        print(f"{source.name}: {result.records} registros {result.header.kind.upper()}, checksums OK")
        print(f"  SAMPTIME: {format_time(result.first_ns)} a {format_time(result.last_ns)}; duracao {result.duration:.9f} s")
        if result.header.kind == "imu":
            print(f"  Escalas: ACC={result.header.accel_scale:.17g}; GYR={result.header.gyro_scale:.17g}")
            print(f"  AUX_RAW: {result.auxiliary_min} a {result.auxiliary_max}; significado nao confirmado.")
            if args.imu_layout == "legacy":
                print("  AVISO: quaternions ausentes no binario; Q0..Q3 = NaN no TXT.")
        if result.sequence_gaps:
            print(f"  AVISO: {result.sequence_gaps} descontinuidades no contador de pacotes.")
        if result.week_rollovers:
            print(f"  AVISO: {result.week_rollovers} viradas de semana; SAMPTIME reinicia no domingo.")
        if result.output:
            print(f"  Salvo: {result.output}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())


"""
## Uso

Na raiz deste repositorio:

```powershell
python .\converter.py ..\SN_00040\PROJ1
```

Saidas:

```text
../SN_00040/PROJ1/20250610-163659_00040_Ec_Data.txt
../SN_00040/PROJ1/20250610-163659_00040_Lp_Imu.txt
```

"""