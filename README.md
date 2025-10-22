# String Analyzer API

RESTful API service that analyzes strings and stores their computed properties.

## Features
- Analyze string properties (length, palindrome, character frequency, etc.)
- SHA-256 hashing for unique identification
- Filter strings by multiple criteria
- Natural language query support
- Full CRUD operations

## Tech Stack
- Python 3.11
- Django 5.0
- Django REST Framework
- MySQL

## Local Setup

1. Clone the repository:

2. Create virtual environment:

3. Install dependencies:

4. Set up environment variables

5. Run migrations:

6. Start development server:

API will be available at `http://localhost:8000`

## API Endpoints

### 1. Create String
```
POST /strings
Content-Type: application/json

{
  "value": "hello world"
}
```

### 2. Get String
```
GET /strings/{string_value}
```

### 3. List Strings
```
GET /strings?is_palindrome=true&min_length=5
```

### 4. Natural Language Filter
```
GET /strings/filter-by-natural-language?query=all%20single%20word%20strings
```

### 5. Delete String
```
DELETE /strings/{string_value}
```

## Deployment

Deployed on Heroku: []

## Environment Variables

- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `DATABASE_URL`: Database connection string
