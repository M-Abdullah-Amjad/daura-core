# FastAPI NestJS-Style Application

A FastAPI application built with NestJS-style modular architecture, featuring Keycloak authentication integration.

## Features

- **Modular Architecture**: Organized like NestJS with separate modules for different features
- **Keycloak Integration**: Complete OAuth2/OIDC authentication with Keycloak
- **Clean Code Structure**: Services, routers, schemas, and dependencies properly separated
- **Docker Support**: Containerized deployment ready

## Project Structure

```
app/
├── api/                    # API versioning
│   └── v1/
├── core/                   # Core functionality (config, database, etc.)
├── modules/                # Feature modules (NestJS-style)
│   ├── auth/              # Authentication module
│   ├── users/             # User management
│   └── ...                # Other modules
└── shared/                # Shared utilities
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastapi-nest-style
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment variables**
   Create a `.env` file with:
   ```env
   KEYCLOAK_URL=your-keycloak-url
   KEYCLOAK_REALM=your-realm
   KEYCLOAK_CLIENT_ID=your-client-id
   KEYCLOAK_CLIENT_SECRET=your-client-secret
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## Development

### Code Quality

This project uses several tools for code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **flake8**: Linting

Run all tools:
```bash
black .
isort .
mypy .
flake8 .
```

### Python Cache Files

Python automatically creates `__pycache__` directories and `.pyc` files for performance. These are ignored by git but can accumulate during development.

**To clean cache files:**
```bash
python clean_cache.py
```

Or manually:
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
```

**Prevention:**
- The `.gitignore` file already excludes these files
- Cache files are never committed to version control
- They don't affect production (containers don't include them)

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Authentication

The application uses Keycloak for authentication. Available endpoints:

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/forgot-password` - Password reset request
- `GET /api/v1/auth/userinfo` - Get user information
- And more...

## Docker

Build and run with Docker Compose:
```bash
docker-compose up --build
```

## Testing

Run tests:
```bash
pytest
```

## Contributing

1. Follow the existing code structure
2. Use type hints
3. Write tests for new features
4. Run code quality tools before committing
5. Clean cache files: `python clean_cache.py`

## License

[Your License Here]