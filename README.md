# Movie Recommendation System

This project is a Django-based web application designed to provide a personalized movie recommendation experience. It
allows users to browse a movie catalog, rate movies, manage a watchlist, and potentially receive recommendations based
on various factors. The system leverages Django's robust ORM for data management and is structured to support scalable
deployment with ASGI/WSGI servers.

---

## 📝 Table of Contents

-   [🚀 Tech Stack](#-tech-stack)
-   [✨ Key Features](#-key-features)
-   [📁 Folder Structure](#-folder-structure)
-   [⚙️ Installation Instructions](#-installation-instructions)
-   [▶️ Usage Examples](#%E2%96%B6%EF%B8%8F-usage-examples)
-   [🌍 Configuration / Environment Variables](#-configuration--environment-variables)
-   [💡 How the Code Works](#-how-the-code-works)

---

## 🚀 Tech Stack

The project is built using the following technologies:

-   **Backend Framework**:
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
-   **Programming Language**:
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
-   **Database**: ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
-   **Frontend**:
    -   HTML
    -   CSS (`static/css/style.css`)
    -   JavaScript (`static/js/script.js`)
-   **Application Server Support**: ASGI / WSGI
-   **Key Python Modules**: `os`, `sys`, `re`

---

## ✨ Key Features

Based on the available information, the application offers the following functionalities:

-   **User Authentication & Profiles**: Secure user registration, login, and profiles to store demographic information
(age, gender, occupation, zip code).
-   **Movie Catalog**: Comprehensive listing of movies with titles, genres, years, and poster URLs.
-   **User Ratings**: Ability for users to rate movies (1-5 stars) with unique rating constraints.
-   **Watchlist Management**: Users can add movies to a personal watchlist and mark them as watched.
-   **Admin Interface**: Django's built-in administrative panel for managing models.
-   **Data Management**: Custom Django management command for loading initial data into the application (inferred from
`load_all_data.py`).
-   **Machine Learning Assets**: Presence of `.pkl` files (e.g., `cluster_sim.pkl`, `similarity_matrix.pkl`,
`xgb_model.pkl`) indicates the integration or readiness for machine learning-based features, likely for recommendations.
*Specific details on how these are used in the recommendation logic and user accessibility are not available in the
provided summaries.*

---

## 📁 Folder Structure

```
./
    ├── db.sqlite3
    ├── db_backup.sqlite3
    └── manage.py
    ├── config/
        ├── asgi.py
        ├── settings.py
        ├── urls.py
        ├── wsgi.py
    ├── core/
        ├── admin.py
        ├── apps.py
        ├── models.py
        ├── recommender.py
        ├── tests.py
        ├── urls.py
        ├── views.py
        ├── management/
            ├── commands/
                └── load_all_data.py
        ├── migrations/
            ├── 0001_initial.py
            ├── 0002_alter_userrating_id_alter_watchlistitem_id_and_more.py
    ├── data/
        ├── cluster_sim.pkl
        ├── data.pkl
        ├── movies_for_similarity.pkl
        ├── similarity_matrix.pkl
        └── xgb_model.pkl
    ├── static/
        ├── css/
            └── style.css
        ├── js/
            └── script.js
    ├── templates/
        ├── core/
            ├── admin_dashboard.html
            ├── base.html
            ├── browse.html
            ├── home.html
            ├── login.html
            ├── more_recommendations.html
            ├── movie_card.html
            ├── movie_detail.html
            ├── register.html
            ├── search.html
            └── watchlist.html
```

---

## ⚙️ Installation Instructions

To set up and run the project locally, follow these steps:

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**:
    The project relies on Django. While a `requirements.txt` file is not explicitly provided in the summaries, you will
need to install Django and any other necessary Python packages.
    ```bash
    pip install Django # Or `pip install -r requirements.txt` if available
    ```
    *Note: Please ensure all required Python packages are installed, as a comprehensive `requirements.txt` file was not
available in the provided data.*

4.  **Apply Database Migrations**:
    This will create the necessary database tables based on the models defined in `core/models.py`.
    ```bash
    python manage.py makemigrations core
    python manage.py migrate
    ```

5.  **Load Initial Data (Optional)**:
    If there is a custom management command to load initial data (e.g., movies, users), execute it.
    *(Inferred from `core/management/commands/load_all_data.py`, details about this command are not available.)*
    ```bash
    python manage.py load_all_data
    ```

6.  **Create a Superuser** (for admin access):
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set up a username, email, and password.

7.  **Run the Development Server**:
    ```bash
    python manage.py runserver
    ```
    The application will be accessible at `http://127.0.0.1:8000/`.

---

## ▶️ Usage Examples

Once the server is running, you can:

-   **Access the application**: Open `http://127.0.0.1:8000/` in your web browser.
-   **Register / Log In**: Create a new account or log in with existing credentials to access personalized features.
-   **Browse Movies**: Navigate through the movie catalog.
-   **Rate Movies**: Submit ratings for movies to influence recommendations.
-   **Manage Watchlist**: Add movies to your watchlist or mark watched items.
-   **Admin Interface**: Access the Django admin at `http://127.0.0.1:8000/admin/` using your superuser credentials to
manage application data (users, movies, ratings, etc.).

---

## 🌍 Configuration / Environment Variables

The project's behavior can be influenced by several settings and environment variables:

-   **`DJANGO_SETTINGS_MODULE`**:
    -   **Description**: Specifies the settings module for the Django project.
    -   **Default**: `'config.settings'` (set by `manage.py`, `config/asgi.py`, `config/wsgi.py`).
-   **`SECRET_KEY`**:
    -   **Description**: A unique, unpredictable value used by Django for cryptographic signing.
    -   **Value**: `'django-insecure-wt21csvsm9fv7ob1d*09hpr7ak6wsxks27*g*)*zd1t(dtww(w'` (from `config/settings.py`).
-   **`DEBUG`**:
    -   **Description**: Controls whether Django runs in debug mode.
    -   **Value**: `True` (from `config/settings.py`).
-   **`ALLOWED_HOSTS`**:
    -   **Description**: A list of strings representing the host/domain names that this Django site can serve.
    -   **Value**: `[]` (empty, from `config/settings.py`).
-   **Database Configuration**:
    -   **Engine**: `django.db.backends.sqlite3`
    -   **Name**: `BASE_DIR / 'db.sqlite3'` (from `config/settings.py`).
-   **Static Files**:
    -   **`STATIC_URL`**: `'static/'` (from `config/settings.py`).
    -   **`STATICFILES_DIRS`**: `['BASE_DIR / "static"']` (from `config/settings.py`).
-   **Media Files**:
    -   **`MEDIA_URL`**: `'/media/'` (from `config/settings.py`).
    -   **`MEDIA_ROOT`**: `BASE_DIR / 'media'` (from `config/settings.py`).
-   **Redirect URLs**:
    -   **`LOGIN_REDIRECT_URL`**: `'/'` (from `config/settings.py`).
    -   **`LOGOUT_REDIRECT_URL`**: `'/` (from `config/settings.py`).

---

## 💡 How the Code Works

This Django project follows a standard structure, with clear separation of concerns:

-   **`manage.py`**: This is the primary command-line utility for interacting with the Django project. It sets up the
environment and executes various administrative tasks like running the server, applying migrations, or running custom
commands.

-   **`config/` Directory**: This directory holds the project-wide configuration.
    -   **`settings.py`**: Defines all core Django settings, including installed applications (`core` app is included),
middleware, database configuration (SQLite is used), template settings, static/media file handling, and authentication
redirects.
    -   **`urls.py`**: The root URL configuration file, it routes requests to the Django admin interface (`/admin/`) and
includes all URL patterns defined within the `core` application. It also handles serving static and media files during
development.
    -   **`asgi.py` & `wsgi.py`**: These files expose the ASGI (Asynchronous Server Gateway Interface) and WSGI (Web
Server Gateway Interface) callables, respectively. They are the entry points for modern asynchronous and traditional
synchronous web servers (like Uvicorn, Gunicorn, Daphne) to serve the Django application.

-   **`core/` Application**: This is the main application containing the business logic and models.
    -   **`apps.py`**: Configures the `core` Django application, defining its name as `'core'`.
    -   **`models.py`**: Defines the application's database schema using Django's ORM.
        -   `UserProfile`: Extends Django's built-in `User` model to store additional demographic data like age, gender,
occupation, and zip code.
        -   `Movie`: Stores movie metadata including title, genres, an automatically extracted year, and a poster URL.
It includes methods for cleaning titles and extracting release years.
        -   `UserRating`: Links users to movies with a specific rating (1-5), ensuring that each user can rate a movie
only once.
        -   `WatchlistItem`: Tracks movies that users wish to watch, including a timestamp and a "watched" flag.
    -   **`admin.py`**: This file is currently a placeholder module. It would typically be used to register the
`UserProfile`, `Movie`, `UserRating`, and `WatchlistItem` models with the Django administration interface, allowing easy
management of these models through the web UI.
    -   **`management/commands/load_all_data.py`**: This indicates a custom Django management command designed for
loading all necessary initial data into the database. *(Specific implementation details for this command are not
available in the provided summaries.)*
    -   **`recommender.py`**: This file is likely intended to house the recommendation logic. *(Its summary details were
not available due to a rate limit, so its specific functionalities cannot be described.)*

-   **`data/` Directory**: This directory stores pre-processed data and trained machine learning models.
    -   Files like `cluster_sim.pkl`, `data.pkl`, `movies_for_similarity.pkl`, `similarity_matrix.pkl`, and
`xgb_model.pkl` suggest that the project uses machine learning models (e.g., XGBoost for classification/regression,
similarity matrices for collaborative filtering) to power its recommendation system. *(The exact integration and usage
of these models are not detailed in the provided summaries.)*

-   **`static/` Directory**: Contains static assets like CSS (`style.css`) and JavaScript (`script.js`) files that
define the look and interactive behavior of the frontend. *(Specific contents of these files were not available.)*

-   **`templates/` Directory**: Houses the HTML template files for rendering the web interface. These include
`base.html` for common layout, and specific templates for various pages such as `home.html`, `browse.html`,
`movie_detail.html`, `watchlist.html`, `login.html`, `register.html`, `search.html`, `admin_dashboard.html`,
`movie_card.html`, and `more_recommendations.html`. *(Specific contents of these files were not available.)*
