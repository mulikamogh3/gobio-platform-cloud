import { useState, useEffect } from 'react';
import axios from 'axios';
import { Thermometer, Zap, Wifi, Clock, Power, BrainCircuit, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function LiveDashboard() {
  const [sensorData, setSensorData] = useState(null);
  const [error, setError] = useState(false);
  
  // New State for Machine Learning Predictions
  const [aiPredictions, setAiPredictions] = useState({ anomaly: null, heater_prediction: null });

  // 1. Fetch Live Data from PostgreSQL
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/device/live');
        setSensorData(response.data);
        setError(false);
      } catch (err) {
        console.error("Error fetching live data:", err);
        setError(true);
      }
    };

    fetchData(); 
    const interval = setInterval(fetchData, 2000); 
    return () => clearInterval(interval);
  }, []);

  // 2. Fetch AI Predictions whenever new data arrives
  useEffect(() => {
    if (!sensorData) return;

    const fetchPredictions = async () => {
      try {
        // Send the current sensor state to the AI endpoints
        const anomalyRes = await axios.post('http://127.0.0.1:8000/prediction/anomaly', sensorData);
        const heatingRes = await axios.post('http://127.0.0.1:8000/prediction/heating', sensorData);
        
        setAiPredictions({
          anomaly: anomalyRes.data.anomaly_detected,
          heater_prediction: heatingRes.data.prediction
        });
      } catch (err) {
        console.error("AI Prediction Error:", err);
      }
    };

    fetchPredictions();
  }, [sensorData]); // This triggers every time sensorData changes

  if (error) return <div className="p-8 text-xl font-bold text-red-500 flex items-center justify-center h-full">Error connecting to backend API. Is FastAPI running?</div>;
  // Check if the data is empty or hasn't loaded yet
  if (!sensorData || Object.keys(sensorData).length === 0) {
    return (
      <div style={{ padding: "50px", textAlign: "center", color: "white" }}>
        <h2>🔌 GoBioAI System Online</h2>
        <p>Waiting for the ESP32 hardware to transmit the first sensor payload...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 max-w-6xl mx-auto animate-in fade-in duration-500 pb-10">
        {/* Header */}
        <div className="flex justify-between items-center bg-slate-800 p-6 rounded-3xl border border-slate-700/50 shadow-xl">
            <div>
                <h1 className="text-3xl font-bold text-white mb-2">Live Pasteurization Monitor</h1>
                <p className="text-slate-400 flex items-center gap-2 font-medium">
                    <span className="bg-slate-900 px-3 py-1 rounded-lg text-sm text-blue-400 font-mono tracking-wider shadow-inner">ID: {sensorData.machine_id}</span>
                    <span className="text-slate-600">•</span>
                    Last Updated: {new Date(sensorData.timestamp).toLocaleTimeString()}
                </p>
            </div>
            <div className={`px-5 py-2.5 rounded-full font-bold flex items-center gap-2 shadow-lg ${sensorData.process === 'HEATING' ? 'bg-orange-500/10 text-orange-400 border border-orange-500/30' : 'bg-green-500/10 text-green-400 border border-green-500/30'}`}>
                <Clock className="w-5 h-5" />
                {sensorData.process} MODE ({sensorData.mode})
            </div>
        </div>

        {/* Existing Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Temperature Card */}
            <div className="bg-slate-800 p-6 rounded-3xl shadow-xl border border-slate-700/50 relative overflow-hidden group hover:border-red-500/30 transition-colors">
                <div className="absolute -top-4 -right-4 p-4 opacity-10 group-hover:opacity-20 group-hover:scale-110 transition-all duration-300">
                    <Thermometer className="w-32 h-32 text-red-500" />
                </div>
                <h3 className="text-slate-400 font-medium mb-1">Current Temperature</h3>
                <div className="text-5xl font-black text-white flex items-baseline gap-1 mt-2">
                    {sensorData.temperature.toFixed(1)}<span className="text-2xl text-slate-500">°C</span>
                </div>
                <div className="mt-6 text-sm text-slate-400 flex justify-between items-center bg-slate-900/50 p-3 rounded-xl">
                    <span>Target</span>
                    <span className="text-white font-bold">{sensorData.target_temperature}°C</span>
                </div>
            </div>

            {/* Voltage Card */}
            <div className="bg-slate-800 p-6 rounded-3xl shadow-xl border border-slate-700/50 relative overflow-hidden group hover:border-yellow-500/30 transition-colors">
                <div className="absolute -top-4 -right-4 p-4 opacity-10 group-hover:opacity-20 group-hover:scale-110 transition-all duration-300">
                    <Zap className="w-32 h-32 text-yellow-500" />
                </div>
                <h3 className="text-slate-400 font-medium mb-1">Voltage Input</h3>
                <div className="text-5xl font-black text-white flex items-baseline gap-1 mt-2">
                    {sensorData.voltage.toFixed(1)}<span className="text-2xl text-slate-500">V</span>
                </div>
                <div className="mt-6 text-sm text-slate-400 flex justify-between items-center bg-slate-900/50 p-3 rounded-xl">
                    <span>Power Output</span>
                    <span className="text-white font-bold">{sensorData.power.toFixed(2)} kW</span>
                </div>
            </div>

            {/* Heater Status Card */}
            <div className="bg-slate-800 p-6 rounded-3xl shadow-xl border border-slate-700/50 relative overflow-hidden group hover:border-orange-500/30 transition-colors">
                <div className="absolute -top-4 -right-4 p-4 opacity-10 group-hover:opacity-20 group-hover:scale-110 transition-all duration-300">
                    <Power className="w-32 h-32 text-orange-500" />
                </div>
                <h3 className="text-slate-400 font-medium mb-1">Heater Relay</h3>
                <div className={`mt-4 inline-flex items-center justify-center w-16 h-16 rounded-2xl ${sensorData.heater_status ? 'bg-orange-500 text-white shadow-[0_0_30px_rgba(249,115,22,0.3)]' : 'bg-slate-900 text-slate-600'} transition-all duration-500`}>
                    <Power className={`w-8 h-8 ${sensorData.heater_status ? 'animate-pulse' : ''}`} />
                </div>
                <div className="mt-6 text-sm text-slate-400 flex justify-between items-center bg-slate-900/50 p-3 rounded-xl">
                    <span>Status</span>
                    <span className={`font-bold ${sensorData.heater_status ? 'text-orange-400' : 'text-slate-500'}`}>{sensorData.heater_status ? 'ACTIVE' : 'OFF'}</span>
                </div>
            </div>

            {/* AI Heater Decision Card */}
            <div className="bg-slate-800 p-6 rounded-3xl shadow-xl border border-slate-700/50 relative overflow-hidden group hover:border-red-500/30 transition-colors">
                <div className="absolute -top-6 -right-4 p-4 opacity-10 group-hover:opacity-20 group-hover:scale-110 transition-all duration-300">
                    <span className="text-8xl">🔥</span>
                </div>
                <h3 className="text-slate-400 font-medium mb-1 flex items-center gap-2">
                    🔥 AI Heater Decision
                </h3>
                <div className="text-5xl font-black text-white flex items-baseline gap-1 mt-2">
                    {sensorData.heater_decision?.recommended_power ?? 0}<span className="text-2xl text-slate-500">%</span>
                </div>
                
                {/* Progress Bar */}
                <div className="w-full h-3 bg-slate-900 rounded-full mt-4 overflow-hidden shadow-inner border border-slate-700/50">
                    <div 
                        className="h-full transition-all duration-1000 ease-in-out"
                        style={{ 
                            width: `${sensorData.heater_decision?.recommended_power ?? 0}%`,
                            backgroundColor: (sensorData.heater_decision?.recommended_power ?? 0) === 0 ? '#64748b' :
                                             (sensorData.heater_decision?.recommended_power ?? 0) <= 10 ? '#22c55e' :
                                             (sensorData.heater_decision?.recommended_power ?? 0) <= 25 ? '#0ea5e9' :
                                             (sensorData.heater_decision?.recommended_power ?? 0) <= 50 ? '#eab308' :
                                             (sensorData.heater_decision?.recommended_power ?? 0) <= 75 ? '#f97316' : '#ef4444'
                        }}
                    />
                </div>
                
                <div className="mt-5 flex flex-col gap-2">
                    <div className="text-sm text-slate-400 flex justify-between items-center bg-slate-900/50 p-2.5 rounded-xl">
                        <span>Action</span>
                        <span className="text-white font-bold text-right">{sensorData.heater_decision?.action ?? 'N/A'}</span>
                    </div>
                    <div className="text-sm text-slate-400 flex justify-between items-center bg-slate-900/50 p-2.5 rounded-xl">
                        <span>Status</span>
                        <span className="text-white font-bold text-right">{sensorData.heater_decision?.status ?? 'N/A'}</span>
                    </div>
                    <div className="text-sm text-slate-400 flex justify-between items-center bg-slate-900/50 p-2.5 rounded-xl">
                        <span>Diff</span>
                        <span className="text-white font-bold text-right">
                            {sensorData.heater_decision?.difference ?? 0}°C 
                            {sensorData.temperature < sensorData.target_temperature ? ' Below Target' : 
                             (sensorData.temperature > sensorData.target_temperature ? ' Above Target' : ' At Target')}
                        </span>
                    </div>
                </div>
            </div>

            {/* WiFi Status Card */}
            <div className="bg-slate-800 p-6 rounded-3xl shadow-xl border border-slate-700/50 relative overflow-hidden group hover:border-blue-500/30 transition-colors">
                <div className="absolute -top-4 -right-4 p-4 opacity-10 group-hover:opacity-20 group-hover:scale-110 transition-all duration-300">
                    <Wifi className="w-32 h-32 text-blue-500" />
                </div>
                <h3 className="text-slate-400 font-medium mb-1">ESP32 Connection</h3>
                <div className={`mt-4 inline-flex items-center justify-center w-16 h-16 rounded-2xl ${sensorData.wifi_connected ? 'bg-blue-500 text-white shadow-[0_0_30px_rgba(59,130,246,0.3)]' : 'bg-red-500 text-white shadow-[0_0_30px_rgba(239,68,68,0.3)]'} transition-all duration-500`}>
                    <Wifi className="w-8 h-8" />
                </div>
                <div className="mt-6 text-sm text-slate-400 flex justify-between items-center bg-slate-900/50 p-3 rounded-xl">
                    <span>Network</span>
                    <span className={`font-bold ${sensorData.wifi_connected ? 'text-blue-400' : 'text-red-400'}`}>{sensorData.wifi_connected ? 'STABLE' : 'DISCONNECTED'}</span>
                </div>
            </div>
        </div>

        {/* --- NEW MACHINE LEARNING INSIGHTS SECTION --- */}
        <div className="mt-4">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <BrainCircuit className="w-6 h-6 text-purple-400" /> 
                Live AI Insights
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Anomaly Detection AI */}
                <div className={`p-6 rounded-3xl shadow-xl border flex items-center gap-6 transition-colors ${aiPredictions.anomaly ? 'bg-red-900/20 border-red-500/50' : 'bg-slate-800 border-slate-700/50'}`}>
                    <div className={`p-4 rounded-2xl ${aiPredictions.anomaly ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                        {aiPredictions.anomaly ? <AlertTriangle className="w-10 h-10" /> : <ShieldCheck className="w-10 h-10" />}
                    </div>
                    <div>
                        <h3 className="text-slate-400 font-medium text-sm tracking-wider uppercase mb-1">System Health (Isolation Forest)</h3>
                        {aiPredictions.anomaly === null ? (
                            <div className="text-2xl font-bold text-slate-500 animate-pulse">Analyzing...</div>
                        ) : (
                            <div className={`text-2xl font-bold ${aiPredictions.anomaly ? 'text-red-400' : 'text-emerald-400'}`}>
                                {aiPredictions.anomaly ? 'ANOMALY DETECTED' : 'OPTIMAL'}
                            </div>
                        )}
                        <p className="text-slate-500 text-sm mt-1">Constantly checking physics for mechanical failures.</p>
                    </div>
                </div>

                {/* AI Heater Control Prediction */}
                <div className="bg-slate-800 p-6 rounded-3xl shadow-xl border border-slate-700/50 flex items-center gap-6">
                    <div className="p-4 rounded-2xl bg-purple-500/20 text-purple-400">
                        <BrainCircuit className="w-10 h-10" />
                    </div>
                    <div>
                        <h3 className="text-slate-400 font-medium text-sm tracking-wider uppercase mb-1">AI Heater Target (Random Forest)</h3>
                        {aiPredictions.heater_prediction === null ? (
                            <div className="text-2xl font-bold text-slate-500 animate-pulse">Calculating...</div>
                        ) : (
                            <div className="text-2xl font-bold text-white">
                                {aiPredictions.heater_prediction === 1.0 ? 'SHOULD BE ON' : 'SHOULD BE OFF'}
                            </div>
                        )}
                        <p className="text-slate-500 text-sm mt-1">Predicting optimal thermal state based on historical data.</p>
                    </div>
                </div>

            </div>
        </div>
    </div>
  );
}
