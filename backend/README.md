# Tweeza Backend Documentation

## Table of Contents

1. System Overview
2. Architecture
3. API Documentation
4. Database Schema
5. Authentication & Authorization
6. Setup & Deployment
7. Testing
8. Security Considerations

## System Overview

Tweeza is a platform that facilitates resource sharing, event management, and organizational collaboration. The backend is built with FastAPI, providing a high-performance, easy-to-use REST API with automatic interactive documentation.

**Core Features:**
- User management with role-based access control
- Organization management
- Event coordination and collaboration
- Resource sharing and tracking
- Secure authentication and authorization

## Architecture

### System Design

```
┌─────────────────┐      ┌────────────────┐      ┌─────────────────┐
│   Client Apps   │◄────►│ FastAPI Backend │◄────►│ SQLite Database │
└─────────────────┘      └────────────────┘      └─────────────────┘
                               │
                               │
            ┌─────────────────────────────────────┐
            │                                     │
┌───────────▼────────────┐   ┌───────────────────▼┐
│  Authentication &      │   │ Business Logic &   │
│  Authorization         │   │ Data Services      │
└────────────────────────┘   └────────────────────┘
```

### Component Structure

```
backend/
├── app/                      # Main application package
│   ├── api/                  # API endpoints and routers
│   │   └── v1/               # API version 1
│   │       └── endpoints/    # API endpoint modules
│   │           ├── auth.py   # Authentication endpoints
│   │           ├── users.py  # User management
│   │           ├── organizations.py
│   │           ├── events.py
│   │           └── resources.py
│   ├── core/                 # Core application modules
│   │   ├── config.py         # Configuration settings
│   │   └── security.py       # Security utilities
│   ├── db/                   # Database related code
│   │   ├── base.py           # SQLAlchemy base
│   │   ├── models/           # Database models
│   │   └── session.py        # Database connection
│   ├── schemas/              # Pydantic schemas for validation
│   └── services/             # Business logic services
├── migrations/               # Alembic database migrations
├── tests/                    # Test suite
└── scripts/                  # Utility scripts
```

## API Documentation

The API is organized into the following modules:

### Authentication

- `POST /api/v1/auth/login` - User login with email/password
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/register-organization` - Register a new organization with admin user

### Users

- `GET /api/v1/users/` - List users (admin only)
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user information
- `DELETE /api/v1/users/{user_id}` - Delete user
- `POST /api/v1/users/roles` - Add role to user
- `DELETE /api/v1/users/{user_id}/roles/{role_id}` - Remove role from user

### Organizations

- `GET /api/v1/organizations/` - List organizations
- `POST /api/v1/organizations/` - Create organization
- `GET /api/v1/organizations/{organization_id}` - Get organization details
- `PUT /api/v1/organizations/{organization_id}` - Update organization
- `DELETE /api/v1/organizations/{organization_id}` - Delete organization

### Events

- `GET /api/v1/events/` - List events
- `POST /api/v1/events/` - Create event
- `GET /api/v1/events/{event_id}` - Get event details
- `PUT /api/v1/events/{event_id}` - Update event
- `DELETE /api/v1/events/{event_id}` - Delete event
- `POST /api/v1/events/{event_id}/collaborators` - Add collaborator to event

### Resources

- `GET /api/v1/resources/` - List resources
- `POST /api/v1/resources/` - Create resource
- `GET /api/v1/resources/{resource_id}` - Get resource details
- `PUT /api/v1/resources/{resource_id}` - Update resource
- `DELETE /api/v1/resources/{resource_id}` - Delete resource

## Database Schema

### Core Entities

1. **User**
   - Primary entity for authentication and access control
   - Stores personal information, credentials, and location data
   - Connected to roles through UserRole junction table

2. **Organization**
   - Represents a group or entity that can host events and manage resources
   - Has members (users) with different roles

3. **Event**
   - Coordinated activities with time, location, and description
   - Can have multiple collaborators (users)
   - Associated with the organizing organization

4. **Resource**
   - Items or services that can be shared or tracked
   - Associated with organizations or events
   - Includes metadata like availability, description, and quantity

### Relationships

- **User-Organization**: Many-to-many through organization memberships with roles
- **User-Event**: Many-to-many through event collaborators
- **Organization-Event**: One-to-many (an organization can host many events)
- **Organization-Resource**: One-to-many (organization owns/manages resources)
- **Event-Resource**: Many-to-many (resources can be used in multiple events)

## Authentication & Authorization

### Authentication Flow

1. User provides credentials (email/password)
2. System validates credentials against database
3. If valid, JWT token is generated and returned
4. Token includes user ID and expiration
5. Client includes token in Authorization header for subsequent requests

### Role-Based Access Control

The system implements a comprehensive role-based access control system:

- **Super Admin**: Has complete access to all system features
- **Admin**: Can manage users, resources, and events within their organization
- **User**: Basic access to view and participate in events and use resources

Super Admin creation is handled through a dedicated script detailed in super_admin_guide.md.

### Security Implementation

- Password hashing using modern algorithms
- JWT tokens with configurable expiration
- CORS protection for API endpoints
- Input validation using Pydantic schemas

## Setup & Deployment

### Prerequisites

- Python 3.8+
- SQLite (default) or other database supported by SQLAlchemy
- Environment configured according to settings in `app/core/config.py`

### Installation Steps

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up the database:
   ```
   alembic upgrade head
   ```
4. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

### Environment Variables

The application uses the following environment variables:

- `SECRET_KEY`: Secret key for JWT token encryption
- `INITIALIZE_DB`: Boolean to automatically initialize database tables
- `ORIGINS`: List of allowed CORS origins (comma separated)
- `API_STR`: API prefix (default: "/api")
- `PROJECT_NAME`: Name of the project (default: "Tweeza")

### Docker Deployment

A Dockerfile is provided for containerized deployment:

```
docker build -t tweeza-backend .
docker run -p 8000:8000 tweeza-backend
```

## Testing

### Test Strategy

The application uses pytest for testing:

- Unit tests for services and utilities
- Integration tests for API endpoints
- Coverage reports to identify untested code paths

### Running Tests

To run the test suite:

```
python run_tests.py
```

To generate a coverage report:

```
python run_tests.py --coverage
```

To run only failing tests:

```
python run_failing_tests.py
```

## Security Considerations

- All passwords are hashed and never stored in plain text
- JWT tokens have short expiration time to minimize risk of stolen tokens
- Input validation prevents SQL injection and similar attacks
- Role-based permissions prevent unauthorized access to sensitive operations
- CORS settings restrict which domains can access the API

---

# Super Admin Role

The Super Admin has complete access to all system functionality and can:

- View and modify all users, organizations, events, and resources
- Create and manage roles for any user
- Delete any entity in the system

For security reasons, Super Admin creation is restricted to the command line using a dedicated script. See super_admin_guide.md for detailed instructions on creating a Super Admin user.

---

# System Design Documentation

## High-Level Architecture

Tweeza follows a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                        │
└───────────────────────────────────┬─────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────┐
│                     Service Layer (Business Logic)              │
└───────────────────────────────────┬─────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────┐
│                     Data Access Layer (SQLAlchemy)              │
└───────────────────────────────────┬─────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────┐
│                         Database (SQLite)                       │
└─────────────────────────────────────────────────────────────────┘
```

## Database Design

### Entity-Relationship Diagram

```
┌────────────┐     ┌───────────┐     ┌─────────────┐
│   User     │     │  UserRole │     │    Role     │
├────────────┤     ├───────────┤     ├─────────────┤
│ id         │─┐ ┌─│ user_id   │   ┌─│ id          │
│ email      │ │ │ │ role_id   │───┘ │ name        │
│ password   │ └─┤ └───────────┘     │ description │
│ first_name │   │                   └─────────────┘
│ last_name  │   │
│ latitude   │   │   ┌────────────────────┐
│ longitude  │   │   │   Organization     │
└────────────┘   │   ├────────────────────┤
                 └───┤ id                 │
                     │ name               │
┌────────────┐       │ description        │
│   Event    │       │ location           │
├────────────┤       └────────────────────┘
│ id         │               │
│ title      │               │
│ start_date │               │
│ end_date   │               │
│ org_id     │───────────────┘
└────────────┘
      │
      │
┌─────▼──────┐
│  Resource  │
├────────────┤
│ id         │
│ name       │
│ type       │
│ quantity   │
│ event_id   │
└────────────┘
```

## Request Flow

1. Client makes HTTP request to API endpoint
2. FastAPI routes request to appropriate endpoint handler
3. Endpoint handler validates input using Pydantic schemas
4. Authentication middleware verifies JWT token and user permissions
5. Service layer processes business logic using validated data
6. Data access layer interacts with database
7. Response is formatted and returned to client

## Scalability Considerations

- Database connection pooling for efficient resource utilization
- Stateless API design allows horizontal scaling
- Pagination implemented for list endpoints to handle large datasets
- Efficient SQL queries optimized for performance
- Caching strategies can be implemented for frequent queries

## Future Expansion

The modular architecture allows for easy expansion in the following areas:

1. **Additional Authentication Methods**
   - OAuth integration for social logins
   - Two-factor authentication

2. **Advanced Search**
   - Full-text search for resources
   - Geospatial queries for location-based features

3. **Analytics**
   - Usage statistics
   - Resource utilization reporting

4. **Notification System**
   - Email notifications
   - Push notifications for mobile clients
