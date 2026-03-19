from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import datetime
from fastapi.responses import FileResponse
import os


DATABASE_URL = "sqlite:///./pharmacy.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DeviceModel(Base):
    __tablename__ = "active_devices"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String)
    ip = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

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
    try: yield db
    finally: db.close()
@app.get("/")
async def read_index():
    # التأكد إن الملف موجود في الفولدر
    if os.path.exists("index.html"):
        return FileResponse('index.html')
    return {"error": "ملف index.html غير موجود في السيرفر!"}

@app.post("/register/")
def register_device(data: DeviceRegister, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host
    ua = request.headers.get("user-agent")
    new_device = DeviceModel(customer_name=data.customer_name, ip=client_ip, user_agent=ua)
    db.add(new_device)
    db.commit()
    return {"status": "SUCCESS", "msg": f"تم التفعيل يا {data.customer_name} ✅"}

@app.get("/admin/list/")
def get_admin_list(db: Session = Depends(get_db)):
    devices = db.query(DeviceModel).order_by(DeviceModel.created_at.desc()).all()
    return {"status": "SUCCESS", "data": devices}

# --- دالة الحذف اليومي ---
@app.delete("/admin/clear-all/")
def clear_all_devices(db: Session = Depends(get_db)):
    db.query(DeviceModel).delete()
    db.commit()
    return {"status": "SUCCESS", "msg": "تم تنظيف الجدول ليوم جديد 🧹"}
