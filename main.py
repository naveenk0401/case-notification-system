from fastapi import FastAPI, Depends, HTTPException, Path, status
from typing import List
from sqlalchemy.orm import Session
import models, schemas, crud, database, auth
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth import get_current_user
from apscheduler.schedulers.background import BackgroundScheduler
from notifications import notify_upcoming_cases

app = FastAPI()

# Create tables
models.Base.metadata.create_all(bind=database.engine)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    OAuth2-compatible token endpoint.
    Client sends form-data: username & password.
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
    

@app.get("/")
def root():
    return {"message": "Advocate Daily Case Notification running!"}

# Signup
@app.post("/users/", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # uniqueness checks
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    if crud.get_user_by_mobile(db, user.mobile):
        raise HTTPException(status_code=400, detail="Mobile already exists")
    # hash password before storing
    hashed = auth.get_password_hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed
    created = crud.create_user(db, schemas.UserCreate(**user_data))
    return created

@app.get("/me", response_model=schemas.UserOut)
def read_own_profile(current_user = Depends(auth.get_current_user)):
    # returns the current user and included cases
    return current_user


# Login (returns user info + their cases)
@app.post("/login/", response_model=schemas.UserOut)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return db_user

# Get all users (admin)
@app.get("/users/", response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db.query(models.User).all()

# Delete user by ID (admin)
@app.delete("/users/{user_id}")
def delete_user(user_id: int, current_user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

# Add case (admin)
@app.post("/cases/", response_model=schemas.CaseOut)
def add_case(case: schemas.CaseCreate, db: Session = Depends(get_db)):
    return crud.create_case(db, case)

scheduler = BackgroundScheduler()
# Run daily at 9:00 AM
scheduler.add_job(notify_upcoming_cases, 'cron', hour=9, minute=0)
scheduler.start()
