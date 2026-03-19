from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List
import datetime

# 1. إعداد قاعدة البيانات
DATABASE_URL = "sqlite:///./pharmacy.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. الموديل (أضفت حقل البصمة عشان المصيدة)
class MedicineModel(Base):
    __tablename__ = "medicines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    user_agent = Column(String, nullable=True) # بصمة الجهاز

Base.metadata.create_all(bind=engine)

# 3. السكيما
class MedicineSchema(BaseModel):
    id: int
    name: str
    price: float
    quantity: int
    class Config:
        from_attributes = True

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- المسارات المعدلة للـ Test ---

@app.get("/")
def home():
    return {"status": "OK", "msg": "سيرفر الصيدلية والمصيدة شغال بنجاح! 🚀"}

@app.get("/medicines/")
def get_medicines(request: Request, db: Session = Depends(get_db)):
    # هنا المصيدة: بنسجل بصمة أي زول بيطلب القائمة
    ua = request.headers.get("user-agent")
    all_meds = db.query(MedicineModel).all()
    return {
        "status": "SUCCESS",
        "msg": "تم جلب البيانات",
        "user_agent_detected": ua, # عشان تتأكد إن البصمة مقروءة
        "data": all_meds
    }

@app.post("/add-medicine/")
def add_medicine(med: MedicineSchema, db: Session = Depends(get_db)):
    db_med = MedicineModel(id=med.id, name=med.name, price=med.price, quantity=med.quantity)
    db.add(db_med)
    db.commit()
    return {"status": "SUCCESS", "msg": "تم الحفظ في الداتابيز!"}
