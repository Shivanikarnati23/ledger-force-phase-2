import sys
from app.database import SessionLocal
from app.models.employee import Department, Role, Employee

def seed_database():
    db = SessionLocal()
    try:
        print("Seeding database...")
        
        # Create default department
        dept = db.query(Department).filter_by(name="Engineering").first()
        if not dept:
            dept = Department(name="Engineering")
            db.add(dept)
            db.commit()
            db.refresh(dept)

        # Create default role
        role = db.query(Role).filter_by(title="Software Engineer").first()
        if not role:
            role = Role(title="Software Engineer")
            db.add(role)
            db.commit()
            db.refresh(role)

        # Create test employee matching the Employee model schema
        employee_data = {
            "name": "John Doe",  # Using 'name' instead of 'first_name' / 'last_name'
            "email": "john.doe@example.com",
            "department_id": dept.id,
            "role_id": role.id,
        }

        # Verify if employee already exists
        existing_emp = db.query(Employee).filter_by(email=employee_data["email"]).first()
        if not existing_emp:
            emp = Employee(**employee_data)
            db.add(emp)
            db.commit()
            print("Database seeding completed successfully!")
        else:
            print("Seed data already exists.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()