# Verwenden Sie das offizielle Python-Image als Basis
FROM python:3.9

# Legen Sie das Arbeitsverzeichnis innerhalb des Containers fest
WORKDIR /app

# Kopieren Sie die Anwendungsdateien in den Container
COPY . .

# Stellen Sie sicher, dass die .env-Datei kopiert wird
COPY .env .env

# Installieren Sie die Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Starten Sie die Anwendung
CMD ["python", "run.py"]
