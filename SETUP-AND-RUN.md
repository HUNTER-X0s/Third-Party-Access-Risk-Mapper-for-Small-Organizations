# 🚀 AccessGuard — Setup & Run Guide

---

## 📋 Table of Contents

1. [What You Need (Prerequisites)](#1-what-you-need-prerequisites)
2. [Download the Project](#2-download-the-project)
3. [Set Up the Backend (Python)](#3-set-up-the-backend-python)
4. [Set Up the Frontend (Node.js)](#4-set-up-the-frontend-nodejs)
5. [Configure Environment Variables](#5-configure-environment-variables)
6. [Run the Project](#6-run-the-project)
7. [Open in Browser & Login](#7-open-in-browser--login)
8. [Run the Test Suite (Optional)](#8-run-the-test-suite-optional)
9. [Stopping the Project](#9-stopping-the-project)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. What You Need (Prerequisites)

Before you start, make sure you have these three programs installed on your computer.

### ✅ Python 3.11 or higher

> Python runs the backend (the server side of AccessGuard).

**Check if you already have Python:**
```
python --version
```
If you see `Python 3.11.x` or higher — you are good! ✅  
If not, download it from: **https://www.python.org/downloads/**

> ⚠️ **IMPORTANT during Python installation on Windows:**  
> Tick the checkbox that says **"Add Python to PATH"** before clicking Install.

---

### ✅ Node.js 18 or higher

> Node.js runs the frontend (the website you see in your browser).

**Check if you already have Node.js:**
```
node --version
```
If you see `v18.x.x` or higher — you are good! ✅  
If not, download it from: **https://nodejs.org/** (choose the "LTS" version)

---

### ✅ Git (to download the project)

**Check if you already have Git:**
```
git --version
```
If not, download it from: **https://git-scm.com/downloads**

---

## 2. Download the Project

Open a terminal (Command Prompt or PowerShell on Windows, Terminal on Mac/Linux) and run:

```bash
git clone https://github.com/your-org/accessguard.git
```

Then move into the project folder:
```bash
cd accessguard
```

> 💡 **What is a terminal?**  
> On Windows: Press `Win + R`, type `cmd`, press Enter.  
> On Mac: Press `Cmd + Space`, type `Terminal`, press Enter.

---

## 3. Set Up the Backend (Python)

The backend is the server that powers AccessGuard. Follow these steps carefully.

### Step 3.1 — Move into the backend folder

```bash
cd backend
```

### Step 3.2 — Create a virtual environment

A virtual environment keeps AccessGuard's Python packages separate from the rest of your computer. Think of it as a clean room just for this project.

**On Windows (Command Prompt or PowerShell):**
```
python -m venv venv
```

**On Mac / Linux:**
```
python3 -m venv venv
```

You should now see a new folder called `venv` inside the `backend` folder. That's correct. ✅

### Step 3.3 — Activate the virtual environment

You must activate the virtual environment every time you want to run the backend.

**On Windows (PowerShell):**
```
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```
.\venv\Scripts\activate.bat
```

**On Mac / Linux:**
```
source venv/bin/activate
```

> ✅ You will know it worked when you see `(venv)` at the start of your terminal line, like this:
> ```
> (venv) C:\accessguard\backend>
> ```

> ⚠️ **Windows PowerShell Policy Error?**  
> If you see a message about "running scripts is disabled", run this command first:
> ```
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try the activation command again.

### Step 3.4 — Install Python packages

```
pip install -r requirements.txt
```

This downloads all the Python libraries AccessGuard needs. It may take 1–2 minutes.

### Step 3.5 — Go back to the project root

```
cd ..
```

---

## 4. Set Up the Frontend (Node.js)

The frontend is the website interface you see in your browser.

### Step 4.1 — Open a **second terminal window**

Keep your first terminal open (you will use it for the backend). Open a fresh new terminal.

### Step 4.2 — Move into the frontend folder

```
cd accessguard/frontend
```

(Or if you are already in the `accessguard` folder: `cd frontend`)

### Step 4.3 — Install Node.js packages

```
npm install
```

This downloads all the JavaScript libraries the frontend needs. It may take 1–3 minutes.

> ✅ When it finishes without any red `ERROR` text, you are ready.

---

## 5. Configure Environment Variables

AccessGuard needs a configuration file to know its secret key, database location, and organization name. This is a one-time setup.

### Step 5.1 — Copy the example configuration file

**On Windows (Command Prompt / PowerShell):**
```
copy .env.example backend\.env
```

**On Mac / Linux:**
```
cp .env.example backend/.env
```

### Step 5.2 — (Optional) Edit the configuration

For a quick local test run, **you do not need to change anything**. The default settings work out of the box.

If you want to customize, open `backend/.env` in any text editor (Notepad, VS Code, etc.) and change:

```env
# The name of your organization shown in the platform
ORGANIZATION_NAME="Your Organization Name"
ORGANIZATION_DOMAIN="yourorg.tech"

# Secret key — MUST be changed in production (keep it long and random)
SECRET_KEY="CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY_IN_PRODUCTION"
```

> 🔒 **Never share your `.env` file or commit it to GitHub.** It contains your secret key.

---

## 6. Run the Project

You need **two terminals running at the same time** — one for the backend and one for the frontend.

### 🖥️ Terminal 1 — Start the Backend

Make sure you are in the project root folder (`accessguard/`) and your virtual environment is activated (you should see `(venv)` at the start of the line).

**On Windows:**
```powershell
$env:PYTHONPATH = "backend"
.\backend\venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload
```

**On Mac / Linux:**
```bash
export PYTHONPATH=backend
backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

> ✅ **Success looks like this:**
> ```
> INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
> INFO:     Started reloader process
> INFO:     Application startup complete.
> ```

> 💡 The first time it starts, AccessGuard automatically creates the database and seeds all the demo data. This is normal and expected.

---

### 🌐 Terminal 2 — Start the Frontend

In your **second terminal**, make sure you are in the `frontend/` folder:

```
cd accessguard/frontend
```

Then run:
```
npm run dev
```

> ✅ **Success looks like this:**
> ```
>   VITE v5.4.x  ready in 800 ms
>
>   ➜  Local:   http://localhost:5173/
>   ➜  Network: http://192.168.x.x:5173/
> ```

---

## 7. Open in Browser & Login

Open your web browser (Chrome, Firefox, Edge) and go to:

```
http://localhost:5173
```

You will see the AccessGuard login page. Use any of these demo accounts:

| Role | Email | Password | What You Can Do |
|------|-------|----------|-----------------|
| 🔴 **Super Admin** | `superadmin@anurag.tech` | `DemoPass123!` | Everything — user management, system reset |
| 🟠 **Security Admin** | `admin@anurag.tech` | `DemoPass123!` | Full security operations — recommended for demos |
| 🔵 **Auditor** | `auditor@anurag.tech` | `DemoPass123!` | Read-only — view findings & evidence |
| 🟢 **App Owner** | `devops@anurag.tech` | `DemoPass123!` | Restricted to assigned applications |
| ⚪ **Viewer** | `viewer@anurag.tech` | `DemoPass123!` | Dashboard overview only |

> 💡 **Recommended for first login:** Use `admin@anurag.tech` with password `DemoPass123!` — this gives you full access to explore all features.

---

### 🗺️ What to Explore First

Once logged in:

| Page | What to Look At |
|------|-----------------|
| **Overview (Dashboard)** | Security posture score, blast radius, KPI metrics, priority queue |
| **Applications** | All third-party SaaS apps and their risk scores |
| **Findings** | Security vulnerabilities discovered by the risk engine |
| **Access Map** | Interactive graph of who has access to what |
| **Monitoring** | Real-time change detection and security incidents |
| **Suppliers (C-SCRM)** | Supply chain risk for vendors |
| **Connectors** | Live SaaS integration management |

---

## 8. Run the Test Suite (Optional)

AccessGuard includes 102 automated security tests. To run them:

Make sure your virtual environment is active and you are in the project root, then:

**On Windows:**
```powershell
$env:PYTHONPATH = "backend"
.\backend\venv\Scripts\pytest backend/tests/ -v
```

**On Mac / Linux:**
```bash
export PYTHONPATH=backend
backend/venv/bin/pytest backend/tests/ -v
```

> ✅ You should see all 102 tests pass. This confirms the entire security engine and backend are working correctly.

---

## 9. Stopping the Project

To stop the servers:

- In **Terminal 1** (backend): Press `Ctrl + C`
- In **Terminal 2** (frontend): Press `Ctrl + C`

---

## 10. Troubleshooting

### ❌ "python is not recognized" or "python3 is not found"

Python is not installed or not added to PATH.  
**Fix:** Reinstall Python from https://www.python.org/downloads/ and make sure to check **"Add Python to PATH"** during installation.

---

### ❌ "npm is not recognized"

Node.js is not installed.  
**Fix:** Download and install Node.js from https://nodejs.org/ (choose the LTS version), then close and reopen your terminal.

---

### ❌ Backend starts but shows database errors on first run

The database is being created for the first time.  
**Fix:** Wait 5–10 seconds and look for `Application startup complete.` It should resolve itself. If it doesn't, delete any `.db` file in the `backend/` folder and restart.

**On Windows:**
```powershell
Remove-Item backend\*.db -ErrorAction SilentlyContinue
```

**On Mac / Linux:**
```bash
rm -f backend/*.db
```

---

### ❌ "Port 8000 is already in use"

Something else is using port 8000.  
**Fix:** Either stop that program, or change the port:
```
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```
If you change the backend port, also update `frontend/vite.config.ts` — change `target: 'http://127.0.0.1:8000'` to match the new port.

---

### ❌ "Port 5173 is already in use"

Another Vite project is running.  
**Fix:** Stop it, or Vite will automatically try port 5174, 5175, etc. Check the terminal output to see which port it picked.

---

### ❌ PowerShell says "running scripts is disabled"

Windows is blocking the virtual environment activation script.  
**Fix:** Run this once in PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### ❌ Frontend loads but shows "Failed to fetch" or API errors

The backend is not running, or the ports don't match.  
**Fix:**
1. Make sure Terminal 1 (backend) is running and shows `Application startup complete.`
2. Make sure you are using `http://localhost:5173` — not `http://127.0.0.1:5173`.

---

### ❌ npm install fails with permission errors (Mac/Linux)

**Fix:** Do NOT use `sudo npm install`. Instead, fix npm permissions:
```bash
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

---

## 📂 Quick Reference — File Locations

| File | Purpose |
|------|---------|
| `backend/.env` | Your configuration (secret key, DB URL, org name) |
| `backend/accessguard.db` | The SQLite database (auto-created on first run) |
| `backend/requirements.txt` | Python dependencies list |
| `frontend/package.json` | Node.js dependencies list |
| `frontend/src/` | Frontend React source code |
| `backend/app/` | Backend FastAPI source code |
| `backend/tests/` | 102 automated security tests |

---

## 🆘 Still Stuck?

If you have followed every step and something still doesn't work:

1. Check the terminal output carefully — the error message almost always tells you what went wrong.
2. Make sure both terminals are running — the backend **and** the frontend must be running at the same time.
3. Try restarting both terminals from scratch.
4. Open a GitHub Issue with the full error message pasted in.

---

<div align="center">

**✅ You're all set! AccessGuard should now be running at http://localhost:5173**

*If this guide helped you, consider giving the repository a ⭐ on GitHub!*

</div>
