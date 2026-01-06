# Acad AI

Acad AI is a Django-based assessment engine designed to handle course management, exam delivery, and automated grading. It uses Google's Gemini LLM to provide intelligent feedback on student submissions, with a built-in fallback system for reliability.

## Features

- **Automated Grading**: Integration with Gemini 1.5 Flash for nuanced evaluation of student answers.
- **Reliability**: A keyword-based mock grader that takes over if the LLM service is unavailable.
- **Security**: JWT-based authentication for students and instructors, with role-based access control.
- **API Documentation**: Interactive documentation available via Swagger/OpenAPI.
- **Testing**: A comprehensive suite of 56 unit and integration tests covering the entire grading and authentication flow.

## Technical Setup

### 1. Environment Preparation
Clone the repository and set up a Python virtual environment:

```bash
cd acad_ai
python3 -m venv venv
source venv/bin/activate
```

### 2. Dependencies
Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory. You will need to configure the following variables:

- `SECRET_KEY`: Your Django secret key.
- `DEBUG`: Set to `True` for development.
- `LLM_API_KEY`: Your Google Gemini API key.
- `LLM_MODEL`: Defaults to `gemini-1.5-flash`.
- `GRADING_SERVICE`: Use `llm` for Gemini or `mock` for local keyword grading.

### 4. Database Initialization
Generate and apply migrations to set up the SQLite database:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Running the Application
Start the development server:

```bash
python manage.py runserver
```

Once the server is running, you can access the documentation at `http://localhost:8000/docs/` to test the various endpoints.

## Core Endpoints & Permissions

The API uses role-based access control. Below are the primary endpoints and the users authorized to access them.

### Authentication (Public)
- `POST /auth/register/`: Create a new user account.
- `POST /auth/login/`: Authenticate and receive JWT access/refresh tokens.

### Instructor Operations
Only users with the `INSTRUCTOR` role can access these:
- `POST /exams/courses/`: Create a new academic course.
- `POST /exams/create/`: Create a new exam with nested questions and rubrics.
- `PUT /exams/{uuid}/update/`: Modify an existing exam.
- `DELETE /exams/{uuid}/delete/`: Remove an exam from the system.

### Student Operations
Only users with the `STUDENT` role can access these:
- `GET /exams/`: View a list of all available exams.
- `GET /exams/{uuid}/`: Retrieve specific exam details and questions.
- `POST /submissions/`: Submit answers for an exam.
- `GET /submissions/list/`: View a list of your past submissions.
- `GET /submissions/{uuid}/`: View specific submission details, including score and LLM-generated feedback.

## Quality Assurance

To run the full test suite and verify the implementation:

```bash
pytest
```

The project follows `black` for formatting and `flake8` for linting to ensure code consistency.

## Usage Note
Authentication is required for most endpoints. After registering or logging in, include the access token in the `Authorization` header as a `Bearer` token for subsequent requests.
