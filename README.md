# 🚀 TaskFlow — Team Task & Project Management Web Application

[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.15+-red?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

**TaskFlow** is a production-style, role-based Team Task & Project Management web application built with **Python**, **Django**, and **Django REST Framework (DRF)**. It bridges server-rendered Django templates with an asynchronous, interactive JavaScript Kanban board powered by a RESTful API.

Designed and engineered following enterprise Python/Django standards: zero N+1 database queries, custom role-based access control, database indexing, comprehensive automated unit tests, and production logging.

---

## 📌 Key Features

### 1. Role-Based Access Control (RBAC) & Authentication
- **Custom User Model (`accounts.User`)**: Extends Django's `AbstractUser` with explicit role choices:
  - 👑 **Admin**: Full system authority across all projects, tasks, and users.
  - 💼 **Manager**: Can create new projects, add/remove team members, and assign tasks.
  - 👤 **Member**: Can view assigned projects, update task statuses, and post comments.
- **Enhanced UX**: Includes password show/hide toggle buttons on login and registration pages.
- **Smart Auto-Enrollment**: Automatically enrolls newly registered team members into default workspaces.

### 2. Projects & Team Collaboration
- Dedicated project workspaces with Many-to-Many team membership via an explicit intermediate table (`ProjectMembership`).
- Prevents duplicate assignments with database-level `UniqueConstraint`.
- Lead/creator assignment and team roster overview.

### 3. Task Management & Discussion
- Tasks with **Priority** (`Low`, `Medium`, `High`, `Urgent`), **Status** (`To Do`, `In Progress`, `Done`), and **Due Date**.
- Real-time `is_overdue` calculation banner.
- Threaded task comments timeline for team activity history.

### 4. Interactive JavaScript Kanban Board (Zero Page Reload)
- Responsive 3-column Kanban interface (`To Do`, `In Progress`, `Done`).
- Uses **HTML5 Drag-and-Drop API** paired with native **JavaScript `fetch()`** to call `PATCH /api/tasks/{id}/update-status/` in real time.
- Integrated **Quick-Move Action Menus** for mobile/touchscreen accessibility.
- Automatic column counter updates and Bootstrap Toast feedback.

### 5. Robust Django REST Framework (DRF) API
- Token-based (`Authorization: Token <key>`) and session-based authentication.
- Field-level validation: rejects due dates in the past with HTTP 400.
- Object-level validation: ensures assignees belong to the target project.
- Custom permission class (`IsProjectMemberOrAdmin`): strictly isolates multi-tenant project data.
- Built-in search (`?search=`), filtering (`?status=&priority=&project=&assigned_to=me`), and pagination.

### 6. Performance & Code Quality
- **N+1 Query Elimination**: Employs `select_related()` for ForeignKey joins and `prefetch_related()` for ManyToMany sets.
- **Database Indexing**: Compound indexes on `['project', 'status']`, `['assigned_to', 'status']`, and `['due_date']`.
- **100% Automated Unit Test Suite**: 13 unit tests covering models, permissions, views, and DRF endpoints.
- **Production Logging**: Structured file and console logging (`taskflow.log`).

---

## 🏗️ Architecture & Project Structure

```text
taskflow/
├── manage.py
├── taskflow.log                  # Structured application logs
├── db.sqlite3                    # Local SQLite database (or MySQL)
├── .env.example                  # Environment configuration sample
├── requirements.txt              # Project dependencies
├── taskflow_project/             # Project Core Configuration
│   ├── settings.py               # Database, auth, DRF, and logging settings
│   ├── urls.py                   # Root URL router with custom error handlers
│   ├── wsgi.py
│   └── asgi.py
├── accounts/                     # Custom Authentication & RBAC
│   ├── models.py                 # User model with Role choices
│   ├── admin.py                  # UserAdmin with custom role filters
│   ├── forms.py                  # UserRegisterForm & UserLoginForm
│   ├── views.py                  # Login, register, logout controllers
│   └── urls.py
├── tasks/                        # Business Logic, REST API & Templates
│   ├── models.py                 # Project, ProjectMembership, Task, TaskComment
│   ├── admin.py                  # Tabular inlines and editable list fields
│   ├── forms.py                  # ProjectForm, TaskForm, TaskCommentForm
│   ├── views.py                  # Dashboard, CRUD views, and Kanban view
│   ├── serializers.py            # DRF serializers with validation
│   ├── api_views.py              # DRF ViewSets with search & custom actions
│   ├── permissions.py            # IsProjectMemberOrAdmin permission class
│   ├── tests.py                  # 13 automated unit tests
│   ├── urls.py                   # Template routes
│   ├── api_urls.py               # REST API DefaultRouter
│   └── management/commands/
│       └── seed_data.py          # One-step database population command
├── templates/                    # Bootstrap 5 HTML Layouts
│   ├── base.html                 # Main layout with role badge navbar
│   ├── 403.html / 404.html / 500.html # Custom error pages
│   ├── accounts/                 # login.html, register.html
│   └── tasks/                    # dashboard, project detail, kanban, etc.
└── static/
    ├── css/kanban.css            # Kanban board styling & transitions
    └── js/kanban.js              # Fetch client & drag-drop logic
```

---

## ⚡ Quick Start & Local Setup

### 1. Clone & Enter Project
```bash
git clone https://github.com/your-username/taskflow.git
cd taskflow
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Seed Sample Data
```bash
python manage.py migrate
python manage.py seed_data
```

> **Seeded Test Accounts:**
> | Role | Username | Password |
> |---|---|---|
> | **Admin** | `admin` | `admin123` |
> | **Manager** | `manager1` | `manager123` |
> | **Member** | `member1` | `member123` |

### 5. Launch the Django Backend
```bash
python manage.py runserver
```
Visit: `http://127.0.0.1:8000/` in your browser.

### 6. Launch the React SPA Frontend (Optional)
TaskFlow includes a decoupled React Single Page Application in the `frontend/` directory:
```bash
cd frontend
npm install
npm run dev
```
Visit: `http://localhost:5173/` in your browser to experience the full-stack React SPA connecting to your DRF backend with Token Authentication!

---

## 📡 REST API Reference

All API endpoints are prefixed with `/api/` and support both **Token Authentication** (`Authorization: Token <key>`) and **Session Authentication**.

| Method | Endpoint | Description | Auth Required | Query Parameters / Payload |
|---|---|---|---|---|
| `POST` | `/api/auth/token/` | Obtain API auth token | None | `{"username": "...", "password": "..."}` |
| `GET` | `/api/projects/` | List accessible projects | Yes | `?search=term&ordering=-created_at` |
| `POST` | `/api/projects/` | Create a new project | Manager / Admin | `{"name": "...", "description": "...", "members": [1, 2]}` |
| `GET` | `/api/projects/{id}/` | Retrieve project details | Project Member | — |
| `PUT/PATCH` | `/api/projects/{id}/` | Update project details | Project Creator / Admin | Project fields |
| `DELETE` | `/api/projects/{id}/` | Delete project | Project Creator / Admin | — |
| `GET` | `/api/tasks/` | List accessible tasks | Yes | `?status=todo&priority=high&project=1&assigned_to=me&search=keyword` |
| `POST` | `/api/tasks/` | Create a new task | Project Member | `{"title": "...", "project": 1, "due_date": "YYYY-MM-DD", ...}` |
| `GET` | `/api/tasks/{id}/` | Retrieve task details | Project Member | — |
| `PATCH` | `/api/tasks/{id}/` | Partial task update | Project Member | Task fields |
| `PATCH` | `/api/tasks/{id}/update-status/` | **Kanban update action** | Project Member | `{"status": "in_progress"}` (`todo`, `in_progress`, `done`) |
| `DELETE` | `/api/tasks/{id}/` | Delete task | Task Creator / Admin | — |
| `GET` | `/api/comments/` | List task comments | Yes | `?task={task_id}` |
| `POST` | `/api/comments/` | Add comment to a task | Project Member | `{"task": 1, "content": "Progress update..."}` |

---

## 🧪 Automated Testing

TaskFlow includes a comprehensive automated test suite verifying models, views, and DRF API endpoints:

```bash
python manage.py test
```

**Test Coverage Highlights:**
- ✅ Custom User Role helper methods (`is_admin_role`, `is_manager_role`, `is_member_role`)
- ✅ Project membership permission checks (`is_member()`)
- ✅ `is_overdue` computed property logic
- ✅ Database `UniqueConstraint` on `ProjectMembership`
- ✅ Unauthenticated redirects to login (`302 Found`)
- ✅ Authenticated dashboard metrics and project filtering
- ✅ DRF Token Authentication generation
- ✅ DRF serializer validation (past `due_date` rejection with HTTP 400)
- ✅ Kanban status update action (`update_status`)
- ✅ Project member isolation (outsiders cannot view or edit tasks)

---

## 🗄️ Database: Switching to MySQL (Production Ready)

To switch from the default SQLite database to MySQL:

1. Install MySQL driver:
   ```bash
   pip install mysqlclient
   ```
2. Set the environment variable in your `.env` or system environment:
   ```env
   USE_MYSQL=True
   MYSQL_DATABASE=taskflow_db
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```

---

## 📸 Screenshots

| Feature | Screenshot |
|---|---|
| **Executive Dashboard** | *Metrics cards, overdue warnings, and assigned task table* |
| **Interactive Kanban Board** | *Async drag-and-drop status transitions with Toast feedback* |
| **Project & Task Details** | *Collaborative comment timelines and status badges* |
| **Django REST Framework UI** | *Browsable API with query filtering and token auth* |

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
