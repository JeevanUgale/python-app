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
- Docker (for containerized deployments)
- Kubernetes cluster (for K8s deployment)
- Helm (for Helm deployment)

## Setup Instructions

### 1. Setup Database

**Important:** Run migrations in this exact order:

```bash
git clone <repository-url>
cd python-app

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

**Note:** For containerized deployments, edit the service URLs in .env with the docker service names (admin, user, auth, web) as mentioned in the docker-compose.yml.

## Deployment Options

### Option 1: Docker Compose Deployment

#### Build and Run with Docker Compose

```bash
# Build the images
docker compose build

# Run the services
docker compose up -d
```

#### Verify Docker Containers

```bash
docker compose ps
```

#### Stop the Services

```bash
docker compose down
```

### Option 2: Kubernetes Deployment

#### Prerequisites
- A running Kubernetes cluster
- `kubectl` configured to access the cluster

#### Deploy to Kubernetes

```bash
# Create the namespace
kubectl apply -f k8s-manifest/namespace.yml

# Deploy ConfigMaps and Secrets
kubectl apply -f k8s-manifest/common/

# Deploy Service Account and RBAC
kubectl apply -f k8s-manifest/serviceac/

# Deploy Database Server (if not using external DB)
kubectl apply -f k8s-manifest/db-server.yml

# Deploy Services
kubectl apply -f k8s-manifest/admin-service/
kubectl apply -f k8s-manifest/auth-service/
kubectl apply -f k8s-manifest/user-service/
kubectl apply -f k8s-manifest/web-frontend/
```

#### Verify Deployment

```bash
kubectl get pods -n python
kubectl get services -n python
```

#### Access the Application

- Get the external IP of the web-frontend service:
```bash
kubectl get svc web-frontend -n python
```

- Access the application at `http://<external-ip>:5000`

#### Clean Up

```bash
kubectl delete -f k8s-manifest/ --recursive
```

### Option 3: Helm Deployment

#### Prerequisites
- A running Kubernetes cluster
- `kubectl` configured to access the cluster
- Helm installed

#### Install the Helm Chart

```bash
# Add the chart repository (if hosted remotely) or use local path
cd python-app-helm

# For development environment
helm install python-app-dev . -f values-dev.yaml -n python --create-namespace

# For production environment
helm install python-app-prod . -f values-prod.yaml -n python --create-namespace

# Or use default values
helm install python-app . -n python --create-namespace
```

#### Verify Helm Deployment

```bash
helm list -n python
kubectl get pods -n python
kubectl get services -n python
```

#### Access the Application

- Get the external IP of the web-frontend service:
```bash
kubectl get svc web-frontend -n python
```

- Access the application at `http://<external-ip>:5000`

#### Upgrade the Release

```bash
helm upgrade python-app . -n python
```

#### Uninstall the Release

```bash
helm uninstall python-app -n python
```

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
- **Container issues**: Check Docker/Kubernetes logs for detailed error messages
- **Helm deployment issues**: Use `helm status <release-name> -n python` to check release status
