import os, sys, pathlib
from dotenv import load_dotenv
load_dotenv()
project_root = pathlib.Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root)) 