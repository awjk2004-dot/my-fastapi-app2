from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

# الـ CORS اللي فعلته إنت (عشان الـ HTML يشتغل)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# موديل الدواء
class Medicine(BaseModel):
    id: int
    name: str
    price: float
    quantity: int

# لستة الأدوية (مبدئياً)
pharmacy_stock = [
    Medicine(id=1, name="Panadol", price=500.0, quantity=20),
    Medicine(id=2, name="Amoxicillin", price=1200.0, quantity=10)
]

@app.get("/medicines/", response_model=List[Medicine])
def get_all_medicines():
    return pharmacy_stock

@app.post("/add-medicine/")
def add_medicine(med: Medicine):
    pharmacy_stock.append(med)
    return {"message": "تمت إضافة الدواء بنجاح!", "data": med}
