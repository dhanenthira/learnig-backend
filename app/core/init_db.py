import logging
import pymysql
from datetime import datetime, timedelta
from sqlalchemy import text
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.database import engine, Base, SessionLocal, init_db_engine
from app.models.sql_models import (
    UserModel,
    QuestionModel,
    CodingProblemModel,
    LearningModuleModel,
    LessonModel,
    DailySetModel,
    AssessmentTestModel,
    NotificationModel,
    UserFollowModel,
)

logger = logging.getLogger("codearena.init_db")

def create_database_if_not_exists():
    """
    Creates the MySQL database schema if it doesn't already exist.
    """
    try:
        conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD or "",
            autocommit=True
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{settings.MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            logger.info(f"Database `{settings.MYSQL_DATABASE}` ensured in MySQL.")
        conn.close()
        return True
    except Exception as e:
        logger.warning(f"Could not auto-create database `{settings.MYSQL_DATABASE}`: {e}")
        return False

def purge_dummy_data(db):
    """
    Purges any hardcoded/sample dummy data from MySQL tables.
    """
    try:
        # 1. Remove dummy questions
        dummy_q_ids = ["q_apt_01", "q_apt_02", "q_tech_01", "q_tech_02", "q1", "q2", "q3", "q4", "q5"]
        db.query(QuestionModel).filter(QuestionModel.id.in_(dummy_q_ids)).delete(synchronize_session=False)

        # 2. Remove dummy user follows, notifications, submissions associated with dummy users
        dummy_user_ids = ["user_student_01", "user_student_02"]
        db.query(UserFollowModel).filter(
            (UserFollowModel.follower_id.in_(dummy_user_ids)) | (UserFollowModel.following_id.in_(dummy_user_ids))
        ).delete(synchronize_session=False)
        db.query(NotificationModel).filter(NotificationModel.user_id.in_(dummy_user_ids)).delete(synchronize_session=False)

        # 3. Remove dummy students
        db.query(UserModel).filter(
            (UserModel.id.in_(dummy_user_ids)) | 
            (UserModel.email.in_(["student@codearena.com", "sophia@codearena.com"]))
        ).delete(synchronize_session=False)

        # 4. Remove dummy daily sets & tests referencing dummy questions
        dummy_set_ids = ["ds_apt_today", "ds_tech_today"]
        db.query(DailySetModel).filter(DailySetModel.id.in_(dummy_set_ids)).delete(synchronize_session=False)
        dummy_test_ids = ["test_nationwide_01"]
        db.query(AssessmentTestModel).filter(AssessmentTestModel.id.in_(dummy_test_ids)).delete(synchronize_session=False)

        db.commit()
        logger.info("Purged dummy/sample data from database successfully.")
    except Exception as e:
        logger.warning(f"Error purging dummy records: {e}")
        db.rollback()

def seed_database_records():
    """
    Ensures essential system tables are ready and ensures master admin account exists.
    Does NOT seed any dummy questions or dummy student accounts.
    """
    if SessionLocal is None:
        init_db_engine()
    if SessionLocal is None:
        return

    db = SessionLocal()
    try:
        # First purge any existing dummy/sample data
        purge_dummy_data(db)

        # Ensure single master administrator exists for admin panel access
        admin_id = "user_admin_01"
        admin_user = db.query(UserModel).filter(UserModel.role == "admin").first()
        if not admin_user:
            admin_user = UserModel(
                id=admin_id,
                student_id="ADM-001",
                email="admin@codearena.com",
                password=get_password_hash("adminpassword123"),
                name="System Administrator",
                role="admin",
                college_name="CodeArena HQ",
                department="Platform Core",
                graduation_year=2024,
                bio="Platform Administrator",
                avatar_url="https://api.dicebear.com/7.x/bottts/svg?seed=admin",
                streak_days=0,
                total_points=0,
                problems_solved=0,
                questions_solved=0,
                overall_accuracy=0.0,
                coding_problems_solved=0,
                battles_won=0,
                followers_count=0,
                following_count=0,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            logger.info("Master Administrator verified in MySQL database.")
    except Exception as e:
        logger.warning(f"Error initializing admin record: {e}")
        db.rollback()
    finally:
        db.close()

def init_tables():
    """
    Creates all defined tables in MySQL and seeds initial records if needed.
    """
    try:
        create_database_if_not_exists()
        init_db_engine()
        if engine is not None:
            Base.metadata.create_all(bind=engine)
            logger.info("MySQL tables created / verified successfully.")
            seed_database_records()
            return True
    except Exception as e:
        logger.warning(f"Error initializing MySQL tables: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Connecting and initializing MySQL tables...")
    success = init_tables()
    if success:
        print(f"SUCCESS: MySQL database '{settings.MYSQL_DATABASE}' and tables ready!")
    else:
        print("NOTE: Make sure MySQL (XAMPP / MySQL Service) is running on port 3306.")
