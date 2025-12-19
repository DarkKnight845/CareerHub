# Backend/models.py
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    create_engine,
)
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker,
)

load_dotenv()
# db_path = os.path.join(os.path.dirname(__file__), "../../app.db")
# db_path = os.path.abspath(db_path)  # make sure it's an absolute path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
print(f"Using database URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)  # noqa: F811

Base = declarative_base()

# Association table for the many-to-many relationship between User and Course
user_courses_table = Table(
    "user_courses",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True),
)

# Association table for the many-to-many relationship between User and Gig
user_gigs_table = Table(
    "user_gigs",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("gig_id", ForeignKey("gigs.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Profile fields
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    date_of_birth: Mapped[str | None] = mapped_column(String(255))
    gender: Mapped[str | None] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255))
    profile_picture: Mapped[str | None] = mapped_column(String(255))
    type: Mapped[str | None] = mapped_column(String(50))  # "Business" or "Student"

    certifications: Mapped[list["Certification"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    quiz_responses: Mapped[list["QuizResponse"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # Many-to-many relationships
    enrolled_courses: Mapped[list["Course"]] = relationship(
        secondary=user_courses_table, back_populates="users"
    )
    completed_gigs: Mapped[list["Gig"]] = relationship(
        secondary=user_gigs_table, back_populates="users"
    )

    quizzes: Mapped[list["Quiz"]] = relationship(back_populates="user")
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="user"
    )


class Certification(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    title: Mapped[str] = mapped_column(String(255))
    issuer: Mapped[str] = mapped_column(String(255))
    earned_on: Mapped[datetime] = mapped_column(Date)
    verification_id: Mapped[str | None] = mapped_column(String(255))
    view_url: Mapped[str | None] = mapped_column(String(255))
    download_url: Mapped[str | None] = mapped_column(String(255))

    user: Mapped["User"] = relationship(back_populates="certifications")


class Quiz(Base):
    __tablename__ = "quizzes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quiz_answers: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="quizzes")
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="quiz"
    )


class Recommendation(Base):
    __tablename__ = "recommendations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    career_title: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[str | None] = mapped_column(Text)
    personality_match: Mapped[str | None] = mapped_column(String(255))
    education_required: Mapped[str | None] = mapped_column(String(255))
    average_salary_usd: Mapped[float | None] = mapped_column(Float)
    job_outlook: Mapped[str | None] = mapped_column(String(255))
    learning_resources: Mapped[str | None] = mapped_column(Text)
    similarity_score: Mapped[float | None] = mapped_column(Float)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    quiz_id: Mapped[int | None] = mapped_column(ForeignKey("quizzes.id"))

    user: Mapped["User"] = relationship(back_populates="recommendations")
    quiz: Mapped["Quiz"] = relationship(back_populates="recommendations")


class Career(Base):
    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    skills: Mapped[str | None] = mapped_column(String(255))
    personality_match: Mapped[str | None] = mapped_column(String(255))
    education_required: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    salary: Mapped[float | None] = mapped_column(Float)
    job_outlook: Mapped[str | None] = mapped_column(String(255))
    resources: Mapped[str | None] = mapped_column(String)

    courses: Mapped[list["Course"]] = relationship(
        back_populates="career", cascade="all, delete"
    )
    gigs: Mapped[list["Gig"]] = relationship(
        back_populates="career", cascade="all, delete"
    )


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id"))

    title: Mapped[str] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    tags: Mapped[str | None] = mapped_column(String(255))
    rating: Mapped[float | None] = mapped_column(Float)
    # Changed to String to store a comma-separated list of names
    students_enrolled: Mapped[str | None] = mapped_column(String(255))
    count_students: Mapped[int | None] = mapped_column(Integer, default=0)
    duration_weeks: Mapped[int | None] = mapped_column(Integer)
    cost_type: Mapped[str | None] = mapped_column(String(255))
    level: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(255))
    course_image_url: Mapped[str | None] = mapped_column(String(255))

    career: Mapped["Career"] = relationship(back_populates="courses")
    users: Mapped[list["User"]] = relationship(
        secondary=user_courses_table, back_populates="enrolled_courses"
    )


class Gig(Base):
    __tablename__ = "gigs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    career_id: Mapped[int] = mapped_column(ForeignKey("careers.id"))

    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    budget_min_usd: Mapped[float | None] = mapped_column(Float)
    budget_max_usd: Mapped[float | None] = mapped_column(Float)
    # Changed to String to include 'weeks' text
    duration_weeks: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255))
    # Changed to String to store a comma-separated list of names
    applicants: Mapped[str | None] = mapped_column(String(255))
    count_applicants: Mapped[int | None] = mapped_column(Integer, default=0)
    required_skills: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(255))
    posted_hours_ago: Mapped[int | None] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(255))
    # New column for status
    status: Mapped[str | None] = mapped_column(String(255))

    career: Mapped["Career"] = relationship(back_populates="gigs")
    users: Mapped[list["User"]] = relationship(
        secondary=user_gigs_table, back_populates="completed_gigs"
    )


class QuizResponse(Base):
    __tablename__ = "quiz_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    answers: Mapped[dict] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="quiz_responses")


def create_db_tables():
    """Creates all database tables based on the SQLAlchemy models."""
    Base.metadata.create_all(bind=engine)


def drop_db_tables():
    """Drops all database tables based on the SQLAlchemy models."""
    Base.metadata.drop_all(bind=engine)


Session = SessionLocal
