/*'use client';
import { useEffect, useState } from 'react';

export default function RealTimeChart() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');
    socket.onmessage = (event) => {
      setData(JSON.parse(event.data));
    };
    socket.onclose = () => console.log("WebSocket disconnected.");
    socket.onerror = (e) => console.error("WebSocket error:", e);

    return () => socket.close();
  }, []);

  return (
    <div className="border p-4 rounded shadow">
      <h2 className="font-bold text-lg">实时数据展示（Real & Predict）</h2>
      <pre className="mt-4 text-sm">
        {data ? JSON.stringify(data, null, 2) : "正在等待数据..."}
      </pre>
    </div>
  );
}


'use client';
import { useEffect, useState } from 'react';
import {
  LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend
} from 'recharts';

export default function RealTimeChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');
    socket.onmessage = (event) => {
      const receivedData = JSON.parse(event.data);
      setData((prevData) => [
        ...prevData.slice(-20),  // 保留最近20个点
        {
          timestamp: new Date().toLocaleTimeString(),
          real_wind: receivedData.real.P_wind,
          real_solar: receivedData.real.P_solar,
          real_consumption: receivedData.real.house_consumption,
          predict_wind: receivedData.predict.P_wind,
          predict_solar: receivedData.predict.P_solar,
          predict_consumption: receivedData.predict.house_consumption,
        }
      ]);
    };

    return () => socket.close();
  }, []);

  return (
    <div className="border p-4 rounded shadow">
      <h2 className="font-bold text-lg mb-4">实时数据动态折线图 (Real & Predict)</h2>
      <LineChart width={800} height={400} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
        <Legend />
        
        <Line type="monotone" dataKey="real_wind" stroke="#8884d8" name="Real Wind" />
        <Line type="monotone" dataKey="real_solar" stroke="#82ca9d" name="Real Solar" />
        <Line type="monotone" dataKey="real_consumption" stroke="#ffc658" name="Real Consumption" />

        
        <Line type="monotone" dataKey="predict_wind" stroke="#8884d8" strokeDasharray="5 5" name="Predict Wind" />
        <Line type="monotone" dataKey="predict_solar" stroke="#82ca9d" strokeDasharray="5 5" name="Predict Solar" />
        <Line type="monotone" dataKey="predict_consumption" stroke="#ffc658" strokeDasharray="5 5" name="Predict Consumption" />
      </LineChart>
    </div>
  );
}
*/
'use client';
import { useEffect, useState } from 'react';
import {
  AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

export default function RealTimeChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws');
    socket.onmessage = (event) => {
      const receivedData = JSON.parse(event.data);
      setData((prevData) => [
        ...prevData.slice(-20),
        {
          timestamp: new Date().toLocaleTimeString(),
          real_wind: receivedData.real.P_wind,
          real_solar: receivedData.real.P_solar,
          real_consumption: receivedData.real.house_consumption,
          predict_wind: receivedData.predict.P_wind,
          predict_solar: receivedData.predict.P_solar,
          predict_consumption: receivedData.predict.house_consumption,
        }
      ]);
    };

    return () => socket.close();
  }, []);

  const [selected, setSelected] = useState('wind');

  const handleChange = (e) => {
    setSelected(e.target.value);
  };

  return (
    <div className="border p-4 rounded shadow space-y-4">
      <h2 className="font-bold text-lg">实时数据动态折线图（Real vs Predict）</h2>
      <div>
        <select value={selected} onChange={handleChange} className="border p-2 rounded">
          <option value="wind">风能 (Wind)</option>
          <option value="solar">太阳能 (Solar)</option>
          <option value="consumption">用电量 (Consumption)</option>
        </select>
      </div>
      <ResponsiveContainer width="100%" height={400}>
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
    </div>
  );
}
