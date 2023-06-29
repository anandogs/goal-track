import os
import requests
from requests.auth import HTTPBasicAuth
from base64 import b64encode
from datetime import datetime, timedelta

def get_time_entries(email, password):
    today = datetime.now()
    tomorrow = today + timedelta(days=1)

    date_today = today.strftime('%Y-%m-%d')
    date_tomorrow = tomorrow.strftime('%Y-%m-%d')

    payload = {'start_date': date_today, 'end_date': date_tomorrow}

    URL = 'https://api.track.toggl.com/api/v9/me/time_entries'
    credentials = b64encode(f"{email}:{password}".encode("utf-8")).decode("ascii")

    headers = {
        'content-type': 'application/json',
        'Authorization': f'Basic {credentials}'
    }

    response = requests.get(URL, headers=headers, params=payload, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None
