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

1. **Multi-hour Prediction**
   - Extends predictions to multiple time horizons
   - Provides trend analysis for future consumption
   - Enables long-term planning and optimization

2. **Trading Recommendations**
   - Advanced trading strategy with multiple decision factors:
     - Dynamic threshold adjustment based on prediction confidence
     - Multiple time horizon analysis
     - Risk management and volatility consideration
     - Market trend analysis
   - Confidence-based decision making:
     - High confidence trades (>80% confidence)
     - Moderate confidence trades with trend consideration (>60% confidence)
     - Risk-adjusted position sizing
   - Detailed trade analysis:
     - Action recommendation (buy/sell/hold)
     - Trade amount calculation
     - Confidence score
     - Decision reasoning
   - Risk management features:
     - Safety thresholds for storage levels
     - Maximum trade size limits
     - Trend-based position sizing
     - Volatility-adjusted confidence scoring

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

# Energy Trading System

A real-time energy trading system that uses machine learning to predict energy production and consumption, and provides trading recommendations.

## Features

- Real-time energy monitoring dashboard
- Machine learning-based predictions for:
  - Wind power generation
  - Solar power generation
  - Power consumption
- Storage level analysis
- Automated trading recommendations
- WebSocket-based real-time updates

## Trading Strategy

The system uses a comprehensive trading strategy that considers multiple factors:

1. **Supply-Demand Analysis**
   - Compares total power generation (wind + solar) with total demand
   - Considers current storage levels
   - Evaluates future predictions

2. **Trading Actions**
   - **Buy**: When total generation is less than demand and storage is low
   - **Sell**: When total generation exceeds demand and storage is high
   - **Hold**: When storage levels are sufficient or supply-demand difference is small

3. **Confidence Levels**
   - High confidence (>60%): Clear supply-demand imbalance
   - Low confidence (<60%): Small supply-demand difference
   - Recommendations include confidence percentage

4. **Storage Management**
   - Monitors current storage levels
   - Tracks 24-hour minimum and maximum storage
   - Considers storage capacity (30 kWh)
   - Provides storage percentage utilization

5. **Risk Management**
   - Cautious operation recommended for low confidence scenarios
   - Considers storage buffer for system stability
   - Evaluates multiple time horizons for decision making

## Technical Stack

- Frontend: Next.js, React, TailwindCSS
- Backend: FastAPI, Python
- Machine Learning: PyTorch
- Real-time Communication: WebSocket
- Data Visualization: Recharts

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   # Backend
   cd model_simulation/backend
   pip install -r requirements.txt

   # Frontend
   cd model_simulation/frontend
   npm install
   ```

3. Start the servers:
   ```bash
   # Backend (from model_simulation/backend)
   uvicorn main:app --reload --host 127.0.0.1 --port 8000

   # Frontend (from model_simulation/frontend)
   npm run dev
   ```

4. Access the dashboard at http://localhost:3000

## API Endpoints

- WebSocket: ws://127.0.0.1:8000/ws
- REST API: http://127.0.0.1:8000/docs

## Data Flow

1. Real-time data collection from energy sources
2. ML model predictions for future values
3. Trading strategy analysis
4. WebSocket updates to frontend
5. Real-time visualization updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request