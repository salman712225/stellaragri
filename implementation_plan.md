# Implementation Plan: Admin Sign-In & MongoDB Enquiry Management

Add secure **Admin Sign-In Authentication** and **MongoDB Atlas Enquiry Persistence** to store farmer call requests and manage them directly in the Admin Dashboard.

---

## 🏛️ Architecture & Flow

```mermaid
flowchart TD
    subgraph Farmer Flow
        Farmer[Farmer Web Portal (index.html)] -->|POST /api/request-call| API[FastAPI Server]
        API -->|1. Save Enquiry| MongoDB[(MongoDB Atlas / Local Fallback)]
        API -->|2. Trigger Call| SnapServe[SnapServe Voice Engine]
    end

    subgraph Admin Security Flow
        AdminUser[Admin User] -->|Visit /admin| AuthGuard{Is Authenticated?}
        AuthGuard -- No --> Login[Sign In Page (/login)]
        Login -->|POST /api/auth/login| AuthAPI[Auth Service]
        AuthAPI -->|Valid Token / Cookie| AdminDashboard[Admin Dashboard (/admin)]
        AuthGuard -- Yes --> AdminDashboard
    end

    subgraph Admin Features
        AdminDashboard --> Tab1[🤖 MCP & Voice Agents]
        AdminDashboard --> Tab2[📞 Live Call Logs & Transcripts]
        AdminDashboard --> Tab3[📋 Farmer Enquiries (MongoDB)]
        AdminDashboard --> Tab4[⚠️ Errors & Diagnostics]
        AdminDashboard --> Tab5[🚀 Outbound Dialer]
    end
```

---

## 📋 Implemented Changes

### 1. Authentication & Security Layer
- ✅ `frontend/pages/login.html`: Glassmorphic sign-in page with credential checking, auto-forwarding if already logged in, and automatic redirection to `/admin`.
- ✅ `backend/app/routes/auth.py`:
  - `POST /api/auth/login`: Issues tamper-proof HMAC session cookie & bearer token.
  - `POST /api/auth/logout`: Clears session cookie and logs out.
  - `GET /api/auth/me`: Verifies active session token.
- ✅ `backend/app/main.py`:
  - Enforces server-side authentication guard on `GET /admin` (redirects 302 to `/login` if unauthenticated).
  - Redirects authenticated users visiting `GET /login` straight to `/admin`.

### 2. MongoDB Atlas Database Layer
- ✅ `backend/app/core/database.py`:
  - Asynchronous Motor client with zero-crash automatic fallback to local JSON storage (`backend/storage/enquiries.json`).
  - CRUD operations: `save_enquiry()`, `get_enquiries()`, `update_enquiry_status()`, `delete_enquiry()`.
- ✅ `backend/app/routes/chat.py`: Automatically persists new call enquiries into MongoDB/storage upon dispatch.

### 3. Admin Dashboard Enhancements
- ✅ `frontend/pages/admin.html`:
  - Added **"📋 Farmer Enquiries"** tab with full lead details table.
  - Added **"🚪 Sign Out"** button in navbar.
  - Added quick action buttons: "📞 Redial", "✅ Mark Resolved", "🗑️ Delete".
- ✅ `frontend/js/admin.js`:
  - Client-side auth guard on page load.
  - Sign-out event listener.
  - Enquiries fetcher, status updater, live search, and filters.
- ✅ `backend/app/routes/admin.py`: Enquiries REST API (`GET /api/admin/enquiries`, `PATCH /api/admin/enquiries/{id}/status`, `DELETE /api/admin/enquiries/{id}`, `GET /api/admin/database-status`).

---

## 🔍 Verification Status
- ✅ **Automated Tests Passed**:
  - `GET /admin` without auth returns `302 Found` (redirect to `/login`).
  - `POST /api/auth/login` with invalid credentials returns `401 Unauthorized`.
  - `POST /api/auth/login` with valid credentials returns `200 OK` + session cookie.
  - `GET /admin` with valid session cookie returns `200 OK` (Admin Dashboard).
  - `GET /login` with valid session cookie returns `302 Found` (redirect to `/admin`).
  - `POST /api/auth/logout` terminates session and clears cookies.
