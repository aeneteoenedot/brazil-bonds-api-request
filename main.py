import requests
"""
This module provides functionality to authenticate and fetch data from the ANBIMA API, specifically for retrieving and analyzing secondary market prices of public government bonds. It includes:
Classes:
    anbima_api: Handles authentication (token management) and data retrieval from the ANBIMA API.
Functions:
    volatility(df, asset_tp): Calculates the annualized volatility of a specified asset type using the standard deviation of daily log-returns from indicative rates.
    main(): Orchestrates the process of fetching data for a range of business days, compiling it into a DataFrame, and computing volatility for a specific asset type.
Usage:
    - The script uses a credentials file (JSON) to manage API authentication.
    - It leverages the 'bizdays' library to handle business day calculations using the ANBIMA calendar.
    - Data is fetched for a specified range of business days and analyzed for volatility.
    - The script is designed for both sandbox and production environments of the ANBIMA API.
Note:
    The ANBIMA API sandbox environment returns static data for all dates, so volatility calculations will yield zero. The code is structured for use with the production environment, where real data will provide meaningful results.
"""
import pandas as pd
import json
from datetime import datetime
from dateutil import parser
from bizdays import Calendar
import numpy as np

# This class is responsible for managing the authentication and fetching of data from the ANBIMA API.
# For more information on the API, please refer to https://developers.anbima.com.br/en/
class anbima_api:
    def __init__(self, token_file):
        self.token_file = token_file
        self.token = None

    def generate_token(self):
        global client_id
        # Try to reuse token if not expired
        try:
            with open(self.token_file, 'r') as file:
                credentials = json.load(file)
                client_id = credentials['client_id']
                client_secret = credentials['client_secret']
                token_info = credentials.get('token_info', {})
                access_token = token_info.get('access_token')
                expires_at = token_info.get('expires_at')
                now = datetime.utcnow().timestamp()
            if access_token and expires_at and now < expires_at:
                self.token = access_token
                return
        except Exception:
            pass  # Ignore and fetch new token

        # Fetch new token
        token_url = "https://api.anbima.com.br/oauth/access-token"
        payload = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(token_url, data=payload, verify=True, allow_redirects=False, auth=(client_id, client_secret))
        if response.status_code in (200, 201):
            data = response.json()
            self.token = data.get('access_token')
            expires_in = data.get('expires_in', 3600)
            # Save token and expiry to file
            credentials['token_info'] = {
                                        'access_token': self.token,
                                        'expires_at': datetime.utcnow().timestamp() + expires_in - 60  # 60s buffer
                                        }
            with open(self.token_file, 'w') as file:
                json.dump(credentials, file)
        else:
            raise Exception(f"Failed to generate token: {response.status_code} {response.text}")

    def get_data_by_date(self, url, date):
        if not self.token:
            raise Exception("Token is not generated. Call generate_token() first.")
        headers = {
            'client_id': client_id,
            'access_token': self.token,
            'Content-Type': 'application/json'
        }
        url_request = url + f'?data={date}'
        response = requests.get(url_request, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code} {response.text}")

def volatility(df, asset_tp):
    # Calculate the volatility of the asset using the standard deviation of the daily log-returns.
    # The daily log-returns are calculated using the "Indicative Rate" column (Taxas Indicativas), it is preferable to use the log-returns instead of simple returns for financial data, given the lack of symmetry in the return distribution.
    # The asset_tp parameter will be used to filter the dataframe for the specific asset type.
    df = df[df['tipo_titulo'] == asset_tp]
    sigma = {}
    for maturity in df['data_vencimento'].unique():
        sigma[str(maturity)] = float(df.query("data_vencimento == @maturity")['taxa_indicativa'].astype(float).apply(lambda x: np.log(1 + x / 100)).diff().std() * np.sqrt(252))
    # The standard deviation is multiplied by the square root of 252 to annualize the volatility.
    # This is a common practice in finance to convert daily volatility to annual volatility.
    return sigma


def main():
    # Define the base URL for the ANBIMA API endpoint we desire to access.
    # In this case, we are interested in the secondary market prices of public government bonds.
    # The URL is defined as a constant for example purposes.
    url_request = "https://api-sandbox.anbima.com.br/feed/precos-indices/v1/titulos-publicos/mercado-secundario-TPF"
    # Initialize Class anbima_api with the token file.
    api = anbima_api(token_file)
    # Generate the token using the credentials stored in the token file.
    api.generate_token()
    # Fetch data for a range of dates using the ANBIMA API.
    # The date format is YYYY-MM-DD.
    for date in cal.seq(cal.offset(datetime.today(),-bdays_range), datetime.today()):
        datetime_str = date.strftime('%Y-%m-%d')
        # Fetch data for the given date, and generate a dataframe for further processing. 
        data = api.get_data_by_date(url_request, datetime_str)
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])
        df['data_referencia'] = datetime_str
        if 'result_df' not in locals():
            result_df = df
        else:
            result_df = pd.concat([result_df, df], ignore_index=True)
    result = volatility(result_df, 'LTN')
    print(result)
    # Unfortunately, the ANBIMA API sandbox environment returns the same information for all dates, therefore volatility will be 0 for all dates.
    # However, the code have the production environment in mind and is ready to be used.
    # The volatility information is just one of many possible analyses that can be realized with the data retreived from the ANBIMA API.
    # It could be interesting to analyse the correlation between the the indicative rates of different asset types, or the maturities of the same asset type.


if __name__ == '__main__':
    # Here we are going to define a date range to retrieve data from ANBIMA public government bond prices using bizdays.
    # The use of bizdays is justified for already containing the ANBIMA calendar for banking holidays in Brazil.
    cal = Calendar.load("ANBIMA")
    bdays_range = 10 # Number of business days to offset.
    # Define the authentication file that will manage client_id and client_secret, aswell as store used tokens that are still valid for recycling.
    token_file = 'anbimaAuth.json'
    main()

