FROM python:3.11

COPY . .

WORKDIR /app

COPY /requirements.txt .
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python3", "main.py" ]
