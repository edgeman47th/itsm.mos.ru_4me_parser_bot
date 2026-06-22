from datetime import datetime, timedelta
import requests
from config import BEARER_TOKEN, ACCOUNT_ID
    
class ItemParser:
    def check_new_requests():
        resp = requests.get(f'https://api.itsm.mos.ru/requests/assigned_to_my_team?status=assigned',
                            headers={
                                'Authorization': f'Bearer {BEARER_TOKEN}',
                                'X-4me-Account': ACCOUNT_ID
                            })
        print(resp.json())
        return resp.json()