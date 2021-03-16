import os
from typing import Optional

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return f"Hello {os.getenv('PRENOM', 'Unknown')}"
