# 🎓 Django LMS Platform

A production-oriented Learning Management System backend built with **Django REST Framework**, designed around real-world learning workflows, asynchronous processing, authentication, content progression, assessments, gamification, and scalable backend architecture.

> **Portfolio Project — Backend-focused implementation**

---

## ✨ Overview

**Django LMS Platform** is a backend system for an online learning platform where users can authenticate through OTP, access structured educational content, complete lessons and assessments, submit exercises, receive feedback, and progress through learning stages based on predefined rules.

The project was designed to go beyond basic CRUD and demonstrate backend engineering concepts such as:

* Authentication & authorization
* Redis-backed OTP workflows
* JWT authentication
* Course progression and content locking
* Quiz and assessment systems
* File and image submissions
* Background task processing
* Audit logging
* Gamification
* Dockerized infrastructure
* PostgreSQL
* Celery & Redis

---

## 🚀 Key Features

### 🔐 Authentication

* Custom Django user model
* Phone-number based authentication
* OTP-based login and registration
* Redis-backed OTP storage
* OTP expiration
* OTP attempt limiting
* OTP request rate limiting
* JWT access & refresh tokens
* Password change and recovery flows

---

### 📚 Learning Management

The platform uses a hierarchical learning structure:

```text
Course
 ├── Chapter
 │    ├── Lesson
 │    │    ├── Quiz
 │    │    └── Exercise
 │    └── Final Exam
```

Users have individual progression states for learning content, allowing the backend to control:

* Locked / unlocked content
* Started / completed lessons
* Chapter progression
* Exercise progression
* Quiz progression
* Final exam status

---

### 🧠 Quiz & Assessment System

The platform supports:

* Multiple-choice questions
* Ordered questions
* Quiz attempts
* Answer submission
* Automatic answer evaluation
* Correct / incorrect answer tracking
* Quiz result reporting
* Attempt tracking
* User-specific quiz status

---

### 📝 Exercise & Assignment Workflow

Exercises support a more complex submission workflow:

```text
Not Attempted
      ↓
   Pending
      ↓
 ┌────┴────┐
 ↓         ↓
Approved  Rejected
```

Users can submit:

* Text answers
* Files
* Images

Administrators can review submissions and provide feedback.

---

### 🏆 Gamification

The platform includes a points-based progression system with support for:

* User points
* Challenge-based progression
* Leaderboards
* Achievement-oriented learning workflows

---

### 🧾 Audit Logging

A dedicated audit application records important user and system actions.

Audit events can be associated with:

* Authentication
* Courses
* Points
* Notifications
* Payments

This provides traceability for important backend operations.

---

### ⚙️ Asynchronous Processing

Background workloads are handled using:

* **Celery**
* **Redis**

This architecture allows expensive operations to run outside the request/response cycle.

Example:

```text
API Request
     │
     ▼
Create Task
     │
     ▼
   Redis
     │
     ▼
Celery Worker
     │
     ▼
Background Processing
```

---

## 🏗️ Architecture

The project follows a modular Django application structure:

```text
django-lms-platform/
│
├── accounts/          # Authentication & user management
├── course/            # Courses, lessons, quizzes & exercises
├── audit/             # Audit logging
├── notifications/     # Notification system
├── points/            # Gamification & points
├── config/             # Django & Celery configuration
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

The application is structured as a **modular monolith**, where domain responsibilities are separated into Django applications while sharing the same deployment unit and database.

---

## 🛠️ Tech Stack

| Technology            | Purpose                     |
| --------------------- | --------------------------- |
| Python                | Backend language            |
| Django                | Web framework               |
| Django REST Framework | REST APIs                   |
| PostgreSQL            | Relational database         |
| Redis                 | Caching / OTP / task broker |
| Celery                | Background processing       |
| SimpleJWT             | JWT authentication          |
| Docker                | Containerization            |
| Docker Compose        | Local infrastructure        |
| Jazzmin               | Django Admin UI             |
| Pillow                | Image processing            |
| CKEditor              | Rich content management     |
| TinyMCE               | Rich text editing           |

---

## 🐳 Running with Docker

### 1. Clone the repository

```bash
git clone https://github.com/barbodjangjoo/django-lms-platform.git

cd django-lms-platform
```

### 2. Create environment variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1

SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=lms_db
SQL_USER=postgres
SQL_PASSWORD=postgres
SQL_HOST=postgres
SQL_PORT=5432
```

Additional environment variables may be required depending on the enabled integrations.

### 3. Start the services

```bash
docker compose up --build
```

The development environment includes:

```text
Django / Gunicorn
PostgreSQL
Redis
Celery Worker
Celery Beat
```

---

## 🧪 Running Tests

Run the test suite with:

```bash
python manage.py test
```

For a specific application:

```bash
python manage.py test accounts
```

The project includes tests covering authentication-related models, serializers, OTP handling, validation and Redis-backed rate limiting.

---

## 🔒 Security Considerations

The project uses several backend security mechanisms, including:

* JWT authentication
* Authenticated API endpoints
* OTP expiration
* OTP attempt limiting
* OTP request throttling
* Django password validation
* Environment-based secret configuration
* CSRF protection
* Permission-based API access

Production deployments should additionally configure:

* HTTPS
* Secure cookies
* Production-grade secret management
* Trusted origins
* Proper CORS policy
* Production email/SMS providers
* Object/file storage
* Monitoring and centralized logging

---

## 📈 Engineering Focus

This project focuses on backend engineering problems that appear in real-world educational platforms rather than only implementing CRUD endpoints.

### Core backend concerns

* Designing relational domain models
* Managing user-specific state
* Implementing content progression
* Handling asynchronous workloads
* Designing authentication workflows
* Preventing abuse through rate limiting
* Processing user submissions
* Tracking important system events
* Keeping expensive operations outside request handling

---

## 🗺️ Roadmap

Planned improvements include:

* [ ] Complete payment integration
* [ ] Expand automated test coverage across course workflows
* [ ] Improve service-layer separation
* [ ] Add API documentation with OpenAPI / Swagger
* [ ] Improve query optimization across complex endpoints
* [ ] Add CI pipeline
* [ ] Add production deployment configuration
* [ ] Add centralized structured logging
* [ ] Integrate production SMS provider
* [ ] Add monitoring and health checks

---

## 📌 Project Status

This repository is an actively developed backend portfolio project.

The architecture and feature set are based on real LMS requirements and are continuously being improved toward a more production-ready backend implementation.

---

## 👨‍💻 Author

**Barbod Jangjo**

Backend Developer focused on:

```text
Python
Django
Django REST Framework
PostgreSQL
Redis
Celery
Docker
```

* GitHub: https://github.com/barbodjangjoo
* LinkedIn: https://www.linkedin.com/in/barbod-jangjoo

---

## 📄 License

This project is licensed under the MIT License.
