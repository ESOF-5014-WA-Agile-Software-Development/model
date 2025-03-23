'use client';
import { useState } from 'react';
import { purchaseEnergy } from '../utils/api';

export default function ControlPanel() {
  const [amount, setAmount] = useState('');
  const [type, setType] = useState('wind');

  const handlePurchase = async () => {
    if (!amount || parseFloat(amount) <= 0) {
      alert("请输入有效的购买量");
      return;
    }
    
    try {
      const res = await purchaseEnergy({ type, amount: parseFloat(amount) });
      if (res.data.success) {
        alert(`购买成功！剩余存量: ${res.data.storage}`);
      } else {
        alert(`购买失败，存量不足！剩余存量: ${res.data.storage}`);
      }
    } catch (error) {
      alert("请求失败，请检查后端服务是否正常运行。");
    }
  };

  return (
    <div className="border p-4 rounded shadow space-y-4">
      <h2 className="font-bold text-lg">能源购买 (统一存量: 800)</h2>
      <div className="space-x-2">
        <select value={type} onChange={(e) => setType(e.target.value)} className="border p-2 rounded">
          <option value="wind">风能 (Wind)</option>
          <option value="solar">太阳能 (Solar)</option>
        </select>
        <input
          type="number"
          placeholder="输入购买量"
          className="border p-2 rounded"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <button
          onClick={handlePurchase}
          className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        >
          购买
        </button>
      </div>
    </div>
  );
}
