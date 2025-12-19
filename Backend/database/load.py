import random

import pandas as pd
from dotenv import load_dotenv
from models import Career, Course, Gig, SessionLocal, create_db_tables
from sqlalchemy.exc import IntegrityError

load_dotenv()


def load_data_from_csvs():
    """
    Loads data from careers.csv, gigs.csv, and courses.csv into the database.
    This function assumes the tables are already created.
    """
    session = SessionLocal()

    # List of random names for students
    student_names = [
        "Liam Johnson",
        "Olivia Smith",
        "Noah Williams",
        "Emma Brown",
        "Oliver Davis",
        "Ava Miller",
        "Elijah Wilson",
        "Charlotte Moore",
        "James Taylor",
        "Amelia Anderson",
        "Benjamin Thomas",
        "Isabella Jackson",
        "Lucas White",
        "Mia Harris",
        "Mason Martin",
        "Harper Thompson",
        "Ethan Garcia",
        "Evelyn Martinez",
        "Alexander Robinson",
        "Abigail Clark",
        "Henry Rodriguez",
        "Elizabeth Lewis",
        "Sebastian Lee",
        "Sofia Walker",
    ]

    try:
        # Load Careers data first, as it's the parent table
        print("Loading data from careers.csv...")
        file_path = r"C:\Users\ayemi\Documents\CareerHub\data\careers.csv"
        careers_df = pd.read_csv(file_path)
        for index, row in careers_df.iterrows():
            career = Career(
                name=row["career_title"],
                skills=row["skills"],
                personality_match=row["personality_match"],
                education_required=row["education_requirement"],
                description=row["description"],
                salary=row["average_salary_usd"],
                job_outlook=row["job_outlook"],
                resources=row["learning_resources"],
            )
            session.add(career)
        session.commit()
        print(f"Successfully loaded {len(careers_df)} careers.")

        # Load Courses data
        print("Loading data from courses.csv...")
        file_path = r"C:\Users\ayemi\Documents\CareerHub\data\courses.csv"
        courses_df = pd.read_csv(file_path)
        for index, row in courses_df.iterrows():
            # Find the parent Career based on career_title
            parent_career = (
                session.query(Career).filter_by(name=row["career_title"]).first()
            )
            if parent_career:
                # Join the list of tags into a single string
                tags_list = (
                    [tag.strip() for tag in row["tags"].split(",")]
                    if pd.notna(row["tags"])
                    else []
                )
                tags_string = ", ".join(tags_list)

                # Generate a random number of students enrolled and join them into a string
                num_students = random.randint(0, len(student_names))
                students_list = random.sample(student_names, num_students)
                students_string = ", ".join(students_list)

                course = Course(
                    career_id=parent_career.id,
                    title=row["course_title"],
                    provider=row["provider"],
                    description=row["description"],
                    tags=tags_string,
                    rating=row["rating"],
                    students_enrolled=students_string,
                    count_students=len(students_list),
                    duration_weeks=row["duration_weeks"],
                    cost_type=row["cost_type"],
                    level=row["level"],
                    url=row["url"],
                    course_image_url=row["course_image_url"],
                )
                session.add(course)

        session.commit()  # Commit courses before loading gigs
        print(f"Successfully loaded {len(courses_df)} courses.")

        # Load Gigs data
        print("Loading data from gigs.csv...")
        file_path = r"C:\Users\ayemi\Documents\CareerHub\data\gigs.csv"
        gigs_df = pd.read_csv(file_path)

        # Define category mapping based on career titles in the dataset
        category_mapping = {
            "Data Scientist": "Data Science",
            "AI Engineer": "Artificial Intelligence",
            "Cybersecurity Analyst": "Cybersecurity",
            "UX/UI Designer": "Design",
            "Cloud Solutions Architect": "Cloud Computing",
            "Blockchain Developer": "Blockchain",
            "Game Developer": "Game Development",
            "Digital Marketing Specialist": "Digital Marketing",
            "Robotics Engineer": "Robotics",
            "Mobile App Developer": "Mobile Development",
            "Data Analyst": "Data Analysis",
            "Full Stack Developer": "Web Development",
            "Product Manager": "Product Management",
            "Bioinformatics Scientist": "Biotechnology",
            "Embedded Systems Engineer": "Hardware Engineering",
            "Machine Learning Engineer": "Machine Learning",
            "Network Engineer": "Networking",
            "DevOps Engineer": "DevOps",
            "AR/VR Developer": "AR/VR",
            "Ethical Hacker": "Cybersecurity",
            "Full-Stack Developer": "Web Development",
            "Data Engineer": "Data Engineering",
            "UX Researcher": "User Research",
            "IoT Developer": "Internet of Things",
            "Cloud Security Engineer": "Cloud Security",
            "Technical Writer": "Technical Writing",
            "Site Reliability Engineer (SRE)": "Site Reliability",
            "Financial Analyst": "Finance",
            "Quantum Computing Engineer": "Quantum Computing",
            "Database Administrator": "Database Management",
            "Aerospace Engineer": "Aerospace",
            "Human Resources Manager": "Human Resources",
            "Project Manager": "Project Management",
            "Social Media Manager": "Social Media",
            "Electrical Engineer": "Electrical Engineering",
            "Business Analyst": "Business Analysis",
            "Robotics Process Automation (RPA) Developer": "Process Automation",
            "Game Designer": "Game Design",
            "Data Visualization Specialist": "Data Visualization",
            "Network Security Engineer": "Network Security",
            "Systems Analyst": "Systems Analysis",
            "Content Strategist": "Content Strategy",
            "UX Writer": "UX Writing",
            "Podiatrist": "Healthcare",
            "Urban Planner": "Urban Planning",
            "Dietetic Technician": "Healthcare",
            "Forensic Scientist": "Forensic Science",
            "Chiropractor": "Healthcare",
            "Copywriter": "Copywriting",
            "Optometrist": "Healthcare",
            "Industrial Designer": "Industrial Design",
            "Public Relations Specialist": "Public Relations",
            "Occupational Therapist": "Healthcare",
            "Linguist": "Linguistics",
            "Animator": "Animation",
            "Medical Assistant": "Healthcare",
            "Curator": "Arts & Culture",
            "Biomedical Engineer": "Biomedical Engineering",
            "Forest Ranger": "Environmental Science",
            "Financial Quantitative Analyst": "Quantitative Finance",
            "Marine Biologist": "Marine Biology",
            "Travel Agent": "Travel & Tourism",
            "Pharmacist": "Healthcare",
            "Market Research Analyst": "Market Research",
            "School Counselor": "Education",
            "Urban Farmer": "Agriculture",
            "Event Planner": "Event Management",
            "Interior Designer": "Interior Design",
            "Graphic Designer": "Graphic Design",
        }

        # List of random names to use for applicants
        applicant_names = [
            "John Doe",
            "Jane Smith",
            "Peter Jones",
            "Mary Brown",
            "Alex Williams",
            "Sarah Miller",
            "Michael Davis",
            "Jessica Garcia",
            "David Rodriguez",
            "Laura Wilson",
            "James Martinez",
            "Patricia Anderson",
            "Robert Thomas",
            "Jennifer Jackson",
            "Charles White",
            "Linda Harris",
            "Daniel Martin",
            "Elizabeth Thompson",
            "Joseph Garcia",
            "Susan Robinson",
        ]

        gigs_added = 0
        for index, row in gigs_df.iterrows():
            # Find the parent Career based on career_title
            parent_career = (
                session.query(Career).filter_by(name=row["career_title"]).first()
            )
            if parent_career:
                # Get category based on career title mapping
                category = category_mapping.get(row["career_title"], "General")

                # Generate a random number of applicants (between 0 and the number of names)
                num_applicants = random.randint(0, len(applicant_names))
                # Select a random sample of names and join them into a string
                applicants_list = random.sample(applicant_names, num_applicants)
                applicants_string = ", ".join(applicants_list)

                # Generate a random status for the gig
                gig_status = random.choice(["Active", "Completed"])

                gig = Gig(
                    career_id=parent_career.id,
                    title=row["gig_title"],
                    company=row["company"],
                    description=row["description"],
                    budget_min_usd=row["budget_min_usd"],
                    budget_max_usd=row["budget_max_usd"],
                    # Append " weeks" to the duration and convert to string
                    duration_weeks=f"{row['duration_weeks']} weeks",
                    location=row["location"],
                    applicants=applicants_string,
                    count_applicants=len(applicants_list),
                    required_skills=row["required_skills"],
                    category=category,  # Category mapped from career_title
                    posted_hours_ago=random.randint(
                        1, 720
                    ),  # Random hours ago between 1-720 (30 days)
                    url=row["url"],
                    status=gig_status,
                )
                session.add(gig)
                gigs_added += 1
                print(
                    f"Added gig: {row['gig_title']} with category: {category} and status: {gig_status}"
                )
            else:
                print(f"Warning: No career found for '{row['career_title']}'")

        session.commit()  # Commit all gigs
        print(f"Successfully loaded {gigs_added} gigs.")

    except IntegrityError as e:
        session.rollback()
        print(f"Database integrity error: {e}")
        raise
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    # print("Dropping existing database tables and recreating them...")
    # drop_db_tables()
    create_db_tables()
    print("Database tables created successfully.")

    # # Load initial data from CSV files
    load_data_from_csvs()
