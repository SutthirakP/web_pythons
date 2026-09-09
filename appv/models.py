from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import relationship
from .database import Base

class StudentDB(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    score = Column(Float, nullable=False)
    
    phones = relationship(
        "PhoneDB", back_populates="student"
    )

class PhoneDB(Base):
    __tablename__ = "phones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_no = Column(String)
    student_id = Column(Integer, ForeignKey("students.id"))
    student = relationship("StudentDB", back_populates="phones")