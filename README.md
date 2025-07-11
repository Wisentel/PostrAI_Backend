# PostrAI Backend

This is the backend API for the PostrAI application, built with FastAPI and MongoDB.

## Features

- User registration and authentication with password hashing (bcrypt)
- MongoDB integration for data storage
- RESTful API endpoints
- CORS support for frontend integration
- Input validation with Pydantic models
- Secure password hashing with bcrypt

## Setup Instructions

1. **Prerequisites:**
   - Python 3.8+
   - MongoDB Atlas account or local MongoDB instance

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration:**
   - Copy `.env.example` to `.env`
   - Update the MongoDB URI with your credentials
   ```bash
   cp .env.example .env
   ```

4. **Run the server:**
   ```bash
   python app_main.py
   ```
   
   Alternatively, you can use uvicorn directly:
   ```bash
   uvicorn app_main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **API Access:**
   - Main API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/signup`: User registration
  - Body: `{"firstName": "John", "lastName": "Doe", "email": "john@example.com", "password": "securepassword"}`
  - Returns: User profile data (without password)

- `POST /api/login`: User login
  - Body: `{"email": "john@example.com", "password": "securepassword"}`
  - Returns: User profile data (without password)

### Utility
- `GET /api/health`: Health check endpoint

### Other
- `POST /api/scraper/master-scraper`: Scraper endpoint (placeholder)

## Database Schema

### User Profile Collection (`user_profile`)
```json
{
  "_id": "ObjectId",
  "user_id": "6-character-string",
  "firstName": "string",
  "lastName": "string", 
  "email": "string (unique)",
  "password": "hashed-password",
  "created_at": "ISO-date-string",
  "updated_at": "ISO-date-string"
}
```

## Security Features

- Password hashing using bcrypt
- Email uniqueness validation
- Input validation with Pydantic models
- CORS protection
- MongoDB connection with proper error handling

## File Structure

```
backend/
├── app_main.py           # Main FastAPI application
├── models.py             # Pydantic data models
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── .env.example         # Environment variables example
├── helpers/
│   └── user.py          # Password hashing utilities
└── database/
    └── mongodb.py       # MongoDB connection and operations
```

## Development Notes

- **Data Storage**: All data is stored in MongoDB - no local JSON files are used
- The MongoDB connection is configured in `database/mongodb.py`
- Password hashing utilities are in `helpers/user.py`
- All user passwords are hashed using bcrypt before storage
- The database creates indexes automatically for better performance
- Error handling is implemented for all database operations
- Email uniqueness is enforced at the database level 