import json
from typing import List, Optional

import numpy as np
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

from Backend.api import auth
from Backend.api.auth import get_current_user
from Backend.api.schemas import (
    CareerCreate,
    CareerRead,
    CourseCreate,
    CourseRead,
    DashboardSummary,
    GigCreate,
    GigRead,
    LoginRequest,
    ProfileCreate,
    RecommendRequest,
    RecommendResponse,
    TokenResponse,
    UserCreate,
)
from Backend.database import models
from Backend.database.models import Quiz, Recommendation
from model.recommender import get_recommendations, recommender

app = FastAPI(title="AI Career Recommendation (Semantic + Auth)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_tags_string(tags_string: str | None) -> List[str]:
    """
    Splits a comma-separated string into a list of strings.
    """
    if tags_string:
        return [tag.strip() for tag in tags_string.split(",")]
    return []


@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(auth.get_db)):
    db_user = auth.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = auth.get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw,
        type=user.type,
    )
    if user.type.lower() == "Business".lower():
        new_user.type = "Business"
    elif user.type.lower() == "Student".lower():
        new_user.type = "Student"
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid account type. Must be 'Business' or 'Student'.",
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


@app.post("/Createprofile")
# create endpoint for first name, last name, bio
def create_profile(user: ProfileCreate, db: Session = Depends(auth.get_db)):
    db_user = auth.get_user(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db_user.date_of_birth = user.date_of_birth
    db_user.gender = user.gender
    db_user.bio = user.bio
    db_user.location = user.location
    db_user.profile_picture = user.profile_picture
    db.commit()
    db.refresh(db_user)
    return {"message": "Profile updated successfully"}


# update endpoint for profile
@app.put("/UpdateProfile")
def update_profile(user: ProfileCreate, db: Session = Depends(auth.get_db)):
    db_user = auth.get_user(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Update profile fields
    db_user.location = user.location
    db_user.bio = user.bio
    db.commit()
    db.refresh(db_user)
    return {"message": "Profile updated successfully"}


@app.get("/profile")
def get_profile(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(auth.get_db),
):
    profile = db.query(models.User).filter(models.User.id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "date_of_birth": profile.date_of_birth,
    }


@app.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(auth.get_db)):
    user = auth.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.username})
    user_out = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "profile": getattr(user, "profile", None),
        "isPremium": getattr(user, "isPremium", None),
        "account_type": user.type,
    }
    return {"access_token": access_token, "token_type": "bearer", "user": user_out}


@app.get("/health")
def health():
    return {"status": "ok"}


# Career Endpoints


@app.post("/careers", response_model=CareerRead)
def create_career(career: CareerCreate, db: Session = Depends(auth.get_db)):
    db_career = models.Career(**career.dict())
    db.add(db_career)
    db.commit()
    db.refresh(db_career)
    return db_career


@app.get("/careers", response_model=List[CareerRead])
def get_careers(db: Session = Depends(auth.get_db)):
    careers = db.query(models.Career).all()
    for career in careers:
        if isinstance(career.resources, str):
            try:
                career.resources = json.loads(career.resources)
            except Exception:
                career.resources = {}
        elif career.resources is None:
            career.resources = {}
    return careers


@app.post("/courses", response_model=CourseRead)
def create_course(course: CourseCreate, db: Session = Depends(auth.get_db)):
    tags_string = ", ".join(course.tags) if course.tags else None

    db_course = models.Course(**course.dict(exclude={"tags"}), tags=tags_string)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)

    db_course.tags = parse_tags_string(db_course.tags)

    return db_course


@app.get("/courses", response_model=List[CourseRead])
def get_courses(
    db: Session = Depends(auth.get_db),
    search: Optional[str] = Query(
        None, description="Search term for course title or tags"
    ),
    level: Optional[str] = Query(
        None, description="Filter by course level (e.g., 'Beginner', 'Intermediate')"
    ),
    cost_type: Optional[str] = Query(
        None, description="Filter by cost type (e.g., 'Free', 'Paid')"
    ),
    skip: int = 0,
    limit: int = 100,
):
    try:
        courses = db.query(models.Course)
        print(f"Courses fetched successfully: {courses.count()}")

        # Apply filters
        if search:
            search_term = f"%{search.lower()}%"
            courses = courses.filter(
                (func.lower(models.Course.title).like(search_term))
                | (func.lower(models.Course.tags).like(search_term))
            )
            print(f"After search filter '{search}': {courses.count()}")

        if level:
            courses = courses.filter(models.Course.level == level)
            print(f"After level filter '{level}': {courses.count()}")

        if cost_type:
            courses = courses.filter(models.Course.cost_type == cost_type)
            # print(f"After cost_type filter '{cost_type}': {courses.count()}")

        final_courses = courses.offset(skip).limit(limit).all()

        print(f"Final courses returned: {len(final_courses)}")

        # Convert tags
        for course in final_courses:
            course.tags = parse_tags_string(course.tags)

        return final_courses
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/courses/count")
def get_courses_count(db: Session = Depends(auth.get_db)):
    total_courses = db.query(models.Course).count()
    return {"total_courses": total_courses}


# get endpoint to retrieve a single course by title
@app.get("/courses/{title}", response_model=CourseRead)
def get_course_by_title(title: str, db: Session = Depends(auth.get_db)):
    course = db.query(models.Course).filter(models.Course.title == title).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course.tags = parse_tags_string(course.tags)

    return course


# get endpoint to retrieve a course by ID
@app.get("/courses/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: Session = Depends(auth.get_db)):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    course.tags = parse_tags_string(course.tags)

    return course


# post endpoint to update a course by ID
@app.put("/courses/{course_id}", response_model=CourseRead)
def update_course(
    course_id: int, course: CourseCreate, db: Session = Depends(auth.get_db)
):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    tags_string = ", ".join(course.tags) if course.tags else None
    for key, value in course.dict(exclude={"tags"}).items():
        setattr(db_course, key, value)
    db_course.tags = tags_string
    db.commit()
    db.refresh(db_course)
    db_course.tags = parse_tags_string(db_course.tags)
    return db_course


@app.delete("/courses/{course_id}", response_model=CourseRead)
def delete_course(course_id: int, db: Session = Depends(auth.get_db)):
    db_course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(db_course)
    db.commit()
    return db_course


@app.post("/courses/{course_title}/enroll")
def enroll_in_course_by_title(
    course_title: str,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user),
):
    course = db.query(models.Course).filter(models.Course.title == course_title).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if isinstance(course.students_enrolled, str):
        try:
            course.students_enrolled = json.loads(course.students_enrolled)
        except json.JSONDecodeError:
            course.students_enrolled = []
    elif course.students_enrolled is None:
        course.students_enrolled = []
    if not isinstance(course.students_enrolled, list):
        raise HTTPException(
            status_code=500, detail="Invalid students_enrolled format in course data"
        )

    # Check if the user is already enrolled
    if current_user.id in course.students_enrolled:
        raise HTTPException(
            status_code=400, detail="User already enrolled in this course"
        )
    course.students_enrolled.append(current_user.id)
    course.students_enrolled = json.dumps(course.students_enrolled)
    db.add(course)
    db.commit()

    return {"message": "User enrolled successfully"}


# post endpoint for user enrollment
@app.post("/courses/{course_id}/enroll")
def enroll_in_course(
    course_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user),
):
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if isinstance(course.students_enrolled, str):
        try:
            course.students_enrolled = json.loads(course.students_enrolled)
        except json.JSONDecodeError:
            course.students_enrolled = []
    elif course.students_enrolled is None:
        course.students_enrolled = []
    if not isinstance(course.students_enrolled, list):
        raise HTTPException(
            status_code=500, detail="Invalid students_enrolled format in course data"
        )
    if current_user.id in course.students_enrolled:
        raise HTTPException(
            status_code=400, detail="User already enrolled in this course"
        )

    # Enroll the user
    course.students_enrolled.append(current_user.username)
    course.students_enrolled = json.dumps(course.students_enrolled)
    db.add(course)
    db.commit()

    return {"message": "User enrolled successfully"}


@app.get("/users/{user_id}/courses", response_model=List[CourseRead])
def get_user_courses(user_id: int, db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Assuming students_enrolled is a list of user IDs in the Course model
    courses = (
        db.query(models.Course)
        .filter(models.Course.students_enrolled.contains(user_id))
        .all()
    )

    # Convert tags string to list for response
    for course in courses:
        course.tags = parse_tags_string(course.tags)

    return courses


@app.get("/users/{username}/courses")
def get_user_courses_by_username(username: str, db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Assuming students_enrolled is a list of user IDs in the Course model
    courses = (
        db.query(models.Course)
        .filter(models.Course.students_enrolled.contains(user.id))
        .all()
    )

    # Convert tags string to list for response
    for course in courses:
        course.tags = parse_tags_string(course.tags)

    return courses


# Ratings & ReviewS
# @app.post("/courses/{course_id}/r")
# def add_course_review(course_id: int, review: str, rating: float, db: Session = Depends(auth.get_db), current_user: models.User = Depends(get_current_user)):
#     course = db.query(models.Course).filter(models.Course.id == course_id).first()
#     if not course:
#         raise HTTPException(status_code=404, detail="Course not found")
#     if not (1 <= rating <= 5):
#         raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
#     # Assuming Course model has a reviews field which is a list of dictionaries
#     review_entry = {
#         "user_id": current_user.id,
#         "review": review,
#         "rating": rating
#     }
#     if not course.reviews:
#         course.reviews = []
#     course.reviews.append(review_entry)
#     db.commit()
#     return {"message": "Review added successfully"}


@app.get("/courses/{course_title}/rating")
def get_course_rating(course_title: int, db: Session = Depends(auth.get_db)):
    course = db.query(models.Course).filter(models.Course.tit == course_title).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.rating:
        return {"message": "No rating found for this course"}
    return {"rating": course.rating}


# Gig Endpoints
@app.post("/gigs", response_model=GigRead)
def create_gig(gig: GigCreate, db: Session = Depends(auth.get_db)):
    db_gig = models.Gig(**gig.dict())
    db.add(db_gig)
    db.commit()
    db.refresh(db_gig)
    return db_gig


@app.get("/gigs", response_model=List[GigRead])
def get_gigs(
    db: Session = Depends(auth.get_db),
    search: Optional[str] = Query(
        None, description="Search term for gig title, description, or required skills"
    ),
    category: Optional[str] = Query(
        None, description="Filter by gig category (e.g., 'Web Development')"
    ),
    location: Optional[str] = Query(
        None, description="Filter by gig location (e.g., 'Remote', 'New York')"
    ),
    skip: int = 0,
    limit: int = 100,
):
    gigs = db.query(models.Gig)
    if search:
        search_term = f"%{search.lower()}%"
        gigs = gigs.filter(
            (func.lower(models.Gig.title).like(search_term))
            | (func.lower(models.Gig.description).like(search_term))
            | (func.lower(models.Gig.required_skills).like(search_term))
        )
    if category:
        gigs = gigs.filter(models.Gig.category == category)
    if location:
        gigs = gigs.filter(models.Gig.location.ilike(f"%{location}%"))
    gigs = gigs.offset(skip).limit(limit).all()
    return gigs


@app.get("/gigs/id/{gig_id}", response_model=GigRead)
def get_gig(gig_id: int, db: Session = Depends(auth.get_db)):
    gig = db.query(models.Gig).filter(models.Gig.id == gig_id).first()
    if not gig:
        raise HTTPException(status_code=404, detail="Gig not found")
    return gig


@app.get("/gigs/title/{gig_title}", response_model=GigRead)
def get_gig_by_title(gig_title: str, db: Session = Depends(auth.get_db)):
    gig = (
        db.query(models.Gig)
        .filter(func.lower(models.Gig.title) == gig_title.lower())
        .first()
    )
    if not gig:
        raise HTTPException(status_code=404, detail="Gig not found")
    return gig


# POST ENDPOINT FOR USER TO APPLY FOR A GIG
@app.post("/gigs/id/{gig_id}/apply")
def apply_for_gig(
    gig_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user),
):
    gig = db.query(models.Gig).filter(models.Gig.id == gig_id).first()
    if not gig:
        raise HTTPException(status_code=404, detail="Gig not found")

    applicants_list = (
        [applicant.strip() for applicant in gig.applicants.split(",")]
        if gig.applicants
        else []
    )

    if current_user.username in applicants_list:
        raise HTTPException(
            status_code=400, detail="User has already applied for this gig"
        )

    applicants_list.append(current_user.username)
    gig.applicants = ", ".join(applicants_list)
    db.add(gig)
    db.commit()
    db.refresh(gig)

    return {"message": f"Successfully applied for gig '{gig.title}'"}


@app.post("/gigs/title/{gig_title}/apply")
def apply_for_gig_by_title(
    gig_title: str,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user),
):
    gig = db.query(models.Gig).filter(models.Gig.title == gig_title).first()
    if not gig:
        raise HTTPException(status_code=404, detail=f"Gig '{gig_title}' not found")
    applicants_list = (
        [applicant.strip() for applicant in gig.applicants.split(",")]
        if gig.applicants
        else []
    )

    if current_user.username in applicants_list:
        raise HTTPException(
            status_code=400, detail="User has already applied for this gig"
        )

    applicants_list.append(current_user.username)
    gig.applicants = ", ".join(applicants_list)
    db.add(gig)
    db.commit()
    db.refresh(gig)
    return {"message": f"Successfully applied for gig '{gig.title}'"}


@app.get("/users/{user_id}/gigs", response_model=List[GigRead])
def get_user_gigs(user_id: int, db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    gigs = (
        db.query(models.Gig)
        .filter(models.Gig.applicants.ilike(f"%{user.username}%"))
        .all()
    )
    if not gigs:
        raise HTTPException(status_code=404, detail="No gigs found for this user")
    for gig in gigs:
        if gig.applicants:
            gig.applicants_list = [
                applicant.strip() for applicant in gig.applicants.split(",")
            ]
        else:
            gig.applicants_list = []
    return gigs


# Dashboard Endpoints
@app.get("/Userdashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(auth.get_db),
):
    from Backend.database.models import user_gigs_table  # Import association table

    """
    Retrieves summary statistics for the user's dashboard.
    Includes total posted gigs, total applicants, active gigs, completed gigs,
    total revenue, and average rating.
    """

    if current_user.type.lower() != "business":
        raise HTTPException(
            status_code=403,
            detail="Access denied. This endpoint is for business users only.",
        )

    posted_gigs_query = (
        db.query(models.Gig)
        .join(user_gigs_table, models.Gig.id == user_gigs_table.c.gig_id)
        .filter(user_gigs_table.c.user_id == current_user.id)
    )

    posted_gigs_list = posted_gigs_query.all()
    posted_gigs_count = len(posted_gigs_list)

    active_gigs_count = (
        db.query(models.Gig)
        .join(user_gigs_table, models.Gig.id == user_gigs_table.c.gig_id)
        .filter(
            user_gigs_table.c.user_id == current_user.id,
            models.Gig.status == "Active",
        )
        .count()
    )

    total_applicants = 0
    for gig in posted_gigs_list:
        applicants_list = (
            [a.strip() for a in gig.applicants.split(",")] if gig.applicants else []
        )
        total_applicants += len(applicants_list)

    completed_gigs_count = (
        db.query(models.Gig)
        .join(user_gigs_table, models.Gig.id == user_gigs_table.c.gig_id)
        .filter(
            user_gigs_table.c.user_id == current_user.id,
            models.Gig.status == "Completed",
        )
        .count()
    )

    total_invested = (
        db.query(func.sum(models.Gig.budget_max_usd))
        .join(user_gigs_table, models.Gig.id == user_gigs_table.c.gig_id)
        .filter(
            user_gigs_table.c.user_id == current_user.id,
            models.Gig.status == "Completed",
        )
        .scalar()
        or 0
    )

    average_rating = (
        np.mean([gig.rating for gig in posted_gigs_list if gig.rating is not None])
        if posted_gigs_list
        else 0.0
    )

    return {
        "posted_gigs": posted_gigs_count,
        "total_applicants": total_applicants,
        "active_gigs": active_gigs_count,
        "completed_gigs": completed_gigs_count,
        "total_revenue": total_invested,
        "avg_rating": average_rating,
    }


@app.get("/dashboard/my_gigs", response_model=List[GigRead])
def get_my_gigs(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retrieves all gigs posted by the currently authenticated user.
    """
    gigs = (
        db.query(models.Gig).filter(models.Gig.company == current_user.username).all()
    )
    return gigs


# Recommendation Endpoints


@app.post("/recommend", response_model=RecommendResponse)
def recommend(
    payload: RecommendRequest,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not payload.quiz_answers.strip():
        raise HTTPException(status_code=400, detail="quiz_answers required")

    # Use the pre-initialized recommender instance here!
    if recommender is None:
        raise HTTPException(
            status_code=503,
            detail="Recommender model not loaded. Please try again later.",
        )

    recs = get_recommendations(payload.quiz_answers, top_n=5)

    quiz_entry = Quiz(quiz_answers=payload.quiz_answers, user_id=current_user.id)
    db.add(quiz_entry)
    db.commit()
    db.refresh(quiz_entry)

    for rec in recs:
        rec["learning_resources"] = json.dumps(rec.get("learning_resources", {}))
        db.add(Recommendation(user_id=current_user.id, quiz_id=quiz_entry.id, **rec))
    db.commit()

    return {"recommendations": recs}


@app.get("/history")
def get_user_history(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(get_current_user),
):
    history = (
        db.query(Recommendation).filter(Recommendation.user_id == current_user.id).all()
    )

    results = []
    for rec in history:
        results.append(
            {
                "career_title": rec.career_title,
                "description": rec.description,
                "salary": rec.average_salary_usd,
            }
        )
    return results
