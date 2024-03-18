# Sunsynk Solar Data Fetcher

This Python script automates the process of fetching solar energy production and consumption data from the Sunsynk API, processes it, and exports the data into an Excel file with separate sheets for monthly and daily data.

## Features

- **Authentication**: Securely logs in to the Sunsynk API to retrieve a bearer token for authenticated requests.
- **Data Collection**: Fetches both monthly and daily solar energy data.
- **Data Processing**: Organizes the fetched data into a structured format.
- **Excel Export**: Exports the processed data into an Excel file, with separate tabs for monthly and daily statistics.

## Prerequisites

Before you can run the script, ensure you have Python installed on your system. This script has been tested with Python 3.8+.

You will also need to install the following Python libraries:

- `requests`
- `pandas`
- `python-dotenv`
- `openpyxl`

You can install these with the following command:

```bash
pip install requests pandas python-dotenv openpyxl
```

## Setup

1. Clone this repository to your local machine.
2. Copy the `.env.example` file to a new file named `.env` in the same directory.
    ```bash
    cp .env.example .env
    ```
3. Open the `.env` file and update it with your Sunsynk credentials.
    - USERNAME: Your Sunsynk username (email).
    - PASSWORD: Your Sunsynk password.

## Running the Script

To run the script, navigate to the project directory in your terminal and execute:

```bash
python sunsynk.py
```

The script will authenticate with the Sunsynk API, fetch the requested data, process it, and finally export it to an Excel file named `solar_data_history.xlsx` in the project directory.

## Output

The output Excel file will contain two sheets:

- `Monthly Data`: Shows solar energy data aggregated by month.
- `Daily Data`: Contains detailed daily energy data, including production and consumption at different times of the day.

## Security Note

This script uses environment variables to securely handle your Sunsynk credentials. Never hard-code your credentials in the script or commit them to a public repository.

## Contributing

Contributions to improve the script are welcome. Please feel free to fork the repository, make your changes, and submit a pull request.

## License

This project is open source and available under the [MIT License](LICENSE).
