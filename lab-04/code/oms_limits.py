import pandas as pd
import os

def create_oms_limits_files():
    DIR_OMS_DATA = os.path.join("data", "oms")
    os.makedirs(DIR_OMS_DATA, exist_ok=True)
    # Daily (24h or equivalent short-term) guideline values
    daily_data = {
        "pollutant": ["pm25", "pm10", "no2", "o3", "so2", "co"],
        "limit": [15, 45, 25, 100, 40, 3.49],  # units: µg/m³ except CO = ppm
        "units": ["µg/m³", "µg/m³", "µg/m³", "µg/m³", "µg/m³", "ppm"],
    }

    daily_df = pd.DataFrame(daily_data)
    daily_path = os.path.join(DIR_OMS_DATA, "oms_daily_limits.csv")
    daily_df.to_csv(daily_path, index=False, encoding="utf-8-sig")

    # Annual guideline values
    annual_data = {
        "pollutant": ["pm25", "pm10", "no2"],
        "limit": [5, 15, 10],  # units: µg/m³
        "units": ["µg/m³", "µg/m³", "µg/m³"],
    }

    annual_df = pd.DataFrame(annual_data)
    annual_path = os.path.join(DIR_OMS_DATA, "oms_annual_limits.csv")
    annual_df.to_csv(annual_path, index=False, encoding="utf-8-sig")

    return daily_path, annual_path

if __name__ == "__main__":
    daily_file, annual_file = create_oms_limits_files()
    print(f"OMS Daily Limits File Created: {daily_file}")
    print(f"OMS Annual Limits File Created: {annual_file}")
