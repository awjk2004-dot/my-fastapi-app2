from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import datetime

# 1. إعداد قاعدة البيانات (SQLite للتست)
DATABASE_URL = "sqlite:///./pharmacy.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. الموديل المعدل (جدول الأجهزة والزبائن)
class DeviceModel(Base):
    __tablename__ = "active_devices"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String) # هنا بتكتب (Honor-1, Honor-2, إلخ)
    ip = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# 3. بروتوكول استقبال البيانات
class DeviceRegister(BaseModel):
    customer_name: str

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

# --- المسارات (Endpoints) ---

@app.get("/")
def home():
    return {"status": "OK", "msg": "سيرفر المصيدة جاهز للصيد! 🛰️"}

# مسار تسجيل جهاز جديد (الزبون بيستخدمه)
@app.post("/register/")
def register_device(data: DeviceRegister, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host
    ua = request.headers.get("user-agent")
    
    # فحص إذا كان الـ IP ده سجل قبل كدة ببصمة مختلفة (كشف تشيير)
    existing = db.query(DeviceModel).filter(DeviceModel.ip == client_ip).first()
    if existing and existing.user_agent != ua:
        # هنا ممكن نرسل تنبيه أو نسجلها كـ "حالة مشبوهة"
        print(f"ALERT: Hotspot detected on IP {client_ip}")

    new_device = DeviceModel(
        customer_name=data.customer_name,
        ip=client_ip,
        user_agent=ua
    )
    db.add(new_device)
    db.commit()
    return {"status": "SUCCESS", "msg": f"تم تسجيلك يا {data.customer_name} بنجاح!"}

# مسار الإدارة (إنت بتشوف منه الـ 20 جهاز)
@app.get("/admin/list/")
def get_admin_list(db: Session = Depends(get_db)):
    devices = db.query(DeviceModel).order_by(DeviceModel.created_at.desc()).all()
    return {"status": "SUCCESS", "data": devices}
