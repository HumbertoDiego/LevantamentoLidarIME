# LevantamentoLidarIME
Aulas e instruções sobre levantamento de nuvem de pontos 3D por meio de equipamento LiDAR para o 2º ano do Curso Básico do Instituto Militar de Engenharia.

## Sequência didática

- [01 Introdução ao LiDAR](01_Intro.ipynb): teoria LiDAR/SLAM, atributos e formatos de nuvem, leitura e visualização interativa de amostras PCD e LAS.
- [02 Planejamento](02_Planejamento.ipynb): valores humanos, EAP, juntada de requisitos e métodos de gestão de tarefas.
- [03 Execução](03_Execucao.ipynb): equipamento, campanhas de campo, controle de qualidade, registro, filtragem, classificação e reconstrução 3D.
- [04 Entregas e Análise](04_Analise.ipynb): produtos esperados e validação
- [05 Encerramento](05_Encerramento.ipynb): apresentação, demonstração, aceite, entrega final e lições aprendidas.


## Requisitos

- [Python 3.12](https://www.python.org/downloads/)
- [VS Code](https://code.visualstudio.com/)
- [Extensão Jupyter do VS Code](https://marketplace.visualstudio.com/search?term=jupyter&target=VSCode&category=All%20categories&sortBy=Relevance)


## Dicas para gerenciar múltiplas versões do Python

- Instale o [Python Install Manager](https://www.python.org/downloads/)
```powershell
> py install 3.9 3.10 3.11 3.12 3.14 # Instala as versões python de 3.9 a 3.14
> python --version # Python 3.14.5
> $Env:PYTHON_MANAGER_DEFAULT = "3.12" # Altera a versão para esta seção de terminal apenas
> python --version # Python 3.12.10 --> Daqui pode-se criar o ambiente
```

## Criar o ambiente

```powershell
> python -m venv .venv
> .\.venv\Scripts\Activate.ps1 
(.venv) > python -m pip install --upgrade pip
(.venv) > python -m pip install -r requirements.txt
```

- Após criar o ambiente, verifique se está usando uma cópia do Python 3.12 da pasta `.venv`:

```powershell
> python -c "import sys; print(sys.executable)" # C:\Users\...\Python\pythoncore-3.12-64\python.exe
> python -m venv .venv
> .\.venv\Scripts\Activate.ps1 
(.venv) > python -c "import sys; print(sys.executable)" # ...\cdg-ime\.venv\Scripts\python.exe
```

- Então instale as bibliotecas Python:
```powershell
> python -m pip install -r requirements.txt
```

## Selecionar este ambiente Python em um notebook (`.ipynb`) no VS Code

- `Select Kernel` > `Python Environments...` > `.venv\Scripts\python.exe`

<!--
git pull lidar main
git add * ; git commit -m "aula update"; git push lidar main
jupyter nbconvert --to slides 01_Intro.ipynb --TagRemovePreprocessor.remove_input_tags="hide_input" --SlidesExporter.reveal_scroll=True --post serve

# reset
git init
git remote add lidar https://github.com/HumbertoDiego/LevantamentoLidarIME
git add * ; git commit -m "aula update"; git push lidar main --force

# comandos
pelo adb shell:
echo | nc -w 2 -q 1 192.168.56.1 19700 >/dev/null 2>&1 && echo "19700 OPEN" || echo "19700 CLOSED"

pelo Windows:
Status Check Command:
curl --location --request GET 'http://192.168.10.1:19700/slam/get_error_status'
Success:
{
  "data": {
    "code_camera": 0,
    "code_command": 0,
    "code_fpga": 0,
    "code_i2000": 0,
    "code_imu": 0,
    "code_lidar": 0,
    "code_mcu": 0,
    "code_raster": 0,
    "code_time_sync": 0
  },
  "message": "",
  "status": 0
}
Ready State Condition::
code_command & 0x01 << 15 == 1 indicates the device is operational.

Starting the Device:
curl --location --request GET 'http://192.168.10.1:19700/slam/start_work'
Success:
{
  "data": {
    "status": 2
  },
  "message": "",
  "status": 0
}
Stopping the Device:
curl --location --request GET 'http://192.168.10.1:19700/slam/end_work'
Successful
{
  "data": {
    "status": 3
  },
  "message": "",
  "status": 0
}

outros:
https://wiki.feima.cool/en/sdk/slam/http
-->
