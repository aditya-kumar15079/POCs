@echo off
REM Activates the virtual environment
call venv\Scripts\activate

REM Runs the Python script
cd C:\TestFoundry_Framework
python main.py

REM Keeps the command window open after execution
exit
