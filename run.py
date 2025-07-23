import os, sys, pathlib
from dotenv import load_dotenv
load_dotenv()

# Ensure project root is on PYTHONPATH for child processes (e.g., uvicorn reload)
project_root = str(pathlib.Path(__file__).resolve().parent)
os.environ["PYTHONPATH"] = project_root + os.pathsep + os.environ.get("PYTHONPATH", "")

import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True) 