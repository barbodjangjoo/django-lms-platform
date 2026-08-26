from celery import shared_task
from .otp_handler import store_otp, normalize_phone
import random
import requests
import logging
from config.settings import x_api_key, template_id

logger = logging.getLogger(__name__)


@shared_task
def send_sms_code(phone_number, code):
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain",
        "x-api-key": str(x_api_key),
    }

    payload = {
        "mobile": phone_number,
        "templateId": int(template_id),
        "parameters": [
            {"name": "CODE", "value": code}  
        ]
    }

    try:
        response = requests.post('https://api.sms.ir/v1/send/verify', json=payload, headers=headers, timeout=10)
        data = response.json()
        logger.warning(f"SMS.ir response for {phone_number}: {data}") 

        if data.get("status") == 1:
            return {"success": True, "data": data}
        else:
            return {"success": False, "data": data}

    except Exception as e:
        return {"success": False, "error": str(e)}



def send_otp_to_user(phone_number, purpose="login"):
    phone_number = normalize_phone(phone_number)
    code = str(random.randint(100000, 999999))

    store_otp(phone_number, purpose.lower(), code)

    send_sms_code.delay(phone_number, code)

    return code