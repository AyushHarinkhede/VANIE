# 🚀 VANIE Deployment & Production Setup Guide

## Overview

This guide covers everything needed to deploy VANIE in different environments:
- Local development
- Production server
- Cloud platforms
- Docker containerization

---

## 🏠 Local Development Setup

### Windows
```batch
@echo off
cd /d "C:\Users\AASHU\Documents\Ayush🍌\VANIE👾"
pip install -r requirements.txt
python VANIE_FIXED.py
```

### Linux/Mac
```bash
cd ~/VANIE
pip3 install -r requirements.txt
python3 VANIE_FIXED.py
```

### Verify Setup
```bash
# In another terminal/tab
curl http://localhost:5000/health
# Should return: {"status": "healthy", "version": "2.0-FIXED"}
```

---

## 🌐 Production Deployment

### Option 1: Using Gunicorn (Production-Grade)

#### Install Gunicorn
```bash
pip install gunicorn
```

#### Create Production Config (gunicorn_config.py)
```python
workers = 4
worker_class = 'sync'
bind = '0.0.0.0:5000'
timeout = 30
keepalive = 2
errorlog = 'error.log'
accesslog = 'access.log'
loglevel = 'info'
```

#### Run with Gunicorn
```bash
gunicorn -c gunicorn_config.py VANIE_FIXED:app
```

### Option 2: Using Waitress (Windows-Friendly)

#### Install
```bash
pip install waitress
```

#### Create startup.py
```python
from waitress import serve
from VANIE_FIXED import app

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
```

#### Run
```bash
python startup.py
```

### Option 3: Using WSGI with Apache

1. Install mod_wsgi
2. Configure Apache VirtualHost
3. Point to VANIE app

---

## 🐳 Docker Deployment

### Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY VANIE_FIXED.py .
COPY VANIE_FIXED.html .

EXPOSE 5000

CMD ["python", "VANIE_FIXED.py"]
```

### Build Docker Image
```bash
docker build -t vanie:latest .
```

### Run Docker Container
```bash
docker run -p 5000:5000 vanie:latest
```

### Docker Compose
Create docker-compose.yml:
```yaml
version: '3.8'
services:
  vanie:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./logs:/app/logs
```

Run:
```bash
docker-compose up
```

---

## ☁️ Cloud Deployment

### Heroku

1. **Create requirements.txt** (already done)

2. **Create Procfile**
```
web: gunicorn VANIE_FIXED:app
```

3. **Create runtime.txt**
```
python-3.9.7
```

4. **Deploy**
```bash
heroku login
heroku create vanie-assistant
git push heroku main
heroku open
```

### AWS (EC2)

1. **Launch EC2 Instance**
   - Use Ubuntu 20.04 LTS
   - Allow ports 80, 443, 5000

2. **SSH into Instance**
```bash
ssh -i key.pem ubuntu@your-instance-ip
```

3. **Install Dependencies**
```bash
sudo apt update
sudo apt install python3-pip
sudo apt install nginx
```

4. **Setup Application**
```bash
cd /home/ubuntu
git clone <your-repo>
cd VANIE
pip3 install -r requirements.txt
```

5. **Configure Nginx**
Create `/etc/nginx/sites-available/vanie`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

6. **Enable and Start**
```bash
sudo ln -s /etc/nginx/sites-available/vanie /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

7. **Run VANIE**
```bash
python3 VANIE_FIXED.py
```

### Google Cloud Platform (GCP)

1. **Create App Engine app**
```bash
gcloud app create
```

2. **Create app.yaml**
```yaml
runtime: python39

env: standard
entrypoint: gunicorn -b :$PORT VANIE_FIXED:app

env_variables:
  FLASK_ENV: "production"
```

3. **Deploy**
```bash
gcloud app deploy
```

### Azure

1. **Create App Service**
```bash
az group create -n vanie-group -l eastus
az appservice plan create -n vanie-plan -g vanie-group --sku B1
```

2. **Deploy App**
```bash
az webapp create -n vanie -g vanie-group -p vanie-plan
az webapp config appsettings set -n vanie -g vanie-group --settings WEBSITES_PORT=5000
```

3. **Configure for Python**
```bash
az webapp deployment source config-zip -n vanie -g vanie-group --src VANIE.zip
```

---

## 🔒 Security Configuration

### HTTPS Setup

#### Generate SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d your-domain.com
```

#### Update Nginx Config
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Rest of config...
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### Rate Limiting
Add to VANIE_FIXED.py:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
```

### Environment Variables
Create .env file:
```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key
MAX_CONTENT_LENGTH=16777216
```

---

## 📊 Monitoring & Logging

### Setup Logging
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('vanie.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('VANIE startup')
```

### Performance Monitoring
```bash
# Install New Relic
pip install newrelic

# Run with monitoring
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program python VANIE_FIXED.py
```

### Health Checks
```bash
# Systemd service file (/etc/systemd/system/vanie.service)
[Unit]
Description=VANIE AI Assistant
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/vanie
ExecStart=/usr/bin/python3 VANIE_FIXED.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🚀 Auto-Start Configurations

### Windows Startup Script
Create vanie-startup.vbs:
```vbscript
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd /k python VANIE_FIXED.py", 0
WScript.Sleep 1000
```

### Linux Systemd Service
```ini
[Unit]
Description=VANIE Backend Service
After=network.target

[Service]
Type=simple
User=vanie
WorkingDirectory=/opt/vanie
ExecStart=/usr/bin/python3 VANIE_FIXED.py
Restart=on-failure
StandardOutput=append:/var/log/vanie/stdout.log
StandardError=append:/var/log/vanie/stderr.log

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable vanie
sudo systemctl start vanie
```

---

## 🧪 Testing in Production

### Load Testing
```bash
pip install locust
```

Create locustfile.py:
```python
from locust import HttpUser, task, between

class VanieUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def chat(self):
        self.client.post("/chat", json={"message": "Hello"})
    
    @task
    def health(self):
        self.client.get("/health")
```

Run:
```bash
locust -f locustfile.py --host=http://localhost:5000
```

### Smoke Testing
```python
import requests
import time

BASE_URL = "http://localhost:5000"

# Health check
r = requests.get(f"{BASE_URL}/health")
assert r.status_code == 200

# Chat test
r = requests.post(f"{BASE_URL}/chat", json={"message": "Hello"})
assert r.status_code == 200
assert 'response' in r.json()

# DateTime test
r = requests.get(f"{BASE_URL}/info/datetime")
assert r.status_code == 200

print("✓ All smoke tests passed!")
```

---

## 📋 Pre-Deployment Checklist

- [ ] All dependencies in requirements.txt
- [ ] .env file configured
- [ ] HTTPS certificates ready
- [ ] Logging configured
- [ ] Database backups setup
- [ ] Monitoring enabled
- [ ] Rate limiting configured
- [ ] CORS properly set
- [ ] Error handling tested
- [ ] Performance tested
- [ ] Security headers added
- [ ] Documentation updated

---

## 🔄 Continuous Deployment

### GitHub Actions
Create .github/workflows/deploy.yml:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: "vanie-assistant"
          heroku_email: ${{ secrets.HEROKU_EMAIL }}
```

---

## 📊 Performance Optimization

### Caching
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/info/weather')
@cache.cached(timeout=300)
def get_weather():
    # Returns cached for 5 minutes
    return jsonify(vanie_engine.get_weather_info())
```

### Compression
```bash
pip install flask-compress
```

```python
from flask_compress import Compress
Compress(app)
```

---

## 🎓 Best Practices

1. **Always use HTTPS** in production
2. **Enable logging** for debugging
3. **Set proper CORS** headers
4. **Use environment variables** for secrets
5. **Implement rate limiting** to prevent abuse
6. **Monitor performance** metrics
7. **Regular backups** of data
8. **Security updates** regularly
9. **Test thoroughly** before deployment
10. **Document everything** clearly

---

## ✅ Deployment Complete!

Your VANIE is now ready for production use with:
- ✅ Scalable infrastructure
- ✅ Security features
- ✅ Monitoring & logging
- ✅ Auto-restart capability
- ✅ HTTPS support
- ✅ Performance optimization

---

**Happy Deployment! 🚀**
