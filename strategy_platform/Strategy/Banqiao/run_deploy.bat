
set CONDAPATH=C:\ProgramData\Miniconda3
set ENVPATH="D:\Teahouse Source Code\pyenv"
set PYSCRIPT="D:\Teahouse Source Code\tea_strategy_platform\Strategy\Banqiao\banqiao_deploy.py"

call %CONDAPATH%\Scripts\activate.bat %ENVPATH%

python %PYSCRIPT%