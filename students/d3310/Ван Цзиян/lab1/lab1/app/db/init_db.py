from sqlmodel import SQLModel
from app.db.session import engine
import app.db.base
from sqlmodel import Session, select
from app.models.category import Category
from app.models.user import User

def init_db():
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
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