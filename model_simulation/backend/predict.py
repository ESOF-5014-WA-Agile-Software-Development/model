import torch
from model_definition import LSTMPredictor

def load_model(model_path):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    input_size = 3  # ← 明确这里为3维！
    hidden_size = 64
    num_layers = 2

    model = LSTMPredictor(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model, device

def predict_next_hour(model, recent_sequence, device):
    with torch.no_grad():
        input_seq = torch.FloatTensor(recent_sequence).unsqueeze(0).to(device)
        prediction = model(input_seq)
    return prediction.cpu().numpy()


from predict import predict_next_hour
import torch

def predict_multiple_hours(model, recent_sequence, device, hours=24):
    seq = recent_sequence.copy()
    future_predictions = []

    for _ in range(hours):
        pred = predict_next_hour(model, seq, device).flatten().tolist()
        future_predictions.append(pred)
        seq = seq[1:] + [pred]  # 滚动窗口

    return future_predictions

import numpy as np

def calculate_trade_action(storage, future_predictions, capacity_max=30.0):
    """
    Aggressive oscillation with:
    - 20-hour forecast window
    - Looser buy/sell thresholds
    - Random noise for simulation volatility
    """
    future_storage = [storage]
    for p in future_predictions:
        # Add small noise to generation and consumption to simulate uncertainty
        noise = np.random.normal(0, 0.01)  # ±0.01 random fluctuation
        delta = p[0] + p[1] - p[2] + noise
        next_val = max(0, min(capacity_max, future_storage[-1] + delta))
        future_storage.append(next_val)

    min_future = min(future_storage)
    max_future = max(future_storage)

    if storage < 0.6 * capacity_max and min_future < 0.5 * capacity_max:
        buy_amount = min(0.6 * capacity_max - storage, 5)
        return {"action": "buy", "amount": round(buy_amount, 2)}, future_storage

    elif storage > 0.55 * capacity_max and max_future > 0.65 * capacity_max:
        sell_amount = min(storage - 0.4 * capacity_max, 5)
        return {"action": "sell", "amount": round(sell_amount, 2)}, future_storage

    else:
        return {"action": "hold", "amount": 0}, future_storage

