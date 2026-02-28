from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware # عشان الـ HTML يقدر يكلم الـ API

app = FastAPI()

# تفعيل الـ CORS عشان المتصفح ما يرفض الطلب
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Student(BaseModel):
    id: int
    name: str
    grade: int

students = [
    Student(id=1, name="ahmed abdu", grade=1),
    Student(id=2, name="ali momode", grade=2),
]

@app.get("/student/")
def read_student():
    return students
    
@app.post("/student/")
def create_student(New_Student: Student):
    students.append(New_Student)
    return New_Student
    
@app.put("/student/{student_id}") 
def update_student(student_id: int, updated_student: Student):
    for index, student in enumerate(students):
        if student.id == student_id:
            students[index] = updated_student
            return updated_student
    return {"error": "not found"}

@app.delete("/student/{student_id}")
def delete_student(student_id: int):
    for index, student in enumerate(students):
        if student.id == student_id:
            del students[index]
            return {"message": "Student deleted"}
    return {"message": "error Student not found"}
