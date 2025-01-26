import subprocess
import sys

# Determina se deve usar 'python' ou 'python3'
python_cmd = "python3" if sys.platform.startswith("linux") else "python"

scripts = [
    "ProcessTypeCalled.py",
    "ProcessTypeAllInfoCalled.py",
    "ProcessResponse.py",
    "ProcessFirstResponses.py",
    "ProcessLastResponse.py",
    "ProcessEmptyResponses.py",
    "data_processing.py"
]

for script in scripts:
    subprocess.run([python_cmd, script])
