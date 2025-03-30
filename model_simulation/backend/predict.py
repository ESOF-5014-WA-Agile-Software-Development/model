import torch
from model_definition import LSTMPredictor

def load_model(model_path):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    input_size = 3  # Explicitly set to 3 dimensions!
    hidden_size = 64
    num_layers = 2

    model = LSTMPredictor(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    return model, device

def predict_next_hour(model, recent_sequence, device):
    """Predict values for the next hour"""
    with torch.no_grad():
        input_seq = torch.FloatTensor(recent_sequence).unsqueeze(0).to(device)
        prediction = model(input_seq)
        # Ensure return is a 1D array
        return prediction.squeeze().cpu().numpy()

def predict_multiple_hours(model, input_sequence, device, hours=10):
    """Predict values for multiple future hours"""
    model.eval()
    predictions = []
    
    with torch.no_grad():
        current_sequence = input_sequence.copy()
        for _ in range(hours):
            # Predict next hour
            pred = predict_next_hour(model, current_sequence, device)
            predictions.append({
                'P_wind': float(pred[0]),
                'P_solar': float(pred[1]),
                'house_consumption': float(pred[2])
            })
            # Update sequence
            current_sequence = current_sequence[1:] + [list(pred)]
    
    return predictions

import numpy as np

def calculate_trade_action(storage, future_predictions, capacity_max=30.0):
    """
    Aggressive oscillation with:
    - 20-hour forecast window
    - Looser buy/sell thresholds
    - Random noise for simulation volatility
    """
    # Initialize storage projection
    future_storage = [storage]
    confidence_scores = []
    
    # Calculate future storage projections with confidence
    for p in future_predictions:
        # Add uncertainty based on prediction variance
        noise = np.random.normal(0, 0.01)
        delta = p[0] + p[1] - p[2] + noise
        
        # Calculate confidence based on prediction stability
        confidence = 1 - abs(noise)  # Higher confidence for stable predictions
        confidence_scores.append(confidence)
        
        next_val = max(0, min(capacity_max, future_storage[-1] + delta))
        future_storage.append(next_val)
    
    # Calculate key metrics
    min_future = min(future_storage)
    max_future = max(future_storage)
    avg_confidence = np.mean(confidence_scores)
    storage_trend = np.polyfit(range(len(future_storage)), future_storage, 1)[0]
    
    # Dynamic threshold adjustment based on confidence
    confidence_factor = 0.1 + 0.2 * avg_confidence  # 0.1 to 0.3 range
    
    # Risk management thresholds
    risk_threshold = 0.7 * capacity_max
    safety_threshold = 0.3 * capacity_max
    
    # Market trend analysis
    trend_strength = abs(storage_trend) * 10  # Scale trend for decision making
    
    # Trading decision logic
    if storage < safety_threshold and min_future < safety_threshold * 1.2:
        # High confidence buy signal
        if avg_confidence > 0.8:
            buy_amount = min(0.6 * capacity_max - storage, 5)
            return {
                "action": "buy",
                "amount": round(buy_amount, 2),
                "confidence": round(avg_confidence, 2),
                "reason": "Low storage with high confidence"
            }, future_storage
        
        # Moderate confidence buy with trend consideration
        elif avg_confidence > 0.6 and storage_trend < 0:
            buy_amount = min(0.5 * capacity_max - storage, 3)
            return {
                "action": "buy",
                "amount": round(buy_amount, 2),
                "confidence": round(avg_confidence, 2),
                "reason": "Low storage with negative trend"
            }, future_storage
    
    elif storage > risk_threshold and max_future > risk_threshold * 1.1:
        # High confidence sell signal
        if avg_confidence > 0.8:
            sell_amount = min(storage - 0.4 * capacity_max, 5)
            return {
                "action": "sell",
                "amount": round(sell_amount, 2),
                "confidence": round(avg_confidence, 2),
                "reason": "High storage with high confidence"
            }, future_storage
        
        # Moderate confidence sell with trend consideration
        elif avg_confidence > 0.6 and storage_trend > 0:
            sell_amount = min(storage - 0.5 * capacity_max, 3)
            return {
                "action": "sell",
                "amount": round(sell_amount, 2),
                "confidence": round(avg_confidence, 2),
                "reason": "High storage with positive trend"
            }, future_storage
    
    # Hold decision with detailed analysis
    return {
        "action": "hold",
        "amount": 0,
        "confidence": round(avg_confidence, 2),
        "reason": "Stable storage levels or low confidence predictions"
    }, future_storage

