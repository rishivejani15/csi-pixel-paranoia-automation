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
