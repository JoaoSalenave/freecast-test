import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django
django.setup()

import pytest
from django.core.management import call_command
from catalog.models import Show, Movie

@pytest.mark.django_db
def test_import_commands_run_without_error():
    call_command("import_shows", verbosity=0)
    call_command("import_movies", verbosity=0)
    call_command("update_ratings", verbosity=0)
    call_command("validate_sources", verbosity=0)

    assert Show.objects.exists()
    assert Movie.objects.exists()

@pytest.mark.django_db
def test_models_created_have_required_fields():
    call_command("import_movies", verbosity=0)
    m = Movie.objects.first()
    assert m.title != ""
    assert m.release_year is not None
