# 4-Service User Management Application

A microservices-based Flask application with authentication, user management, and admin functionality.

## Architecture

- **Web Frontend** (Port 5000) - User interface and service orchestration
- **Auth Service** (Port 5001) - JWT-based authentication for users and admins
- **User Service** (Port 5002) - User CRUD operations
- **Admin Service** (Port 5003) - Admin dashboard and audit logging

## Prerequisites

- Python 3.11+
- MySQL 8.0+
- Git

## Setup Instructions

### 1. Setup Database

**Important:** Run migrations in this exact order:

```bash
git clone <repository-url>
cd pythhon-app

# 1. Create the database (requires MySQL root access)
mysql -u root -p < create_DB_Dump.sql

# 2. Create tables in order
mysql -u flaskuser -p users_db < db_dump.sql
```

### 2. Clone and configure environments

```bash
git clone <repository-url>
cd python-app
cp .env.example .env

# Edit .env with your database credentials and secrets
```
**Edit the service URL's with the docker service name (admin, user, auth, web) -- mentioned in the docker-compose.yml**

### 3. Run docker compose file

```bash
docker compose up -d
```

### 4. Verify docker containers status

```bash
docker compose ps
```


### 6. Access Application

- **Web App**: http://localhost:5000
- **Admin Login**: Use admin/admin (configured in .env)

## API Endpoints

### Auth Service (Port 5001)
- `POST /api/auth/login` - User/Admin login
- `POST /api/auth/verify` - Verify JWT token

### User Service (Port 5002)
- `GET /api/users` - List users (JWT required)
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user (JWT required)
- `PUT /api/users/{id}` - Update user (JWT required)
- `DELETE /api/users/{id}` - Delete user (JWT required)

### Admin Service (Port 5003)
- `GET /api/admin/dashboard` - Admin dashboard (admin JWT required)
- `GET /api/admin/users` - List all users (admin JWT required)
- `PUT /api/admin/users/{id}` - Update user (admin JWT required)
- `DELETE /api/admin/users/{id}` - Delete user (admin JWT required)
- `GET /api/admin/audit-logs` - View audit logs (admin JWT required)

## Development

- All services auto-create database tables on startup
- JWT tokens expire after 3600 seconds (1 hour)
- Circuit breaker pattern protects against service failures
- Comprehensive audit logging for admin actions

## Troubleshooting

- **Database connection errors**: Check MySQL is running and credentials in .env
- **Service startup failures**: Ensure all dependencies are installed
- **Authentication issues**: Verify JWT_SECRET in all services matches