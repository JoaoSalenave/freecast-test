# FreeCast Test

A small media‐catalog backend (Django + Celery) with a read‐only FastAPI service. Everything is Dockerized for straightforward local setup and testing. This README explains the overall architecture, important design decisions, setup instructions, and decisions encountered during development.

---

## 1. Project Overview

- **Django (in `media/`)**  
  - **Purpose**: Store TV shows, movies, episodes, and their “sources” in a SQLite database.  
  - **Key Features**:  
    - Models for `Show`, `Season`, `Episode`, `Movie`, and `Source`.  
    - Four background tasks (Celery) for importing data, updating ratings, and validating source URLs.  
    - A small admin interface (out‐of‐the‐box Django admin) to inspect and manage records.  
    - Four management commands (`import_shows`, `import_movies`, `update_ratings`, `validate_sources`) for running background tasks synchronously.

- **Celery (worker + beat)**  
  - Uses Redis as a broker (containerized).  
  - On startup, enqueues one‐time “import shows” and “import movies” tasks, then schedules:  
    - `import_shows_task` and `import_movies_task` every 24 hours.  
    - `update_ratings_task` every 3 minutes.  
    - `validate_sources_task` every 6 hours.  
  - Celery and beat run together in a single container (`worker`) using `--beat --pool=solo`; this was chosen to keep the test setup simple.

- **FastAPI (in `service/`)**  
  - **Purpose**: Expose a read‐only API that queries the same SQLite database via Django’s ORM.  
  - **Endpoints**:  
    - `GET /shows/` – List all shows as JSON.  
    - `GET /shows/{id}/seasons` – List seasons for a show.  
    - `GET /shows/{id}/episodes` – List episodes for a show.  
    - `GET /episodes/{episode_id}/sources` – List source URLs for a particular episode.  
    - `GET /movies/` – List all movies.  
    - `GET /movies/{id}` – Details for a movie.  
    - `GET /movies/{id}/sources` – List source URLs for that movie.  

---

## 2. Setup

Prerequisites
-------------
- Docker + Docker Compose installed.

Clone & Run
-----------
```
git clone https://github.com/JoaoSalenave/freecast-test.git
cd freecast-test
docker-compose up --build 
```
Environment
-----------
A ready-made `.env` file is committed for demo purposes.  
It seeds a super-user:
```
    user: admin
    password: admin123
```
(Django stays with DEBUG=True, too. This is obviously not secure, but fine for a test repo.)

────────────────────────────────────────────────────────────────────────

Open the app
-------------
Service           | URL                              | Notes
------------------|----------------------------------|---------------------------------------------
Django Admin      | http://localhost:8000/admin/     | Log in with `admin` / `admin123`
FastAPI Swagger   | http://localhost:8001/docs       | Explore `/shows/`, `/movies/`, etc.

Everything else—Celery worker+beat, Redis, and migrations—starts automatically inside Docker.


---

## 3. Architectural Decisions

1. **Populating the Data Feed**  
   - **Why**: The JSON feeds supplied with the assignment provide only top-level movie / show information. To expose hierarchical data (show → season → episode → source) in the API, I generated placeholder Seasons, Episodes, and Sources during the first import.  
   - **How it works**:  
     - **`import_shows_task`** downloads `shows.json`, upserts a `Show`, then creates **two Seasons** (1 & 2). Inside each season I generated **two Episodes** (1 & 2) and attach one dummy `Source` per episode (`https://example.com/episode-placeholder.mp4`).  
     - **`import_movies_task`** downloads `movies.json`, upserts a `Movie`, and attaches **one** dummy `Source` (`https://example.com/movie-placeholder.mp4`).  
     - I default the custom field `kinopoisk_rating` to `0.0` because a real project would later enrich that value from an external API. Later on, this is updated by a background task. 
     - Both tasks run once at startup (via Celery’s `on_after_finalize`) and then every 24 hours. They can be called sync by management commands. 

2. **Background Tasks**  
   - **Why**: For a lightweight test environment I chose to run Celery worker *and* beat in the **same** container (`celery_worker`). A single process (`celery -A celery_app worker --beat --pool=solo`) keeps the stack to two containers (Django + Celery) instead of three.  
   - **How it works**: In `celery_app.py` I register four periodic tasks inside the `@on_after_finalize` hook:  

     | Task | Purpose | Frequency |
     |------|---------|-----------|
     | `import_shows_task` | Pull *shows.json* and upsert each **Show**, then generate two Seasons × two Episodes, each with a dummy Source. | Once at startup **and** every 24 h |
     | `import_movies_task` | Pull *movies.json* and upsert each **Movie**, then attach one dummy Source. | Once at startup **and** every 24 h |
     | `update_ratings_task` | Placeholder: assign each Movie / Show a random Kinopoisk rating between 5.0–9.0. | Every 3 min |
     | `validate_sources_task` | Issue a `HEAD` request to every Source URL; mark inactive on non-200/exception. | Every 6 h |

   - Because I schedule these tasks programmatically, Celery only needs to start once; beat runs inside the same process. Using `--pool=solo` avoids SQLite write-lock contention.
   - I schedule `update_ratings_task` every **3 minutes** and fill ratings with random values purely so we can see the scheduler working without waiting hours. We can run a management command aswell.
   - `validate_sources_task` flips a Source’s `is_active` flag, but the FastAPI layer still returns every source. In a production API I would either filter out inactive sources or surface that flag in the schema so clients can ignore dead links.
     
3. **Synchronous Management Commands**  
   - In a real production stack I would let every management command enqueue its task with `.delay()` and rely on the broker (Redis / RabbitMQ). For this test, I refactored all four commands to call the underlying task functions **directly**, sync.  
   - Example (`import_movies`):

     ```python
     from django.core.management.base import BaseCommand
     from catalog.tasks import import_movies_task

     class Command(BaseCommand):
         help = "Run import_movies_task synchronously (no Celery)"

         def handle(self, *args, **kwargs):
             import_movies_task()
             self.stdout.write(self.style.SUCCESS(
                 "import_movies_task completed synchronously"
             ))
     ```

   - Result: `docker-compose exec media_app python manage.py import_shows` (or any of the other three commands) always succeeds—even if Redis is down—because it never attempts a broker connection.
   - Production could have a try for both broker queue and sync.

4. **Entrypoint Logic to Avoid SQLite Locks**  
   - On a cold start **both** containers tried `python manage.py migrate` at the same time. SQLite allows only one writer, so Celery often died with *“database is locked.”* on first setups. Even though running docker-compose build again would work, I tried to fix it.  
   - **My fix**: In `media/entrypoint.sh` I check the first CLI argument.  
     - If `$1 = python` (the Django container) → run `migrate` and create the super-user.  
     - If `$1 = celery` (the worker container) → skip migrations entirely.  
   - With that change, `docker-compose up` always applies migrations first in Django, then lets Celery connect once the schema is ready—no more lock errors.
   - Of course, not ideal for prod, but sufficient for test purpose.

5. **FastAPI + Django Bootstrapping (and Tests)**  
   - Because the API layer queries Django models, I bootstrap Django *inside* `service/main.py`:

     ```python
     import os, sys, django

     sys.path.insert(0, "/app")  # import service.* and catalog.models
     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
     django.setup()
     ```

   - pytest needs the same setup. I call `django.setup()` at the top of `service/tests/test_fastapi.py` and mark the two DB-touching tests with `@pytest.mark.django_db` so they can exercise the endpoints without raising “database access not allowed.”


---

## 5. Management Commands (Sync)

Run any of the management commands directly inside the Django container.
Each one bypasses Celery and executes immediately.
```@root
    docker-compose exec media python manage.py import_shows
    docker-compose exec media python manage.py import_movies
    docker-compose exec media python manage.py update_ratings
    docker-compose exec media python manage.py validate_sources
```

## 6. Running Tests

Django-side tests:

```docker-compose exec media pytest -q```

FastAPI-side tests:

```docker-compose exec service pytest -q```

---

## 7. Further Improvements

• Move off SQLite to a multi-writer database; the ORM layer stays the
  same but the single-writer bottleneck disappears.

• Split Celery beat into its own container (or use django-celery-beat’s
  DB scheduler) so periodic tasks survive a worker crash.

• Re-enable `.delay()` in the management commands once a stable broker
  is guaranteed; long-running imports then stay off the CLI.

• Swap the rating stub for a real OMDb / TMDb call and expose
  `is_active` in the API, filtering out dead sources.

• Add JWT auth, pagination, and filtering to the FastAPI layer.

• Wire up a small CI pipeline that builds the images and runs both test
  suites on every push.

• Expand test coverage: unit tests for tasks, contract tests for API,
  and an integration test proving scheduled jobs reach the broker.

---

Thanks in advance for the opportunity, and for taking the time to review this project!


