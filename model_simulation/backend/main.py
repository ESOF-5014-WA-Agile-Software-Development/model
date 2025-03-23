import asyncio
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from predict import load_model, predict_next_hour
from pydantic import BaseModel

app = FastAPI()

storage = {'wind': 500, 'solar': 500}

# 加载数据
data_df = pd.read_csv('data/processed_data_0101_to_1231.csv', index_col=0)
data_records = data_df.to_dict(orient='records')

# 加载模型
model, device = load_model('model/house_consumption_model_3d.pth')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    i = 0
    while True:
        try:
            # 每3秒对应csv数据的一小时数据
            current_data = data_records[i % len(data_records)]
            
            recent_sequence = [list(current_data.values())] * 24  # 简单模拟最近24小时数据
            predicted_values = predict_next_hour(model, recent_sequence, device).flatten().tolist()

            real = {
                "P_wind": current_data['P_wind'],
                "P_solar": current_data['P_solar'],
                "house_consumption": current_data['house_consumption']
            }

            predict = {
                "P_wind": predicted_values[0],
                "P_solar": predicted_values[1],
                "house_consumption": predicted_values[2]
            }

            await websocket.send_json({"real": real, "predict": predict, "storage": storage})
            await asyncio.sleep(3)  # 每3秒更新一次
            i += 1
        except WebSocketDisconnect:
            break
class PurchaseRequest(BaseModel):
    type: str
    amount: float

@app.post('/purchase')
async def purchase_energy(request: PurchaseRequest):
    energy_type = request.type
    amount = request.amount

    if energy_type not in storage:
        return {"success": False, "error": "Invalid energy type.", "storage": storage}

    if storage[energy_type] < amount:
        return {"success": False, "error": "Not enough energy available.", "storage": storage}

    storage[energy_type] -= amount
    return {"success": True, "storage": storage}