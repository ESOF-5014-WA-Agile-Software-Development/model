import asyncio
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from data_handler import EnergyStorage
from predict import load_model, predict_next_hour, calculate_trade_action, predict_multiple_hours
from pydantic import BaseModel

app = FastAPI()

# 跨域请求支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可在部署时指定具体域名或前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

energy_storage = EnergyStorage(initial_storage=17)

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
    datetime_index = data_df.index if isinstance(data_df.index[0], pd.Timestamp) else pd.date_range('2025-01-01', periods=len(data_records), freq='H')

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

            await websocket.send_json({
                "datetime": now_time.strftime('%Y-%m-%d %H:%M'),
                "real": current_data,
                "predict": {
                    "P_wind": predicted_values[0],
                    "P_solar": predicted_values[1],
                    "house_consumption": predicted_values[2]
                },
                "storage": energy_storage.storage,
                "recommendation": recommendation,
                "future_storages": future_storages[1:]  # drop current
            })

            await asyncio.sleep(1)  # 每秒 = 1小时
            i += 1
        except WebSocketDisconnect:
            break
