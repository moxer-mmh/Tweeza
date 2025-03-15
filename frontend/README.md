# Tweeza Frontend

**Empowering Community Support Through Digital Innovation**

Tweeza is a community support platform designed to connect donors, organizations, and beneficiaries across Algeria. The frontend, built with Next.js, React, and Tailwind CSS, provides an intuitive, interactive user interface that supports emergencies, assistance programs, and events.

---

## Table of Contents

- [Tweeza Frontend](#tweeza-frontend)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Technologies](#technologies)
  - [Installation \& Setup](#installation--setup)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
  - [Usage](#usage)
  - [State Management](#state-management)
  - [Best Practices](#best-practices)
  - [Potential Improvements](#potential-improvements)
  - [Troubleshooting](#troubleshooting)
  - [Contributing](#contributing)
  - [License](#license)

---

## Overview

The Tweeza frontend is a Next.js-based application that delivers a dynamic and engaging experience for community support. Key functionalities include:

- **User Authentication:** Facilitates login and registration flows.
- **Interactive Map:** Displays emergency, assistance, and event markers using Leaflet.js.
- **Card-Based UI:** Presents information through Event, Emergency, and Assistance cards.
- **Volunteer & Donation Flows:** Supports multi-step forms for volunteer registration and donation processing.

---

## Features

- **AuthTabs Component:**  
  Manages navigation between login and registration, detecting the active tab using Next.js hooks and styled with Tailwind CSS.

- **Interactive Map:**  
  Utilizes Leaflet.js to render a map with dynamic markers colored by category:  
  - Emergency: `#973535`  
  - Assistance: `#3B82F6`  
  - Events: `#059669`

- **Card Components:**  
  Display content for different categories (Events, Emergencies, Assistance) with a consistent design.

- **Dashboard Page:**  
  Combines an interactive map and a card view, with filtering based on the active tab and integrated search functionality.

- **Volunteer Registration Page:**  
  A multi-step interface that enables volunteers to select tasks, choose time slots, and view location details.

- **Profile Management:**  
  Provides a tabbed interface for viewing personal information, events attended, and donation statuses.

---

## Technologies

- **Next.js:** Server-side rendering and file-based routing.
- **React:** Functional components and Hooks for state management.
- **Leaflet.js:** Dynamic, interactive maps.
- **Tailwind CSS:** Utility-first CSS framework for rapid UI development.
- **Lucide React:** Icon library for scalable vector icons.
- **Next Navigation:** Simplifies client-side routing and navigation.

---

## Installation & Setup

### Prerequisites

- Node.js (v14 or later)
- npm (v6 or later)

### Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/moxer-mmh/Tweeza.git
   cd Tweeza/frontend
   ```

2. **Install Dependencies:**
   ```bash
   npm install
   ```

3. **Run the Development Server:**
   ```bash
   npm run dev
   ```
   The application will be available at [http://localhost:3000](http://localhost:3000).

---

## Usage

- **Dashboard:**  
  Visit the root route (`/`) to view the interactive map and filtered card views.
- **Authentication:**  
  Use the AuthTabs component to navigate between login and registration.
- **Volunteer & Donation Flows:**  
  Access the volunteer registration (`/volunteer/[id]`) and donation pages (`/donate/[id]`) for task selection and scheduling.
- **Profile Management:**  
  Manage your profile, view attended events, and track donations at `/profile`.

---

## State Management

- **Local State:**  
  Used for UI interactions (e.g., active tab, form validations).
- **URL Parameters:**  
  Dynamically pass resource identifiers (e.g., `/donate/[id]`).
- **Effect Hooks:**  
  Manage map marker updates and data fetching with `useEffect`.

---

## Best Practices

- **Component Organization:**  
  Keep reusable components in the `/components` directory; page components reside in the `/app` folder.
- **Dynamic Imports:**  
  Use dynamic imports for Leaflet to avoid SSR issues.
- **Memoization:**  
  Apply memoization to prevent unnecessary re-renders.
- **Accessibility:**  
  Use semantic HTML elements, ARIA labels, and ensure color contrast ratios meet standards.

---

## Potential Improvements

- **Global State Management:**  
  Integrate Redux or Zustand for managing state across components.
- **Map Optimization:**  
  Implement marker clustering for areas with dense data and enhance zoom controls.
- **Advanced Form Handling:**  
  Use Formik or React Hook Form for robust form management.
- **Enhanced Testing:**  
  Add unit tests using Jest/React Testing Library and E2E tests using Cypress.

---

## Troubleshooting

- **Leaflet SSR Issues:**
  ```jsx
  import dynamic from 'next/dynamic';

  const Map = dynamic(() => import('@/components/Map'), { ssr: false });
  ```
- **Responsive Layouts:**  
  Leverage Tailwind CSS responsive prefixes (e.g., `sm:`, `md:`, `lg:`) to ensure mobile-friendly design.
- **Form Validation:**  
  Implement custom validation functions to manage error states effectively.

---

## Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/YourFeature
   ```
3. Commit your changes.
4. Push to your branch and open a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*This frontend was developed as part of the Tweeza project for the Djezzy Code Fest hackathon, aimed at empowering community solidarity and volunteerism in Algeria.*