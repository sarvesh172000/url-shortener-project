 Scalable URL Shortener Service

This project is a high-performance, scalable URL shortener service built with Python (FastAPI). It includes a backend API, a PostgreSQL database for persistent storage, a Redis cache for fast lookups, and a simple frontend interface.

## Features

* **URL Shortening**: Convert any long URL into a short, unique key.
* **Fast Redirection**: Quickly redirects users from the short URL to the original target URL.
* **Click Tracking**: Counts the number of times each shortened URL is used.
* **Analytics Endpoint**: A private endpoint to view the statistics for a specific URL.
* **Caching**: Utilizes Redis to cache frequently accessed URLs, significantly reducing database load and speeding up redirects.
* **API Rate Limiting**: Protects the URL creation endpoint from spam and abuse.
* **Web Interface**: A simple, clean frontend for users to easily shorten URLs.

## Tech Stack

* **Backend**: Python with [FastAPI](https://fastapi.tiangolo.com/)
* **Database**: [PostgreSQL](https://www.postgresql.org/)
* **Caching**: [Redis](https://redis.io/)
* **Containerization**: [Docker](https://www.docker.com/)
* **API Validation**: [Pydantic](https://docs.pydantic.dev/)
* **Database ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
* **Frontend**: HTML, CSS, JavaScript

## Project Structure

```
url-shortener-project/
├── backend/
│   ├── __pycache__/
│   ├── venv/
│   ├── crud.py         # Database interaction functions (Create, Read, Update)
│   ├── database.py     # SQLAlchemy database connection setup
│   ├── main.py         # Main FastAPI application, API endpoints
│   ├── models.py       # SQLAlchemy database models (table schemas)
│   └── schemas.py      # Pydantic models for data validation
│
├── frontend/
│   ├── app.js          # Frontend JavaScript logic
│   ├── index.html      # Main HTML page
│   └── style.css       # Styles for the frontend
│
└── .gitignore          # Specifies files for Git to ignore
```

## Local Development Setup

### Prerequisites

* [Python 3.8+](https://www.python.org/downloads/)
* [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Step-by-Step Instructions

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/sarvesh172000/url-shortener-project.git](https://github.com/sarvesh172000/url-shortener-project.git)
    cd url-shortener-project
    ```

2.  **Set Up the Backend:**
    * Navigate to the `backend` directory:
        ```bash
        cd backend
        ```
    * Create and activate a Python virtual environment:
        * On Windows:
            ```bash
            python -m venv venv
            venv\Scripts\activate
            ```
        * On macOS/Linux:
            ```bash
            python3 -m venv venv
            source venv/bin/activate
            ```
    * Install the required Python packages:
        ```bash
        pip install -r requirements.txt
        ```
        *(Note: You will need to create a `requirements.txt` file first. Run `pip freeze > requirements.txt` in your activated environment to generate it.)*

3.  **Start the Services (Database and Cache):**
    * Make sure Docker Desktop is running.
    * Open a new terminal and run the following commands to start the PostgreSQL and Redis containers:
        ```bash
        # Start PostgreSQL database
        docker run --name url-shortener-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d postgres

        # Start Redis cache
        docker run --name url-shortener-cache -p 6379:6379 -d redis
        ```

4.  **Run the Application:**
    * Navigate to the root directory of the project (`url-shortener-project`).
    * Run the Uvicorn server:
        ```bash
        uvicorn backend.main:app --reload
        ```

5.  **Access the Application:**
    * **Frontend**: Open your browser and go to `http://127.0.0.1:8000`
    * **API Docs**: For interactive API documentation, go to `http://127.0.0.1:8000/docs`

## API Endpoints

#### `POST /shorten`

Creates a new shortened URL.

* **Request Body:**
    ```json
    {
      "target_url": "[https://www.example.com/a-very-long-url-to-shorten](https://www.example.com/a-very-long-url-to-shorten)"
    }
    ```
* **Success Response (200 OK):**
    ```json
    {
      "target_url": "[https://www.example.com/a-very-long-url-to-shorten](https://www.example.com/a-very-long-url-to-shorten)",
      "is_active": true,
      "clicks": 0,
      "url": "[http://127.0.0.1:8000/aBcD1](http://127.0.0.1:8000/aBcD1)",
      "admin_url": "[http://127.0.0.1:8000/admin/aBcD1_secretKey](http://127.0.0.1:8000/admin/aBcD1_secretKey)"
    }
    ```

#### `GET /{url_key}`

Redirects to the original target URL.

* **Example:** `http://127.0.0.1:8000/aBcD1`
* **Success Response:** A `307 Temporary Redirect` to the `target_url`.
* **Failure Response (404 Not Found):** If the `url_key` does not exist.

#### `GET /admin/{secret_key}`

Retrieves the analytics for a specific shortened URL.

* **Example:** `http://127.0.0.1:8000/admin/aBcD1_secretKey`
* **Success Response (200 OK):** The same JSON object as the `POST /shorten` response, with an updated `clicks` count.
* **Failure Response (404 Not Found):** If the `secret_key` does not exist.