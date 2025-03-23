import pandas as pd

def load_initial_data(csv_path):
    data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    return data

class EnergyStorage:
    def __init__(self, initial_wind=500, initial_solar=500):
        self.wind_storage = initial_wind
        self.solar_storage = initial_solar

    def update_storage(self, wind_generation, solar_generation, consumption):
        self.wind_storage += wind_generation - consumption
        self.solar_storage += solar_generation - consumption
        self.wind_storage = max(self.wind_storage, 0)
        self.solar_storage = max(self.solar_storage, 0)

    def purchase_energy(self, amount):
        total_storage = self.wind_storage + self.solar_storage
        if total_storage >= amount:
            if self.wind_storage >= amount:
                self.wind_storage -= amount
            else:
                remaining = amount - self.wind_storage
                self.wind_storage = 0
                self.solar_storage -= remaining
            return True
        return False
