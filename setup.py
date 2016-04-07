import sys
import requests
from cx_Freeze import setup, Executable


build_exe_options = {"packages": ["sip"], "include_files":[(requests.certs.where(),'cacert.pem')]}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "TunetClient",
        version = "0.1",
        description = "Tunet GUI Client!",
        options = {"build_exe": build_exe_options},
        executables = [Executable("TunetLogin.pyw", base=base)])
