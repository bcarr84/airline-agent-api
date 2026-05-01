# SkyLine Airlines — Aria Voice Agent Backend

FastAPI backend for the ElevenLabs airline voice agent demo.

## Deploy to Railway (3 clicks)

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project → Deploy from GitHub repo**
3. Select this repo → Railway auto-detects Python and deploys

Your live URL will appear in the Railway dashboard within ~60 seconds:
`https://your-project-name.up.railway.app`

## Use your URL in ElevenLabs

Replace `YOUR_API_BASE_URL` in each tool with your Railway URL:
- `https://your-project-name.up.railway.app/tools/lookup_booking`
- `https://your-project-name.up.railway.app/tools/get_flight_status`
- etc.

## Test it's working

Visit `https://your-project-name.up.railway.app/health` in your browser.
You should see: `{"status":"ok","service":"SkyLine Airlines Voice Agent API"}`

## All available endpoints

| Endpoint | Purpose |
|---|---|
| POST /tools/lookup_booking | Fetch passenger booking |
| POST /tools/lookup_crew_pairing | Fetch crew pairing |
| POST /tools/get_flight_status | Live flight status |
| POST /tools/get_rebook_options | Rebooking alternatives |
| POST /tools/rebook_passenger | Execute rebooking |
| POST /tools/get_crew_reroute_options | Crew IROP options |
| POST /tools/track_baggage | Bag location & status |
| POST /tools/file_baggage_claim | File PIR report |
| POST /tools/arrange_bag_delivery | Schedule bag delivery |
| POST /tools/issue_voucher | Issue meal/hotel voucher |
| POST /tools/get_loyalty_profile | Miles & tier info |
| POST /tools/check_upgrade_availability | Upgrade inventory |
| POST /tools/apply_upgrade | Process upgrade |
| POST /tools/apply_loyalty_bonus | Credit bonus miles |
| POST /tools/send_confirmation | Send SMS/email |
| POST /tools/transfer_to_agent | Human handoff |
| POST /tools/transfer_to_crew_scheduling | Crew desk transfer |
| GET  /health | Health check |
