# Production Deployment Guide
## Student Placement Data Analysis System

This guide outlines production deployment methods suitable for institutional servers, 24/7 cloud hosting, and containerized Docker environments.

---

## 🌐 Option 1: 24/7 Cloud Hosting (Render.com + Free Managed MySQL)
*Best for: A permanent live production deployment on a cloud domain (`https://student-placement.onrender.com`).*

### Step 1.1: Provision Cloud MySQL Database
Pair Render with a managed cloud MySQL provider:
- **Provider A: Aiven Free MySQL**: [https://aiven.io](https://aiven.io) (Managed MySQL with SSL).
- **Provider B: TiDB Cloud (Serverless MySQL)**: [https://tidbcloud.com](https://tidbcloud.com) (5 GB free permanent MySQL-compatible cluster).
- **Provider C: Railway.app**: [https://railway.app](https://railway.app) (Managed MySQL service).

1. Create a free account on **Aiven**, **TiDB Cloud**, or **Railway**.
2. Create a MySQL database named `placement_db`.
3. Note your connection details:
   - `Host` (e.g., `mysql-instance.aivencloud.com`)
   - `Port` (e.g., `3306` or custom)
   - `User` (e.g., `avnadmin`)
   - `Password`
   - `Database Name` (`placement_db`)
4. Run the database migrations to set up tables and indexes:
   ```bash
   python migrations/migrate.py
   python init_db.py --create-admin
   ```

### Step 1.2: Deploy Web Service to Render.com
1. Push your repository to GitHub:
   ```bash
   git push origin main
   ```
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** &rarr; select **Web Service**.
4. Connect your GitHub repository: `student-placement-data-analysis-system`.
5. Configure the deployment settings:
   - **Name:** `student-placement-system`
   - **Environment:** `Python 3`
   - **Region:** Frankfurt / Singapore / Oregon (select closest to your MySQL instance)
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt && python migrations/migrate.py`
   - **Start Command:** `gunicorn wsgi:app --workers 2 --bind 0.0.0.0:$PORT`
   - **Plan:** `Free`
6. Scroll down to **Environment Variables** and add the following keys:
   | Key | Value Description |
   |---|---|
   | `DB_HOST` | Cloud database hostname |
   | `DB_PORT` | Cloud database port |
   | `DB_USER` | Cloud database user |
   | `DB_PASSWORD` | Cloud database password |
   | `DB_NAME` | `placement_db` |
   | `DB_SSL` | `true` (if using Aiven / TiDB SSL) |
   | `SECRET_KEY` | Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
   | `FLASK_ENV` | `production` |
   | `DEBUG` | `false` |
   | `DEMO_MODE` | `false` |
7. Under **Health Check Path**, enter: `/api/health`
8. Click **Create Web Service**. Render will install dependencies, execute migrations, verify `/api/health`, and assign a public HTTPS domain.

---

## 🐳 Option 2: Docker Multi-Container Deployment
*Best for: Running the entire isolated stack (MySQL 8.0 + Python Gunicorn) anywhere Docker is installed.*

The repository includes a production-grade `Dockerfile` and `docker-compose.yml`.

1. Copy `.env.example` to `.env` and fill in your secrets:
   ```bash
   cp .env.example .env
   ```
2. Launch the container stack:
   ```bash
   docker compose up -d --build
   ```
3. Docker will automatically:
   - Pull and initialize the `mysql:8.0` container with volume persistence.
   - Run `schema.sql` on first boot.
   - Build the Python web application container and launch `gunicorn wsgi:app`.
4. Open your browser at **`http://localhost:5000`**.
5. To view live logs:
   ```bash
   docker compose logs -f web
   ```
6. To gracefully stop the cluster:
   ```bash
   docker compose down
   ```

---

## 📶 Option 3: College Campus LAN / Intranet Deployment
*Best for: On-premise institutional presentations without requiring external cloud access.*

1. Connect your hosting machine to the institutional Wi-Fi or local network.
2. Find your local IPv4 address in PowerShell:
   ```powershell
   ipconfig
   ```
   *(e.g., `192.168.1.50`)*
3. Run the production WSGI server:
   ```powershell
   python wsgi.py
   ```
4. Other authorized devices on the same subnet can navigate directly to:
   ```text
   http://192.168.1.50:5000
   ```

---

## 💾 Database Backup & Disaster Recovery

Run the included backup script to generate timestamped database dumps:
```bash
python scripts/backup_db.py
```
This utility:
- Automatically uses `mysqldump` if available on your system PATH.
- Gracefully falls back to pure-Python export if `mysqldump` is absent.
- Stores backups in `backups/placement_db_backup_<YYYYMMDD_HHMMSS>.sql` (excluded from git).

---

## Production Files Summary

- `wsgi.py`: Production WSGI application entry point.
- `Procfile`: Gunicorn runner command for PaaS platforms (`web: gunicorn wsgi:app --workers 2 --bind 0.0.0.0:$PORT`).
- `Dockerfile`: Multi-stage Python 3.11 container with health check.
- `docker-compose.yml`: Automated composition of web + MySQL 8.0 services.
- `render.yaml`: Infrastructure-as-code blueprint specification.
- `migrations/migrate.py`: Idempotent database migration executor.
- `scripts/backup_db.py`: MySQL database backup and rotation utility.
