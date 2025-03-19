import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os
from house_dataset import HouseConsumptionDataset
from house_model import LSTMPredictor

def load_house_data(data_path, num_houses=20):
    all_data = []
    
    for i in range(1, num_houses + 1):
        file_path = os.path.join(data_path, f'House_{i}.csv')
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['datetime'] = pd.to_datetime(df['Time'])
            df.set_index('datetime', inplace=True)
            hourly_data = df['Aggregate'].resample('H').mean()
            all_data.append(hourly_data)
    
    combined_data = pd.concat(all_data, axis=1)
    combined_data.columns = [f'House_{i+1}' for i in range(len(all_data))]
    return combined_data

def prepare_data(data, seq_length=24, train_split=0.8):
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)
    
    # Create train/test splits
    train_size = int(len(scaled_data) * train_split)
    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size:]
    
    # Create datasets
    train_dataset = HouseConsumptionDataset(train_data, seq_length)
    test_dataset = HouseConsumptionDataset(test_data, seq_length)
    
    return train_dataset, test_dataset, scaler

def train_model(model, train_loader, test_loader, criterion, optimizer, 
                num_epochs, device):
    for epoch in range(num_epochs):
        model.train()
        train_loss = 0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch_x, batch_y in test_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                outputs = model(batch_x)
                val_loss += criterion(outputs, batch_y).item()
        
        print(f'Epoch [{epoch+1}/{num_epochs}], '
              f'Train Loss: {train_loss/len(train_loader):.4f}, '
              f'Val Loss: {val_loss/len(test_loader):.4f}')

if __name__ == "__main__":
    # Parameters
    DATA_PATH = "D:/dataset/Processed_Data_CSV"
    SEQ_LENGTH = 24
    HIDDEN_SIZE = 64
    NUM_LAYERS = 2
    BATCH_SIZE = 32
    NUM_EPOCHS = 50
    LEARNING_RATE = 0.001
    
    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load and prepare data
    data = load_house_data(DATA_PATH)
    train_dataset, test_dataset, scaler = prepare_data(data, SEQ_LENGTH)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)
    
    # Initialize model
    model = LSTMPredictor(
        input_size=data.shape[1],
        hidden_size=HIDDEN_SIZE,
        num_layers=NUM_LAYERS
    ).to(device)
    
    # Define loss function and optimizer
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    # Train model
    train_model(model, train_loader, test_loader, criterion, optimizer, 
                NUM_EPOCHS, device)
    
    # Save model
    torch.save(model.state_dict(), 'house_consumption_model.pth')