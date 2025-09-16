from sqlmodel import SQLModel
from app.db.session import engine
import app.db.base
from sqlmodel import Session, select
from app.models.category import Category
from app.models.user import User
from app.core.security import get_password_hash

def init_db():
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Check if default user exists
        existing_user = session.exec(select(User).where(User.id == 1)).first()
        
        if not existing_user:
            # Create default user
            default_user = User(
                id=1,
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                is_active=True
            )
            session.add(default_user)
            session.commit()
            print("Default user created:")
            print("   - username: admin")
            print("   - password: admin123")
        
        # Check if categories exist
        existing_categories = session.exec(select(Category)).all()
        
        if not existing_categories:
            income_category = Category(name="Income", user_id=1)
            expense_category = Category(name="Expenses", user_id=1)
            
            session.add(income_category)
            session.add(expense_category)
            session.commit()
            print("Default categories created:")
            print("   - category_id=1: Income")
            print("   - category_id=2: Expenses")
        else:
            print("Categories already exist, skipping creation")

if __name__ == "__main__":
    init_db()