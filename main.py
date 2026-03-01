from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List  # لازم تزيد دي عشان الـ List تشتغل

# 1. إعداد قاعدة البيانات (SQLite)
DATABASE_URL = "sqlite:///./pharmacy.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. تعريف جدول الأدوية (الـ Model الحقيقي في الداتابيز)
class MedicineModel(Base):
    __tablename__ = "medicines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    quantity = Column(Integer)

# إنشاء الجدول في ملف pharmacy.db
Base.metadata.create_all(bind=engine)

# 3. بروتوكول البيانات (Pydantic Schema)
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

# دالة مساعدة لفتح وإغلاق الداتابيز
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- المسارات (Endpoints) ---

@app.get("/medicines/", response_model=List[MedicineSchema])
def get_medicines(db: Session = Depends(get_db)):
    return db.query(MedicineModel).all()

@app.post("/add-medicine/")
def add_medicine(med: MedicineSchema, db: Session = Depends(get_db)):
    db_med = MedicineModel(id=med.id, name=med.name, price=med.price, quantity=med.quantity)
    db.add(db_med)
    db.commit()
    return {"message": "تم الحفظ في الداتابيز!"}

@app.delete("/delete-medicine/{med_id}")
def delete_medicine(med_id: int, db: Session = Depends(get_db)):
    db_med = db.query(MedicineModel).filter(MedicineModel.id == med_id).first()
    if not db_med:
        raise HTTPException(status_code=404, detail="الدواء مافي")
    db.delete(db_med)
    db.commit()
    return {"message": "حُذف نهائياً"}

@app.get("/search-medicine/{name}")
def search_medicine(name: str, db: Session = Depends(get_db)):
    return db.query(MedicineModel).filter(MedicineModel.name.contains(name)).all()
