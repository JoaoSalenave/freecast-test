FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app/media

COPY media/requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY media/ ./


COPY media/entrypoint.sh /app/media/entrypoint.sh
RUN chmod +x /app/media/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/media/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
