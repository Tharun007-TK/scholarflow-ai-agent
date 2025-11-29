# 🚀 Deployment Guide: ScholarFlow AI on Vercel

Hosting this application on Vercel requires adapting the architecture because Vercel is a **Serverless** platform. Serverless functions are "stateless," meaning they forget everything (variables, uploaded files) as soon as a request finishes.

Your current app uses **in-memory storage** (`GlobalStore`) and **local file storage**, which will **NOT work** directly on Vercel.

Here is the checklist of what you need to change to make it production-ready:

## 1. 🗄️ Database (Required)
**Why:** You currently store chat history and parsed results in a Python list (`GlobalStore`). On Vercel, this list will be wiped clean after every single API call.
**What you need:**
- A cloud database like **Supabase** (PostgreSQL) or **MongoDB Atlas**.
- **Action:** Rewrite `api.py` to save/load data from the database instead of `store.history`.

## 2. ☁️ Cloud Storage (Required)
**Why:** You currently save PDFs to a temporary folder on your computer. Vercel functions cannot save files permanently.
**What you need:**
- A storage provider like **AWS S3**, **Google Cloud Storage**, or **Supabase Storage**.
- **Action:** Update the `/api/upload` endpoint to upload the PDF to the cloud and get a URL, instead of saving it locally.

## 3. ⚙️ Backend Adaptation
**Option A: Vercel Serverless (All-in-One)**
- You need to wrap `api.py` so Vercel can run it.
- Create an `api/index.py` entry point.
- **Pros:** Free, fast, single URL.
- **Cons:** 10-second timeout limit on free tier (might break long PDF processing).

**Option B: Separate Backend (Recommended)**
- Host the Frontend on **Vercel**.
- Host the Backend on **Render** or **Railway**.
- **Pros:** Persistent memory (easier migration), no timeout issues.
- **Cons:** Might need a paid plan for "always-on" services.

## 4. 🔑 Environment Variables
You need to add these secrets to your Vercel Project Settings:
- `GOOGLE_API_KEY`: For Gemini.
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET`: For Calendar.
- `NEXT_PUBLIC_API_URL`: The URL of your backend (e.g., `https://api.scholarflow.com`).

## 5. 🌐 Google Cloud Console Updates
**Why:** Google only allows logins from authorized domains.
**Action:**
- Go to Google Cloud Console > APIs & Services > Credentials.
- Add your Vercel domain (e.g., `https://scholarflow.vercel.app`) to **Authorized JavaScript origins**.
- Add `https://scholarflow.vercel.app/api/auth/callback` to **Authorized redirect URIs**.

---

## 📝 Summary Recommendation

If you want to deploy **right now** with minimal code changes:

1.  **Frontend**: Deploy `frontend/` to **Vercel**.
2.  **Backend**: Deploy the root directory to **Render** (it supports persistent web services).
3.  **Connect**: Set `NEXT_PUBLIC_API_URL` in Vercel to point to your Render backend URL.

This avoids the need to rewrite the entire app for serverless immediately.
