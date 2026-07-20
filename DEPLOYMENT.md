# Stellar Agri AI - Deployment Guide

This guide provides step-by-step instructions for deploying **Stellar Agri AI** to production using free cloud platforms or Docker containers.

---

## 🚀 Option 1: One-Click Deployment on Render.com (Recommended - Free)

Render allows you to deploy the complete application (Frontend + FastAPI Backend) in a single service for free.

### Steps:
1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Stellar Agri AI"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/stellaragri.git
   git push -u origin main
   ```
2. Log in to [Render.com](https://render.com).
3. Click **New +** -> **Blueprint**.
4. Connect your GitHub repository (`stellaragri`). Render will automatically detect `render.yaml`.
5. Under **Environment Variables**, set:
   - `GEMINI_API_KEY`: Your Google Gemini API Key
   - `GROQ_API_KEY`: (Optional) Your Groq API Key
   - `WEATHER_API_KEY`: `59595d305ea74112b9c105207261907`
6. Click **Apply**. Render will build and deploy your app. Your public URL will be `https://stellar-agri-ai.onrender.com`.

---

## 🐳 Option 2: Containerized Deployment (Docker / Docker Compose)

You can run Stellar Agri AI on any server or VPS (DigitalOcean, AWS EC2, Linode, Hetzner) using Docker.

### Using Docker Compose:
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/stellaragri.git
cd stellaragri

# Start Container
docker-compose up -d --build
```
Your application will be live at `http://your-server-ip:8000`.

### Using Docker Directly:
```bash
docker build -t stellaragri -f backend/Dockerfile .
docker run -d -p 8000:8000 --env-file backend/.env --name stellaragri-app stellaragri
```

---

## 🌐 Option 3: Separate Frontend (Netlify/Vercel) + Backend (Render/Koyeb)

If you prefer hosting the frontend on Netlify or Vercel:

### 1. Backend Deployment (Render or Koyeb):
- Deploy the `backend/` directory as a Python Web Service.
- Set build command: `pip install -r backend/requirements.txt`
- Set start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### 2. Frontend Deployment (Netlify):
- Connect your GitHub repo to Netlify.
- Set Publish directory to `.`.
- In `netlify.toml`, update the redirect rule to your deployed backend URL.

---

## 🔑 Environment Variables Checklist

Ensure the following environment variables are set on your hosting platform:

| Variable | Description | Recommended Value |
|---|---|---|
| `PORT` | Web server port | `8000` (auto-set by Render/Koyeb) |
| `GEMINI_API_KEY` | Primary LLM Key | Your Gemini API Key |
| `GROQ_API_KEY` | Optional Secondary LLM Key | Your Groq API Key |
| `WEATHER_API_KEY` | Live Weather API Key | `59595d305ea74112b9c105207261907` |

---

## ✅ Health Check Verification

After deployment, test the health endpoint:
```bash
curl https://your-deployed-url.com/health
# Expected Output: {"status":"healthy"}
```
