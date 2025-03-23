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
