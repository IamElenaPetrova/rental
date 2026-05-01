FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn",
     "--bind", "0.0.0.0:8000",
     "--workers", "3",
     "--timeout", "120",
     "--graceful-timeout", "30",
     "--access-logfile", "-",
     "--error-logfile", "-",
     "--capture-output",
     "rental.wsgi:application"]