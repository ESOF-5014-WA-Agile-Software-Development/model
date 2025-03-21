import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os

# Convert wind speed to power using the formula
def wind_to_power(V):
    """
    Calculate wind turbine power output based on the provided chart.

    Parameters:
        V (float or np.array): Wind speed in m/s.

    Returns:
        P (float or np.array): Power output in kW.
    """
    # Data points from the chart
    wind_speeds = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
    power_outputs = np.array([0, 0, 0, 0.25, 0.8, 1.65, 2.55, 3.65, 4.85, 6.15, 7.5, 9, 9.5, 10, 8, 6, 2.7, 3, 3, 3, 3, 3, 3, 3, 3])

    # Handle single values or arrays
    if isinstance(V, (int, float)):
        if V < 1 or V > 25:
            return 0
        else:
            return np.interp(V, wind_speeds, power_outputs)
    else:
        # For arrays, clip values outside the range and interpolate
        V = np.clip(V, 1, 25)
        return np.interp(V, wind_speeds, power_outputs)

def dni_to_power(dni, efficiency=0.2, area=100):
    """
    Convert DNI to solar power output.
    
    Parameters:
        dni (float): Direct Normal Irradiance in W/m2
        efficiency (float): Solar panel efficiency (default 20%)
        area (float): Solar panel area in m2
    
    Returns:
        float: Power output in kW
    """
    return dni * efficiency * area / 1000

# Load and process solar data
solar_data = pd.read_csv('D:/dataset/solardata/1216837_46.81_-74.86_tdy-2022.csv', skiprows=2)
solar_data['datetime'] = pd.to_datetime({
    'year': 2014,
    'month': solar_data['Month'],
    'day': solar_data['Day'],
    'hour': solar_data['Hour'],
    'minute': solar_data['Minute']
})
solar_data.set_index('datetime', inplace=True)

# Calculate solar power and resample to hourly averages
solar_data['P_solar'] = solar_data['DNI'].apply(dni_to_power)
hourly_solar = solar_data['P_solar'].resample('h').mean()

print(f"Solar data shape: {hourly_solar.shape}")

# Load and process wind data
wind_data = pd.read_csv('D:\dataset\winddata\wind_2018.csv', skiprows=1)
wind_data['datetime'] = pd.to_datetime(wind_data[['Year', 'Month', 'Day', 'Hour']])
wind_data.set_index('datetime', inplace=True)

# Convert wind speed to power and resample to hourly averages
wind_data['P_wind'] = wind_data['wind speed at 10m (m/s)'].apply(wind_to_power)
hourly_wind = wind_data['P_wind'].resample('h').mean()

print(f"Wind data shape: {hourly_wind.shape}")

# Load house consumption data
house_data = pd.read_csv('D:/dataset/Processed_Data_CSV/House_1.csv')
house_data['datetime'] = pd.to_datetime(house_data['Time'])

# Filter data for the year 2014
start_date = pd.Timestamp('2014-01-01')
end_date = pd.Timestamp('2015-01-01')
house_data = house_data[(house_data['datetime'] >= start_date) & 
                       (house_data['datetime'] < end_date)]

house_data.set_index('datetime', inplace=True)

# Resample house data to hourly averages
hourly_house = house_data['Aggregate'].resample('h').mean()

print(f"House data shape: {hourly_house.shape}")

# Normalize all datasets
scaler_wind = MinMaxScaler()
scaler_solar = MinMaxScaler()
scaler_house = MinMaxScaler()

hourly_wind_normalized = scaler_wind.fit_transform(hourly_wind.values.reshape(-1, 1))
hourly_solar_normalized = scaler_solar.fit_transform(hourly_solar.values.reshape(-1, 1))
hourly_house_normalized = scaler_house.fit_transform(hourly_house.values.reshape(-1, 1))

print(f"Normalized wind shape: {hourly_wind_normalized.shape}")
print(f"Normalized solar shape: {hourly_solar_normalized.shape}")
print(f"Normalized house shape: {hourly_house_normalized.shape}")

# Convert back to series with datetime index
hourly_wind_normalized = pd.Series(hourly_wind_normalized.flatten(), index=hourly_wind.index)
hourly_solar_normalized = pd.Series(hourly_solar_normalized.flatten(), index=hourly_solar.index)
hourly_house_normalized = pd.Series(hourly_house_normalized.flatten(), index=hourly_house.index)

# Align all data to the same year
hourly_wind_normalized.index = hourly_wind_normalized.index.map(lambda x: x.replace(year=2014))

print(f"Wind data range: {hourly_wind_normalized.index.min()} to {hourly_wind_normalized.index.max()}")
print(f"Solar data range: {hourly_solar_normalized.index.min()} to {hourly_solar_normalized.index.max()}")
print(f"House data range: {hourly_house_normalized.index.min()} to {hourly_house_normalized.index.max()}")

# Combine all datasets
combined_data = pd.concat([hourly_wind_normalized, hourly_solar_normalized, hourly_house_normalized], axis=1)
combined_data.columns = ['P_wind', 'P_solar', 'house_consumption']
combined_data.dropna(inplace=True)

print(f"Combined data shape: {combined_data.shape}")

# Create output directory if it doesn't exist
output_dir = 'D:/dataset/output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create output filename with descriptive information
start_date_str = start_date.strftime('%m%d')
end_date_str = (start_date + pd.DateOffset(years=1) - pd.DateOffset(days=1)).strftime('%m%d')
output_filename = f'processed_data_{start_date_str}_to_{end_date_str}.csv'
output_file = os.path.join(output_dir, output_filename)
combined_data.to_csv(output_file)

print(f"Data saved to: {output_file}")