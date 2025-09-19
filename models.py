from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from datetime import date
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    mobile = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    cases = relationship("Case", back_populates="user")

    __table_args__ = (
        UniqueConstraint("username", "email", "mobile", name="uix_1"),
    )

class Case(Base):
    __tablename__ = "cases"

    case_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    case_details = Column(String, nullable=False)
    status = Column(String, default="Pending")  # Pending / Completed
    next_hearing_date = Column(Date, nullable=False)  # Only date
    created_at = Column(Date, default=date.today)     # Only date

    user = relationship("User", back_populates="cases")
