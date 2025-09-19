from sqlalchemy.orm import Session
from datetime import date, timedelta
import random

from database import SessionLocal, engine, Base
import models
import auth
from auth import create_access_token  # make sure this function exists

# 🔹 Reset DB
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()

# 🔹 Sample names
names = [
    "Alice", "Bob", "Charlie", "David", "Eva",
    "Frank", "Grace", "Hannah", "Ian", "Jack",
    "Karen", "Leo", "Mona", "Nina", "Oscar",
    "Paul", "Quinn", "Rita", "Sam", "Tina",
    "Uma", "Victor", "Wendy", "Xavier", "Yara"
]

# 🔹 Generate 25 users
users = []
for i in range(25):
    name = names[i % len(names)]
    username = f"{name.lower()}{i+1}"
    email = f"{username}@gmail.com"
    mobile = f"9{str(i).zfill(9)}"
    password = auth.get_password_hash("password123")
    
    # First user is admin, rest are normal users
    is_admin = True if i == 0 else False

    user = models.User(
        name=name,
        username=username,
        email=email,
        mobile=mobile,
        password=password,
        is_admin=is_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    users.append(user)

# 🔹 Add 5 cases per user
statuses = ["Pending", "Closed"]

for user in users:
    for j in range(5):
        case_details = f"Case {j+1} for {user.username}"
        status = random.choice(statuses)
        next_hearing_date = date.today() + timedelta(days=random.randint(7, 90))

        case = models.Case(
            user_id=user.id,
            case_details=case_details,
            status=status,
            next_hearing_date=next_hearing_date
        )
        db.add(case)

db.commit()

# 🔹 Generate JWT token for admin user (first user)
admin_user = users[0]
token_data = {"sub": admin_user.username}
admin_token = create_access_token(token_data)

db.close()

print("✅ Dummy data inserted: 25 users with 5 cases each (first user is admin).")
print(f"🔑 Admin username: {admin_user.username}")
print(f"🔑 Admin password: password123")
print(f"🔑 Admin JWT token: {admin_token}")
