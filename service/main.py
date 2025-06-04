import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent / "media"
PROJECT_ROOT = BASE_DIR.parent 
load_dotenv(PROJECT_ROOT / ".env")

sys.path.insert(0, str(BASE_DIR))

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from fastapi import FastAPI
from service.api import shows, movies

app = FastAPI(title="Media API")
app.include_router(shows.router)
app.include_router(movies.router)
