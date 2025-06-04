import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media'))
sys.path.insert(0, BASE_DIR)

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from fastapi import FastAPI
from service.api import shows, movies

app = FastAPI(title="Media API")
app.include_router(shows.router)
app.include_router(movies.router)
