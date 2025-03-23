class EnergyStorage:
    def __init__(self, initial_storage=800):
        self.storage = initial_storage

    def update_storage(self, wind_generation, solar_generation, consumption):
        total_generation = wind_generation + solar_generation
        net_storage_change = total_generation - consumption
        self.storage += net_storage_change

    def purchase_energy(self, amount):
        if self.storage >= amount:
            self.storage -= amount
            return True
        return False
