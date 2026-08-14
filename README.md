# LevantamentoLidarIME
Aulas e instruções sobre levantamento de nuvem de pontos 3D por meio de equipamento LiDAR para o 2º ano do Curso Básico do Instituto Militar de Engenharia.

## Sequência didática

- [01 Introdução ao LiDAR](01_Intro.ipynb): teoria LiDAR/SLAM, atributos e formatos de nuvem, leitura e visualização interativa de amostras PCD e LAS.
- [02 Planejamento](02_Planejamento.ipynb): trajetos, cobertura, calibração, apoio GNSS, pipeline e formatos de entrega.
- [03 Execução](03_Execucao.ipynb): campanhas de campo, controle de qualidade, registro, filtragem, segmentação e reconstrução.
- [04 Análise](04_Analise.ipynb): acurácia posicional, classificação, produtos 3D, BIM básico e relatório técnico.
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

reset
git init
git remote add lidar https://github.com/HumbertoDiego/LevantamentoLidarIME
git add * ; git commit -m "aula update"; git push lidar main --force
-->
