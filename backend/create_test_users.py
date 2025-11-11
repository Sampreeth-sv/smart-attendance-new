from utils.db import SessionLocal, init_db
from models.user_model import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users():
    init_db()  # Initialize database first
    db = SessionLocal()
    
    try:
        # Check if users already exist
        existing = db.query(User).first()
        if existing:
            print("✅ Users already exist!")
            print("\nExisting users:")
            users = db.query(User).all()
            for user in users:
                print(f"  - {user.name} ({user.email}) - {'Teacher' if user.is_teacher else 'Student'}")
            
            print("\n⚠️  To add new users, delete attendance.db and run again")
            return
        
        # ========== CREATE 5 STUDENTS ==========
        
        student1 = User(
            usn="1AM23CS180",
            name="Sampreeth S V",
            email="student1@test.com",
            password_hash=pwd_context.hash("stud1pass"),
            is_teacher=False
        )
        
        student2 = User(
            usn="1AM23CS179",
            name="Sakthivel C",
            email="student2@test.com",
            password_hash=pwd_context.hash("stud2pass"),
            is_teacher=False
        )
        
        student3 = User(
            usn="1AM23CS182",
            name="Samuel Joshua K",
            email="student3@test.com",
            password_hash=pwd_context.hash("stud3pass"),
            is_teacher=False
        )
        
        student4 = User(
            usn="1AM23CS128",
            name="Tejeswini",
            email="student4@test.com",
            password_hash=pwd_context.hash("stud4pass"),
            is_teacher=False
        )
        
        student5 = User(
            usn="1AM23CI076",
            name="Madhushri",
            email="student5@test.com",
            password_hash=pwd_context.hash("stud5pass"),
            is_teacher=False
        )
        
        # ========== CREATE 2 TEACHERS ==========
        
        teacher1 = User(
            usn="T001",
            name="Prof Mahalakshmi",
            email="teacher1@test.com",
            password_hash=pwd_context.hash("teach1pass"),
            is_teacher=True
        )
        
        teacher2 = User(
            usn="T002",
            name="Prof. Anand Kumar",
            email="teacher2@test.com",
            password_hash=pwd_context.hash("teach2pass"),
            is_teacher=True
        )
        
        # Add all users to database
        db.add(student1)
        db.add(student2)
        db.add(student3)
        db.add(student4)
        db.add(student5)
        db.add(teacher1)
        db.add(teacher2)
        db.commit()
        
        print("=" * 75)
        print("✅ ALL USERS CREATED SUCCESSFULLY!")
        print("=" * 75)
        
        print("\n📚 STUDENT LOGIN CREDENTIALS (Use Email to Login):")
        print("-" * 75)
        print("  1. Email: student1@test.com  |  Password: stud1pass  |  USN: CS001")
        print("  2. Email: student2@test.com  |  Password: stud2pass  |  USN: CS002")
        print("  3. Email: student3@test.com  |  Password: stud3pass  |  USN: CS003")
        print("  4. Email: student4@test.com  |  Password: stud4pass  |  USN: CS004")
        print("  5. Email: student5@test.com  |  Password: stud5pass  |  USN: CS005")
        
        print("\n👨‍🏫 TEACHER LOGIN CREDENTIALS (Use Email to Login):")
        print("-" * 75)
        print("  1. Email: teacher1@test.com  |  Password: teach1pass  |  USN: T001")
        print("  2. Email: teacher2@test.com  |  Password: teach2pass  |  USN: T002")
        
        print("\n" + "=" * 75)
        print("🎉 Ready to use! Login with EMAIL and password.")
        print("=" * 75 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_users()
