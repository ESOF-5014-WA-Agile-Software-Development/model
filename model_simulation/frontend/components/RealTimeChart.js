'use client';
import { useEffect, useState } from 'react';
import { AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function RealTimeChart() {
  const [data, setData] = useState([]);
  const [selected, setSelected] = useState('wind');
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    // Update time every second
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString('en-US', { 
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      }));
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    let socket = null;
    let reconnectTimeout = null;

    const connectWebSocket = () => {
      socket = new WebSocket('ws://127.0.0.1:8000/ws');
      
      socket.onopen = () => {
        console.log('WebSocket connected successfully');
      };
      
      socket.onmessage = (event) => {
        try {
          const receivedData = JSON.parse(event.data);
          setData(prevData => [
            ...prevData.slice(-20),
            {
              timestamp: new Date().toLocaleTimeString(),
              storage: receivedData.storage || 0,
              real_wind: receivedData.real?.P_wind || 0,
              real_solar: receivedData.real?.P_solar || 0,
              real_consumption: receivedData.real?.house_consumption || 0,
              predict_wind: receivedData.predict?.P_wind || 0,
              predict_solar: receivedData.predict?.P_solar || 0,
              predict_consumption: receivedData.predict?.house_consumption || 0,
              datetime: receivedData.datetime,
              action: receivedData.recommendation?.action || 'hold',
              amount: receivedData.recommendation?.amount || 0,
              confidence: receivedData.recommendation?.confidence || 0,
              reason: receivedData.recommendation?.reason || 'Waiting for data...',
              min_future_storage: receivedData.future_storages ? Math.min(...receivedData.future_storages) : 0,
              max_future_storage: receivedData.future_storages ? Math.max(...receivedData.future_storages) : 0,
              storage_stats: receivedData.recommendation?.storage_stats || {
                current: 0,
                min_24h: 0,
                max_24h: 0
              }
            }
          ]);
        } catch (error) {
          console.error('Error processing WebSocket message:', error);
        }
      };
      
      socket.onclose = () => {
        console.log('WebSocket disconnected. Attempting to reconnect...');
        if (reconnectTimeout) {
          clearTimeout(reconnectTimeout);
        }
        reconnectTimeout = setTimeout(() => {
          if (socket.readyState === WebSocket.CLOSED) {
            connectWebSocket();
          }
        }, 5000);
      };
      
      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    };

    connectWebSocket();

    return () => {
      if (socket) {
        socket.close();
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
      }
    };
  }, []);

  const handleChange = (e) => {
    setSelected(e.target.value);
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'buy': return 'text-green-600';
      case 'sell': return 'text-red-600';
      case 'hold': return 'text-yellow-600';
      default: return 'text-gray-600';
    }
  };

  const latestData = data[data.length - 1] || {
    action: 'hold',
    amount: 0,
    confidence: 0,
    reason: 'Waiting for data...',
    storage_stats: {
      current: 0,
      min_24h: 0,
      max_24h: 0
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">MyEnergy Dashboard</h1>
          <p className="text-gray-600 mt-2">Real-time energy monitoring and trading insights</p>
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Charts */}
          <div className="lg:col-span-2 space-y-6">
            {/* Storage Chart Card */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Storage Level Analysis</h2>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={data}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0"/>
                  <XAxis dataKey="datetime" stroke="#666"/>
                  <YAxis stroke="#666"/>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '0.5rem',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Legend 
                    wrapperStyle={{ 
                      paddingTop: '1rem',
                      fontSize: '0.875rem'
                    }}
                  />
                  <Area type="monotone" dataKey="storage" stroke="#3b82f6" fill="#3b82f6" name="Current Storage"/>
                  <Area type="monotone" dataKey="storage_stats.min_24h" stroke="#f97316" fill="#f97316" name="Min Storage (24h)" opacity={0.3}/>
                  <Area type="monotone" dataKey="storage_stats.max_24h" stroke="#22c55e" fill="#22c55e" name="Max Storage (24h)" opacity={0.3}/>
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Energy Data Chart Card */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-900">Energy Production & Consumption</h2>
                <select 
                  value={selected} 
                  onChange={handleChange} 
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="wind">Wind Power</option>
                  <option value="solar">Solar Power</option>
                  <option value="consumption">Power Consumption</option>
                </select>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="realColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="predictColor" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0"/>
                  <XAxis dataKey="datetime" stroke="#666"/>
                  <YAxis stroke="#666"/>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'white', 
                      border: '1px solid #e5e7eb',
                      borderRadius: '0.5rem',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Legend 
                    wrapperStyle={{ 
                      paddingTop: '1rem',
                      fontSize: '0.875rem'
                    }}
                  />
                  <Area type="monotone" dataKey={`real_${selected}`} stroke="#3b82f6" fillOpacity={1} fill="url(#realColor)" name={`Real ${selected}`} />
                  <Area type="monotone" dataKey={`predict_${selected}`} stroke="#22c55e" fillOpacity={1} fill="url(#predictColor)" name={`Predict ${selected}`} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Right Column - Stats */}
          <div className="space-y-6">
            {/* Trading Recommendation Card */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Trading Recommendation</h2>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">Last Updated:</span>
                  <span className="text-sm font-medium text-gray-900">
                    {currentTime}
                  </span>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="py-3 px-4 text-sm text-gray-600 whitespace-nowrap">Action:</td>
                      <td className="py-3 px-4 text-right">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          data[data.length - 1]?.action === 'buy' ? 'bg-green-100 text-green-800' :
                          data[data.length - 1]?.action === 'sell' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {data[data.length - 1]?.action.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <td className="py-3 px-4 text-sm text-gray-600 whitespace-nowrap">Amount:</td>
                      <td className="py-3 px-4 text-right font-semibold text-gray-900 whitespace-nowrap">
                        {data[data.length - 1]?.amount.toFixed(1)} kWh
                      </td>
                    </tr>
                    <tr>
                      <td className="py-3 px-4 text-sm text-gray-600 whitespace-nowrap">Confidence:</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full ${
                                data[data.length - 1]?.confidence < 0.6 ? 'bg-red-500' : 'bg-green-500'
                              }`}
                              style={{ width: `${(data[data.length - 1]?.confidence * 100)}%` }}
                            />
                          </div>
                          <span className={`font-semibold whitespace-nowrap ${
                            data[data.length - 1]?.confidence < 0.6 ? 'text-red-600' : 'text-green-600'
                          }`}>
                            {(data[data.length - 1]?.confidence * 100).toFixed(0)}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-100">
                <div className="flex items-center justify-between mb-2 h-[24px]">
                  <h3 className="text-sm font-medium text-gray-600">Reason:</h3>
                  <span className="text-xs text-gray-500 whitespace-nowrap">Last Updated: {currentTime}</span>
                </div>
                <div className="bg-white p-3 rounded-md border border-gray-200 h-[120px] w-full overflow-y-auto">
                  <div className="h-full w-full flex items-start">
                    <div className="w-full">
                      <p className="text-sm text-gray-700 leading-relaxed break-words">{data[data.length - 1]?.reason}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Storage Statistics Card */}
            <div className="bg-white rounded-xl shadow-sm p-6 mt-8">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Storage Statistics</h2>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">Capacity:</span>
                  <span className="text-sm font-medium text-gray-900">30 kWh</span>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="py-3 px-4 text-sm text-gray-600 whitespace-nowrap">Current Storage:</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2 whitespace-nowrap">
                          <span className="font-semibold text-gray-900">
                            {data[data.length - 1]?.storage_stats.current.toFixed(1)} kWh
                          </span>
                          <span className="text-sm text-gray-500">
                            ({((data[data.length - 1]?.storage_stats.current / 30) * 100).toFixed(1)}%)
                          </span>
                        </div>
                      </td>
                    </tr>
                    <tr>
                      <td className="py-3 px-4 text-sm text-gray-600 whitespace-nowrap">24h Minimum:</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2 whitespace-nowrap">
                          <span className="font-semibold text-gray-900">
                            {data[data.length - 1]?.storage_stats.min_24h.toFixed(1)} kWh
                          </span>
                          <span className="text-sm text-gray-500">
                            ({((data[data.length - 1]?.storage_stats.min_24h / 30) * 100).toFixed(1)}%)
                          </span>
                        </div>
                      </td>
                    </tr>
                    <tr>
                      <td className="py-3 px-4 text-sm text-gray-600 whitespace-nowrap">24h Maximum:</td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2 whitespace-nowrap">
                          <span className="font-semibold text-gray-900">
                            {data[data.length - 1]?.storage_stats.max_24h.toFixed(1)} kWh
                          </span>
                          <span className="text-sm text-gray-500">
                            ({((data[data.length - 1]?.storage_stats.max_24h / 30) * 100).toFixed(1)}%)
                          </span>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
