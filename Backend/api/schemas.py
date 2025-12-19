from typing import Dict, List, Optional

from pydantic import BaseModel


class RecommendRequest(BaseModel):
    quiz_answers: str
    top_n: int = 5


class CareerItem(BaseModel):
    career_title: str
    description: str
    skills: str
    personality_match: str
    education_required: str
    average_salary_usd: float
    job_outlook: str
    learning_resources: str
    similarity_score: float


class RecommendResponse(BaseModel):
    recommendations: List[CareerItem]


class UserCreate(BaseModel):
    username: str
    email: str  # Added email field
    password: str
    type: str  # Changed from account_type to type


class ProfileCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    bio: str
    location: str
    profile_picture: str


class CareerBase(BaseModel):
    name: str
    description: str
    salary: Optional[float] = None
    resources: Optional[Dict] = None


class CareerCreate(CareerBase):
    pass


class CareerRead(CareerBase):
    id: int

    class Config:
        from_attributes = True


class CourseBase(BaseModel):
    id: int
    career_id: int
    title: str
    provider: str
    description: str
    tags: Optional[List[str]] = None
    rating: Optional[float] = None
    students_enrolled: Optional[str | int] = None
    count_students: Optional[int] = None  # Added count_students_enrolled field
    duration_weeks: Optional[int] = None
    cost_type: Optional[str] = None
    level: Optional[str] = None
    url: str
    course_image_url: Optional[str] = None  # Added course_image_url field


class CourseCreate(CourseBase):
    pass


class CourseRead(CourseBase):
    id: int

    class Config:
        from_attributes = True


# ----------------------------------------
# UPDATED GIG SCHEMAS TO MATCH YOUR MODEL
# ----------------------------------------
class GigBase(BaseModel):
    title: str  # Changed from gig_title
    company: str
    description: str
    budget_min_usd: Optional[float] = None
    budget_max_usd: Optional[float] = None
    duration_weeks: Optional[int | str] = None
    location: Optional[str | int] = None  # Updated to be optional as per your model
    applicants: Optional[int | str] = None
    count_applicants: Optional[int | str] = None
    required_skills: Optional[str | int] = None
    category: Optional[str | int] = None
    posted_hours_ago: Optional[int | str] = None
    url: str
    status: Optional[str] = None  # Added status field
    career_id: int


class GigCreate(GigBase):
    pass


class GigRead(GigBase):
    id: int

    class Config:
        from_attributes = True


class QuizResponseBase(BaseModel):
    user_id: int
    answers: str  # Change to string to match quiz_answers field


class QuizResponseCreate(QuizResponseBase):
    pass


class QuizResponseRead(QuizResponseBase):
    id: int

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int | None = None
    email: str
    username: str
    profile: dict | None = None
    isPremium: bool | None = None
    account_type: str  # Ensure this field exists in your User model


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class LoginRequest(BaseModel):
    email: str
    password: str


class DashboardSummary(BaseModel):
    posted_gigs: int
    total_applicants: int
    active_gigs: int
    completed_gigs: int
    total_revenue: float
    avg_rating: float
