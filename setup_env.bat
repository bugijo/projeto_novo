@echo off

REM Ativar o ambiente virtual usando o Python 3.10
C:\Users\Usuário\OneDrive\Documentos\Python-3.10.16\python.exe -m venv venv
call .\venv\Scripts\activate.bat

REM Instalar as dependências
C:\Users\Usuário\OneDrive\Documentos\Python-3.10.16\python.exe -m pip install -r requirements.txt

REM Mensagem de conclusão
echo Ambiente configurado com sucesso!

pause 