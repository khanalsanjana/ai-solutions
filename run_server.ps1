Set-Location $PSScriptRoot
& "$PSScriptRoot\.venv\Scripts\python.exe" -m flask --app app run --host 127.0.0.1 --port 5000
