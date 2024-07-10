FROM python:3.11

ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
COPY ./entrypoint.sh /app/

RUN sed -i 's/\r$//' /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh


CMD ["python", "manage.py", "runserver"]