# ANBIMA Public Bonds Volatility Analyzer

This Python module connects to the **ANBIMA API** to retrieve secondary market prices for **Brazilian public government bonds**, processes the data over a specified range of business days, and calculates **annualized volatility** for selected asset types.

It is designed for analysts, economists, and developers who want to analyze historical price behavior and volatility of government securities using real-time or sandboxed ANBIMA data.

---

## Features

- 🔐 **Token-Based Authentication**  
  Automatically manages API tokens using a local JSON credentials file (`anbimaAuth.json`).

- 📈 **Volatility Calculation**  
  Computes annualized volatility using daily log-returns of indicative interest rates.

- 📅 **Business Day Range Handling**  
  Uses the ANBIMA calendar to ensure only valid business days are included in the analysis.

- 🧪 **Sandbox & Production Ready**  
  Compatible with both ANBIMA sandbox and production environments. Note: The sandbox returns static data, so volatility will be zero.

---

## How It Works

1. Authenticates with the ANBIMA API using `client_id` and `client_secret`.
2. Fetches daily bond pricing data from the endpoint: "/feed/precos-indices/v1/titulos-publicos/mercado-secundario-TPF"
3. Compiles the data into a single DataFrame.
4. Filters by asset type (e.g., `LTN`) and computes the **annualized volatility** using the standard deviation of daily log-returns.
5. Prints the volatility per bond maturity date.

---

## Usage

### 1. Requirements

Install dependencies:
```bash
pip install pandas requests numpy python-dateutil bizdays
```

### 2. Set Up Credentials
```bash
{
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
}
```

### 3. API Documentation
Full API documentation: https://developers.anbima.com.br
