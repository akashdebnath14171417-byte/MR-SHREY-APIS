# 🔥 MR SHREY API Gateway

Complete API Package with Key Expiry System

## 👨‍💻 Developer
- **MR SHREY**
- [Telegram](https://t.me/MR_SHREY3)

## 📌 Available APIs

| API | Endpoint | Example |
|-----|----------|---------|
| PAN Info | `/pan/<pan>` | `/pan/JCZPS4827P?api_key=MR_SHREY_MONTHLY_001` |
| Aadhar Info | `/aadhar/<number>` | `/aadhar/123456789012?api_key=MR_SHREY_MONTHLY_001` |
| Vehicle Info | `/vehicle/<rc>` | `/vehicle/MH12DE1433?api_key=MR_SHREY_MONTHLY_001` |
| Vehicle91 (Free) | `/vehicle91/<rc>` | `/vehicle91/MH12DE1433` |
| Number Info | `/number/<phone>` | `/number/9876543210?api_key=MR_SHREY_MONTHLY_001` |
| UPI Info | `/upi/<vpa>` | `/upi/example@axl?api_key=MR_SHREY_MONTHLY_001` |
| Key Info | `/keyinfo/<api_key>` | `/keyinfo/MR_SHREY_MONTHLY_001` |

## 🔑 Available Keys

| Plan | API Key | Daily Limit |
|------|---------|-------------|
| 1 Month | `MR_SHREY_MONTHLY_001` | 1000 |
| 2 Months | `MR_SHREY_2MONTH_001` | 2000 |
| 3 Months | `MR_SHREY_3MONTH_001` | 3000 |
| Master (1 Year) | `MR_SHREY_MASTER_001` | 10000 |

## 🚀 Deploy on Vercel

```bash
vercel --prod
