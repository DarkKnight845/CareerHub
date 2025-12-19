# CareerHub AI Recommendation Platform

An intelligent career recommendation system that leverages NLP and transformer-based semantic matching to provide personalized career guidance, course recommendations, and gig opportunities for students and businesses.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Database Models](#database-models)
- [Recommendation System](#recommendation-system)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

CareerHub is an AI-powered platform designed to match users with suitable career paths based on their skills, interests, and personality traits. The platform uses semantic similarity analysis powered by sentence transformers to provide highly accurate and personalized recommendations.

### Key Capabilities

- **AI-Driven Career Matching**: Semantic analysis of user responses to match with optimal career paths
- **Personalized Course Recommendations**: Curated learning resources aligned with career goals
- **Gig Marketplace**: Connect students with freelance opportunities matching their skills
- **Business Dashboard**: Analytics and insights for business users managing gigs and tracking applicants
- **User Profiles**: Comprehensive profile management with certifications and enrollment tracking

## ✨ Features

### For Students
- Interactive career assessment quiz
- AI-powered career recommendations with similarity scores
- Browse and enroll in relevant courses
- Apply for gigs and freelance opportunities
- Track learning progress and certifications
- View personalized dashboards with recommendations history

### For Businesses
- Post and manage gig opportunities
- View applicant profiles and track applications
- Dashboard analytics (posted gigs, applicants, revenue, ratings)
- Search and filter gigs by category, location, and skills

### Core System Features
- JWT-based authentication and authorization
- RESTful API architecture
- Semantic search and filtering for courses and gigs
- Real-time recommendation generation
- Persistent recommendation history
- User enrollment and application tracking

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens), bcrypt password hashing
- **AI/ML**: 
  - Sentence Transformers (all-MiniLM-L6-v2)
  - scikit-learn (cosine similarity)
  - pandas, numpy
  - joblib (model persistence)

### Key Libraries
```
fastapi
sqlalchemy
sentence-transformers
scikit-learn
pandas
numpy
joblib
python-jose[cryptography]
passlib[bcrypt]
python-multipart
```

## 📁 Project Structure
```
CareerHub/
├── Backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication utilities
│   │   ├── routes.py            # API endpoints
│   │   └── schemas.py           # Pydantic models
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── app.db               # SQLite database
│   │   └── load.py              # Database initialization
│   └── __pycache__/
├── model/
│   ├── recommender.py           # Semantic recommendation engine
│   └── cache/                   # Cached embeddings
│       ├── career_embeddings.npy
│       └── career_titles.pkl
├── data/
│   ├── careers.csv              # Career dataset
│   ├── courses.csv              # Course catalog
│   └── gigs.csv                 # Gig listings
├── requirements.txt
├── .env
└── README.md
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/DarkKnight845/CareerHub.git
cd careerhub
```

2. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./Backend/database/app.db
```

5. **Initialize the database**
```bash
python -c "from Backend.database.models import create_db_tables; create_db_tables()"
```

6. **Load initial data (optional)**
```bash
python Backend/database/load.py
```

7. **Run the application**
```bash
uvicorn Backend.api.routes:app --reload
```

The API will be available at `http://localhost:8000`

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT secret key for token generation | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |
| `DATABASE_URL` | SQLite database path | sqlite:///./Backend/database/app.db |

### Model Configuration

The recommendation system uses `all-MiniLM-L6-v2` from Sentence Transformers. To use a different model, modify `model_name` in `model/recommender.py`:
```python
recommender = SemanticRecommender(data, model_name="your-model-name")
```

## 📡 API Endpoints

### Authentication

#### Sign Up
```http
POST /signup
Content-Type: application/json

{
  "username": "string",
  "email": "string",
  "password": "string",
  "type": "Student" | "Business"
}
```

#### Login
```http
POST /login
Content-Type: application/json

{
  "email": "string",
  "password": "string"
}

Response: {
  "access_token": "string",
  "token_type": "bearer",
  "user": { ... }
}
```

### Profile Management

#### Create Profile
```http
POST /Createprofile
Authorization: Bearer {token}

{
  "username": "string",
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "string",
  "gender": "string",
  "bio": "string",
  "location": "string",
  "profile_picture": "string"
}
```

#### Update Profile
```http
PUT /UpdateProfile
Authorization: Bearer {token}

{
  "username": "string",
  "location": "string",
  "bio": "string"
}
```

#### Get Profile
```http
GET /profile
Authorization: Bearer {token}
```

### Courses

#### Get All Courses
```http
GET /courses?search={query}&level={level}&cost_type={type}&skip=0&limit=100
```

**Query Parameters:**
- `search`: Search term for title or tags
- `level`: Filter by level (Beginner, Intermediate, Advanced)
- `cost_type`: Filter by cost (Free, Paid)
- `skip`: Pagination offset
- `limit`: Results per page

#### Get Course by Title
```http
GET /courses/{title}
```

#### Enroll in Course
```http
POST /courses/{course_title}/enroll
Authorization: Bearer {token}
```

#### Get User's Enrolled Courses
```http
GET /users/{username}/courses
```

### Gigs

#### Get All Gigs
```http
GET /gigs?search={query}&category={category}&location={location}&skip=0&limit=100
```

#### Get Gig by ID
```http
GET /gigs/id/{gig_id}
```

#### Get Gig by Title
```http
GET /gigs/title/{gig_title}
```

#### Apply for Gig
```http
POST /gigs/id/{gig_id}/apply
Authorization: Bearer {token}
```
```http
POST /gigs/title/{gig_title}/apply
Authorization: Bearer {token}
```

#### Get User's Applied Gigs
```http
GET /users/{user_id}/gigs
```

### Dashboard (Business Users Only)

#### Get Dashboard Summary
```http
GET /Userdashboard/summary
Authorization: Bearer {token}

Response: {
  "posted_gigs": 0,
  "total_applicants": 0,
  "active_gigs": 0,
  "completed_gigs": 0,
  "total_revenue": 0.0,
  "avg_rating": 0.0
}
```

#### Get My Posted Gigs
```http
GET /dashboard/my_gigs
Authorization: Bearer {token}
```

### Recommendations

#### Get Career Recommendations
```http
POST /recommend
Authorization: Bearer {token}
Content-Type: application/json

{
  "quiz_answers": "I enjoy solving complex problems and working with data..."
}

Response: {
  "recommendations": [
    {
      "career_title": "Data Scientist",
      "description": "...",
      "skills": "...",
      "personality_match": "...",
      "education_required": "...",
      "average_salary_usd": 120000,
      "job_outlook": "...",
      "learning_resources": "...",
      "similarity_score": 0.85
    }
  ]
}
```

#### Get Recommendation History
```http
GET /history
Authorization: Bearer {token}
```

## 🗄️ Database Models

### User
- **Fields**: id, username, email, hashed_password, is_active, first_name, last_name, date_of_birth, gender, bio, location, profile_picture, type
- **Relationships**: certifications, quiz_responses, enrolled_courses, completed_gigs, quizzes, recommendations

### Career
- **Fields**: id, name, skills, personality_match, education_required, description, salary, job_outlook, resources
- **Relationships**: courses, gigs

### Course
- **Fields**: id, career_id, title, provider, description, tags, rating, students_enrolled, count_students, duration_weeks, cost_type, level, url, course_image_url
- **Relationships**: career, users (many-to-many)

### Gig
- **Fields**: id, career_id, title, company, description, budget_min_usd, budget_max_usd, duration_weeks, location, applicants, count_applicants, required_skills, category, posted_hours_ago, url, status
- **Relationships**: career, users (many-to-many)

### Quiz
- **Fields**: id, quiz_answers, user_id
- **Relationships**: user, recommendations

### Recommendation
- **Fields**: id, career_title, description, skills, personality_match, education_required, average_salary_usd, job_outlook, learning_resources, similarity_score, user_id, quiz_id
- **Relationships**: user, quiz

### Certification
- **Fields**: id, user_id, title, issuer, earned_on, verification_id, view_url, download_url
- **Relationships**: user

## 🤖 Recommendation System

### Architecture

The recommendation engine uses **semantic similarity analysis** powered by transformer-based language models:

1. **Text Embedding**: Career data (description, skills, personality match) is encoded into dense vector representations using Sentence Transformers
2. **User Input Processing**: Quiz answers are encoded using the same model
3. **Similarity Calculation**: Cosine similarity measures the alignment between user responses and career profiles
4. **Ranking**: Careers are ranked by similarity score, returning top N matches

### SemanticRecommender Class
```python
class SemanticRecommender:
    def __init__(self, df: pd.DataFrame, model_name="all-MiniLM-L6-v2"):
        # Loads model and computes/caches career embeddings
        
    def recommend(self, quiz_answers_text: str, top_n: int = 5):
        # Returns top N career recommendations with similarity scores
```

### Caching Strategy

- Career embeddings are computed once and cached to disk (`cache/career_embeddings.npy`)
- Career titles are cached separately (`cache/career_titles.pkl`)
- On subsequent runs, cached embeddings are loaded instantly
- Cache is invalidated if dataset length changes

### Performance

- **Embedding Computation**: ~2-5 seconds for 100 careers (one-time)
- **Recommendation Generation**: < 100ms with cached embeddings
- **Model Size**: ~80MB (all-MiniLM-L6-v2)
- **Scalability**: Handles 1000+ careers efficiently

## 📖 Usage

### Example: Getting Career Recommendations
```python
import requests

# 1. Sign up
response = requests.post("http://localhost:8000/signup", json={
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword",
    "type": "Student"
})

# 2. Login
response = requests.post("http://localhost:8000/login", json={
    "email": "john@example.com",
    "password": "securepassword"
})
token = response.json()["access_token"]

# 3. Get recommendations
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/recommend",
    json={
        "quiz_answers": "I love analyzing data and building predictive models. I'm detail-oriented and enjoy problem-solving."
    },
    headers=headers
)
recommendations = response.json()["recommendations"]

# 4. Browse courses
response = requests.get(
    "http://localhost:8000/courses?search=data science&level=Beginner"
)
courses = response.json()

# 5. Enroll in a course
response = requests.post(
    "http://localhost:8000/courses/Introduction to Data Science/enroll",
    headers=headers
)
```

### Example: Business User Dashboard
```python
# Login as business user
response = requests.post("http://localhost:8000/login", json={
    "email": "business@example.com",
    "password": "businesspass"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Get dashboard summary
response = requests.get(
    "http://localhost:8000/Userdashboard/summary",
    headers=headers
)
summary = response.json()
print(f"Posted Gigs: {summary['posted_gigs']}")
print(f"Total Applicants: {summary['total_applicants']}")
print(f"Total Revenue: ${summary['total_revenue']}")
```

## 🧪 Testing

Run the development server:
```bash
uvicorn Backend.api.routes:app --reload
```

Access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Add docstrings to all functions and classes
- Write unit tests for new features
- Update documentation for API changes


## 👥 Authors

- **Aderounmu Adeyemi** - *Initial work* - [GitHub](https://github.com/DarkKnight845)

## 🙏 Acknowledgments

- Sentence Transformers library for semantic encoding
- FastAPI framework for rapid API development
- The open-source community for inspiration and tools

## 📞 Contact

For questions or support, please contact:
- Email: ayemiaded2020@gmail.com
- LinkedIn: [LinkedIn Profile](https://www.linkedin.com/in/adeyemi-aderounmu/)
- GitHub Issues: [Project Issues Page](https://github.com/DarkKnight845/CareerHub.git)

---

**Built with ❤️ for career guidance and professional development**