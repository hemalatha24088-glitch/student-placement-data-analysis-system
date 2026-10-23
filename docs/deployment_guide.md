# Complete Deployment Guide
## Student Placement Data Analysis System

This guide outlines **4 deployment methods** suitable for college reviews, live faculty presentations, and permanent 24/7 cloud hosting.

---

## 🚀 Option 1: Instant Free Public HTTPS URL (Easiest for Faculty Viva)
*Best for: Showing your live running system to professors or opening it on a mobile device immediately without paying for cloud servers.*

You can expose your locally running Flask app through a secure, temporary HTTPS tunnel using **Cloudflare Tunnel (Free, no account needed)** or **Ngrok**.

### Using Cloudflare Quick Tunnel (Recommended & Free):
1. Download the standalone Windows executable `cloudflared.exe` from [Cloudflare Releases](https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe) or install it via winget in PowerShell:
   ```powershell
   winget install --id Cloudflare.cloudflared
   ```
2. With your Flask application running on port `5000`, open a second PowerShell window and run:
   ```powershell
   cloudflared tunnel --url http://127.0.0.1:5000
   ```
3. Cloudflare will output an instant public URL such as:
   ```text
   https://random-words-here.trycloudflare.com
   ```
4. Anyone on the internet can open this HTTPS link on their phone, laptop, or tablet and interact with your placement system live!

---

## 🌐 Option 2: 24/7 Free Cloud Hosting (Render.com + Free Cloud MySQL)
*Best for: A permanent live portfolio project on your resume with a custom cloud domain (`https://student-placement.onrender.com`).*

### Step 2.1: Get a Free Cloud MySQL Database
Since Render's free tier specializes in web servers, pair it with a free cloud MySQL provider:
- **Provider A: TiDB Cloud (Free Serverless MySQL)**: [https://tidbcloud.com](https://tidbcloud.com) (5 GB free permanent MySQL compatible database).
- **Provider B: Aiven Free MySQL**: [https://aiven.io](https://aiven.io) (Free managed MySQL tier).
- **Provider C: Railway.app**: [https://railway.app](https://railway.app) (Free trial MySQL service).

1. Create a free account on **TiDB Cloud** or **Aiven**.
2. Click **Create Cluster** &rarr; select **Serverless (Free)**.
3. Note your cloud database connection parameters:
   - `DB_HOST`: (e.g. `gateway01.ap-southeast-1.prod.aws.tidbcloud.com`)
   - `DB_PORT`: `4000` (or `3306`)
   - `DB_USER`: (e.g. `2aXxxx.root`)
   - `DB_PASSWORD`: (your generated cloud password)
   - `DB_NAME`: `placement_db`
4. Connect using any MySQL client or run `init_db.py` once against the cloud DB to create tables and seed synthetic data.

### Step 2.2: Push Code to GitHub
1. Initialize git and commit your project:
   ```powershell
   cd "c:\Users\M Hemalatha\Desktop\spd"
   git init
   git add .
   git commit -m "Student Placement Analytics full-stack project"
   ```
2. Create a new repository on [GitHub.com](https://github.com) named `student-placement-analysis`.
3. Link and push your repository:
   ```powershell
   git remote add origin https://github.com/<your-username>/student-placement-analysis.git
   git branch -M main
   git push -u origin main
   ```

### Step 2.3: Deploy on Render.com
1. Go to [https://render.com](https://render.com) and sign in with GitHub.
2. Click **New +** &rarr; select **Web Service**.
3. Select your `student-placement-analysis` repository.
4. Set the following settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
5. In **Environment Variables**, add:
   - `DB_HOST`: Your cloud database host
   - `DB_PORT`: Your cloud database port
   - `DB_USER`: Your cloud database username
   - `DB_PASSWORD`: Your cloud database password
   - `DB_NAME`: `placement_db`
   - `SECRET_KEY`: Any secure random string
6. Click **Create Web Service**. Within 2 minutes, your application is live on `https://<your-app-name>.onrender.com`!

---

## 📶 Option 3: College Campus LAN / Wi-Fi Deployment
*Best for: Letting faculty and examiners connect to your laptop directly over the college Wi-Fi or lab network without internet access.*

1. Connect your laptop to the college Wi-Fi or hotspot.
2. Find your laptop's local IPv4 address by running in PowerShell:
   ```powershell
   ipconfig
   ```
   *(Look for `IPv4 Address`, e.g., `192.168.1.45` or `10.0.0.12`).*
3. Run the production Waitress server bound to all network interfaces (`0.0.0.0`):
   ```powershell
   cd "c:\Users\M Hemalatha\Desktop\spd"
   .\.venv\Scripts\python.exe wsgi.py
   ```
4. Now, any faculty member or student connected to the same Wi-Fi can open their phone or laptop browser and visit:
   ```text
   http://192.168.1.45:5000
   ```
   *(Replace `192.168.1.45` with your actual IPv4 address).*

---

## 🐳 Option 4: Docker Container Deployment
*Best for: Running the entire stack (MySQL 8.0 + Web Application) in isolated containers anywhere with Docker installed.*

A pre-configured `docker-compose.yml` and `Dockerfile` are already included in the root directory.

1. Ensure **Docker Desktop** is running on your machine.
2. Open PowerShell in the project directory:
   ```powershell
   cd "c:\Users\M Hemalatha\Desktop\spd"
   ```
3. Launch both the MySQL 8.0 database container and the Flask web application container:
   ```powershell
   docker compose up -d --build
   ```
4. Docker will:
   - Download and start the `mysql:8.0` container.
   - Automatically execute `schema.sql` and `seed.sql` on startup.
   - Build and start the Python web container running with `gunicorn`.
5. Open your browser at **`http://localhost:5000`**.
6. To shut down the containers:
   ```powershell
   docker compose down
   ```

---

## Summary of Prepared Production Files

- `wsgi.py`: Production WSGI wrapper (Waitress / Gunicorn).
- `Procfile`: Gunicorn command for cloud PaaS (Render / Railway / Heroku).
- `Dockerfile`: Minimal Linux container with Python 3.11, GCC, and system dependencies.
- `docker-compose.yml`: Automated multi-container orchestration for Web + MySQL 8.0.
- `render.yaml`: Automated 1-click Render blueprint specification.
