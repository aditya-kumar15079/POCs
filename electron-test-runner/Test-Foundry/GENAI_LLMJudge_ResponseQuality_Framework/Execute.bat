@echo off
REM Activates the virtual environment
call venv\Scripts\activate

REM Runs the Python script
python C:\GENAI_LLMJudge_ResponseQuality_Framework\src/main.py

REM Keeps the command window open after execution
exit
