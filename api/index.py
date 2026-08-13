from http.server import BaseHTTPRequestHandler
import requests
import json
import re
import uuid
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# =====================================================================
# API KEY SYSTEM - MR SHREY
# =====================================================================

API_KEYS = {
    "MR_SHREY_MONTHLY_001": {
        "key": "MR_SHREY_MONTHLY_001",
        "plan": "1 Month",
        "days": 30,
        "daily_limit": 1000,
        "created": "2026-08-13",
        "expiry": "2026-09-13",
        "used_today": 0,
        "last_reset": "2026-08-13"
    },
    "MR_SHREY_2MONTH_001": {
        "key": "MR_SHREY_2MONTH_001",
        "plan": "2 Months",
        "days": 60,
        "daily_limit": 2000,
        "created": "2026-08-13",
        "expiry": "2026-10-13",
        "used_today": 0,
        "last_reset": "2026-08-13"
    },
    "MR_SHREY_3MONTH_001": {
        "key": "MR_SHREY_3MONTH_001",
        "plan": "3 Months",
        "days": 90,
        "daily_limit": 3000,
        "created": "2026-08-13",
        "expiry": "2026-11-13",
        "used_today": 0,
        "last_reset": "2026-08-13"
    },
    "MR_SHREY_MASTER_001": {
        "key": "MR_SHREY_MASTER_001",
        "plan": "Master (1 Year)",
        "days": 365,
        "daily_limit": 10000,
        "created": "2026-08-13",
        "expiry": "2027-08-13",
        "used_today": 0,
        "last_reset": "2026-08-13"
    }
}

# =====================================================================
# VALIDATION FUNCTIONS
# =====================================================================

def validate_api_key(api_key):
    if api_key not in API_KEYS:
        return None, "❌ Invalid API Key!"
    
    key_data = API_KEYS[api_key]
    expiry_date = datetime.strptime(key_data["expiry"], "%Y-%m-%d")
    
    if datetime.now() > expiry_date:
        return None, "❌ API Key Expired!"
    
    today = datetime.now().strftime("%Y-%m-%d")
    if key_data["last_reset"] != today:
        key_data["used_today"] = 0
        key_data["last_reset"] = today
    
    if key_data["used_today"] >= key_data["daily_limit"]:
        return None, f"❌ Daily Limit Reached! (0/{key_data['daily_limit']} remaining)"
    
    return key_data, None

def get_key_info(api_key):
    if api_key not in API_KEYS:
        return None
    
    key_data = API_KEYS[api_key]
    expiry_date = datetime.strptime(key_data["expiry"], "%Y-%m-%d")
    days_left = (expiry_date - datetime.now()).days
    
    return {
        "plan": key_data["plan"],
        "expiry": key_data["expiry"],
        "days_left": days_left,
        "daily_limit": key_data["daily_limit"],
        "used_today": key_data["used_today"],
        "remaining_today": key_data["daily_limit"] - key_data["used_today"],
        "status": "Active" if days_left > 0 else "Expired"
    }

# =====================================================================
# 91WHEELS VEHICLE API
# =====================================================================

def get_91wheels_data(rc_number):
    session_id = f"{uuid.uuid4()}-{uuid.uuid4()}"
    
    payload = {
        "regNo": rc_number.strip().upper(),
        "sessionid": session_id,
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.91wheels.com",
        "Referer": "https://www.91wheels.com/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
    }
    
    try:
        response = requests.post(
            "https://api1.91wheels.com/api/v1/third/rc-detail",
            headers=headers,
            data=json.dumps(payload),
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return {"status": "error", "message": f"91Wheels Error: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def parse_91wheels_data(raw_data):
    if raw_data.get('status') == 'error':
        return raw_data
    
    data = raw_data.get('data', {})
    return {
        "status": "success",
        "source": "91Wheels",
        "vehicle_number": data.get("rc_number"),
        "registration": {
            "date": data.get("registration_date"),
            "registered_at": data.get("registered_at"),
            "fit_up_to": data.get("fit_up_to"),
            "rc_status": data.get("rc_status")
        },
        "vehicle": {
            "chassis_number": data.get("vehicle_chasi_number"),
            "engine_number": data.get("vehicle_engine_number"),
            "maker": data.get("maker_description"),
            "model": data.get("maker_model"),
            "fuel_type": data.get("fuel_type"),
            "color": data.get("color"),
            "cubic_capacity": data.get("cubic_capacity"),
            "seat_capacity": data.get("seat_capacity")
        },
        "owner": {
            "name": data.get("owner_name"),
            "address": data.get("present_address")
        },
        "insurance": {
            "company": data.get("insurance_company"),
            "policy_number": data.get("insurance_policy_number"),
            "insurance_upto": data.get("insurance_upto")
        }
    }

# =====================================================================
# AMAZON PAY UPI API
# =====================================================================

def get_upi_info(vpa):
    url = "https://www.amazon.in/apay/money-transfer/verify-vpa/v2"
    payload = {
        "recipientVpa": vpa,
        "clientContext": {
            "pageType": "EAP",
            "useCase": "SEND_MONEY"
        }
    }
    headers = {
        'User-Agent': "Amazon.com/30.22.0.300 (Android/15/V2509)",
        'content-type': "application/json; charset=utf-8",
        'origin': "https://www.amazon.in",
        'x-requested-with': "in.amazon.mShop.android.shopping",
        'referer': "https://www.amazon.in/apay/money-transfer/assets/ap4-eap/index.html"
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# =====================================================================
# MAIN HANDLER - VERCEL COMPATIBLE
# =====================================================================

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        path = parsed.path.strip("/")
        
        # ===== HOME / ROOT =====
        if not path or path == "":
            self._send_response(200, {
                "service": "MR SHREY API Gateway",
                "developer": "MR SHREY",
                "channel": "https://t.me/MR_SHREY3",
                "endpoints": {
                    "/vehicle91/<rc>": "FREE - No API Key needed",
                    "/pan/<pan>": "Requires API Key",
                    "/number/<phone>": "Requires API Key",
                    "/upi/<vpa>": "Requires API Key",
                    "/keyinfo/<api_key>": "Check API Key details"
                }
            })
            return
        
        parts = path.split("/")
        
        # ===== KEY INFO =====
        if len(parts) >= 2 and parts[0] == "keyinfo":
            api_key = parts[1]
            key_info = get_key_info(api_key)
            
            if key_info:
                self._send_response(200, {
                    "status": "success",
                    "developer": "MR SHREY",
                    "channel": "https://t.me/MR_SHREY3",
                    "key_info": key_info
                })
            else:
                self._send_response(404, {
                    "status": "error",
                    "message": "Invalid API Key!",
                    "developer": "MR SHREY",
                    "channel": "https://t.me/MR_SHREY3"
                })
            return
        
        # ===== VEHICLE91 - FREE =====
        if len(parts) >= 2 and parts[0] == "vehicle91":
            query = parts[1]
            reg_clean = query.strip().upper().replace(" ", "").replace("-", "")
            
            if not re.match(r'^[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{1,4}$', reg_clean):
                self._send_response(400, {
                    "status": "error",
                    "message": "Invalid format. Example: MH12AB1234",
                    "developer": "MR SHREY",
                    "channel": "https://t.me/MR_SHREY3"
                })
                return
            
            raw_data = get_91wheels_data(reg_clean)
            
            if raw_data.get('status') == 'error':
                self._send_response(500, {
                    "status": "error",
                    "message": raw_data.get('message', 'Failed to fetch vehicle data'),
                    "developer": "MR SHREY",
                    "channel": "https://t.me/MR_SHREY3"
                })
                return
            
            parsed = parse_91wheels_data(raw_data)
            parsed["developer"] = "MR SHREY"
            parsed["channel"] = "https://t.me/MR_SHREY3"
            self._send_response(200, parsed)
            return
        
        # ===== ALL OTHER APIS - REQUIRE API KEY =====
        api_key = params.get('api_key', [None])[0]
        
        if not api_key:
            self._send_response(200, {
                "status": "error",
                "message": "❌ API Key Required!",
                "developer": "MR SHREY",
                "channel": "https://t.me/MR_SHREY3",
                "available_plans": {
                    "1 Month": {"key": "MR_SHREY_MONTHLY_001", "daily_limit": 1000},
                    "2 Months": {"key": "MR_SHREY_2MONTH_001", "daily_limit": 2000},
                    "3 Months": {"key": "MR_SHREY_3MONTH_001", "daily_limit": 3000},
                    "Master (1 Year)": {"key": "MR_SHREY_MASTER_001", "daily_limit": 10000}
                }
            })
            return
        
        key_data, error = validate_api_key(api_key)
        
        if not key_data:
            self._send_response(403, {
                "status": "error",
                "message": error,
                "developer": "MR SHREY",
                "channel": "https://t.me/MR_SHREY3"
            })
            return
        
        # ===== PAN INFO =====
        if len(parts) >= 2 and parts[0] == "pan":
            query = parts[1]
            try:
                url = f"https://turtlemintloans.com/api/minterprise/v1/products/personal-loan/leads/existing-lead-by-pan?pan={query}"
                headers = {
                    "x-broker": "turtlemint",
                    "authorization": "Bearer f13517d5a59b689d16aa30c528ccaf7801f823b0f5548f65d6d3793270cfe8d628cea877289aba166e5425c31cfc7a0b",
                    "x-provider": "signzy",
                    "content-type": "application/json"
                }
                r = requests.get(url, headers=headers, timeout=15)
                data = r.json()
                key_data["used_today"] += 1
                
                self._send_response(200, {
                    "status": "success",
                    "developer": "MR SHREY",
                    "channel": "https://t.me/MR_SHREY3",
                    "key_info": get_key_info(api_key),
                    "data": data.get("data", {}),
                    "meta": data.get("meta", {})
                })
            except Exception as e:
                self._send_response(500, {
                    "status": "error",
                    "message": str(e),
                    "developer": "MR SHREY",
                    "channel": "https://t.me/MR_SHREY3"
                })
            return
        
        # ===== NUMBER INFO =====
        if len(parts) >= 2 and parts[0] == "number":
            query = parts[1]
            try:
                r = requests.get(f"https://rootx-osint.in/?type=num&key=seed_bhai&query={query}", timeout=15)
                data = r.json()
                key_data["used_today"] += 1
                
                self._send_response(200, {
                    "status": "success",
                    "developer": "MR SHREY",
                    "channel": "https://t.me/MR_SHREY3",
                    "key_info": get_key_info(api_key),
                    "data": data
                })
            except Exception as e:
                self._send_response(500, {
                    "status": "error",
                    "message": str(e),
                    "developer": "MR SHREY",
                    "channel": "https://t.me/MR_SHREY3"
                })
            return
        
        # ===== UPI INFO =====
        if len(parts) >= 2 and parts[0] == "upi":
            query = parts[1]
            try:
                data = get_upi_info(query)
                key_data["used_today"] += 1
                
                self._send_response(200, {
                    "status": "success",
                    "developer": "MR SHREY",
                    "channel": "https://t.me/MR_SHREY3",
                    "key_info": get_key_info(api_key),
                    "data": data
                })
            except Exception as e:
                self._send_response(500, {
                    "status": "error",
                    "message": str(e),
                    "developer": "MR SHREY",
                    "channel": "https://t.me/MR_SHREY3"
                })
            return
        
        # ===== 404 =====
        self._send_response(404, {
            "status": "error",
            "message": "Endpoint not found",
            "developer": "MR SHREY",
            "channel": "https://t.me/MR_SHREY3",
            "available_endpoints": [
                "/vehicle91/<rc> (FREE)",
                "/pan/<pan>?api_key=YOUR_KEY",
                "/number/<phone>?api_key=YOUR_KEY",
                "/upi/<vpa>?api_key=YOUR_KEY",
                "/keyinfo/<api_key>"
            ]
        })
    
    def _send_response(self, status_code, data):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
