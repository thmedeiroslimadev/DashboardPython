import subprocess

scripts = [
    "ProcessTypeCalled.py",
    "ProcessTypeAllInfoCalled.py",
    "ProcessResponse.py",
    "ProcessFirstResponses.py",
    "ProcessLastResponse.py",
    "ProcessEmptyResponses.py"
]

for script in scripts:
    subprocess.run(["python", script])
