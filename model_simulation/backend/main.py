import asyncio
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from data_handler import EnergyStorage
from predict import load_model, predict_next_hour, calculate_trade_action, predict_multiple_hours
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage
initial_storage = 5  # Initial storage per household 5 kWh
battery_capacity = 30  # Battery capacity 30 kWh

energy_storage = EnergyStorage(initial_storage=initial_storage)

data_df = pd.read_csv('data/processed_data_0101_to_1231.csv', index_col=0)
data_records = data_df.to_dict(orient='records')

model, device = load_model('model/house_consumption_model_3d.pth')

class PurchaseRequest(BaseModel):
    type: str
    amount: float

@app.post('/purchase')
async def purchase_energy(request: PurchaseRequest):
    success = energy_storage.purchase_energy(request.amount)
    return {
        "success": success, 
        "storage": energy_storage.storage
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    i = 0
    datetime_index = data_df.index if isinstance(data_df.index[0], pd.Timestamp) else pd.date_range('2025-01-01', periods=len(data_records), freq='h')

    while True:
        try:
            current_data = data_records[i % len(data_records)]
            now_time = datetime_index[i % len(datetime_index)]

            recent_sequence = [list(current_data.values())] * 24
            predicted_values = predict_next_hour(model, recent_sequence, device).flatten().tolist()

            energy_storage.update_storage(
                wind_generation=current_data['P_wind'],
                solar_generation=current_data['P_solar'],
                consumption=current_data['house_consumption']
            )

            future_predictions = predict_multiple_hours(model, recent_sequence, device, hours=10)
            recommendation, future_storages = calculate_trade_action(energy_storage.storage, future_predictions)

            # Calculate storage statistics
            storage_stats = {
                "current": energy_storage.storage,
                "min_24h": min(future_storages),
                "max_24h": max(future_storages)
            }

            await websocket.send_json({
                "datetime": now_time.strftime('%Y-%m-%d %H:%M'),
                "real": current_data,
                "predict": {
                    "P_wind": predicted_values[0],
                    "P_solar": predicted_values[1],
                    "house_consumption": predicted_values[2]
                },
                "storage": energy_storage.storage,
                "recommendation": {
                    **recommendation,
                    "storage_stats": storage_stats
                },
                "future_storages": future_storages[1:]  # drop current
            })

            await asyncio.sleep(1)  # 1 second = 1 hour
            i += 1
        except WebSocketDisconnect:
            break

def calculate_trade_action(current_storage, future_predictions):
    """Calculate trading recommendations"""
    # Calculate maximum and minimum storage for next 24 hours
    future_storages = [current_storage]
    
    # Calculate supply and demand balance
    total_supply = 0
    total_demand = 0
    
    for pred in future_predictions:
        if isinstance(pred, dict):
            # Power generation
            total_supply += pred.get('P_wind', 0) + pred.get('P_solar', 0)
            # Power demand
            total_demand += pred.get('house_consumption', 0)
            # Calculate storage change
            storage_change = pred.get('P_wind', 0) + pred.get('P_solar', 0) - pred.get('house_consumption', 0)
            future_storages.append(max(0, min(30, current_storage + storage_change)))
    
    min_future = min(future_storages)
    max_future = max(future_storages)
    
    # Calculate confidence, avoid division by zero
    total = total_supply + total_demand
    if total == 0:
        confidence = 0.3  # Use minimum confidence when supply and demand are both 0
    else:
        confidence = min(0.95, max(0.3, abs(total_supply - total_demand) / total))
    
    # Determine trading direction based on supply and demand
    if total_supply > total_demand:
        # Supply exceeds demand, consider selling
        if current_storage > 15:  # Storage above 50%
            amount = min(5, current_storage - 10)  # Sell up to 5kWh, maintain at least 10kWh
            action = 'sell'
            reason = f"Total power generation ({total_supply:.1f}kWh) exceeds total demand ({total_demand:.1f}kWh), and current storage ({current_storage:.1f}kWh) is high. Recommend selling {amount:.1f}kWh to balance supply and demand"
        else:
            action = 'hold'
            amount = 0
            reason = f"Although total power generation ({total_supply:.1f}kWh) exceeds total demand ({total_demand:.1f}kWh), current storage ({current_storage:.1f}kWh) is low. Recommend holding"
    else:
        # Demand exceeds supply, consider buying
        if current_storage < 15:  # Storage below 50%
            amount = min(5, 30 - current_storage)  # Buy up to 5kWh, don't exceed capacity
            action = 'buy'
            reason = f"Total power generation ({total_supply:.1f}kWh) is less than total demand ({total_demand:.1f}kWh), and current storage ({current_storage:.1f}kWh) is low. Recommend buying {amount:.1f}kWh to meet demand"
        else:
            action = 'hold'
            amount = 0
            reason = f"Although total power generation ({total_supply:.1f}kWh) is less than total demand ({total_demand:.1f}kWh), current storage ({current_storage:.1f}kWh) is sufficient. Recommend holding"
    
    # Add additional note for low confidence
    if confidence < 0.6:
        reason += f". Due to small supply-demand difference, prediction confidence is low. Recommend cautious operation"
    
    return {
        "action": action,
        "amount": amount,
        "confidence": confidence,
        "reason": reason
    }, future_storages
