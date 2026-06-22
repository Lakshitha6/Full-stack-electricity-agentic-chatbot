# ⚡ Electricity Board AI Chatbot

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi) ![React](https://img.shields.io/badge/React-18-61DAFB?logo=react) ![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript) ![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite) ![Tailwind](https://img.shields.io/badge/Tailwind-3-06B6D4?logo=tailwindcss) ![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase) ![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis) ![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker) ![License](https://img.shields.io/badge/License-MIT-green)

**An intelligent, production-ready chatbot that converts natural language queries into SQL, fetches real-time electricity billing data, and delivers conversational responses with JWT authentication, Redis caching, and a responsive UI.**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start-docker) • [API Docs](#-api-documentation) • [Deployment](#-manual-development-setup)

---

## 🌟 Overview

The **Electricity Board AI Chatbot** is a full-stack application that enables users to query electricity billing data using natural language. It translates questions like *"What’s my current balance?"* or *"Show my bills for March"* into secure SQL, executes them against PostgreSQL, and generates readable responses with Gemini/Groq LLMs.

### ✨ What Makes It Special

- 🧠 **Agentic Pipeline**: LangGraph orchestrates NL → SQL → validation → execution → response
- 🔒 **Production Security**: JWT auth, RLS-ready schema, parameterized queries, SQL injection protection
- ⚡ **Intelligent Caching**: Redis-backed response cache for repeat queries
- 💬 **Session Management**: Full chat history with create/switch/delete sessions
- 🎨 **Responsive UI**: Unified experience on mobile and desktop
- 🐳 **Docker-Ready**: One-command full-stack deployment
- 📊 **Audit Logging**: Every chat request is logged for compliance

---

## 🚀 Features

### Backend (FastAPI)

- ✅ Agentic NL→SQL pipeline with Gemini and Groq fallback
- ✅ JWT authentication with session cleanup on logout
- ✅ Three-tier memory: session context, episodic, semantic preferences
- ✅ Redis response cache with 10-minute TTL
- ✅ Background task queue using RQ
- ✅ Audit logging for all chat interactions
- ✅ Rate limiting to prevent abuse
- ✅ Supabase integration with Row-Level Security readiness
- ✅ Graceful degradation when Redis is unavailable

### Frontend (React + Vite)

- ✅ Unified chat UI with modal experience on desktop and mobile
- ✅ JWT-based authentication with protected routes
- ✅ Chat session history with create/switch/delete operations
- ✅ Optimistic UI for instant feedback
- ✅ Responsive design with Tailwind CSS
- ✅ Toast notifications for user feedback
- ✅ TypeScript for type safety
- ✅ React Query for smart fetching and caching

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                           │
│ Vite + TypeScript + Tailwind + Zustand + React Query       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON (JWT)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ BACKEND (FastAPI)                                           │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│ │ Auth API │ │ Chat API │ │ Agent    │ │ Cache    │          │
│ │ (JWT)    │ │          │ │(LangGraph)│ │ (Redis) │          │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└────────┬───────────────┬───────────────┬────────────────────┘
         │               │               │
         ▼               ▼               ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ Supabase │ │ Redis    │ │ Gemini/  │
│(Postgres)│ │(Cache +  │ │ Groq LLMs│
│          │ │ Queue)   │ │          │
└──────────┘ └──────────┘ └──────────┘

User Query
↓
[1] Intent Classification (Gemini)
↓
[2] SQL Generation (Gemini → Groq fallback)
↓
[3] SQL Validation (sqlglot security check)
↓
[4] Secure Execution (Supabase RPC)
↓
[5] Response Generation (Gemini)
↓
[6] Cache Store (Redis, 10-min TTL)
↓
Natural Language Response
```

---

## 🛠️ Tech Stack

| Layer             | Technology                 | Purpose                            |
|-------------------|----------------------------|------------------------------------|
| Frontend          | React 18 + TypeScript      | Type-safe UI framework             |
| Build Tool        | Vite 5                     | Fast development server            |
| Styling           | Tailwind CSS 3             | Utility-first CSS                  |
| State             | Zustand                    | Lightweight state management       |
| Data Fetching     | React Query                | Caching + background sync          |
| Backend           | FastAPI                    | Async Python web framework         |
| Agent             | LangGraph                  | Workflow orchestration             |
| LLM               | Gemini + Groq              | Primary + fallback models          |
| Database          | Supabase (PostgreSQL)      | Managed Postgres + Auth            |
| Cache             | Redis 7                    | Response cache + queue storage     |
| Queue             | RQ (Redis Queue)           | Background jobs                    |
| Containerization  | Docker + Compose           | Full-stack deployment              |
| Reverse Proxy     | Nginx                      | SPA routing + API proxy            |

---

## 📦 Quick Start (Docker)

The fastest way to run the entire stack:

```bash
git clone https://github.com/Lakshitha6/Full-stack-electricity-agentic-chatbot.git
cd Electricity-Board-Chatbot

cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

docker compose up --build -d
```

Open the app at:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### 🔧 Manual Development Setup

#### Prerequisites
- Python 3.11+
- Node.js 20+
- Redis 7+ (or Docker)
- Supabase account
- Gemini API key
- Groq API key

#### Backend Setup

```bash
cd backend
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn src.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Then browse to `http://localhost:3000`.

---

## 📁 Project Structure

```text
Electricity-Board-Chatbot/
├── Backend/
│   ├── .env
│   ├── .env.sample
│   ├── config/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── main.py
│   ├── migrations/
│   ├── pyproject.toml
│   ├── README.md
│   ├── requirements.txt
│   └── src/
│       ├── __init__.py
│       ├── main.py
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── chat_agent.py
│       │   ├── memory_manager.py
│       │   └── nl_to_sql.py
│       ├── api/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── chat.py
│       │   └── deps.py
│       ├── db/
│       │   ├── __init__.py
│       │   └── client.py
│       ├── middleware/
│       │   ├── audit_logger.py
│       │   ├── jwt_auth.py
│       │   └── rate_limiter.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── chat.py
│       │   └── user.py
│       ├── prompts/
│       │   ├── __init__.py
│       │   ├── personalization.yaml
│       │   ├── sql_generator.yaml
│       │   └── system_prompt.yaml
│       ├── services/
│       │   ├── __init__.py
│       │   ├── auth_service.py
│       │   ├── cache_service.py
│       │   ├── chat_service.py
│       │   └── preference_service.py
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── config_loader.py
│       │   ├── id_generator.py
│       │   ├── jwt_utils.py
│       │   ├── llm_router.py
│       │   └── sql_validator.py
│       └── workers/
│           └── preference_worker.py
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.js
│   ├── README.md
│   ├── tailwind.config.js
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.css
│       ├── App.tsx
│       ├── assets/
│       │   ├── hero.png
│       │   ├── react.svg
│       │   └── vite.svg
│       ├── components/
│       │   ├── chat/
│       │   │   ├── ChatFab.tsx
│       │   │   ├── ChatModal.tsx
│       │   │   ├── ChatWindow.tsx
│       │   │   ├── MessageBubble.tsx
│       │   │   └── SessionItem.tsx
│       │   ├── layout/
│       │   │   ├── MainLayout.tsx
│       │   │   ├── Navbar.tsx
│       │   │   └── ProtectedRoute.tsx
│       │   └── ui/
│       │       └── Toast.tsx
│       ├── hooks/
│       │   └── useChatSession.ts
│       ├── index.css
│       ├── main.tsx
│       ├── pages/
│       │   ├── Login.tsx
│       │   ├── Profile.tsx
│       │   └── Signup.tsx
│       ├── services/
│       │   ├── api.ts
│       │   ├── auth.ts
│       │   └── chat.ts
│       ├── store/
│       │   ├── authStore.ts
│       │   └── chatStore.ts
│       ├── types/
│       │   └── chat.ts
│       ├── utils/
│       │   ├── cn.ts
│       │   └── downloadFile.ts
│       ├── vite-env.d.ts
│       ├── index.css
│       └── main.tsx
├── docker-compose.yml
└── README.md
```

---

## 🔐 Environment Variables

### Backend (`.env`)

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# LLM APIs
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key

# JWT
JWT_SECRET=your-super-secret-min-32-chars
JWT_EXPIRY_MINUTES=1440

# Redis
REDIS_URL=redis://localhost:6379/0

# Cache
CHAT_CACHE_TTL=600

# App
APP_ENV=development
APP_PORT=8000
```

### Frontend

Local development uses Vite proxy, so no additional frontend env vars are required unless you want to override the backend URL.

```env
VITE_API_URL=https://your-backend-url.com
```

---

## 📚 API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive Swagger UI.

### Authentication Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/auth/register` | POST | Register a new user (returns `electricity_id`) |
| `/api/v1/auth/login` | POST | Login with `electricity_id` (returns JWT) |
| `/api/v1/auth/profile` | GET | Get current user profile (JWT required) |
| `/api/v1/auth/logout` | POST | Logout and end all sessions (JWT required) |
| `/api/v1/auth/account` | DELETE | Delete account (JWT required) |

### Chat Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/chat/sessions` | GET | List user's chat sessions |
| `/api/v1/chat/sessions` | POST | Create a new session |
| `/api/v1/chat/sessions/{id}/messages` | GET | Get messages for a session |
| `/api/v1/chat/message` | POST | Send a chat message |
```

---

## 📄 License

This project is licensed under the MIT License — see the `LICENSE` file for details.

---

## 🙌 Feedback

Your Name — lakshithasandakelum7768@gmail.com

Project Link: https://github.com/YOUR_USERNAME/Electricity-Board-Chatbot

> ⭐ If you found this project useful, please give it a star!
> 
> Made with ❤️ using FastAPI, React, and LangGraph
