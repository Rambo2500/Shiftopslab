import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, Sparkles, Users, BarChart3, LogOut, Menu, Building2, 
  RefreshCw, Database, Cloud, Zap, ShieldAlert, Terminal, MessageSquare,
  Box, Wind, Map, AlertTriangle, ArrowRight, Search, CheckCircle2,
  Briefcase, Crosshair, X, Globe, Settings, Share2, TrendingUp, DollarSign, Milestone, ChevronRight,
  Camera, Upload, FileText, Info, ShieldCheck, Truck, Cog, HardHat, PhoneCall, ListChecks, Thermometer, Gauge,
  Shield, Target, AlertOctagon
} from 'lucide-react';
import FacilityCommand from './components/FacilityCommand';

const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : "https://shiftops-core-np7si5cqka-uc.a.run.app";

const DOMAINS = {
  BAKERY: { id: 'bakery', name: 'Industrial Bakery', industry_pack: "bakery_ops_v1", defaultText: "Line 4 oven temp is fluctuating. Mike called off work. We have 4,000 sourdough units due for the 6 AM Kroger load. Conveyor belt B is making a grinding noise but still running. Priority is OTIF for the fresh bread contract." },
  LOGISTICS: { id: 'logistics', name: 'Global Logistics & 3PL', industry_pack: "logistics_ops_v1", defaultText: "Inbound dock 4 is backed up with 3 unexpected live loads. Outbound lane 7 is waiting on forklift drivers. 88% dock utilization. OTIF penalty triggers in 2 hours for Walmart." },
  HR: { id: 'hr', name: 'Workforce & FTE Engine', industry_pack: "hr_workforce_v1", defaultText: "Call-offs at 12% today. We are short 4 FTEs in the core processing node. Overtime budget is at 98%. The shift manager is requesting agency labor approval." },
  FINANCE: { id: 'finance', name: 'Supply Chain Finance', industry_pack: "finance_ops_v1", defaultText: "EBITDA margin dropping by 1.2% this week. Unplanned downtime on Line 2 caused a $14,000 scrap variance. Need to recalculate recovery horizon." },
  FEMA: { id: 'fema', name: 'Disaster Recovery', industry_pack: "emergency_v1", defaultText: "Local power disruption detected. Backup generators engaged but failing transfer load." }
};

const ParetoChart = ({ data }) => {
  if (!data || data.length === 0) return <div className="h-40 flex items-center justify-center text-slate-400 italic text-xs">No data to show yet.</div>;
  const sorted = [...data].sort((a, b) => b.value - a.value).slice(0, 10);
  const maxVal = sorted[0]?.value || 1;
  return (
    <div className="space-y-6">
      <div className="flex items-end h-64 gap-3 px-2 border-b border-white/10 pb-2">
        {sorted.map((item, i) => {
          const height = Math.max(5, (item.value / maxVal) * 100);
          return (
            <div key={i} className="flex-1 flex flex-col justify-end group relative h-full">
              <div className="absolute -top-12 left-1/2 -translate-x-1/2 bg-rose-600 text-white text-[10px] font-black px-2 py-1 rounded shadow-xl opacity-0 group-hover:opacity-100 transition-opacity z-20 whitespace-nowrap">{item.value.toFixed(0)} units</div>
              <div className={`w-full rounded-t-sm transition-all duration-700 ${i < 2 ? 'bg-rose-500 shadow-[0_0_15px_rgba(244,63,94,0.4)]' : 'bg-slate-700'}`} style={{ height: `${height}%` }} />
              <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-[10px] font-black text-slate-500">{item.label}</div>
            </div>
          );
        })}
      </div>
      <div className="pt-6">
        <div className="flex items-center gap-4 mb-2">
           <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-rose-500 rounded-sm"/> <span className="text-[10px] font-black uppercase text-rose-400 tracking-tighter">Critical (80% Risk)</span></div>
           <div className="flex items-center gap-1.5"><div className="w-3 h-3 bg-slate-700 rounded-sm"/> <span className="text-[10px] font-black uppercase text-slate-500 tracking-tighter">Minor Variance</span></div>
        </div>
        <p className="text-[10px] text-slate-400 font-medium leading-relaxed">The 80/20 Rule: Red bars are your biggest problems.</p>
      </div>
    </div>
  );
};

const DistributionChart = ({ pValue }) => {
  const isShifted = pValue < 0.05;
  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center pt-8">
      <svg viewBox="0 0 400 160" className="w-full h-full overflow-visible">
        <path d="M 20 140 Q 200 0 380 140" fill="none" stroke="rgba(148, 163, 184, 0.2)" strokeWidth="2" strokeDasharray="4 4" />
        <path d={isShifted ? "M 80 140 Q 300 20 420 140" : "M 20 140 Q 200 0 380 140"} fill={isShifted ? "rgba(244, 63, 94, 0.1)" : "rgba(16, 185, 129, 0.1)"} stroke={isShifted ? "#f43f5e" : "#10b981"} strokeWidth="4" className="transition-all duration-1000" />
        <line x1={isShifted ? "300" : "200"} y1="20" x2={isShifted ? "300" : "200"} y2="140" stroke={isShifted ? "#f43f5e" : "#10b981"} strokeWidth="2" strokeDasharray="2 2" />
      </svg>
      <div className="flex justify-between w-full mt-4 px-4 text-[9px] font-black uppercase text-slate-400"><span>Lower Spec</span><span className={isShifted ? "text-rose-500 underline" : ""}>{isShifted ? "Current Mean (Shifted)" : "Mean (Normal)"}</span><span>Upper Spec</span></div>
    </div>
  );
};

export default function App() {
  const [activeView, setActiveView] = useState('intelligence');
  const [viewMode, setViewMode] = useState('actual'); // 'actual' or 'simulation'
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeDomain, setActiveDomain] = useState(DOMAINS.BAKERY);
  const [inputText, setInputText] = useState(DOMAINS.BAKERY.defaultText);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [snapshot, setSnapshot] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [dispatchStatus, setDispatchStatus] = useState({});
  const [messages, setMessages] = useState([
    { role: 'system', text: 'SHIFTOPS-OS // CORE INTELLIGENCE UNIFIED' },
    { role: 'ai', text: 'Floor Manager active. I am watching the ovens, the roster, and the truck schedule.' }
  ]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setMessages(prev => [...prev, { role: 'system', text: `FILE RECEIVED: ${file.name} is being read.` }]);
    }
  };

  const runSynthesis = async () => {
    setIsProcessing(true);
    setMessages(prev => [...prev, { role: 'user', text: `Analyzing floor signals... ${selectedFile ? `(+ ${selectedFile.name})` : ''}` }]);
    try {
      const auditRes = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          site: { id: "site_01", name: activeDomain.name, industry: "Manufacturing", nodes: ["Core"] },
          signals: [
            { area: "Plant", signal_type: "MANUAL", raw_text: inputText, assessor: "Human" },
            ...(selectedFile ? [{ area: "Upload", signal_type: "FILE", raw_text: `file:${selectedFile.name}`, assessor: "System" }] : [])
          ],
          industry_pack: activeDomain.industry_pack
        })
      });
      const auditData = await auditRes.json();
      setAnalysisResult(auditData);
      setAnalysisResult(auditData);
      const ingestedSource = auditData?.statistics?.ingested_source || "System Text";
      const pValue = auditData?.statistics?.p_value !== undefined ? auditData.statistics.p_value : "---";
      setMessages(prev => [...prev, { role: 'ai', text: `Analysis Complete. Source: ${ingestedSource}. P-Value: ${pValue}.` }]);
      setActiveView('arbiter');
    } catch (err) {
      setMessages(prev => [...prev, { role: 'system', text: 'ERROR: Could not connect to the floor.' }]);
    } finally {
      setIsProcessing(false);
    }
  };

  const executeDispatch = async (id, type, target) => {
    setDispatchStatus(prev => ({ ...prev, [id]: 'SENDING...' }));
    try {
      const res = await fetch(`${API_BASE}/api/dispatch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type, target })
      });
      const data = await res.json();
      if (data.status === "success") {
        setDispatchStatus(prev => ({ ...prev, [id]: 'SENT' }));
        setMessages(prev => [...prev, { role: 'ai', text: `ACTION: Sent ${type} to ${target}.` }]);
      }
    } catch (e) {
      setDispatchStatus(prev => ({ ...prev, [id]: 'FAILED' }));
    }
  };

  const navItems = [
    { id: 'arbiter', label: '1. The Decision', icon: <Shield size={18}/> },
    { id: 'define', label: '2. The Situation', icon: <Search size={18}/> },
    { id: 'measure', label: '3. Live Sensors', icon: <Activity size={18}/> },
    { id: 'analyze', label: '4. Root Cause', icon: <BarChart3 size={18}/> },
    { id: 'improve', label: '5. The Fix', icon: <Zap size={18}/> },
    { id: 'control', label: '6. Dispatch Center', icon: <ShieldAlert size={18}/> },
    { id: 'finance', label: '7. Finance (Recon)', icon: <DollarSign size={18}/> },
    { id: 'logistics', label: '8. Logistics (WMS)', icon: <Truck size={18}/> },
  ];

  const paretoData = analysisResult?.state?.production?.map(p => ({ label: p.node_id, value: Math.max(0, p.planned_units - p.actual_units) })) || [];

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden selection:bg-amber-200">
      <aside className={`bg-black/80 text-white transition-all duration-500 flex flex-col z-20 border-r border-white/10 ${isSidebarOpen ? 'w-80' : 'w-24'}`}>
        <div className="p-8 flex items-center gap-4 border-b border-white/5 bg-slate-900/50 backdrop-blur-xl">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-2xl flex items-center justify-center text-white font-black shadow-lg shadow-blue-500/30 ring-1 ring-white/20"><Zap size={20}/></div>
          {isSidebarOpen && <div className="flex flex-col"><span className="font-black tracking-tighter text-2xl uppercase leading-none italic text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">ShiftOps<span className="text-white">PRO</span></span><span className="text-[8px] font-black text-blue-500 tracking-[0.2em] mt-1 uppercase">Universal Operations Intelligence</span></div>}
        </div>
        {isSidebarOpen && (
          <div className="px-6 py-4 border-b border-white/5 bg-slate-900/30">
            <p className="text-[9px] font-black text-slate-500 uppercase tracking-widest mb-3">Diagnostic Domain</p>
            <div className="space-y-2">
               {Object.values(DOMAINS).slice(0, 3).map(dom => (
                 <button 
                   key={dom.id} 
                   onClick={() => { setActiveDomain(dom); setInputText(dom.defaultText); }}
                   className={`w-full text-left p-3 rounded-xl border border-white/5 transition-all flex items-center gap-3 ${activeDomain.id === dom.id ? 'bg-blue-600 shadow-xl shadow-blue-500/20 text-white border-blue-500' : 'hover:bg-white/5 text-slate-400'}`}
                 >
                   {dom.id === 'bakery' ? <Building2 size={16}/> : dom.id === 'logistics' ? <Truck size={16}/> : <Users size={16}/>}
                   <span className="text-xs font-black uppercase tracking-tight">{dom.name}</span>
                 </button>
               ))}
            </div>
          </div>
        )}
        {isSidebarOpen && (
          <div className="p-6 border-b border-white/5 bg-black/40">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2"><Terminal size={12} className="text-blue-400" /> Ground Signal Ingestion</p>
            <div className="relative group mb-4">
              <textarea id="grounding-input" name="grounding-input" value={inputText} onChange={(e) => setInputText(e.target.value)} className="w-full h-32 bg-slate-900 border border-white/10 rounded-2xl p-4 text-[11px] font-mono text-blue-100 focus:outline-none focus:ring-1 focus:ring-blue-500/50 resize-none shadow-inner" placeholder="Paste problem or logs..." />
              <div className="absolute bottom-2 right-2 flex gap-2">
                <input type="file" id="file-upload" name="file-upload" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".csv,.xlsx,.pdf,.jpg,.png,.doc" />
                <button onClick={() => fileInputRef.current.click()} className={`p-2 rounded-lg transition-all ${selectedFile ? 'bg-blue-600 text-white' : 'bg-white/10 text-slate-400 hover:text-white hover:bg-white/20'}`} title="Upload Files"><Upload size={14} /></button>
              </div>
            </div>
            {selectedFile && (
              <div className="mb-4 p-2 bg-white/5 border border-white/10 rounded-xl flex items-center gap-3">
                <div className="p-2 bg-blue-500/20 text-blue-400 rounded-lg"><FileText size={14} /></div>
                <div className="flex-1 truncate"><p className="text-[9px] font-black uppercase text-slate-300 truncate">{selectedFile.name}</p></div>
                <button onClick={() => setSelectedFile(null)} className="text-slate-500 hover:text-rose-400 transition-colors"><X size={14} /></button>
              </div>
            )}
            <button onClick={runSynthesis} disabled={isProcessing} className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 transition-all text-white rounded-xl font-black text-[10px] uppercase tracking-[0.2em] flex items-center justify-center gap-2 shadow-xl">{isProcessing ? <RefreshCw size={14} className="animate-spin" /> : <Zap size={14} />} {isProcessing ? 'SCANNING DATA...' : 'COMBINE REPORTS'}</button>
          </div>
        )}
        {isSidebarOpen && (
          <div className="px-6 py-4 border-b border-white/5 bg-slate-900/30">
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-3">Operating Mode</p>
            <div className="flex bg-black/40 p-1 rounded-xl border border-white/10">
              <button 
                onClick={() => setViewMode('actual')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-[9px] font-black uppercase transition-all ${viewMode === 'actual' ? 'bg-amber-500 text-slate-900 shadow-lg shadow-amber-500/20' : 'text-slate-500 hover:text-slate-300'}`}
              >
                <Activity size={12}/> Actual
              </button>
              <button 
                onClick={() => setViewMode('simulation')}
                className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg text-[9px] font-black uppercase transition-all ${viewMode === 'simulation' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20' : 'text-slate-500 hover:text-slate-300'}`}
              >
                <Sparkles size={12}/> Simulation
              </button>
            </div>
          </div>
        )}
        <nav className="flex-1 mt-4 px-4 space-y-1 overflow-y-auto custom-scrollbar">
          {navItems.map(item => (
            <button key={item.id} onClick={() => setActiveView(item.id)} className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all group relative ${activeView === item.id ? 'bg-blue-600 text-white shadow-xl shadow-blue-500/20' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}>
              <div className={activeView === item.id ? 'scale-110 transition-transform' : 'group-hover:scale-110 transition-transform'}>{item.icon}</div>
              {isSidebarOpen && <span className="font-black text-[11px] uppercase tracking-[0.15em]">{item.label}</span>}
            </button>
          ))}
          <button onClick={() => setActiveView('facility')} className={`w-full flex items-center gap-4 px-5 py-4 rounded-2xl transition-all group relative ${activeView === 'facility' ? 'bg-amber-500 text-slate-900 shadow-xl' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}>
            <Map size={18} />
            {isSidebarOpen && <span className="font-black text-[11px] uppercase tracking-[0.15em]">Floor Map</span>}
          </button>
        </nav>
        {isSidebarOpen && (
          <div className="p-6 border-t border-white/5 bg-black/60 h-40 overflow-y-auto custom-scrollbar pr-2 relative">
             <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none"><Database size={100} /></div>
            {messages.map((msg, i) => (
              <div key={i} className={`text-[9px] leading-relaxed mb-2 ${msg.role === 'ai' ? 'text-indigo-300 italic' : 'text-slate-500 font-mono'}`}>
                {msg.role === 'ai' && <span className="font-black not-italic mr-1 text-indigo-500 uppercase">System:</span>}
                "{msg.text}"
              </div>
            ))}
          </div>
        )}
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden relative bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-900 via-[#0a0f1c] to-black">
         <header className="h-24 bg-white/5 backdrop-blur-3xl border-b border-white/10 flex items-center justify-between px-10 z-10 shadow-lg">
           <div className="flex items-center gap-6">
              <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="p-2.5 hover:bg-white/10 rounded-xl transition-all border border-white/5 hover:border-white/20">
                 {isSidebarOpen ? <X size={20} className="text-slate-400"/> : <Menu size={20} className="text-slate-400"/>}
              </button>
              <div>
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-0.5">Current Operating Mode</p>
                <div className="flex items-center gap-2"><div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(59,130,246,0.8)]" /><span className="text-sm font-black text-white uppercase tracking-tight">{activeDomain.name}</span></div>
              </div>
           </div>
           
           {/* FTE & Finance Global Ribbon */}
           <div className="flex gap-4">
              <div className="px-5 py-3 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 text-right min-w-[140px] drop-shadow-xl flex items-center gap-4">
                 <div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400"><Users size={16}/></div>
                 <div>
                   <p className="text-[8px] font-black text-slate-400 uppercase tracking-widest leading-tight">FTE Variance</p>
                   <p className="text-sm font-black text-white font-mono">{analysisResult?.grounded?.labor ? `-${analysisResult.grounded.labor.reduce((acc,l)=>acc+l.gap,0)}` : '0'}</p>
                 </div>
              </div>
              <div className="px-5 py-3 bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 text-right min-w-[140px] drop-shadow-xl flex items-center gap-4">
                 <div className="p-2 bg-rose-500/20 rounded-lg text-rose-400"><DollarSign size={16}/></div>
                 <div>
                   <p className="text-[8px] font-black text-slate-400 uppercase tracking-widest leading-tight">Rev Risk</p>
                   <p className="text-sm font-black text-white font-mono">${analysisResult?.grounded?.finance?.estimated_revenue_at_risk?.toLocaleString() || '0'}</p>
                 </div>
              </div>
              <div className="px-5 py-3 bg-blue-600/20 backdrop-blur-xl rounded-2xl border border-blue-500/30 text-right min-w-[140px] drop-shadow-xl flex items-center gap-4 shadow-lg shadow-blue-500/10">
                 <div className="p-2 bg-blue-500 text-white rounded-lg"><Shield size={16}/></div>
                 <div>
                   <p className="text-[8px] font-black text-blue-200 uppercase tracking-widest leading-tight">Arbiter Status</p>
                   <p className="text-sm font-black text-white font-mono">{analysisResult ? 'ACTIVE' : 'STANDBY'}</p>
                 </div>
              </div>
           </div>
        </header>

        <div className="flex-1 overflow-y-auto p-10 custom-scrollbar text-slate-100">
          <div className="max-w-[1600px] mx-auto space-y-10">
            
            {activeView === 'arbiter' && (
              <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700 mt-4">
                <div className="col-span-12">
                   <div className="bg-black/60 backdrop-blur-2xl rounded-[3rem] p-12 border border-white/10 shadow-2xl relative overflow-hidden">
                      <div className="absolute -right-20 -top-20 opacity-5 pointer-events-none"><Shield size={400} className="text-blue-500" /></div>
                      <div className="absolute top-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-50"/>
                      <div className="max-w-6xl relative z-10">
                        <div className="flex items-center gap-4 mb-4">
                          <div className="px-3 py-1 bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-full text-[10px] font-black tracking-widest uppercase">Arbiter Override Active</div>
                          <div className="px-3 py-1 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded-full text-[10px] font-black tracking-widest uppercase">Operator Mode Locked</div>
                        </div>
                        <h2 className="text-4xl md:text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-blue-200 italic tracking-tighter mb-4 leading-tight drop-shadow-lg">
                          "{analysisResult?.synthesized?.audit_explanation || 'Awaiting Floor Interception...'}"
                        </h2>
                        
                        {(analysisResult?.synthesized?.invention_metrics?.primary_objective || analysisResult?.synthesized?.invention_metrics?.primary_conflict) && (
                          <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="bg-white/5 border-t border-white/20 border-b-0 border-x-0 rounded-[2rem] p-8 shadow-inner backdrop-blur-md relative overflow-hidden group">
                               <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                               <p className="text-[10px] font-black text-emerald-400 tracking-[0.2em] uppercase mb-4 flex items-center gap-2"><Target size={14}/> Enforced Objective</p>
                               <p className="text-lg font-bold text-white leading-relaxed">{analysisResult?.synthesized?.invention_metrics?.primary_objective}</p>
                            </div>
                            <div className="bg-white/5 border-t border-white/20 border-b-0 border-x-0 rounded-[2rem] p-8 shadow-inner backdrop-blur-md relative overflow-hidden group">
                               <div className="absolute inset-0 bg-gradient-to-br from-rose-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                               <p className="text-[10px] font-black text-rose-400 tracking-[0.2em] uppercase mb-4 flex items-center gap-2"><AlertOctagon size={14}/> Tradeoff Accepted</p>
                               <p className="text-lg font-bold text-white leading-relaxed">{analysisResult?.synthesized?.invention_metrics?.primary_conflict}</p>
                            </div>
                          </div>
                        )}
                      </div>
                   </div>
                </div>
              </div>
            )}
            
            {activeView === 'define' && (
              <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="col-span-12 lg:col-span-8 space-y-8">
                  <section className="bg-white rounded-[2.5rem] shadow-xl border border-slate-100 p-10 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-8 opacity-[0.03] transition-opacity"><Sparkles size={200} /></div>
                    <div className="flex items-center gap-3 mb-8"><div className="p-3 bg-blue-50 text-blue-600 rounded-2xl"><Search size={24} /></div><h3 className="text-lg font-black uppercase tracking-[0.2em] text-slate-800">The Situation // Action Plan</h3></div>
                    <div className="text-xl font-medium text-slate-600 leading-relaxed italic border-l-4 border-blue-500 pl-8 ml-2">{analysisResult?.synthesized?.audit_explanation || 'Reports combined. Reading the floor status now.'}</div>
                    <div className="mt-8 px-8 py-4 bg-slate-50 rounded-2xl border border-slate-100 flex items-center justify-between">
                       <div className="flex items-center gap-3"><Database size={14} className="text-blue-500"/><span className="text-[10px] font-black uppercase text-slate-400">Grounding Source:</span><span className="text-xs font-bold text-slate-700">{analysisResult?.statistics?.ingested_source || 'Direct Manual Input'}</span></div>
                       <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"/><span className="text-[9px] font-black uppercase text-emerald-600 tracking-widest">Active Link</span></div>
                    </div>
                  </section>
                  <section className="bg-white rounded-[2.5rem] shadow-lg border border-slate-100 p-10">
                    <h4 className="text-xs font-black text-slate-400 uppercase tracking-[0.3em] mb-10 flex items-center gap-3"><Milestone size={18} className="text-blue-500" /> Human Response Checklist</h4>
                    <div className="grid grid-cols-4 gap-4">
                      {(analysisResult?.synthesized?.recovery_plan || [{step: 1, action: 'Analyzing...', rationale: 'Waiting for Arbitrator.'}]).map((s, idx) => (
                        <div key={idx} className="relative group text-left">
                          <div className={`p-6 rounded-3xl border h-full transition-all duration-500 ${idx === 0 ? 'bg-slate-900 text-white border-slate-800 shadow-2xl' : 'bg-slate-50 border-slate-100 text-slate-400'}`}>
                            <div className="text-[9px] font-black opacity-50 mb-3 uppercase tracking-widest flex items-center gap-2"><div className="w-4 h-4 rounded-full bg-white/20 flex items-center justify-center text-[8px]">{idx+1}</div> Step</div>
                            <div className="text-sm font-black uppercase tracking-tight mb-2 leading-tight">{s.action}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </section>
                </div>
                <div className="col-span-12 lg:col-span-4 space-y-8">
                  <section className="bg-white rounded-[2.5rem] p-10 border border-slate-100 shadow-lg"><h4 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-8 flex items-center gap-3"><BarChart3 size={18} className="text-rose-500" /> Root Cause Pareto</h4><ParetoChart data={paretoData} /></section>
                  <section className="bg-[#0f172a] rounded-[2.5rem] p-10 text-white shadow-2xl relative overflow-hidden ring-1 ring-white/10">
                    <div className="absolute top-0 right-0 p-6 opacity-5"><ShieldAlert size={150} /></div>
                    <h3 className="text-xs font-black mb-8 flex items-center gap-3 uppercase tracking-[0.2em] text-blue-400"><AlertTriangle size={18}/> Rules Broken</h3>
                    <div className="space-y-4 h-64 overflow-y-auto custom-scrollbar pr-2">
                      {analysisResult?.violations?.map((v, i) => (
                        <div key={i} className="p-5 bg-white/5 rounded-2xl border border-white/10 hover:border-blue-500/50 transition-all group"><p className="text-xs font-black uppercase tracking-tight text-blue-100 mb-1">{v.message}</p><p className="text-[10px] font-mono text-slate-500 uppercase">{v.expression}</p></div>
                      )) || <div className="py-10 text-center opacity-30 italic text-sm">No rules broken. Systems nominal.</div>}
                    </div>
                  </section>
                </div>
              </div>
            )}

            {activeView === 'measure' && (
              <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                 <div className="col-span-12 bg-white rounded-[3rem] p-12 border border-slate-100 shadow-lg">
                    <h2 className="text-2xl font-black uppercase tracking-tight mb-8">Live Floor Sensors</h2>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                       {analysisResult?.state?.production?.slice(0, 8).map(p => (
                         <div key={p.node_id} className="p-6 bg-slate-50 rounded-2xl border border-slate-100">
                            <div className="flex justify-between items-center mb-4"><p className="text-[10px] font-black text-slate-400 uppercase">{p.node_id}</p>{p.status !== 'NORMAL' ? <AlertTriangle size={14} className="text-rose-500 animate-pulse"/> : <CheckCircle2 size={14} className="text-emerald-500"/>}</div>
                            <div className="flex items-end gap-2 mb-4"><p className="text-3xl font-black text-slate-800">{p.uph_actual.toFixed(0)}</p><p className="text-[10px] font-bold text-slate-400 mb-1">UPH</p></div>
                            <div className="space-y-3">
                               <div className="flex justify-between items-center text-[9px] font-bold uppercase"><span className="text-slate-400">Oven Temp</span><span className={p.node_id === 'D4' ? 'text-rose-500' : 'text-slate-600'}>{p.node_id === 'D4' ? '382°F' : '360°F'}</span></div>
                               <div className="flex justify-between items-center text-[9px] font-bold uppercase"><span className="text-slate-400">Belt Speed</span><span className={p.node_id === 'D18' ? 'text-rose-500' : 'text-slate-600'}>{p.node_id === 'D18' ? '12m/s' : '45m/s'}</span></div>
                            </div>
                         </div>
                       ))}
                    </div>
                 </div>
              </div>
            )}

            {activeView === 'analyze' && (
               <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                  <div className="col-span-12 lg:col-span-8 space-y-8">
                    <div className="bg-white rounded-[3rem] p-10 border border-slate-100 shadow-sm">
                      <h3 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-8 flex items-center gap-2"><BarChart3 size={16} className="text-blue-500"/> Statistical Distribution</h3>
                      <div className="h-64 bg-slate-50 rounded-2xl flex items-center justify-center border border-dashed border-slate-200 text-center px-8 relative overflow-hidden"><DistributionChart pValue={analysisResult?.statistics?.p_value || 0.5} /></div>
                      <div className="mt-8 p-10 bg-slate-900 rounded-[2rem] text-white relative overflow-hidden">
                         <div className="absolute top-0 right-0 p-8 opacity-10"><Search size={100}/></div>
                         <h4 className="text-[10px] font-black text-blue-400 uppercase tracking-[0.2em] mb-4">AI Root Cause Analysis</h4>
                         <p className="text-lg font-bold leading-relaxed italic text-slate-200">"{analysisResult?.audit_explanation || "Calculating correlations..."}"</p>
                      </div>
                    </div>
                  </div>
                  <div className="col-span-12 lg:col-span-4">
                    <div className="bg-[#0f172a] rounded-[3rem] p-10 text-white shadow-xl h-full flex flex-col">
                      <h3 className="text-xs font-black uppercase tracking-widest text-blue-400 mb-8 flex items-center gap-2"><ShieldCheck size={16}/> Problem Concentration</h3>
                      <div className="flex-1 min-h-[400px]"><ParetoChart data={paretoData} /></div>
                    </div>
                  </div>
               </div>
            )}

            {activeView === 'improve' && (
              <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                 <div className="col-span-12 lg:col-span-8">
                    <div className="bg-white rounded-[3rem] p-12 border border-slate-100 shadow-xl relative overflow-hidden">
                       <h2 className="text-2xl font-black uppercase tracking-tight mb-8 flex items-center gap-3"><ListChecks size={24} className="text-blue-600"/> The Action Plan</h2>
                       <div className="space-y-6">
                          {(analysisResult?.synthesized?.recovery_plan || [
                            { step: 1, action: 'Waiting for AI Synthesis', rationale: 'Engine resolving physical constraints...', decision_audit_log: 'Pending negotiation...' }
                          ]).map((item, i) => (
                            <div key={i} className="group relative">
                               <div className="flex items-center gap-6 p-8 bg-slate-50 rounded-3xl border border-slate-100 group-hover:border-blue-500/30 transition-all">
                                  <div className="w-16 h-14 bg-white rounded-2xl flex items-center justify-center shadow-sm text-2xl"><Users className="text-blue-500"/></div>
                                  <div className="flex-1">
                                     <div className="flex items-center gap-2 mb-1"><p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Step 0{i+1}</p><span className="text-[8px] bg-blue-100 text-blue-600 px-2 py-0.5 rounded-full font-black uppercase tracking-tighter">Verified</span></div>
                                     <p className="text-sm font-black text-slate-800 mb-2">{item.action}</p>
                                     <div className="bg-white/60 border border-slate-200 rounded-xl p-4 italic text-xs text-slate-500 leading-relaxed shadow-inner"><span className="font-black text-[9px] text-blue-500 not-italic uppercase mr-2 tracking-widest underline">Rationale:</span>"{item.rationale || item.decision_audit_log}"</div>
                                  </div>
                                  <div className="w-10 h-10 rounded-full border-2 border-slate-200 group-hover:border-blue-500 transition-colors flex items-center justify-center"><CheckCircle2 size={20} className="text-white group-hover:text-blue-500 transition-colors"/></div>
                               </div>
                            </div>
                          ))}
                       </div>
                    </div>
                 </div>
                 <div className="col-span-12 lg:col-span-4 space-y-8">
                    <div className="bg-slate-900 rounded-[2.5rem] p-10 text-white shadow-2xl relative overflow-hidden"><div className="absolute -right-10 -bottom-10 opacity-10"><Zap size={200}/></div><h4 className="text-xs font-black uppercase tracking-widest text-blue-400 mb-10 flex items-center gap-2"><Zap size={16}/> System Confidence</h4><div className="space-y-10"><div><p className="text-[10px] font-black text-slate-500 uppercase mb-3">Calculated Fitness Score</p><div className="flex items-end gap-3"><p className="text-5xl font-black text-emerald-400">{analysisResult?.evaluation_metrics?.score || '0.0'}</p></div></div><div><p className="text-[10px] font-black text-slate-400 uppercase mb-3">Ontology Status</p><div className="w-full bg-slate-800 h-3 rounded-full overflow-hidden mb-2"><div className={`h-full w-[100%] shadow-lg ${analysisResult?.domain_data?.ontology_status ? 'bg-rose-500' : 'bg-emerald-500'}`} /></div><p className="text-[10px] font-bold text-slate-400">{analysisResult?.domain_data?.ontology_status || 'Physics Bounds Loaded & Verified'}</p></div></div></div>
                 </div>
              </div>
            )}

            {activeView === 'control' && (
              <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                 <div className="col-span-12 lg:col-span-8">
                    <div className="bg-white rounded-[3rem] p-12 border border-slate-100 shadow-xl relative overflow-hidden">
                       <h2 className="text-2xl font-black uppercase tracking-tight mb-8 flex items-center gap-3"><PhoneCall size={24} className="text-blue-600"/> Floor Dispatch Center</h2>
                       <div className="space-y-6">
                          {(analysisResult?.synthesized?.recovery_plan || []).map((step, i) => (
                            <div key={i} className="p-8 bg-blue-50 border border-blue-100 rounded-[2rem] flex items-center justify-between">
                              <div><p className="text-xs font-black text-blue-600 uppercase mb-1">Generated Action</p><p className="text-lg font-black text-slate-800">{step.action}</p><p className="text-sm font-bold text-slate-500">{step.rationale}</p></div>
                              <button onClick={() => executeDispatch(`act_${i}`, 'SYS_ALRT', 'OPERATOR')} className={`px-8 py-4 ${dispatchStatus[`act_${i}`] === 'SENT' ? 'bg-emerald-500' : 'bg-blue-600'} text-white font-black rounded-2xl transition-all shadow-lg active:scale-95`}>{dispatchStatus[`act_${i}`] || 'DISPATCH'}</button>
                            </div>
                          ))}
                       </div>
                    </div>
                 </div>
                 <div className="col-span-12 lg:col-span-4 space-y-8"><div className="bg-white rounded-[2.5rem] p-10 shadow-lg border border-slate-100"><h4 className="text-xs font-black uppercase tracking-widest text-slate-400 mb-6 flex items-center gap-2"><Cog size={16}/> Machine Connections</h4><div className="space-y-4">{['PLC_MODBUS_OVEN', 'WMS_DB_GATEWAY', 'ADP_HR_SYNC', 'AS400_ELKHART'].map(s => (<div key={s} className="flex justify-between items-center p-4 bg-slate-50 rounded-2xl"><span className="text-[10px] font-black text-slate-600">{s}</span><div className="flex items-center gap-2"><div className="w-1.5 h-1.5 bg-emerald-500 rounded-full" /><span className="text-[9px] font-black text-emerald-600 uppercase">Connected</span></div></div>))}</div></div></div>
              </div>
            )}

            {activeView === 'finance' && (
              <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                 <div className="col-span-12 lg:col-span-8">
                    <div className="bg-white rounded-[3rem] p-12 border border-slate-100 shadow-xl">
                       <div className="flex justify-between items-start mb-8"><h2 className="text-2xl font-black uppercase tracking-tight flex items-center gap-3"><DollarSign size={24} className="text-emerald-600"/> BP174 Reconciliation</h2><div className={`px-4 py-2 ${analysisResult?.report_context?.type === 'BP174_AS400' ? 'bg-slate-900' : 'bg-slate-200'} text-white rounded-xl text-[9px] font-black uppercase tracking-widest`}>{analysisResult?.report_context?.type === 'BP174_AS400' ? 'AS400 LINKED' : 'MANUAL MODE'}</div></div>
                       <div className="space-y-6"><div className="grid grid-cols-2 gap-6"><div className="p-8 bg-slate-50 rounded-3xl border border-slate-100 text-center"><p className="text-[10px] font-black text-slate-400 uppercase mb-2">Theoretical Yield</p><p className="text-3xl font-black text-slate-800">{analysisResult?.report_context?.planned_units?.toLocaleString() || '0'}</p><p className="text-[10px] font-bold text-slate-400 mt-1 uppercase">Units Scheduled</p></div><div className="p-8 bg-rose-50 rounded-3xl border border-rose-100 text-center"><p className="text-[10px] font-black text-rose-400 uppercase mb-2">Actual Scaled</p><p className="text-3xl font-black text-rose-600">{analysisResult?.report_context?.actual_units?.toLocaleString() || '0'}</p><p className="text-[10px] font-bold text-rose-400 mt-1 uppercase text-rose-400">-{analysisResult?.report_context?.total_shortage_units?.toLocaleString() || '0'} Units Lost</p></div></div>
                          <div className="p-8 bg-white border border-slate-100 rounded-3xl shadow-sm"><h4 className="text-xs font-black uppercase text-slate-400 mb-6">Top SKU Shortages</h4><div className="space-y-4">{(analysisResult?.report_context?.top_losses || []).map((v, i) => (<div key={i} className="flex items-center gap-4"><div className="w-48 text-[9px] font-black text-slate-500 uppercase truncate">{v['Product Description'] || v.name}</div><div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden"><div className="bg-rose-500 h-full" style={{width: `${Math.min(100, (Math.abs(v['Over/Short'] || v.variance) / 8000) * 100)}%`}} /></div><div className="text-[10px] font-mono font-black text-slate-700">{(v['Over/Short'] || v.variance).toLocaleString()}</div></div>))}{!(analysisResult?.report_context?.top_losses) && <div className="text-slate-400 italic text-sm py-4">No top losses tracked.</div>}</div></div></div>
                    </div>
                 </div>
                 <div className="col-span-12 lg:col-span-4 space-y-8"><div className="bg-slate-900 rounded-[2.5rem] p-10 text-white shadow-2xl h-full flex flex-col justify-center text-center"><h4 className="text-xs font-black uppercase tracking-widest text-blue-400 mb-8 flex items-center gap-2 justify-center"><TrendingUp size={16}/> Margin Recovery Plan</h4><p className="text-sm font-bold text-slate-300 leading-relaxed mb-8 italic">"{analysisResult?.synthesized?.audit_explanation || "No financial recovery projections available."}"</p></div></div>
              </div>
            )}

            {activeView === 'logistics' && (
              <div className="grid grid-cols-12 gap-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
                 <div className="col-span-12 lg:col-span-8"><div className="bg-white rounded-[3rem] p-12 border border-slate-100 shadow-xl"><h2 className="text-2xl font-black uppercase tracking-tight mb-8 flex items-center gap-3"><Truck size={24} className="text-blue-600"/> WMS Outbound Status</h2><div className="space-y-4">{(analysisResult?.logistics?.loads || []).map((load, i) => (<div key={i} className="p-6 bg-slate-50 rounded-2xl border border-slate-100 flex items-center gap-6"><div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center font-black text-[10px] text-blue-600 shadow-sm border border-slate-100">{load.dock || `DOCK ${i+1}`}</div><div className="flex-1"><div className="flex justify-between items-center mb-2"><p className="text-sm font-black text-slate-800 uppercase tracking-tight">{load.destination || load.target}</p><p className="text-[10px] font-black text-slate-400 font-mono">{load.time || 'Pending'}</p></div><div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden"><div className={`h-full ${load.progress === 100 ? 'bg-emerald-500' : 'bg-blue-500'} transition-all`} style={{width: `${load.progress || 0}%`}} /></div></div><div className={`px-4 py-2 rounded-xl text-[9px] font-black uppercase ${load.status === 'STAGED' ? 'bg-emerald-100 text-emerald-700' : 'bg-blue-100 text-blue-700'}`}>{load.status || 'PENDING'}</div></div>))}{(analysisResult?.logistics?.loads || []).length === 0 && <p className="text-slate-400 italic text-sm py-4">No outbound logistics data actively tracking.</p>}</div></div></div>
                 <div className="col-span-12 lg:col-span-4 space-y-8"><div className="bg-white rounded-[2.5rem] p-10 border border-slate-100 shadow-lg"><h4 className="text-xs font-black uppercase text-slate-400 mb-6 flex items-center gap-2"><Globe size={16} className="text-indigo-500"/> Carrier Performance</h4><div className="space-y-4">{['Swift_Transport', 'JB_Hunt', 'FedEx_Freight'].map(c => (<div key={c} className="flex justify-between items-center p-4 bg-slate-50 rounded-2xl"><span className="text-[10px] font-black text-slate-600">{c}</span><span className="text-[9px] font-black text-emerald-600 uppercase">On Time</span></div>))}</div></div></div>
              </div>
            )}



            {activeView === 'facility' && (
              <FacilityCommand 
                viewMode={viewMode}
                analysisResult={analysisResult} 
                apiBase={API_BASE}
                onSimulate={(s) => { 
                  setMessages(prev => [...prev, {role: 'ai', text: `SIMULATION: ${s} scenario initiated. Adjusting labor coefficients.`}]); 
                  runSynthesis(); 
                }} 
              />
            )}

          </div>
        </div>
      </main>
    </div>
  );
}
