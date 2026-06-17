# Product Service API

A comprehensive Flask-based microservice for managing product catalog, inventory, and related operations. This service provides RESTful API endpoints with JWT authentication, database persistence, caching capabilities, and extensive API documentation.

## Overview

The Product Service is built with modern Python frameworks and best practices:

- **Framework**: Flask with flask-smorest for OpenAPI/Swagger documentation
- **Database**: MySQL with SQLAlchemy ORM for data persistence
- **Authentication**: JWT (JSON Web Tokens) with flask-jwt-extended
- **Caching**: Redis for high-performance caching and session management
- **API Security**: CORS support for cross-origin requests with configurable allowed origins
- **Database Migrations**: Alembic for version control of schema changes
- **Testing**: pytest with BDD support via pytest-bdd
- **Containerization**: Multi-stage Docker builds for optimized production images
- **Orchestration**: Kubernetes deployment with Helm charts for cloud-native deployment

## Project Structure $ for authenticity

```
product-service/
├── src/product/                    # Main application source code
│   ├── main.py                     # Flask app factory and configuration
│   ├── __init__.py
│   ├── extentions/                 # Flask extensions (database, Redis client)
│   │   ├── db.py                   # SQLAlchemy database instance
│   │   └── redis_client.py         # Redis connection configuration
│   ├── models/                     # SQLAlchemy ORM models
│   │   └── product_model.py        # Product data model
│   ├── repositories/               # Data access layer (repository pattern)
│   ├── resources/                  # Flask-smorest API blueprints and endpoints
│   │   ├── products.py             # Product API endpoints
│   │   └── health.py               # Health check endpoint
│   ├── schemas/                    # Marshmallow schemas for request/response validation
│   │   └── product_schema.py       # Product serialization schemas
│   ├── services/                   # Business logic layer
│   └── utils/                      # Utility functions and helpers
├── migrations/                     # Alembic database migrations
├── tests/                          # Test suite
│   ├── test_products.py           # Product endpoint tests
│   ├── integration/               # Integration tests
│   └── unit/                      # Unit tests
├── deployment/                     # Deployment configurations
│   └── K8s/                       # Kubernetes manifests
│       └── product-deployment.yaml
├── product-service-chart/         # Helm chart for Kubernetes deployment
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/                 # Kubernetes resource templates
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   ├── hpa.yaml              # Horizontal Pod Autoscaler
│   │   ├── httproute.yaml         # HTTP routing configuration
│   │   └── serviceaccount.yaml    # Service account for RBAC
├── Dockerfile                     # Development Docker image (Alpine-based)
├── Dockerfile.production          # Production Docker image with optimizations
├── Jenkinsfile                    # Jenkins CI/CD pipeline configuration
├── requirements.txt               # Python package dependencies
├── pyproject.toml                # Project metadata and build configuration
├── run.py                        # Application entry point
└── README.md                     # This file
```

## Prerequisites

- **Python**: 3.12 or higher
- **MySQL**: 8.0 or higher
- **Redis**: 6.0 or higher (optional, for caching features)
- **Docker**: For containerized deployment
- **Kubernetes**: For cloud-native orchestration (optional)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd product-service
```

### 2. Create Python Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=product_user
DB_PASSWORD=your_password
DB_NAME=product_db

# Redis Configuration (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT Configuration
JWT_SECRET_KEY=your_secret_key_here
JWT_ACCESS_TOKEN_EXPIRES=3600

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000

# Application Configuration
APP_ENV=development
LOG_LEVEL=DEBUG
```

### 6. Initialize Database

```bash
# Create database and apply migrations
python -m alembic upgrade head
```

### 7. Run the Application

```bash
python run.py
```

The application will start on `http://localhost:5000`

## Docker Deployment

### Development Docker Image

Build and run the development Docker image with live reload support:

```bash
# Build the development image
docker build -t product-service:dev .

# Run the development container
docker run --rm -p 5000:5000 --env-file .env.docker product-service:dev
```

### Production Docker Image

For production deployments with optimized multi-stage builds:

```bash
# Create environment file from template
Copy-Item .env.docker.example .env.docker

# Edit .env.docker with production values
# (Do not commit secrets to version control)

# Build the production image
docker build -f Dockerfile.production -t product-service:prod .

# Run the production container
docker run --rm -p 5000:5000 --env-file .env.docker product-service:prod
```

### Docker Compose (if available)

For local multi-service development:

```bash
docker-compose up
```

## Kubernetes Deployment

The service includes a Helm chart for Kubernetes deployment with production-ready configurations.

### Deploy with Helm

```bash
# Add Helm repository (if applicable)
helm repo add product-charts <repository-url>
helm repo update

# Install the chart
helm install product-service product-service-chart -f product-service-chart/values.yaml

# Upgrade an existing release
helm upgrade product-service product-service-chart -f product-service-chart/values.yaml

# Uninstall the chart
helm uninstall product-service
```

### Direct Kubernetes Deployment

```bash
kubectl apply -f deployment/K8s/product-deployment.yaml
```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:5000/swagger-ui
- **OpenAPI Specification**: http://localhost:5000/openapi.json

## API Endpoints

### Health Check

```bash
GET /health
```

Returns the health status of the service.

### Product Endpoints

- **List Products**: `GET /products`
- **Get Product**: `GET /products/{product_id}`
- **Create Product**: `POST /products`
- **Update Product**: `PUT /products/{product_id}`
- **Delete Product**: `DELETE /products/{product_id}`

All endpoints (except health check) require JWT authentication via the `Authorization` header:

```bash
Authorization: Bearer <your_jwt_token>
```

## Testing

### Run Unit Tests

```bash
pytest tests/unit/
```

### Run Integration Tests

```bash
pytest tests/integration/
```

### Run All Tests with Coverage

```bash
pytest --cov=src tests/
```

### Run Tests with BDD

```bash
pytest --gherkin-terminal-reporter tests/
```

## Database Migrations

Manage database schema changes using Alembic:

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new column"

# Apply pending migrations
alembic upgrade head

# Rollback to previous version
alembic downgrade -1

# View migration history
alembic history
```

## CI/CD Pipeline

The project includes a Jenkins pipeline for continuous integration and deployment.

### Pipeline Stages

1. **Source**: Checkout code from repository
2. **Build**: Compile dependencies and build Docker image
3. **Test**: Execute unit and integration tests
4. **Security Scan**: Vulnerability and static code analysis
5. **Push**: Push image to container registry
6. **Deploy**: Deploy to staging and production environments

See `Jenkinsfile` for detailed pipeline configuration.

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | MySQL database host | localhost |
| `DB_PORT` | MySQL database port | 3306 |
| `DB_USER` | MySQL database user | product_user |
| `DB_PASSWORD` | MySQL database password | secure_password |
| `DB_NAME` | MySQL database name | product_db |
| `JWT_SECRET_KEY` | Secret key for JWT signing | your_secret_key |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_HOST` | Redis server host | localhost |
| `REDIS_PORT` | Redis server port | 6379 |
| `REDIS_DB` | Redis database number | 0 |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | http://localhost:3000 |
| `JWT_ACCESS_TOKEN_EXPIRES` | JWT token expiration time (seconds) | 3600 |
| `LOG_LEVEL` | Application logging level | INFO |

## Troubleshooting

### Database Connection Issues

```bash
# Verify MySQL is running and accessible
mysql -h localhost -u product_user -p product_db -e "SELECT 1;"
```

### Port Already in Use

```bash
# Change the port in run.py or use environment variable
# OR find and kill the process using port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000                  # macOS/Linux
```

### Redis Connection Issues

```bash
# Verify Redis is running
redis-cli ping
```

Should return `PONG` if Redis is accessible.

## Security Considerations

- Never commit `.env` files with secrets to version control
- Use strong JWT secret keys in production
- Implement rate limiting for API endpoints in production
- Enable HTTPS/TLS in production deployments
- Regularly update dependencies for security patches
- Use dedicated service accounts and roles in Kubernetes deployments
- Enable audit logging for compliance and monitoring

## Performance Optimization

- Redis caching reduces database load for frequently accessed products
- Database connection pooling through SQLAlchemy
- Horizontal Pod Autoscaler (HPA) for dynamic scaling in Kubernetes
- Multi-stage Docker builds minimize image size
- Asynchronous request processing for long-running operations

## Monitoring and Logging

The application logs important events and errors to help with troubleshooting:

```bash
# View logs in Docker container
docker logs <container_id>

# View logs in Kubernetes pod
kubectl logs <pod_name>
```

Configure logging level via `LOG_LEVEL` environment variable.

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes and write tests
3. Run tests to ensure they pass: `pytest`
4. Commit your changes: `git commit -m "Add your feature"`
5. Push to the branch: `git push origin feature/your-feature`
6. Submit a pull request for review

## License

See [LICENCE](LICENCE) file for license information.

## Support

For issues, questions, or contributions, please refer to the project's issue tracker or contact the development team.
