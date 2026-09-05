import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.routes.chat import request_insurance_call, InsuranceCallEnquiryRequest

async def test_insurance():
    req = InsuranceCallEnquiryRequest(
        farmer_name="Muthuvel",
        phone_number="+919876543210",
        location="Cuddalore, Tamil Nadu",
        language="ta-IN",
        disaster_type="Cyclone Michaung Inundation",
        crop="Samba Paddy"
    )
    res = await request_insurance_call(req)
    print("Status Code:", res.status_code)
    print("Response JSON:", res.body.decode("utf-8"))

if __name__ == "__main__":
    asyncio.run(test_insurance())
