# House Energy Consumption Prediction Model

This project focuses on predicting house energy consumption using three key parameters through a Long Short-Term Memory (LSTM) neural network. The model provides real-time predictions and interactive visualization through a web application interface.

## Demo
Watch the demo video: [House Energy Consumption Prediction Demo](https://www.youtube.com/watch?v=cDp7dxbFAkM)

![House Energy Consumption Prediction Demo](https://i.ytimg.com/vi/cDp7dxbFAkM/maxresdefault.jpg)

The demo showcases:
- Real-time energy consumption prediction
- Interactive parameter adjustment
- Live visualization of predictions
- Historical data comparison

## Project Structure

```
.
├── model_simulation/           # Web application for model simulation
│   ├── backend/               # FastAPI backend server
│   └── frontend/              # React frontend application
├── house_dataset.py           # Dataset handling and preprocessing
├── house_model.py             # Model architecture definition
├── house_prediction.py        # Prediction and inference logic
├── house_consumption_model_3d.pth  # Trained model weights
├── preprocess.py              # Data preprocessing utilities
└── train_3d_model.py         # Model training script
```

## Contents
* Overview
* Model Architecture
* Data Preprocessing and Model Building
* Web Application
* Getting Started
* Usage
* Future Improvements

## Overview

This project implements a simplified and efficient approach to house energy consumption prediction by focusing on three key parameters. The model uses LSTM architecture to capture temporal dependencies and patterns in energy consumption data.

## Model Architecture

The LSTM-based model architecture consists of:

- **Input Layer**: Processes three key parameters for house energy consumption prediction
- **LSTM Layers**: Multiple LSTM layers with dropout for capturing temporal dependencies
- **Output Layer**: Linear layer for generating predictions

Key features of the model:
- Simplified from 20 parameters to 3 key parameters for focused prediction
- Captures long-term dependencies in energy consumption patterns
- Uses dropout regularization to prevent overfitting
- Processes data in sequence format (batch_size, sequence_length, 3 parameters)

## Data Preprocessing and Model Building

The project implements a comprehensive data processing and model building pipeline:

### Data Processing Components
1. **house_dataset.py**
   - Handles dataset loading and organization
   - Implements data splitting for training and validation
   - Manages data batching for model training

2. **preprocess.py**
   - Implements data normalization using MinMaxScaler
   - Handles feature selection and parameter reduction
   - Prepares sequences for LSTM input
   - Performs data validation and cleaning

3. **house_model.py**
   - Defines the LSTM model architecture
   - Implements the neural network layers
   - Handles model initialization and configuration

4. **house_prediction.py**
   - Manages real-time prediction pipeline
   - Handles model inference and data processing
   - Implements prediction optimization functions

## Web Application

The web application provides an interactive interface for simulating and visualizing energy consumption predictions:

### Features
- Real-time energy consumption prediction based on three parameters
- Interactive visualization of consumption patterns
- Historical data comparison
- Parameter adjustment for different house characteristics
- Real-time updates using WebSocket connections
- Multi-hour prediction visualization
- Trading recommendation dashboard

### Technical Implementation
- **Backend**: FastAPI server handling model inference and data processing
- **Frontend**: React application with Recharts for data visualization
- **Real-time Updates**: WebSocket integration for live data streaming
- **Data Processing**: MinMaxScaler for feature normalization
- **Trading Logic**: Integration of prediction-based trading recommendations

### Application Functions
The model simulation includes additional optimization functions:

### Confidence Assessment
Evaluates prediction reliability by incorporating random noise to simulate realistic forecast volatility, quantifying confidence as a function of prediction stability:

![Confidence Formula](https://latex.codecogs.com/svg.image?\epsilon\sim&space;N(0,&space;0.01^2),\quad\text{Confidence}=1-|\epsilon|)

### Storage Projections
Simulates future energy storage conditions by accounting for predicted power generation and consumption, storage capacity constraints, and forecast uncertainties:

![Storage Projection Formula](https://latex.codecogs.com/svg.image?\text{FutureStorage}_{t+1}=\min\left(C_{max},\max\left(0,\text{Storage}_{t}+(P_{wind,t}+P_{solar,t}-C_{house,t}+\epsilon)\right)\right),\quad&space;C_{max}=30.0\,\text{kWh})


### Risk Management Thresholds
Defines clear operational thresholds for maintaining system stability and resource allocation:

![Risk Management Thresholds](https://latex.codecogs.com/svg.image?\text{Risk&space;threshold}=0.7\times&space;C_{max},\quad\text{Safety&space;threshold}=0.3\times&space;C_{max})

### Market Trend Analysis
Uses linear regression trend analysis derived from storage projections to reinforce trading decisions, allowing responsive adjustments to emerging market conditions:

![Market Trend Analysis](https://latex.codecogs.com/svg.image?\text{StorageTrend}=\text{slope}\left(\text{Storage}_{t:t+n}\right))


## Getting Started

### Prerequisites
- Python 3.x
- Node.js and npm
- Required Python packages (see requirements.txt)

### Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Train the model:
```bash
python model.py
```

4. Start the web application:
```bash
# Start backend
cd model_simulation/backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Start frontend (in a new terminal)
cd model_simulation/frontend
npm install axios socket.io-client recharts
npm run dev
```

## Usage

1. Access the web application at `http://localhost:3000`
2. The backend API will be running at `http://127.0.0.1:8000`
3. Use the web interface to:
   - **Storage Monitoring**
     - View current hour storage levels
     - Compare with 24-hour minimum and maximum storage values
     - Track storage trends over time
   
   - **Energy Trading Recommendations**
     - Get real-time sell/buy/hold recommendations
     - View recommendation confidence levels
     - Access historical trading performance
   
   - **Consumption Analysis**
     - Compare predicted vs actual values for:
       - Wind energy generation (kWh)
       - Solar energy generation (kWh)
       - Personal consumption (kWh)


## Future Improvements

* **Additional Parameters**: Explore the impact of adding more parameters while maintaining model efficiency
* **Advanced Visualization**: Implement more sophisticated data visualization techniques
* **Model Optimization**: Further optimize the LSTM architecture for better performance
* **Real-time Monitoring**: Add real-time monitoring capabilities for continuous prediction
* **API Integration**: Enable integration with external energy monitoring systems

## Technical Stack

- Frontend: Next.js, React, TailwindCSS
- Backend: FastAPI, Python
- Machine Learning: PyTorch
- Real-time Communication: WebSocket
- Data Visualization: Recharts
