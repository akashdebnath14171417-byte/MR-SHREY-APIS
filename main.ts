// =====================================================================
// MR SHREY API - Deno Deploy Version
// =====================================================================

import { serve } from "https://deno.land/std@0.208.0/http/server.ts";

// =====================================================================
// API KEY SYSTEM
// =====================================================================

const API_KEYS: Record<string, any> = {
  "MR_SHREY_MONTHLY_001": {
    key: "MR_SHREY_MONTHLY_001",
    plan: "1 Month",
    days: 30,
    daily_limit: 1000,
    created: "2026-08-13",
    expiry: "2026-09-13",
    used_today: 0,
    last_reset: "2026-08-13"
  },
  "MR_SHREY_2MONTH_001": {
    key: "MR_SHREY_2MONTH_001",
    plan: "2 Months",
    days: 60,
    daily_limit: 2000,
    created: "2026-08-13",
    expiry: "2026-10-13",
    used_today: 0,
    last_reset: "2026-08-13"
  },
  "MR_SHREY_3MONTH_001": {
    key: "MR_SHREY_3MONTH_001",
    plan: "3 Months",
    days: 90,
    daily_limit: 3000,
    created: "2026-08-13",
    expiry: "2026-11-13",
    used_today: 0,
    last_reset: "2026-08-13"
  },
  "MR_SHREY_MASTER_001": {
    key: "MR_SHREY_MASTER_001",
    plan: "Master (1 Year)",
    days: 365,
    daily_limit: 10000,
    created: "2026-08-13",
    expiry: "2027-08-13",
    used_today: 0,
    last_reset: "2026-08-13"
  }
};

// =====================================================================
// HELPERS
// =====================================================================

function getKeyInfo(apiKey: string) {
  const data = API_KEYS[apiKey];
  if (!data) return null;
  
  const expiryDate = new Date(data.expiry);
  const now = new Date();
  const daysLeft = Math.ceil((expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  
  return {
    plan: data.plan,
    expiry: data.expiry,
    days_left: daysLeft,
    daily_limit: data.daily_limit,
    used_today: data.used_today,
    remaining_today: data.daily_limit - data.used_today,
    status: daysLeft > 0 ? "Active" : "Expired"
  };
}

function validateApiKey(apiKey: string) {
  const data = API_KEYS[apiKey];
  if (!data) return { valid: false, error: "❌ Invalid API Key!" };
  
  const expiryDate = new Date(data.expiry);
  if (new Date() > expiryDate) {
    return { valid: false, error: "❌ API Key Expired!" };
  }
  
  const today = new Date().toISOString().split('T')[0];
  if (data.last_reset !== today) {
    data.used_today = 0;
    data.last_reset = today;
  }
  
  if (data.used_today >= data.daily_limit) {
    return { valid: false, error: `❌ Daily Limit Reached! (0/${data.daily_limit} remaining)` };
  }
  
  return { valid: true, data };
}

// =====================================================================
// HANDLER
// =====================================================================

async function handler(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const path = url.pathname;
  const params = url.searchParams;
  const parts = path.split('/').filter(p => p);
  
  const headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
  };
  
  // CORS Preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers });
  }
  
  // =============================================================
  // HOME
  // =============================================================
  if (parts.length === 0) {
    return new Response(JSON.stringify({
      service: "MR SHREY API Gateway",
      developer: "MR SHREY",
      channel: "https://t.me/MR_SHREY3",
      version: "2.0",
      endpoints: {
        "/pan/<pan>": { method: "GET", params: { api_key: "Required" }, example: "/pan/JCZPS4827P?api_key=MR_SHREY_MONTHLY_001" },
        "/vehicle91/<rc>": { method: "GET", params: { api_key: "Optional" }, example: "/vehicle91/MH12DE1433" },
        "/keyinfo/<api_key>": { method: "GET", description: "Check API Key Details", example: "/keyinfo/MR_SHREY_MONTHLY_001" }
      },
      available_plans: {
        "1 Month": { key: "MR_SHREY_MONTHLY_001", daily_limit: 1000 },
        "2 Months": { key: "MR_SHREY_2MONTH_001", daily_limit: 2000 },
        "3 Months": { key: "MR_SHREY_3MONTH_001", daily_limit: 3000 },
        "Master (1 Year)": { key: "MR_SHREY_MASTER_001", daily_limit: 10000 }
      }
    }, null, 2), { status: 200, headers });
  }
  
  // =============================================================
  // KEY INFO
  // =============================================================
  if (parts[0] === "keyinfo" && parts.length === 2) {
    const apiKey = parts[1];
    const keyInfo = getKeyInfo(apiKey);
    
    return new Response(JSON.stringify({
      status: keyInfo ? "success" : "error",
      developer: "MR SHREY",
      channel: "https://t.me/MR_SHREY3",
      key_info: keyInfo || "Invalid API Key!"
    }, null, 2), { status: 200, headers });
  }
  
  // =============================================================
  // VEHICLE91 (FREE - No API Key Required)
  // =============================================================
  if (parts[0] === "vehicle91" && parts.length === 2) {
    const rc = parts[1];
    const regClean = rc.toUpperCase().replace(/[\s-]/g, '');
    
    if (!/^[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{1,4}$/.test(regClean)) {
      return new Response(JSON.stringify({
        status: "error",
        message: "Invalid format. Example: MH12AB1234",
        developer: "MR SHREY",
        channel: "https://t.me/MR_SHREY3"
      }, null, 2), { status: 400, headers });
    }
    
    try {
      const sessionId = `${crypto.randomUUID()}-${crypto.randomUUID()}`;
      const response = await fetch("https://api1.91wheels.com/api/v1/third/rc-detail", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
          "Origin": "https://www.91wheels.com",
          "Referer": "https://www.91wheels.com/",
          "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
        },
        body: JSON.stringify({ regNo: regClean, sessionid: sessionId })
      });
      
      const data = await response.json();
      
      return new Response(JSON.stringify({
        status: "success",
        developer: "MR SHREY",
        channel: "https://t.me/MR_SHREY3",
        data: data
      }, null, 2), { status: 200, headers });
      
    } catch (error) {
      return new Response(JSON.stringify({
        status: "error",
        message: error.message,
        developer: "MR SHREY",
        channel: "https://t.me/MR_SHREY3"
      }, null, 2), { status: 500, headers });
    }
  }
  
  // =============================================================
  // PAN INFO
  // =============================================================
  if (parts[0] === "pan" && parts.length === 2) {
    const pan = parts[1];
    const apiKey = params.get('api_key');
    
    if (!apiKey) {
      return new Response(JSON.stringify({
        status: "error",
        message: "❌ API Key Required!",
        developer: "MR SHREY",
        channel: "https://t.me/MR_SHREY3"
      }, null, 2), { status: 400, headers });
    }
    
    const validation = validateApiKey(apiKey);
    if (!validation.valid) {
      return new Response(JSON.stringify({
        status: "error",
        message: validation.error,
        developer: "MR SHREY",
        channel: "https://t.me/MR_SHREY3"
      }, null, 2), { status: 403, headers });
    }
    
    try {
      const response = await fetch(
        `https://turtlemintloans.com/api/minterprise/v1/products/personal-loan/leads/existing-lead-by-pan?pan=${pan}`,
        {
          headers: {
            "x-broker": "turtlemint",
            "authorization": "Bearer f13517d5a59b689d16aa30c528ccaf7801f823b0f5548f65d6d3793270cfe8d628cea877289aba166e5425c31cfc7a0b",
            "x-provider": "signzy",
            "content-type": "application/json"
          }
        }
      );
      
      const data = await response.json();
      validation.data.used_today += 1;
      const keyInfo = getKeyInfo(apiKey);
      
      return new Response(JSON.stringify({
        status: "success",
        developer: "MR SHREY",
        channel: "https://t.me/MR_SHREY3",
        key_info: keyInfo,
        data: data
      }, null, 2), { status: 200, headers });
      
    } catch (error) {
      return new Response(JSON.stringify({
        status: "error",
        message: error.message,
        developer: "MR SHREY",
        channel: "https://t.me/MR_SHREY3"
      }, null, 2), { status: 500, headers });
    }
  }
  
  // =============================================================
  // 404
  // =============================================================
  return new Response(JSON.stringify({
    status: "error",
    message: "Endpoint not found",
    developer: "MR SHREY",
    channel: "https://t.me/MR_SHREY3"
  }, null, 2), { status: 404, headers });
}

// =====================================================================
// SERVER START
// =====================================================================

serve(handler, { port: 8000 });

console.log("🚀 MR SHREY API Server running on http://localhost:8000");
console.log("👨‍💻 Developer: MR SHREY");
console.log("📢 Channel: https://t.me/MR_SHREY3");
