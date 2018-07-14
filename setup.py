import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os"], "excludes": ["tkinter"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win64":
    base = "Win64GUI"

setup(name="tcp_udp",
      version="8.1",
      description="application!",
      options={"build_exe": build_exe_options},
      executables=[Executable("main.py", base=base, targetName='main.exe', icon="shared.ico")])