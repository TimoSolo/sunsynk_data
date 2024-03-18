import os
import requests
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
API_URL_TEMPLATE = "https://api.sunsynk.net/api/v1/plant/energy/{id}/month?lan=en&date={date}&id={id}"
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Headers for API request
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

def fetch_data_for_month(id, date):
    """
    Fetches data for a given month.
    :param id: Plant ID
    :param date: Date in the format YYYY-MM
    :return: JSON response from the API
    """
    url = API_URL_TEMPLATE.format(id=id, date=date)
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
    daily_url_template = "https://api.sunsynk.net/api/v1/plant/energy/{id}/day?lan=en&date={date}&id={id}"
    url = daily_url_template.format(id=id, date=date)
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
                        time = date

                    value = float(record['value'])
                    if time not in processed_data:
                        processed_data[time] = {}
                    processed_data[time][label] = processed_data[time].get(label, 0) + value

    df = pd.DataFrame.from_dict(processed_data, orient='index').sort_index()
    df.index.name = 'Date/Time' if is_daily else 'Date'
    return df

def main():
    id = "227328" # "306756" <-- Tim # Your Plant ID
    monthly_data = []
    daily_data = []

    # Start with monthly data collection
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

    # Process monthly data
    df_monthly = process_data(monthly_data)
    
    # Continue with daily data collection
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

    # Process daily data
    df_daily = process_data(daily_data, True)

    # Export to Excel with two sheets
    excel_filename = "solar_data_history.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        df_monthly.to_excel(writer, sheet_name='Monthly Data')
        df_daily.to_excel(writer, sheet_name='Daily Data')
    print(f"Data exported to {excel_filename}")

if __name__ == "__main__":
    main()