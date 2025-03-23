'use client';
import { useEffect, useState } from 'react';
import { AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function RealTimeChart() {
  const [data, setData] = useState([]);
  const [selected, setSelected] = useState('wind');

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');
    socket.onmessage = (event) => {
      const receivedData = JSON.parse(event.data);
      setData(prevData => [
        ...prevData.slice(-20),
        {
          timestamp: new Date().toLocaleTimeString(),
          storage: receivedData.storage,
          real_wind: receivedData.real.P_wind,
          real_solar: receivedData.real.P_solar,
          real_consumption: receivedData.real.house_consumption,
          predict_wind: receivedData.predict.P_wind,
          predict_solar: receivedData.predict.P_solar,
          predict_consumption: receivedData.predict.house_consumption,
        }
      ]);
    };

    socket.onclose = () => console.log("WebSocket disconnected.");
    socket.onerror = (e) => console.error("WebSocket error:", e);

    return () => socket.close();
  }, []);

  const handleChange = (e) => {
    setSelected(e.target.value);
  };

  return (
    <div className="border p-4 rounded shadow space-y-4">
      <h2 className="font-bold text-xl">实时能源数据展示（Real & Predict）</h2>
      
      <div>
        <select value={selected} onChange={handleChange} className="border p-2 rounded">
          <option value="wind">风能 (Wind)</option>
          <option value="solar">太阳能 (Solar)</option>
          <option value="consumption">用电量 (Consumption)</option>
        </select>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="realColor" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="predictColor" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#82ca9d" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3"/>
          <XAxis dataKey="timestamp"/>
          <YAxis/>
          <Tooltip/>
          <Legend/>
          <Area type="monotone" dataKey={`real_${selected}`} stroke="#8884d8" fillOpacity={1} fill="url(#realColor)" name={`Real ${selected}`} />
          <Area type="monotone" dataKey={`predict_${selected}`} stroke="#82ca9d" fillOpacity={1} fill="url(#predictColor)" name={`Predict ${selected}`} />
        </AreaChart>
      </ResponsiveContainer>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3"/>
          <XAxis dataKey="timestamp"/>
          <YAxis/>
          <Tooltip/>
          <Legend/>
          <Area type="monotone" dataKey="storage" stroke="#1f77b4" fill="#1f77b4" name="Total Storage"/>
        </AreaChart>
      </ResponsiveContainer>

      <pre className="mt-4 text-sm">
        {data.length ? JSON.stringify(data[data.length - 1], null, 2) : "正在等待数据..."}
      </pre>
    </div>
  );
}
