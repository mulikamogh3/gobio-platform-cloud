import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, AreaChart, Area, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { Activity, Zap } from 'lucide-react';

export default function AnalyticsView() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        // Fetch the last 50 data points from the new endpoint
        const response = await axios.get('http://127.0.0.1:8000/device/history');
        setHistory(response.data);
        setError(false);
      } catch (err) {
        console.error("Failed to fetch history:", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
    // Refresh the charts every 5 seconds to show new data flowing in
    const interval = setInterval(fetchHistory, 5000);
    return () => clearInterval(interval);
  }, []);

  if (error) return <div className="p-8 text-red-500 font-bold">Failed to load analytics database.</div>;
  if (loading) return <div className="p-8 text-blue-400 font-bold animate-pulse">Crunching historical data...</div>;

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6 animate-in fade-in duration-500 pb-10">
      
      {/* Header */}
      <div className="bg-slate-800 p-6 rounded-3xl shadow-xl border border-slate-700/50">
        <h1 className="text-3xl font-bold text-white mb-2">Historical Analytics</h1>
        <p className="text-slate-400 font-medium">Live visualization of the Pasteurizer's thermal and electrical telemetry.</p>
      </div>

      {/* Chart 1: Thermal Curve */}
      <div className="bg-slate-800 p-6 rounded-3xl shadow-xl border border-slate-700/50">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Activity className="w-6 h-6 text-red-400" />
          Thermal Pasteurization Curve
        </h2>
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickMargin={10} />
              <YAxis stroke="#94a3b8" fontSize={12} domain={['auto', 'auto']} tickFormatter={(value) => `${value}°`} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }}
                itemStyle={{ fontWeight: 'bold' }}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" />
              <Line 
                type="monotone" 
                name="Actual Temp (°C)" 
                dataKey="temperature" 
                stroke="#ef4444" 
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 6, fill: '#ef4444', stroke: '#0f172a', strokeWidth: 2 }}
              />
              <Line 
                type="monotone" 
                name="Target Temp (°C)" 
                dataKey="target" 
                stroke="#64748b" 
                strokeWidth={2} 
                strokeDasharray="5 5"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chart 2: Energy Consumption */}
      <div className="bg-slate-800 p-6 rounded-3xl shadow-xl border border-slate-700/50">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Zap className="w-6 h-6 text-yellow-400" />
          Power Draw & Efficiency
        </h2>
        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <defs>
                <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#eab308" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#eab308" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
              <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} tickMargin={10} />
              <YAxis stroke="#94a3b8" fontSize={12} tickFormatter={(value) => `${value} W`} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', color: '#fff' }}
              />
              <Area 
                type="stepAfter" 
                name="Power (Watts)" 
                dataKey="power" 
                stroke="#eab308" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorPower)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}
