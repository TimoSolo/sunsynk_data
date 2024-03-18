import os
import requests
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
BEARER_TOKEN = None
PLANT_ID = os.getenv("PLANT_ID") # eg "306756"  Replace with your plant ID, not sure how to get the plant ID from API yet

def get_bearer_token():
    global BEARER_TOKEN
    if BEARER_TOKEN:
        return BEARER_TOKEN

    url = "https://api.sunsynk.net/oauth/token"
    headers = {"Content-Type": "application/json"}
    payload = {
        "areaCode": "sunsynk",
        "client_id": "csp-web",
        "grant_type": "password",
        "source": "sunsynk",
        "username": USERNAME,
        "password": PASSWORD
    }
    print("Logging in to Sunsynk as " + USERNAME + "...")
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get('success') and 'data' in response_data:
            print("Login successful")
            BEARER_TOKEN = response_data['data'].get('access_token')
            return BEARER_TOKEN
        else:
            raise Exception("Login failed or access token not found in response")
    else:
        response_data = response.json()
        error_message = response_data.get('msg', 'Failed to retrieve bearer token')
        raise Exception(error_message)
    
def fetch_plant_id():
    """
    Fetches the plant ID.
    :return: Plant ID
    """
    print("Fetching plant information...")
    global BEARER_TOKEN
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }
    url = "https://api.sunsynk.net/api/v1/plants?page=1&limit=1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get('msg') == "Success" and 'infos' in response_data['data']:
            plant_info = response_data['data']['infos'][0]  # Get the first plant info
            print(f"Found plant: {plant_info['name']} {plant_info['id']}")
            return plant_info['id']
        else:
            raise Exception("Failed to fetch plant information or plant information not found in response")
    else:
        raise Exception("Failed to retrieve plant information")

def fetch_data_for_month(id, date):
    """
    Fetches data for a given month.
    :param id: Plant ID
    :param date: Date in the format YYYY-MM
    :return: JSON response from the API
    """
    headers = {
        "Authorization": f"Bearer {get_bearer_token()}"
    }
    url = f"https://api.sunsynk.net/api/v1/plant/energy/{id}/month?lan=en&date={date}&id={id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json().get('data'):
        return response.json()['data']['infos']
    else:
        return None

def fetch_data_for_day(id, date):
    """
    Fetches data for a given day.
    :param id: Plant ID
    :param date: Date in the format YYYY-MM-DD
    :return: JSON response from the API
    """
    headers = {
        "Authorization": f"Bearer {get_bearer_token()}"
    }
    url = f"https://api.sunsynk.net/api/v1/plant/energy/{id}/day?lan=en&date={date}&id={id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json().get('data'):
        return response.json()['data']['infos']
    else:
        return None

def process_data(data, is_daily=False):
    """
    Processes the data to fit the desired Excel structure.
    :param data: List of data dictionaries from the API.
    :param is_daily: Boolean indicating if the data being processed is daily data.
    :return: DataFrame ready for Excel export.
    """
    processed_data = {}

    for entry in data:
        for date, infos in entry.items():
            for category in infos:
                label = f"{category['label']} ({category['unit']})"
                for record in category['records']:
                    if is_daily:
                        # For daily data, prepend the date to the time to make it unique
                        time = f"{date} {record['time']}"
                    else:
                        # For monthly data, use the date as is
                        time = f"{record['time']}"

                    value = float(record['value'])
                    if time not in processed_data:
                        processed_data[time] = {}
                    processed_data[time][label] = processed_data[time].get(label, 0) + value

    df = pd.DataFrame.from_dict(processed_data, orient='index').sort_index()
    df.index.name = 'Date/Time' if is_daily else 'Date'
    return df

def main():
    global BEARER_TOKEN, PLANT_ID
    # Login to get the bearer token
    get_bearer_token()

    # Fetch the plant ID
    PLANT_ID = fetch_plant_id()
    id = PLANT_ID
    monthly_data = []
    daily_data = []

    # Monthly data collection
    current_month = datetime.now()
    while True:
        month_str = current_month.strftime("%Y-%m")
        print(f"Fetching monthly data for {month_str}...")
        monthly_data_chunk = fetch_data_for_month(id, month_str)
        if monthly_data_chunk:
            monthly_data.append({month_str: monthly_data_chunk})
            # Move to the previous month
            current_month -= timedelta(days=current_month.day + 1)
        else:
            print("No more monthly data found.")
            break

    # Daily data collection
    current_day = datetime.now()
    while True:
        day_str = current_day.strftime("%Y-%m-%d")
        print(f"Fetching daily data for {day_str}...")
        daily_data_chunk = fetch_data_for_day(id, day_str)
        if daily_data_chunk:
            daily_data.append({day_str: daily_data_chunk})
            current_day -= timedelta(days=1)  # Move to the previous day
        else:
            print("No more daily data found.")
            break

    # Processing data
    df_monthly = process_data(monthly_data, is_daily=False)
    df_daily = process_data(daily_data, is_daily=True)

    # Exporting to Excel
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"solar_data_history_{PLANT_ID}_{current_datetime}.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df_monthly.to_excel(writer, sheet_name='Monthly Data')
        df_daily.to_excel(writer, sheet_name='Daily Data')
    print(f"Data exported to {excel_filename}")

if __name__ == "__main__":
    main()