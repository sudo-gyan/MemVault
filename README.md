# MemVault

A comprehensive memory management system built with Django REST Framework that allows users, teams, and organizations to store and manage memories with intelligent processing via Mem0 AI integration.

## 🚀 Overview

MemVault is a powerful Django-based API that provides hierarchical memory management across three scopes:

- **User Memories**: Personal memory storage for individual users
- **Team Memories**: Shared memories within team contexts
- **Organization Memories**: Organization-wide memory storage and management

### Key Features

- 🏗️ **Hierarchical Organization Structure**: Users → Teams → Organizations
- 🤖 **AI Integration**: Automatic memory processing with Mem0 AI
- ⚡ **Asynchronous Processing**: Celery + Redis for background tasks
- 📦 **Docker Ready**: Complete containerized deployment setup
- 🔍 **Advanced Filtering**: Search, status filtering, and pagination
- 📊 **Class-Based Views**: Clean, maintainable REST API architecture

### Technology Stack

- **Backend**: Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Cache & Queue**: Redis + Celery
- **AI Integration**: Mem0 API
- **Deployment**: Docker + Docker Compose
- **Web Server**: Gunicorn (production)

## 🚀 Quick Start


### Deployment

1. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Configure production values in .env:**
   ```bash
   SECRET_KEY=your-super-secret-production-key-here
   DEBUG=False
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost
   POSTGRES_DB=memvault_prod
   POSTGRES_USER=memvault_user
   POSTGRES_PASSWORD=your-secure-database-password
   MEM0_API_KEY=your-actual-mem0-api-key
   ```

3. **Build and start services:**
   ```bash
   docker compose up -d --build
   ```

4. **Setup users:**

   Open Django Shell to Create User:
   ```bash
   docker exec -it memvault-web-1 bash
   python manage.py shell
   ```
   
   Run in Django Shell:
   ```python
   from user.models import User
   
   admin = User.objects.create_superuser(username='admin', password='admin123')
   USERS = {
       'alice':  'alice123',
       'bob': 'bob123',
       'charlie':'charlie123',
       'dana': 'dana123',  # Org A admin
       'eve': 'eve123',  # Org B admin
   }
   for username, password in USERS.items():
       USERS[username]=User.objects.create_user(username=username, password=password)
   ```

## 📚 API Documentation

### Authentication

All API endpoints require authentication. Include your API key in request headers:

```bash
X-API-Key: YOUR_API_KEY_HERE
```

### MemoryVault API

#### User Memory Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/memories/users/me/` | List user's memories |
| POST | `/api/memories/users/me/` | Create new user memory |
| GET | `/api/memories/users/me/{id}/` | Get specific memory |
| PATCH | `/api/memories/users/me/{id}/` | Update memory |
| DELETE | `/api/memories/users/me/{id}/` | Delete memory |

#### Team Memory Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/memories/teams/{team_id}/` | List team memories |
| POST | `/api/memories/teams/{team_id}/` | Create team memory |
| GET | `/api/memories/teams/{team_id}/{id}/` | Get specific team memory |
| PATCH | `/api/memories/teams/{team_id}/{id}/` | Update team memory |
| DELETE | `/api/memories/teams/{team_id}/{id}/` | Delete team memory |

#### Organization Memory Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/memories/orgs/{org_id}/` | List organization memories |
| POST | `/api/memories/orgs/{org_id}/` | Create organization memory |
| GET | `/api/memories/orgs/{org_id}/{id}/` | Get specific org memory |
| PATCH | `/api/memories/orgs/{org_id}/{id}/` | Update org memory |
| DELETE | `/api/memories/orgs/{org_id}/{id}/` | Delete org memory |

### Team Management API

#### Organization & Team Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/organizations/` | List user's organizations |
| GET | `/api/user/organizations/{org_id}/teams/` | List teams in organization |
| POST | `/api/user/organizations/{org_id}/teams/` | Create new team |
| GET | `/api/user/organizations/{org_id}/teams/{team_id}/` | Get team details |
| PUT | `/api/user/organizations/{org_id}/teams/{team_id}/` | Update team |
| DELETE | `/api/user/organizations/{org_id}/teams/{team_id}/` | Delete team |

#### Team Member Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/organizations/{org_id}/teams/{team_id}/members/` | List team members |
| POST | `/api/user/organizations/{org_id}/teams/{team_id}/members/` | Add team member |
| DELETE | `/api/user/organizations/{org_id}/teams/{team_id}/members/{user_id}/` | Remove member |

### Query Parameters

All memory list endpoints support:

- **Filtering**: `?status=completed&search=keyword`
- **Ordering**: `?ordering=-created_at`
- **Pagination**: `?page=2&page_size=20`
