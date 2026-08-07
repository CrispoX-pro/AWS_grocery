# 🛒 AWS GroceryMate

![AWS](https://img.shields.io/badge/AWS-Cloud-orange)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-black)
![Docker](https://img.shields.io/badge/Docker-Container-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)

## 📌 Projektbeschreibung

AWS GroceryMate ist eine moderne Grocery-Webanwendung mit einer cloudbasierten Architektur.

Die Anwendung ermöglicht Benutzern:

- Benutzerregistrierung und Login
- Verwaltung eines Benutzerprofils
- Upload von Profilbildern
- Verwaltung von Favoriten
- Verwaltung eines Warenkorbs
- Speicherung gekaufter Produkte

Das Backend läuft containerisiert auf Amazon EC2 und verwendet Amazon RDS PostgreSQL als Datenbank sowie Amazon S3 für die Speicherung von Benutzerbildern.

---

# 🏗️ Architektur

```text
                     User
                       |
                       v
                   Frontend
                       |
                       v
                  Flask API
                       |
          +------------+------------+
          |                         |
          v                         v
     Amazon RDS                 Amazon S3
     PostgreSQL              Avatar Storage
          ^
          |
      Amazon EC2
          |
          v
    Docker Container
          |
          v
    Flask Backend
```

---

# 🚀 Features

## 👤 Benutzerverwaltung

- Registrierung
- Login mit JWT Authentication
- Benutzerinformationen abrufen
- Profilverwaltung
- Avatar Upload

## 🛒 Warenkorb

- Produkte hinzufügen
- Mengen aktualisieren
- Warenkorb synchronisieren
- Warenkorb nach Kauf leeren

## ⭐ Favoriten

- Produkte favorisieren
- Favoriten entfernen
- Favoriten anzeigen

## 🖼️ Avatar Storage

Die Benutzerbilder werden über Amazon S3 gespeichert.

S3 Bucket:

```text
grocerymate-avatars-chris
```

Struktur:

```text
avatars/
 ├── user_1_timestamp.jpg
 └── user_2_timestamp.png
```

Die Kommunikation erfolgt über eine AWS IAM Role.

Es werden keine AWS Access Keys im Code gespeichert.

---

# 🛠️ Technologie Stack

## Backend

- Python 3.9
- Flask
- Flask SQLAlchemy
- Flask JWT Extended
- Flask Migrate
- PostgreSQL
- Boto3

## Infrastruktur

- Amazon EC2
- Amazon RDS PostgreSQL
- Amazon S3
- AWS IAM
- Docker

## Development

- Git
- GitHub
- Virtual Environment
- dotenv

---

# 📂 Projektstruktur

```text
AWS_grocery/
│
├── backend/
│   ├── app/
│   │   ├── controllers/
│   │   │   └── user_controller.py
│   │   ├── models/
│   │   │   ├── user_model.py
│   │   │   └── product_model.py
│   │   ├── services/
│   │   │   └── user_service.py
│   │   └── __init__.py
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│
├── docker-compose.yml
│
└── README.md
```

---

# ⚙️ Installation

## Repository klonen

```bash
git clone https://github.com/CrispoX-pro/AWS_grocery.git

cd AWS_grocery
```

---

# 🔧 Backend Setup

## Virtuelle Umgebung erstellen

```bash
python -m venv venv
```

### Aktivieren

**Linux / macOS:**

```bash
source venv/bin/activate
```

**Windows:**

```powershell
venv\Scripts\activate
```

---

## Dependencies installieren

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variablen

Erstelle im Backend eine Datei:

```text
.env
```

Beispiel:

```ini
JWT_SECRET_KEY=your_secret_key

FLASK_ENV=development

POSTGRES_URI=postgresql://user:password@host:5432/database

USE_S3_STORAGE=true

S3_BUCKET_NAME=grocerymate-avatars-chris

S3_REGION=eu-central-1
```

> **Hinweis:** Die `.env`-Datei sollte niemals in Git eingecheckt werden. Füge sie zu deiner `.gitignore` hinzu.

---

# 🐳 Docker

Das Backend kann als Docker-Container betrieben werden.

Build:

```bash
docker build -t grocerymate-backend ./backend
```

Container starten:

```bash
docker run -p 5000:5000 grocerymate-backend
```

Falls `docker-compose.yml` verwendet wird:

```bash
docker compose up --build
```

---

# ☁️ AWS Deployment

Die Anwendung ist für eine cloudbasierte AWS-Infrastruktur ausgelegt.

## Amazon EC2

Der Flask-Backend-Service läuft containerisiert auf einer Amazon EC2 Instanz.

## Amazon RDS

Amazon RDS PostgreSQL übernimmt die persistente Speicherung von:

- Benutzerdaten
- Produktdaten
- Warenkorbdaten
- Favoriten
- gekauften Produkten

## Amazon S3

Amazon S3 wird für die Speicherung von Benutzer-Avataren verwendet.

## AWS IAM

Der Zugriff auf S3 erfolgt über eine IAM Role. Dadurch müssen keine AWS Access Keys im Quellcode hinterlegt werden.

---

# 🔒 Sicherheit

- JWT-basierte Authentifizierung
- Secrets werden über Environment Variablen verwaltet
- Keine AWS Access Keys im Quellcode
- S3-Zugriff über IAM Role
- PostgreSQL als persistente Datenbank
- Containerisierte Backend-Anwendung

---

# 📖 Verwendung

Nach dem Start der Anwendung kann das Backend beispielsweise über folgende Adresse erreicht werden:

```text
http://localhost:5000
```

Die konkrete URL hängt von der lokalen Docker-Konfiguration bzw. dem AWS Deployment ab.

---

# 🤝 Mitwirken

Beiträge zu diesem Projekt sind willkommen.

1. Repository forken.
2. Einen Feature-Branch erstellen.
3. Änderungen implementieren.
4. Änderungen committen.
5. Branch pushen.
6. Pull Request erstellen.

---

# 📜 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert.
