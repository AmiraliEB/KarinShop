FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y gettext locales && \
    sed -i -e 's/^# \(fa_IR UTF-8\)/\1/' /etc/locale.gen && \
    LC_ALL=C dpkg-reconfigure --frontend=noninteractive locales && \
    rm -rf /var/lib/apt/lists/*
ENV LANG fa_IR.UTF-8
ENV LANGUAGE fa_IR:fa
ENV LC_ALL fa_IR.UTF-8

WORKDIR /app

COPY backend/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

WORKDIR /app/backend
CMD ["python", "manage.py", "runserver","0.0.0.0:8000"]