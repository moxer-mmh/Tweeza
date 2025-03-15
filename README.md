# Tweeza

**Empowering Community Solidarity & Volunteerism**

Tweeza is a donation and resource sharing platform designed to connect donors, organizations, and beneficiaries in Algeria. By leveraging cutting-edge technology, Tweeza aims to combat food waste, optimize resource allocation, and improve humanitarian aid distribution—empowering community solidarity and volunteerism.

This repository contains the complete source code for both the backend and frontend components developed for the Djezzy Code Fest hackathon.

---

## Table of Contents

- [Tweeza](#tweeza)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Architecture](#architecture)
    - [Backend Architecture](#backend-architecture)
    - [Frontend Architecture](#frontend-architecture)
  - [Features](#features)
  - [Technologies](#technologies)
  - [Installation](#installation)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
    - [Docker](#docker)
  - [Usage](#usage)
  - [Testing](#testing)
    - [Backend Testing](#backend-testing)
  - [Contributing](#contributing)
  - [License](#license)

---

## Overview

Tweeza is a comprehensive platform that:

* **Tracks Donations:** Securely handles user registration, authentication (JWT, OAuth, and two-factor authentication), and donation management.
* **Manages Resources:** Facilitates the creation and tracking of resource requests, contributions, and allocation optimization.
* **Coordinates Volunteers:** Supports volunteer registration and management, event creation, and real-time notifications.
* **Optimizes Distribution:** Implements smart resource allocation algorithms to prioritize urgent needs and minimize waste.

The platform is tailored to Algeria's unique context, with localization for Arabic, French, and English, and optimization for areas with limited connectivity.

---

## Architecture

### Backend Architecture

The backend is built with FastAPI and SQLAlchemy, following a layered architecture:

```
Client Layer → API Layer → Service Layer → Data Access Layer → Database Layer
```

Key components:

* **FastAPI Application:** High-performance API server.
* **SQLAlchemy ORM:** For database operations.
* **SQLite Database:** Used during development (configurable to PostgreSQL for production).
* **JWT Authentication & OAuth Integration:** Securing endpoints and enabling social logins.
* **Comprehensive Testing:** 85% code coverage including API, service, and model tests.

A detailed sequence diagram and ER diagram are provided in the documentation.

### Frontend Architecture

The frontend is developed using Next.js and React with a focus on interactivity and accessibility:

* **Next.js (App Router):** Provides SSR and file-based routing.
* **React Functional Components:** Leveraging Hooks for state management.
* **Leaflet.js:** For interactive mapping with dynamic markers based on content type.
* **Tailwind CSS:** For utility-first responsive styling.
* **Lucide React:** For iconography.

Components include:

* **AuthTabs:** For login/registration navigation.
* **Interactive Map:** Displays emergencies, assistance, and events with category-based marker colors.
* **Card Components:** EventCard, EmergencyCard, AssistanceCard to display various content.
* **Dashboard & Volunteer Pages:** Centralized views for main functionality and volunteer registration.

---

## Features

* **User & Organization Management:** Registration, authentication, profile management, and role-based permissions.
* **Event Management:** Creation and discovery of events, including location-based searches.
* **Resource Management:** Creation of resource requests and tracking of contributions.
* **Notification System:** Email, in-app, and SMS notifications.

---

## Technologies

* **Backend:** FastAPI, SQLAlchemy, SQLite/PostgreSQL, JWT, OAuth, Docker
* **Frontend:** Next.js, React, Leaflet.js, Tailwind CSS, Lucide React

---

## Installation

### Backend Setup

1. **Clone the Repository & Navigate to Backend Directory:**

   ```bash
   git clone https://github.com/moxer-mmh/Tweeza.git
   cd Tweeza/backend
   ```
2. **Create a Virtual Environment and Install Dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration values (SECRET_KEY, OAuth credentials, etc.)
   ```
4. **Run the Development Server:**

   ```bash
   uvicorn main:app --reload
   ```

   The API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Frontend Setup

1. **Navigate to the Frontend Directory:**

   ```bash
   cd ../frontend
   ```
2. **Install Dependencies:**

   ```bash
   npm install
   ```
3. **Run the Development Server:**

   ```bash
   npm run dev
   ```

   The application will be accessible at [http://localhost:3000](http://localhost:3000/).

### Docker

   ```
   docker-compose up -d
   ```

---

## Usage

* **API Endpoints:**

  The backend exposes endpoints for authentication, user, organization, event, resource, and notification management. Refer to the API documentation section in the backend docs for details.
* **Interactive Dashboard:**

  The frontend dashboard integrates a dynamic map with card-based displays for emergencies, assistance, and events. Navigate through tabs to filter content and access individual resource pages.
* **Volunteer & Donation Flows:**

  Users can register as volunteers or donors via dedicated forms. The multi-step forms ensure data is collected accurately for each user type.

---

## Testing

### Backend Testing

* **Run All Tests:**
  ```bash
  python run_tests.py
  ```
* **HTML Coverage Report:**
  ```bash
  python run_tests.py --html
  ```
* **Run a Specific Test Module:**
  ```bash
  python run_tests.py --path tests/test_api/test_auth.py
  ```

---

## Contributing

Contributions are welcome! Please follow these steps in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

This project is licensed under the [MIT License](/LICENSE).

---

*This repository was developed as part of the Djezzy Code Fest hackathon to empower community-driven initiatives in Algeria, promoting efficient donation tracking, resource management, and volunteer coordination.*
