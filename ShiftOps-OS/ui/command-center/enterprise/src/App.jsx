import React, { useState, useEffect } from 'react';
import { 
  Activity, Sparkles, Users, BarChart3, LogOut, Menu, Building2, 
  RefreshCw, Database, Cloud
} from 'lucide-react';
import FacilityCommand from './components/FacilityCommand';

const API_BASE = "http://localhost:8000";

export default function App() {
  const [activeView, setActiveView] = useState('facility');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchAnalysis = async () => {
    setIsSyncing(true);
    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site: {
            id: "elkhart_01",
            name: "Elkhart Facility",
            industry: "Bakery / Manufacturing",
            nodes: ["Line 1", "Line 2", "Line 3", "Dock A", "Dock B"]
          },
          signals: [
            { area: "Line 1", signal_type: "PROCESS_BOTTLENECK", raw_text: "Oven timing variance detected.", assessor: "System" }
          ]
        })
      });
      const data = await response.json();
      setAnalysisResult(data);
    } catch (e) {
      console.error("API Sync Failed:", e);
    } finally {
      setLoading(false);
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
    const interval = setInterval(fetchAnalysis, 30000); // Sync every 30s
    return () => clearInterval(interval);
  }, []);

  const handleSimulate = async (scenario) => {
    console.log("Triggering SaaS Simulation:", scenario);
    // Future: Call /simulate endpoint
  };

  const navItems = [
    { id: 'analytics', label: 'Strategic Insights', icon: <BarChart3 size={18}/> },
    { id: 'facility', label: 'Facility Command', icon: <Activity size={18}/> },
    { id: 'intelligence', label: 'Intelligence Lab', icon: <Sparkles size={18}/> },
    { id: 'workforce', label: 'Workforce Hub', icon: <Users size={18}/> },
  ];

  if (loading) return (
    <div className="h-screen bg-slate-900 flex flex-col items-center justify-center text-white">
       <div className="w-12 h-12 bg-amber-500 rounded-xl animate-bounce flex items-center justify-center text-slate-900 font-black mb-4">S</div>
       <p className="text-xs font-black uppercase tracking-widest animate-pulse">Initializing ShiftOps-OS...</p>
    </div>
  );

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden selection:bg-amber-200">
      {/* Sidebar */}
      <aside className={`bg-slate-900 text-white transition-all duration-500 flex flex-col z-20 ${isSidebarOpen ? 'w-72' : 'w-24'}`}>
        <div className="p-8 flex items-center gap-4 border-b border-white/5 bg-slate-900/50 backdrop-blur-xl">
          <div className="w-10 h-10 bg-gradient-to-br from-amber-400 to-amber-600 rounded-2xl flex items-center justify-center text-slate-900 font-black shadow-lg shadow-amber-500/20">S</div>
          {isSidebarOpen && (
            <div className="flex flex-col animate-in fade-in duration-1000">
              <span className="font-black tracking-tighter text-2xl uppercase leading-none">ShiftOps<span className="text-amber-500">OS</span></span>
              <span className="text-[8px] font-black text-slate-500 tracking-[0.2em] mt-1 uppercase">Platform v1.0</span>
            </div>
          )}
        </div>

        <nav className="flex-1 mt-8 px-4 space-y-2">
          {navItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all group relative ${
                activeView === item.id 
                ? 'bg-amber-500 text-slate-900 shadow-xl shadow-amber-500/20' 
                : 'text-slate-400 hover:bg-white/5 hover:text-white'
              }`}
            >
              <div className={activeView === item.id ? 'scale-110 transition-transform' : 'group-hover:scale-110 transition-transform'}>
                {item.icon}
              </div>
              {isSidebarOpen && <span className="font-black text-xs uppercase tracking-widest">{item.label}</span>}
              {activeView === item.id && <div className="absolute left-0 w-1 h-6 bg-slate-900 rounded-full ml-1"/>}
            </button>
          ))}
        </nav>

        <div className="p-6 border-t border-white/5 space-y-4">
           <div className={`flex items-center gap-4 px-5 py-3 bg-white/5 rounded-2xl border border-white/5 ${!isSidebarOpen && 'justify-center'}`}>
              <Building2 size={18} className="text-amber-500"/>
              {isSidebarOpen && (
                <div className="overflow-hidden">
                  <p className="text-[9px] font-black text-slate-500 uppercase tracking-tighter">Active Site</p>
                  <p className="text-xs font-bold truncate">Elkhart Facility</p>
                </div>
              )}
           </div>
           <button className="w-full flex items-center gap-4 px-5 py-4 text-slate-500 hover:text-rose-400 transition-all font-black text-xs uppercase tracking-widest">
              <LogOut size={18}/>
              {isSidebarOpen && <span>Sign Out</span>}
           </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Header */}
        <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-10 z-10">
           <div className="flex items-center gap-6">
              <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2.5 hover:bg-slate-100 rounded-xl transition-all active:scale-95 border border-slate-100">
                 {isSidebarOpen ? <X size={20} className="text-slate-500"/> : <Menu size={20} className="text-slate-500"/>}
              </button>
              <div className="h-8 w-px bg-slate-200"/>
              <div className="flex items-center gap-3">
                 <div className={`p-2 rounded-lg ${isSyncing ? 'bg-amber-50 text-amber-600 animate-spin' : 'bg-emerald-50 text-emerald-600'}`}>
                    <RefreshCw size={16}/>
                 </div>
                 <div>
                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Gateway Status</p>
                    <p className="text-xs font-bold text-slate-700">{isSyncing ? 'Synchronizing City Layers...' : 'Engines Integrated'}</p>
                 </div>
              </div>
           </div>
           
           <div className="flex items-center gap-8">
              <div className="flex items-center gap-4 px-4 py-2 bg-slate-50 rounded-xl border border-slate-100">
                 <Database size={14} className="text-slate-400"/>
                 <div className="flex flex-col">
                    <span className="text-[8px] font-black text-slate-400 uppercase">Ontology Pack</span>
                    <span className="text-[10px] font-bold text-slate-600 tracking-tight">MANUFACTURING_V4</span>
                 </div>
              </div>
              <div className="w-10 h-10 bg-slate-100 rounded-2xl border border-slate-200 shadow-inner flex items-center justify-center overflow-hidden hover:ring-2 hover:ring-amber-500 transition-all cursor-pointer group">
                 <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="User" className="group-hover:scale-110 transition-transform"/>
              </div>
           </div>
        </header>

        {/* Dynamic Viewport */}
        <div className="flex-1 overflow-y-auto p-10 bg-slate-50/30">
          <div className="max-w-[1600px] mx-auto">
            {activeView === 'facility' && analysisResult && (
              <FacilityCommand analysisResult={analysisResult} onSimulate={handleSimulate} />
            )}
            
            {activeView === 'analytics' && (
              <div className="h-[600px] flex flex-col items-center justify-center border-4 border-dashed border-slate-200 rounded-[40px] text-slate-300">
                <div className="p-6 bg-slate-100 rounded-3xl mb-4">
                   <Cloud size={48}/>
                </div>
                <p className="text-lg font-black uppercase tracking-[0.3em]">GCP BigQuery Hub</p>
                <p className="text-sm font-bold text-slate-400 mt-2">Provisioning Analytics Warehouse...</p>
              </div>
            )}

            {activeView === 'intelligence' && (
              <div className="h-[600px] flex flex-col items-center justify-center border-4 border-dashed border-slate-200 rounded-[40px] text-slate-300">
                <div className="p-6 bg-amber-50 rounded-3xl mb-4 text-amber-500">
                   <Sparkles size={48}/>
                </div>
                <p className="text-lg font-black uppercase tracking-[0.3em] text-amber-600">Intelligence Lab</p>
                <p className="text-sm font-bold text-slate-400 mt-2">Gemini 2.0 Reasoning Context: ACTIVE</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
