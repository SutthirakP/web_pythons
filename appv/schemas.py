from pydantic import BaseModel

class Phone(BaseModel):
    phone_no: str


class PhoneCreate(Phone):
    pass

class PhoneResponse(Phone):
    id: int
    class Config:
        from_attributes = True

class Student(BaseModel):
    __tablename__ = "students"

    id: int | None = None
    name: str
    score: float

    # class Config:
    #     orm_mode = True
        
# in
class StudentCreate(Student):
    #pass
    phones: list[PhoneCreate]

# out
class StudentResponse(Student):
    id: int
    phones: list[PhoneResponse]

    class Config:
        from_attributes = True
