# SetList Music Store

## Description

SetList Music Store is a full-stack Django-based web application designed for managing and selling sheet music collections. The platform allows users to browse curated music collections, view individual sheet music items, manage a shopping cart, and complete a checkout process. In addition to the web interface, the project exposes REST API endpoints for programmatic access to collections and reviews.

This project was built as a portfolio piece to demonstrate full-stack development skills, Django architecture, REST API design, database integration, and clean UI styling without external frontend frameworks.

---

## Key Features

- **User Authentication**
  - Login and logout functionality
  - Token-based authentication for API access

- **Music & Collection Management**
  - Create, edit, view, and delete music collections
  - Browse individual sheet music items within collections
  - Composer-based collection filtering via API

- **Shopping Cart & Checkout**
  - Add, update, and remove items from a user cart
  - Checkout workflow with order processing logic

- **REST API**
  - Public and authenticated API endpoints
  - Token authentication using Django REST Framework
  - Endpoints for collections, sheet music, and reviews

- **Media Handling**
  - Upload and display cover images and sheet music previews
  - Media served locally in development

- **Social Integration**
  - Twitter (X) OAuth 1.0a integration for posting updates with optional media uploads

---

## Technologies Used

- **Backend:** Python, Django 5, Django REST Framework
- **Database:** MariaDB (MySQL-compatible)
- **Frontend:** Django Templates, HTML, CSS
- **Authentication:** Django Auth, DRF Token Authentication
- **External APIs:** Twitter (X) API via OAuth 1.0a
- **Media Processing:** Pillow
- **Environment:** Python virtual environment

---

## Architecture Overview

- Monolithic Django architecture with clear separation of concerns
- Traditional server-rendered HTML views for the web interface
- RESTful API layer built using Django REST Framework
- Token-protected API endpoints for authenticated access
- MariaDB used for persistent relational data storage
- Local media and static file handling for development

---

## Styling & UI Design

The application uses a custom global stylesheet (`style.css`) focused on clarity, consistency, and usability rather than heavy visual frameworks.

### Design Principles

- Minimalist, dark-themed interface to reduce visual noise
- Consistent layout and typography across all pages
- Clear contrast and readable fonts for accessibility
- Framework-free CSS to demonstrate core styling fundamentals

### Layout & Structure

- Centralised content layout with constrained widths for readability
- Flexbox-based navigation and grid layouts
- Shared header and footer across the application

### Components Styled

- Navigation menus and action buttons
- Forms (authentication, uploads, checkout)
- Sheet music cards and collection grids
- Image previews with controlled scaling
- Inline and block-level links with consistent hover behaviour

---

## Security Notes

- Django’s built-in authentication system is used for user accounts
- Token authentication secures REST API endpoints
- Sensitive credentials should be stored in environment variables in production
- OAuth tokens for Twitter are persisted locally for development convenience

---

## Environment Configuration

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Configure database and email settings in `settings.py` or via environment variables for production use.

---

## Database Setup

1. Create a MariaDB database:
   ```sql
   CREATE DATABASE setlist_db;
   ```
2. Update database credentials in `settings.py`
3. Run migrations:
   ```bash
   python manage.py migrate
   ```

---

## Running the Application

1. Apply migrations:
   ```bash
   python manage.py migrate
   ```
2. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
3. Start the development server:
   ```bash
   python manage.py runserver
   ```
4. Access the application at:
   ```
   http://127.0.0.1:8000/
   ```

---

## API Usage

- Obtain an authentication token:
  ```
  POST /api-token-auth/
  ```

- Example endpoints:
  - `/api/collections/`
  - `/api/sheetmusic/`
  - `/api/sheetmusic/<id>/reviews/`
  - `/api/composers/<id>/collections/`

API access requires a valid token for protected routes.

---

## Notes

- This project was completed prior to being uploaded to GitHub as part of a professional portfolio
- Styling intentionally avoids frontend frameworks to highlight core CSS and layout skills
- The application is configured for local development and demonstration purposes
