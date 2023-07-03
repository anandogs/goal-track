from base64 import b64encode
from datetime import datetime, timedelta
import requests
import pytz

def get_time_entries(email, password):
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    items_today = []


    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    date_yesterday = yesterday.strftime('%Y-%m-%d')
    date_tomorrow = tomorrow.strftime('%Y-%m-%d')

    payload = {'start_date': date_yesterday, 'end_date': date_tomorrow}

    URL = 'https://api.track.toggl.com/api/v9/me/time_entries'
    credentials = b64encode(f"{email}:{password}".encode("utf-8")).decode("ascii")

    headers = {
        'content-type': 'application/json',
        'Authorization': f'Basic {credentials}'
    }

    response = requests.get(URL, headers=headers, params=payload, timeout=5)

    if response.status_code == 200:
        if (len(response.json()) == 0):
            return None
        for item in response.json():
            start_time_utc = datetime.fromisoformat(item['start'].replace('Z', '+00:00'))
            stop_time_utc = datetime.fromisoformat(item['stop'].replace('Z', '+00:00'))

            start_time_ist = start_time_utc.astimezone(ist)
            stop_time_ist = stop_time_utc.astimezone(ist)

            if start_of_day <= start_time_ist <= end_of_day or start_of_day <= stop_time_ist <= end_of_day:
                item['start'] = start_time_ist.isoformat()
                item['stop'] = stop_time_ist.isoformat()
                items_today.append(item)
        data = items_today
        return data
   
    return None
