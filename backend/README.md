# Tweeza Backend

Tweeza is a backend solution designed for the Djezzy Code Fest hackathon. It provides a robust API for managing users, organizations, events, resources, and notifications while ensuring security, scalability, and performance in an Algerian context.

## Table of Contents

- [Tweeza Backend](#tweeza-backend)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Architecture](#architecture)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
    - [Docker Deployment](#docker-deployment)
  - [API Documentation](#api-documentation)
  - [Testing](#testing)
  - [DevOps \& Deployment](#devops--deployment)
  - [Security Considerations](#security-considerations)
  - [Contributing](#contributing)
  - [License](#license)

## Overview

Tweeza is built using FastAPI and SQLAlchemy with an SQLite database for development. The backend implements a layered architecture that separates the API, service, and data access layers to ensure maintainability and scalability. Key functionality includes user authentication (JWT and OAuth), organization and event management, and resource tracking.

## Features

- **User Authentication:** Supports JWT, two-factor authentication, and OAuth (Google, Facebook, etc.).
- **Role-Based Access Control:** Fine-grained permissions for users, organization admins, and super admins.
- **Organization & Event Management:** Create, update, and delete organizations and events, with member and collaborator management.
- **Resource Tracking:** Manage resource requests and contributions linked to events.
- **Notifications:** In-app notifications with email/SMS support.
- **Performance:** Pagination, caching opportunities, and optimized SQL queries.

## Architecture

The backend follows a layered architecture:

- **Client Layer:** Web, mobile, and admin clients interact with the API.
- **API Layer:** FastAPI application with middleware for authentication, CORS, and error handling.
- **Service Layer:** Contains core business logic (AuthService, UserService, etc.).
- **Data Access Layer:** Utilizes SQLAlchemy models and a session manager.
- **Database Layer:** SQLite for development; configurable for production.

Refer to the [Technical Documentation](./docs/DOCUMENTATION.md) for detailed architectural diagrams and flows.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/moxer-mmh/Tweeza.git
   cd backend
   ```
2. **Create a Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Copy the sample environment file and update the configuration variables:

```bash
cp .env.example .env
```

Key environment variables include:

- `SECRET_KEY`
- `ALGORITHM`
- `APP_ENV`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- OAuth credentials (Google, Facebook, etc.)
- Email and SMS service configurations

## Running the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Swagger documentation is accessible at `/docs` and ReDoc at `/redoc`.

### Docker Deployment
 
 A Dockerfile is provided for containerized deployment:
 
 ```
 docker build -t tweeza-backend .
 docker run -p 8000:8000 tweeza-backend
 ```
 or
 ```
 docker-compose up
 ```
 
## API Documentation

The API endpoints are categorized by functionality. For example:

- **Authentication:** `/api/v1/auth/login`, `/api/v1/auth/register`, etc.
- **User Management:** `/api/v1/users/me`, `/api/v1/users/{user_id}`, etc.
- **Organization & Event Management:** `/api/v1/organizations/`, `/api/v1/events/`, etc.
- **Resource & Notification Endpoints:** `/api/v1/resources/requests`, `/api/v1/notifications/`, etc.

Detailed API specifications and examples are available in the [Technical Documentation](./DOCUMENTATION.md).

## Testing

Tests are organized into API, services, and models directories.

Run all tests with coverage:

```bash
python run_tests.py
```

For an HTML coverage report:

```bash
python run_tests.py --html
```

To run a specific test module:

```bash
python run_tests.py --path tests/test_api/test_auth.py
```

## DevOps & Deployment

The backend supports both development and production environments. Refer to the `DevOps Setup` section in the documentation for:

- Environment configuration flow
- Database initialization
- CORS setup
- Deployment guidelines

## Security Considerations

- **Data Protection:** Secure password hashing, input validation, and proper CORS configurations.
- **Authentication Security:** Robust JWT token management and two-factor authentication.
- **API Protection:** Rate limiting and thorough error handling to prevent information leaks.
- **Infrastructure:** Secure database connections and HTTPS enforcement in production.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any improvements or bug fixes.

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/YourFeature`.
3. Commit your changes.
4. Push to the branch and open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

---

*This README is part of a hackathon project, designed to address the criteria for innovation, technical execution, and user experience in the Algerian context. For further details, refer to the comprehensive documentation provided in the repository.*
