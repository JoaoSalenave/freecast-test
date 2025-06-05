FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY service/requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY media/ ./media/
COPY service/ ./service/

EXPOSE 8001

CMD ["uvicorn", "service.main:app", "--host", "0.0.0.0", "--port", "8001"]
