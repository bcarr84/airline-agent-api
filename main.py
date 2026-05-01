"""
SkyLine Airlines Voice Agent — Backend API
Deploy this to any Python host (Railway, Render, AWS Lambda, etc.)
Replace YOUR_API_BASE_URL in tool_schemas.json with your deployed URL.

Install dependencies:
  pip install fastapi uvicorn pydantic

Run locally:
  uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import random
import string
import uuid

app = FastAPI(title="SkyLine Airlines Voice Agent API", version="1.0.0")

# ---------------------------------------------------------------------------
# AUTH — validate ElevenLabs webhook secret
# ---------------------------------------------------------------------------
ELEVENLABS_WEBHOOK_SECRET = "YOUR_ELEVENLABS_WEBHOOK_SECRET"  # set in ElevenLabs dashboard

def verify_secret(x_elevenlabs_signature: Optional[str] = Header(None)):
    # In production, verify HMAC signature from ElevenLabs
    # For now, basic check
    if x_elevenlabs_signature != ELEVENLABS_WEBHOOK_SECRET:
        pass  # Uncomment below to enforce in production
        # raise HTTPException(status_code=401, detail="Unauthorized")

# ---------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------

class LookupBookingRequest(BaseModel):
    pnr: str
    last_name: str

class LookupCrewRequest(BaseModel):
    employee_id: str
    pairing_number: str

class FlightStatusRequest(BaseModel):
    flight_number: str
    date: str

class RebookOptionsRequest(BaseModel):
    pnr: str
    origin: str
    destination: str
    preferred_date: Optional[str] = None

class RebookPassengerRequest(BaseModel):
    pnr: str
    new_flight_number: str
    new_date: str
    cabin: str
    change_type: str

class CrewRerouteRequest(BaseModel):
    employee_id: str
    pairing_number: str

class TrackBaggageRequest(BaseModel):
    bag_tag_number: str

class FileBaggageClaimRequest(BaseModel):
    pnr: str
    incident_type: str
    bag_tag_number: Optional[str] = None
    description: str
    delivery_address: Optional[str] = None

class ArrangeBagDeliveryRequest(BaseModel):
    bag_tag_number: str
    delivery_address: str
    contact_phone: Optional[str] = None

class IssueVoucherRequest(BaseModel):
    pnr: str
    voucher_type: str
    value: Optional[float] = None
    reason: str

class LoyaltyProfileRequest(BaseModel):
    ffn: str

class UpgradeAvailabilityRequest(BaseModel):
    flight_number: str
    date: str
    target_cabin: str

class ApplyUpgradeRequest(BaseModel):
    pnr: str
    target_cabin: str
    method: str
    miles_amount: Optional[float] = None
    cash_amount: Optional[float] = None

class LoyaltyBonusRequest(BaseModel):
    ffn: str
    miles: float
    reason: str

class SendConfirmationRequest(BaseModel):
    pnr: str
    channel: str
    message_type: str
    recipient: str

class TransferToAgentRequest(BaseModel):
    caller_id: str
    issue_summary: str
    queue: str

class TransferToCrewRequest(BaseModel):
    employee_id: str
    pairing_number: str
    reason: str

# ---------------------------------------------------------------------------
# MOCK DATA HELPERS
# Replace these with real PSS / GDS / World Tracer / CRM integrations
# ---------------------------------------------------------------------------

def mock_booking(pnr: str, last_name: str):
    return {
        "pnr": pnr.upper(),
        "passenger_name": f"{last_name.title()}, James",
        "ffn": "SK" + "".join(random.choices(string.digits, k=8)),
        "tier": random.choice(["Gold", "Platinum", "Silver", "Blue"]),
        "miles_balance": random.randint(5000, 120000),
        "flights": [
            {
                "flight_number": "SK456",
                "origin": "LHR",
                "destination": "JFK",
                "departure": "2024-03-15T09:30:00Z",
                "arrival": "2024-03-15T12:45:00Z",
                "cabin": "economy",
                "seat": "32A",
                "status": "delayed"
            }
        ],
        "bags": [{"tag": "SK" + "".join(random.choices(string.digits, k=10)), "count": 1}],
        "contact_email": f"{last_name.lower()}@example.com",
        "contact_phone": "+1-555-" + "".join(random.choices(string.digits, k=7))
    }

DELAY_REASONS = [
    "Late inbound aircraft",
    "Air traffic control restriction",
    "Weather at origin airport",
    "Crew availability",
    "Technical inspection required"
]

# ---------------------------------------------------------------------------
# ENDPOINTS
# ---------------------------------------------------------------------------

@app.post("/tools/lookup_booking")
async def lookup_booking(req: LookupBookingRequest):
    """Fetch passenger booking from PSS"""
    if len(req.pnr) != 6:
        return {"success": False, "error": "Booking reference not found. Please check and try again."}
    booking = mock_booking(req.pnr, req.last_name)
    return {"success": True, "booking": booking}


@app.post("/tools/lookup_crew_pairing")
async def lookup_crew_pairing(req: LookupCrewRequest):
    """Fetch crew pairing from crew management system"""
    return {
        "success": True,
        "crew_member": {
            "employee_id": req.employee_id,
            "name": "Captain Sarah Mitchell",
            "role": "Captain",
            "base": "LHR",
            "pairing_number": req.pairing_number,
            "flights": [
                {"flight": "SK456", "role": "PIC", "departure": "2024-03-15T09:30:00Z"}
            ],
            "duty_hours_today": 6.5,
            "max_duty_hours": 13,
            "rest_hours_required": 11,
            "last_rest_start": "2024-03-14T20:00:00Z"
        }
    }


@app.post("/tools/get_flight_status")
async def get_flight_status(req: FlightStatusRequest):
    """Get live flight status from operations"""
    delay_minutes = random.choice([0, 45, 90, 180, 0])
    status = "on_time" if delay_minutes == 0 else "delayed"
    return {
        "success": True,
        "flight": {
            "flight_number": req.flight_number,
            "date": req.date,
            "status": status,
            "delay_minutes": delay_minutes,
            "delay_reason": random.choice(DELAY_REASONS) if delay_minutes > 0 else None,
            "scheduled_departure": "09:30",
            "estimated_departure": f"0{9 + delay_minutes // 60}:{delay_minutes % 60:02d}" if delay_minutes > 0 else "09:30",
            "gate": "B22",
            "terminal": "5"
        }
    }


@app.post("/tools/get_rebook_options")
async def get_rebook_options(req: RebookOptionsRequest):
    """Get rebooking alternatives from PSS"""
    options = [
        {
            "rank": 1,
            "flight_number": "SK458",
            "origin": req.origin,
            "destination": req.destination,
            "departure": "11:45",
            "arrival": "14:55",
            "cabin": "economy",
            "seats_available": 12,
            "fare_difference": 0,
            "change_fee": 0
        },
        {
            "rank": 2,
            "flight_number": "SK462",
            "origin": req.origin,
            "destination": req.destination,
            "departure": "14:20",
            "arrival": "17:35",
            "cabin": "economy",
            "seats_available": 28,
            "fare_difference": 0,
            "change_fee": 0
        },
        {
            "rank": 3,
            "flight_number": "SK458",
            "origin": req.origin,
            "destination": req.destination,
            "departure": "11:45",
            "arrival": "14:55",
            "cabin": "business",
            "seats_available": 4,
            "fare_difference": 450,
            "change_fee": 0
        }
    ]
    return {"success": True, "options": options}


@app.post("/tools/rebook_passenger")
async def rebook_passenger(req: RebookPassengerRequest):
    """Execute rebooking in PSS"""
    new_pnr_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=2))
    return {
        "success": True,
        "confirmation": {
            "pnr": req.pnr,
            "new_flight": req.new_flight_number,
            "new_date": req.new_date,
            "cabin": req.cabin,
            "seat": f"{random.randint(10, 45)}{random.choice('ABCDEF')}",
            "change_type": req.change_type,
            "change_fee_charged": 0 if req.change_type == "involuntary" else 75,
            "confirmation_code": f"RBK{new_pnr_suffix}{datetime.now().strftime('%H%M')}"
        }
    }


@app.post("/tools/get_crew_reroute_options")
async def get_crew_reroute_options(req: CrewRerouteRequest):
    """Get duty-compliant rerouting from crew management system"""
    return {
        "success": True,
        "options": [
            {
                "rank": 1,
                "flight_number": "SK458",
                "role": "Captain",
                "departure": "11:45",
                "duty_hours_added": 2.5,
                "total_duty_hours": 9.0,
                "compliant": True,
                "rest_violation": False
            },
            {
                "rank": 2,
                "flight_number": "SK470",
                "role": "Captain",
                "departure": "16:00",
                "duty_hours_added": 5.5,
                "total_duty_hours": 12.0,
                "compliant": True,
                "rest_violation": False
            }
        ],
        "non_compliant_options_suppressed": 1
    }


@app.post("/tools/track_baggage")
async def track_baggage(req: TrackBaggageRequest):
    """Track bag via World Tracer integration"""
    statuses = [
        {"status": "in_transit", "location": "LHR Baggage Hub", "estimated_delivery": "Within 4 hours"},
        {"status": "on_next_flight", "location": "Loaded on SK458", "estimated_delivery": "Arriving 15:10 JFK"},
        {"status": "at_destination", "location": "JFK Baggage Claim Belt 7", "estimated_delivery": "Available now"},
        {"status": "not_located", "location": None, "estimated_delivery": None}
    ]
    result = random.choice(statuses)
    return {
        "success": True,
        "bag_tag": req.bag_tag_number,
        **result
    }


@app.post("/tools/file_baggage_claim")
async def file_baggage_claim(req: FileBaggageClaimRequest):
    """File PIR in baggage management system"""
    pir_ref = "PIR" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return {
        "success": True,
        "pir_reference": pir_ref,
        "incident_type": req.incident_type,
        "pnr": req.pnr,
        "next_steps": "Our baggage team will contact you within 24 hours. Check status at skyline.com/baggage",
        "claim_deadline": (datetime.now() + timedelta(days=21)).strftime("%Y-%m-%d")
    }


@app.post("/tools/arrange_bag_delivery")
async def arrange_bag_delivery(req: ArrangeBagDeliveryRequest):
    """Schedule bag delivery via courier integration"""
    delivery_ref = "DEL" + "".join(random.choices(string.digits, k=8))
    return {
        "success": True,
        "delivery_reference": delivery_ref,
        "bag_tag": req.bag_tag_number,
        "delivery_address": req.delivery_address,
        "estimated_delivery": "Within 6-8 hours",
        "tracking_url": f"https://skyline.com/track/{delivery_ref}"
    }


@app.post("/tools/issue_voucher")
async def issue_voucher(req: IssueVoucherRequest):
    """Issue voucher via customer services platform"""
    voucher_defaults = {
        "meal": 15.00,
        "hotel": 150.00,
        "transport": 40.00,
        "lounge": 0.00
    }
    voucher_code = "VCH" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    value = req.value or voucher_defaults.get(req.voucher_type, 0)
    return {
        "success": True,
        "voucher_code": voucher_code,
        "type": req.voucher_type,
        "value": value,
        "currency": "USD",
        "valid_until": (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M"),
        "redemption_info": "Show this code at any airport restaurant / hotel desk / transport desk"
    }


@app.post("/tools/get_loyalty_profile")
async def get_loyalty_profile(req: LoyaltyProfileRequest):
    """Fetch loyalty profile from CRM"""
    tiers = ["Blue", "Silver", "Gold", "Platinum"]
    tier = random.choice(tiers)
    miles = random.randint(8000, 250000)
    flights_this_year = random.randint(1, 120)
    return {
        "success": True,
        "profile": {
            "ffn": req.ffn,
            "name": "James Chen",
            "tier": tier,
            "miles_balance": miles,
            "miles_expiry": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "tier_miles_ytd": random.randint(5000, 80000),
            "tier_renewal_miles_needed": 25000 if tier != "Platinum" else 0,
            "flights_this_year": flights_this_year,
            "milestone_flight": flights_this_year in [50, 100],
            "recent_irop": random.choice([True, False]),
            "birthday_within_7_days": random.choice([True, False]),
            "eligible_upgrades": 2 if tier in ["Gold", "Platinum"] else 0,
            "lounge_access": tier in ["Gold", "Platinum"],
            "complimentary_bags": 2 if tier in ["Gold", "Platinum"] else (1 if tier == "Silver" else 0)
        }
    }


@app.post("/tools/check_upgrade_availability")
async def check_upgrade_availability(req: UpgradeAvailabilityRequest):
    """Check upgrade inventory from revenue management"""
    available = random.choice([True, True, True, False])
    return {
        "success": True,
        "flight_number": req.flight_number,
        "date": req.date,
        "target_cabin": req.target_cabin,
        "available": available,
        "seats_remaining": random.randint(1, 8) if available else 0,
        "miles_cost": {"premium_economy": 8000, "business": 15000, "first": 30000}.get(req.target_cabin),
        "cash_bid_price": {"premium_economy": 89, "business": 199, "first": 450}.get(req.target_cabin),
        "upgrade_window_closes": "2 hours before departure"
    }


@app.post("/tools/apply_upgrade")
async def apply_upgrade(req: ApplyUpgradeRequest):
    """Apply upgrade via PSS and loyalty platform"""
    new_seat = f"{random.randint(1, 8)}{random.choice('ABCDF')}"
    return {
        "success": True,
        "pnr": req.pnr,
        "new_cabin": req.target_cabin,
        "new_seat": new_seat,
        "method": req.method,
        "miles_deducted": req.miles_amount if req.method == "miles" else 0,
        "amount_charged": req.cash_amount if req.method == "cash" else 0,
        "boarding_pass_updated": True,
        "confirmation_code": "UPG" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    }


@app.post("/tools/apply_loyalty_bonus")
async def apply_loyalty_bonus(req: LoyaltyBonusRequest):
    """Credit bonus miles to loyalty account"""
    return {
        "success": True,
        "ffn": req.ffn,
        "miles_credited": req.miles,
        "reason": req.reason,
        "new_balance": random.randint(10000, 150000) + int(req.miles),
        "effective_date": datetime.now().strftime("%Y-%m-%d"),
        "transaction_id": "TXN" + str(uuid.uuid4())[:8].upper()
    }


@app.post("/tools/send_confirmation")
async def send_confirmation(req: SendConfirmationRequest):
    """Send confirmation via notifications platform"""
    return {
        "success": True,
        "pnr": req.pnr,
        "channel": req.channel,
        "message_type": req.message_type,
        "recipient": req.recipient,
        "sent_at": datetime.now().isoformat(),
        "message_id": "MSG" + str(uuid.uuid4())[:10].upper()
    }


@app.post("/tools/transfer_to_agent")
async def transfer_to_agent(req: TransferToAgentRequest):
    """Initiate warm transfer to human agent queue"""
    wait_times = {"general": 4, "crew_scheduling": 1, "baggage_claims": 6, "complaints": 8, "refunds": 10}
    return {
        "success": True,
        "caller_id": req.caller_id,
        "queue": req.queue,
        "estimated_wait_minutes": wait_times.get(req.queue, 5),
        "transfer_initiated": True,
        "context_summary_sent": True
    }


@app.post("/tools/transfer_to_crew_scheduling")
async def transfer_to_crew_scheduling(req: TransferToCrewRequest):
    """Transfer crew member to duty scheduling desk"""
    return {
        "success": True,
        "employee_id": req.employee_id,
        "pairing_number": req.pairing_number,
        "reason": req.reason,
        "duty_desk_notified": True,
        "estimated_wait_minutes": 1,
        "transfer_initiated": True
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "SkyLine Airlines Voice Agent API"}


# ---------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
