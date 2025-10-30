from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class ScanRequest(BaseModel):
    qr_id: str


@app.post("/scan")
def scan_qr(request: ScanRequest):
    qr_id = request.qr_id.strip()

    response = supabase.table("users").update({"status": "REGISTERED"}).eq("qr_id", qr_id).execute()
    result = response.data if hasattr(response, "data") else response.json()

    print("Supabase response:", result)

    if not result:
        supabase.table("users").insert({"qr_id": qr_id, "status": "REGISTERED"}).execute()
        return {"message": f"No user found. Created new user with QR ID '{qr_id}'."}

    return {"message": f"User with QR ID '{qr_id}' marked as REGISTERED!", "updated_data": result}


class FoodRequest(BaseModel):
    qr_id: str


@app.post("/had_food")
def mark_had_food(request: FoodRequest):
    qr_id = request.qr_id.strip()

    user_check = supabase.table("users").select("status").eq("qr_id", qr_id).execute()
    user_data = user_check.data if hasattr(user_check, "data") else user_check.json()

    if not user_data:
        return {"error": f"No user found with QR ID '{qr_id}'."}

    user_status = user_data[0].get("status")

    if user_status != "REGISTERED":
        return {"error": f"User with QR ID '{qr_id}' is not registered. Cannot mark hadFood."}

    response = supabase.table("users").update({"hadFood": True}).eq("qr_id", qr_id).execute()
    result = response.data if hasattr(response, "data") else response.json()

    print("Supabase response:", result)

    return {"message": f"User with QR ID '{qr_id}' marked as hadFood = TRUE!", "updated_data": result}
