# Django Backend API

A Django REST Framework backend server with JWT authentication.

## Features

- Django 4.2 with Django REST Framework
- PostgreSQL database
- JWT token-based authentication
- User registration and login
- Custom User model with email as username
- CORS enabled for frontend integration
- Password validation
- Protected API endpoints

## Prerequisites

- Python 3.8 or higher
- PostgreSQL (local or cloud service)
- pip (Python package manager)

## Getting Started

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Configuration
DB_NAME=backend
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# CORS Settings (optional)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 4. Create PostgreSQL Database

```bash
# Using psql
createdb backend

# Or using SQL
psql -U postgres
CREATE DATABASE backend;
```

### 5. Run Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The server will start on `http://localhost:8000`

## API Endpoints

### Public Endpoints

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Protected Endpoints

- `GET /api/auth/profile/` - Get current user profile (requires authentication)

## API Usage Examples

### Register a User

**POST** `/api/auth/register/`

Request body:
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "password2": "securepassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

Response:
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "refresh": "refresh_token_here",
    "access": "access_token_here"
  }
}
```

### Login

**POST** `/api/auth/login/`

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tokens": {
    "refresh": "refresh_token_here",
    "access": "access_token_here"
  }
}
```

### Access Protected Routes

Include the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Get User Profile

**GET** `/api/auth/profile/`

Headers:
```
Authorization: Bearer <access_token>
```

Response:
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-01-01T00:00:00Z"
  }
}
```

## Project Structure

```
Back_Back/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in git)
├── .gitignore               # Git ignore rules
├── backend/                 # Main project directory
│   ├── __init__.py
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── authentication/         # Authentication app
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py          # User model
│   ├── admin.py           # Admin configuration
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   └── urls.py            # App URL configuration
└── README.md              # This file
```

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/`

Use the superuser credentials created with `python manage.py createsuperuser`

## Development

### Running Migrations

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Creating a Superuser

```bash
python manage.py createsuperuser
```

### Collecting Static Files (for production)

```bash
python manage.py collectstatic
```

## Production Deployment

Before deploying to production:

1. Set `DEBUG=False` in `.env`
2. Update `SECRET_KEY` with a secure random key
3. Configure `ALLOWED_HOSTS` with your domain
4. Set up proper database (PostgreSQL recommended)
5. Configure static files serving
6. Set up SSL/HTTPS
7. Use environment variables for sensitive data

## License

ISC
