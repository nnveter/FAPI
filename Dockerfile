FROM python:3.12-slim

# Не писать .pyc и не буферизовать stdout/stderr.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Сначала зависимости — для кэширования слоёв.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем исходный код приложения.
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
