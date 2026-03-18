import React, { useState, useEffect } from 'react';
import { 
  Activity, Clock, Truck, Box, AlertTriangle, 
  CheckCircle2, ChevronRight, Settings2, Map as MapIcon,
  Search, ShieldCheck, Zap, Info
} from 'lucide-react';

const DOCK_LAYOUT = [
  { id: 1, label: 'Recon' }, { id: 2, label: 'Recycle' }, { id: 3, label: 'Special' },
  { id: 4, label: 'Swing' }, { id: 5, label: 'Inv OB' }, { id: 6, label: 'Inv OB' },
  { id: 7, label: 'Special' }, { id: 8, label: 'OPEN' }, { id: 9, label: 'Inbound' },
  { id: 10, label: 'FCR' }, { id: 11, label: 'FJA' }, { id: 12, label: 'KC/Riverside' },
  { id: 13, label: 'N Aurora (1)' }, { id: 14, label: 'N Aurora (2)' }, { id: 15, label: 'S Bend (1)' },
  { id: 16, label: 'S Bend (2)' }, { id: 17, label: 'Inbound' }, { id: 18, label: 'BROKEN' }
];

export default function FacilityCommand({ analysisResult, onSimulate, viewMode = 'actual', apiBase }) {
  const [uphOverride, setUphOverride] = useState(4132);
  const [traysPerStack, setTraysPerStack] = useState(170);
  const [currentTime, setCurrentTime] = useState(new Date());

  // BIFURCATED DATA MAPPING
  const isSim = viewMode === 'simulation';
  const data = isSim ? analysisResult?.synthesized : analysisResult?.grounded;
  
  // Grounded data is ALWAYS the production metrics and labor gaps
  const production = analysisResult?.grounded?.production || [];
  const labor = analysisResult?.grounded?.labor || [];
  
  const enrichment = analysisResult?.synthesized?.enrichment_signals || [];
  const confidence = analysisResult?.domain_confidence || [];

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const nextLoad = production?.find(l => l.status === 'DELAY' || l.status === 'CRITICAL') || production?.[0];

  return (
    <div className={`space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700 ${isSim ? 'simulation-active' : ''}`}>
      {/* Top Priority Ribbon */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className={`lg:col-span-2 bg-white rounded-2xl shadow-sm border-l-8 ${isSim ? 'border-indigo-600' : 'border-amber-500'} p-6 flex flex-col justify-between group hover:shadow-md transition-all relative overflow-hidden`}>
          {isSim && <div className="absolute inset-0 bg-indigo-500/5 pointer-events-none animate-pulse" />}
          <div className="flex justify-between items-start relative">
            <span className={`text-[10px] font-black uppercase tracking-widest flex items-center gap-1 ${isSim ? 'text-indigo-600' : 'text-amber-600'}`}>
              {isSim ? <Sparkles size={12}/> : <Activity size={12}/>} {isSim ? 'Projected Outcome' : 'Next Critical Node'}
            </span>
            <div className={`px-2 py-0.5 text-[10px] font-bold rounded uppercase ${isSim ? 'bg-indigo-100 text-indigo-800' : 'bg-amber-100 text-amber-800 animate-pulse'}`}>
              {isSim ? 'AI Prediction' : 'Live Production'}
            </div>
          </div>
          <h2 className="text-4xl font-black text-slate-900 mt-2 tracking-tight relative">
            {nextLoad?.node_id || '---'}
          </h2>
          <div className="grid grid-cols-3 gap-4 mt-4 relative">
            <div>
              <p className="text-[10px] text-slate-400 uppercase font-black">Plan</p>
              <p className="text-xl font-bold text-slate-700">{nextLoad?.planned_units || '0'}</p>
            </div>
            <div>
              <p className="text-[10px] text-slate-400 uppercase font-black">{isSim ? 'Projected' : 'Actual'}</p>
              <p className={`text-xl font-bold ${isSim ? 'text-indigo-600' : 'text-amber-600'}`}>{nextLoad?.actual_units || '0'}</p>
            </div>
            <div>
              <p className="text-[10px] text-slate-400 uppercase font-black">UPH</p>
              <p className="text-xl font-bold text-slate-700">{nextLoad?.uph_actual?.toFixed(0) || '0'}</p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-slate-100 flex justify-between items-center text-[10px] text-slate-400 font-bold uppercase tracking-tighter relative">
            <span>{isSim ? 'Simulation Logic v2.5' : 'Deterministic Math via Production Engine'}</span>
            <span className={nextLoad?.status === 'DELAY' ? 'text-rose-500 animate-pulse' : 'text-emerald-500'}>
              {nextLoad?.status || 'NORMAL'}
            </span>
          </div>
        </div>

        {/* Real-time KPIs */}
        <div className={`rounded-2xl p-6 text-white flex flex-col justify-between shadow-xl ring-1 ring-white/10 relative overflow-hidden ${isSim ? 'bg-indigo-900' : 'bg-slate-900'}`}>
          {isSim && <div className="absolute inset-0 bg-white/5 pointer-events-none" style={{ backgroundImage: 'linear-gradient(45deg, transparent 48%, rgba(255,255,255,0.1) 50%, transparent 52%)', backgroundSize: '10px 10px' }} />}
          <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest flex items-center gap-1 relative">
            {isSim ? <Sparkles size={12}/> : <Clock size={12}/>} {isSim ? 'Simulation Forecast' : 'Shift Horizon'}
          </span>
          <div className="mt-2 relative">
            <div className="flex justify-between text-[11px] mb-1 font-black uppercase tracking-wider">
              <span>Throughput</span>
              <span>{isSim ? (analysisResult?.synthesized?.forecasted_otif || 0).toFixed(1) : ((production?.reduce((acc, p) => acc + p.actual_units, 0) / production?.reduce((acc, p) => acc + p.planned_units, 1)) * 100 || 0).toFixed(1)}%</span>
            </div>
            <div className="w-full bg-black/30 h-2.5 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-1000 ${isSim ? 'bg-indigo-400 shadow-[0_0_15px_rgba(129,140,248,0.5)]' : 'bg-amber-500 shadow-[0_0_15px_rgba(245,158,11,0.5)]'}`} 
                style={{ width: `${isSim ? analysisResult?.synthesized?.forecasted_otif : (production?.reduce((acc, p) => acc + p.actual_units, 0) / production?.reduce((acc, p) => acc + p.planned_units, 1)) * 100}%` }}
              />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2 mt-4 text-center relative">
             <div className="bg-white/5 p-2 rounded-lg border border-white/5">
                <p className="text-[8px] text-slate-500 uppercase font-black">{isSim ? 'Rec. Opp' : 'Revenue Risk'}</p>
                <p className={`text-xs font-bold ${isSim ? 'text-indigo-300' : 'text-amber-400'}`}>${analysisResult?.grounded?.finance?.estimated_revenue_at_risk?.toLocaleString() || '0'}</p>
             </div>
             <div className="bg-white/5 p-2 rounded-lg border border-white/5">
                <p className="text-[8px] text-slate-500 uppercase font-black">Efficiency</p>
                <p className="text-xs font-bold text-emerald-400">{(analysisResult?.grounded?.finance?.labor_efficiency_ratio * 100 || 0).toFixed(0)}%</p>
             </div>
             <div className="bg-white/5 p-2 rounded-lg border border-white/5">
                <p className="text-[8px] text-slate-500 uppercase font-black">Horizon</p>
                <p className="text-xs font-bold text-rose-400">{isSim ? analysisResult?.synthesized?.simulated_recovery_days : analysisResult?.grounded?.finance?.recovery_horizon_days || 0}d</p>
             </div>
          </div>
        </div>

        {/* Intelligence Scoping (THE SCOUT) */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 flex flex-col justify-between overflow-hidden relative">
          <div className={`absolute -top-6 -right-6 w-24 h-24 rounded-full opacity-50 blur-2xl ${isSim ? 'bg-indigo-50' : 'bg-amber-50'}`}/>
          <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest flex items-center gap-1 relative">
            <Search size={12} className={isSim ? 'text-indigo-500' : 'text-amber-500'}/> {isSim ? 'Synthetic Reasoning' : 'Scout Enrichment'}
          </span>
          <div className="mt-3 space-y-2 relative">
             {enrichment.slice(0, 3).map((signal, i) => (
               <div key={i} className="flex items-center gap-2 text-[10px] font-bold text-slate-600 bg-slate-50 px-2 py-1 rounded-md border border-slate-100">
                  <div className={`w-1 h-1 rounded-full ${isSim ? 'bg-indigo-400' : 'bg-amber-400'}`}/> {signal}
               </div>
             ))}
          </div>
          <div className="mt-4 pt-3 border-t border-slate-50">
             <div className="flex justify-between items-center text-[9px] font-black uppercase text-slate-400">
                <span>{isSim ? 'Inference Depth' : 'Domain Confidence'}</span>
                <span className={isSim ? 'text-indigo-600' : 'text-amber-600'}>{(confidence[0]?.score * 100 || 0).toFixed(0)}% Match</span>
             </div>
             <div className="w-full bg-slate-100 h-1.5 rounded-full mt-1 overflow-hidden">
                <div className={`h-full ${isSim ? 'bg-indigo-400' : 'bg-amber-400'}`} style={{ width: `${(confidence[0]?.score * 100 || 0)}%` }}/>
             </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-2 space-y-6">
          {/* Intelligence Playbook */}
          <div className={`bg-white rounded-2xl shadow-sm border-t-4 ${isSim ? 'border-indigo-600' : 'border-amber-500'} overflow-hidden`}>
            <div className="px-8 py-6">
               <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center gap-2">
                    <div className={`p-2 rounded-lg ${isSim ? 'bg-indigo-100 text-indigo-600' : 'bg-amber-100 text-amber-600'}`}>
                      <Zap size={18}/>
                    </div>
                    <div>
                      <h3 className="text-xs font-black uppercase tracking-widest text-slate-800">{isSim ? 'AI Synthesis Roadmap' : 'Strategic Shift Playbook'}</h3>
                      <p className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">Powered by {analysisResult?.synthesized?.invention_metrics?.framework || 'Standard Operations'}</p>
                    </div>
                  </div>
                  
                  <div className="flex gap-4">
                    <div className="text-right">
                       <p className="text-[8px] font-black text-slate-400 uppercase">Agentic Consensus</p>
                       <div className={`flex items-center gap-1 text-[10px] font-black ${analysisResult?.synthesized?.invention_metrics?.agentic_consensus ? 'text-indigo-500' : 'text-rose-500'}`}>
                          {analysisResult?.synthesized?.invention_metrics?.agentic_consensus ? 'UNIFIED' : 'NEGOTIATING'}
                       </div>
                    </div>
                    <div className="text-right">
                       <p className="text-[8px] font-black text-slate-400 uppercase">Safety Gate</p>
                       <div className={`flex items-center gap-1 text-[10px] font-black ${analysisResult?.synthesized?.invention_metrics?.safety?.includes('VALIDATED') ? 'text-emerald-500' : 'text-rose-500'}`}>
                          <ShieldCheck size={12}/> {analysisResult?.synthesized?.invention_metrics?.safety || 'PENDING'}
                       </div>
                    </div>
                  </div>
               </div>

               {/* Step-by-Step Strategic Plan with Agent Audit */}
               <div className="space-y-4 mb-6">
                  {analysisResult?.synthesized?.recovery_plan && Array.isArray(analysisResult.synthesized.recovery_plan) ? (
                    analysisResult.synthesized.recovery_plan.map((step, i) => (
                      <div key={i} className="flex gap-4 group relative">
                         <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-black border-2 ${isSim ? 'border-indigo-100 bg-indigo-50 text-indigo-600' : 'border-amber-100 bg-amber-50 text-amber-600'}`}>
                            {i+1}
                         </div>
                         <div className="flex-1 pb-4 border-b border-slate-50 group-last:border-0">
                            <div className="flex justify-between items-start">
                              <p className="text-[11px] font-black text-slate-800 uppercase leading-none mb-1">{step.action}</p>
                              {/* Agent Voting Dots */}
                              <div className="flex gap-1">
                                <div className={`w-1.5 h-1.5 rounded-full ${step.agent_votes?.efficiency === 'YES' ? 'bg-emerald-400' : 'bg-rose-400'}`} title="Efficiency Agent" />
                                <div className={`w-1.5 h-1.5 rounded-full ${step.agent_votes?.safety === 'YES' ? 'bg-emerald-400' : 'bg-rose-400'}`} title="Safety Agent" />
                                <div className={`w-1.5 h-1.5 rounded-full ${step.agent_votes?.resilience === 'YES' ? 'bg-emerald-400' : 'bg-rose-400'}`} title="Resilience Agent" />
                              </div>
                            </div>
                            <p className="text-[10px] font-medium text-slate-500 leading-tight italic mb-2">{step.rationale}</p>
                            
                            {/* Execution Controls (The Feedback Loop) */}
                            <div className="flex gap-2 mb-2">
                               <button 
                                 onClick={() => {
                                   fetch(`${apiBase}/api/outcome`, {
                                     method: 'POST',
                                     headers: { 'Content-Type': 'application/json' },
                                     body: JSON.stringify({ decision_id: `step-${i}-${Date.now()}`, action: step.action, status: 'SUCCESS' })
                                   });
                                   alert('Experience Anchored: Success recorded.');
                                 }}
                                 className="px-2 py-1 bg-emerald-50 text-emerald-600 border border-emerald-100 rounded text-[8px] font-black uppercase hover:bg-emerald-100 transition-all"
                               >
                                 Executed (Worked)
                               </button>
                               <button 
                                 onClick={() => {
                                   fetch(`${apiBase}/api/outcome`, {
                                     method: 'POST',
                                     headers: { 'Content-Type': 'application/json' },
                                     body: JSON.stringify({ decision_id: `step-${i}-${Date.now()}`, action: step.action, status: 'FAILURE' })
                                   });
                                   alert('Experience Anchored: Ineffective result recorded.');
                                 }}
                                 className="px-2 py-1 bg-rose-50 text-rose-600 border border-rose-100 rounded text-[8px] font-black uppercase hover:bg-rose-100 transition-all"
                               >
                                 Ineffective
                               </button>
                            </div>

                            {/* Decision Audit Log (ISO 42001) */}
                            <div className="bg-slate-50 p-2 rounded border border-slate-100 hidden group-hover:block animate-in fade-in duration-300">
                               <p className="text-[8px] font-black text-slate-400 uppercase mb-1">Audit Rationale (ISO 42001)</p>
                               <p className="text-[9px] text-slate-600 font-medium leading-tight">{step.decision_audit_log}</p>
                            </div>
                         </div>
                      </div>
                    ))
                  ) : (
                    <div className="prose prose-slate prose-sm max-w-none">
                      <p className="text-slate-600 leading-relaxed font-medium whitespace-pre-wrap">
                        {analysisResult?.synthesized?.audit_explanation || 'Ingesting facility signals and running deterministic simulations...'}
                      </p>
                    </div>
                  )}
               </div>
            </div>
          </div>

          {/* Operational Node Table */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="bg-slate-50 px-6 py-4 border-b border-slate-100 flex justify-between items-center">
               <h3 className="text-xs font-black uppercase text-slate-500 tracking-wider">Production Node Performance</h3>
               <div className="text-[9px] font-bold text-slate-400 uppercase flex items-center gap-2">
                 <div className="w-2 h-2 bg-emerald-500 rounded-full"/> {isSim ? 'Simulated via ML Kernel' : 'Synchronized with Platform Core'}
               </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="text-[9px] font-black uppercase text-slate-400 border-b border-slate-50">
                  <tr>
                    <th className="px-6 py-4">Node ID</th>
                    <th className="px-6 py-4">Planned</th>
                    <th className="px-6 py-4">{isSim ? 'Expected' : 'Actual'}</th>
                    <th className="px-6 py-4 text-center">Staff Gap</th>
                    <th className="px-6 py-4 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {production?.map((prod, idx) => {
                    const lGap = Array.isArray(labor) ? labor?.find(l => l.node_id === prod.node_id) : null;
                    return (
                      <tr key={idx} className="hover:bg-slate-50/80 transition-colors group">
                        <td className="px-6 py-4 font-black text-slate-900 tracking-tight">{prod.node_id}</td>
                        <td className="px-6 py-4 font-bold text-slate-600">{prod.planned_units.toLocaleString()}</td>
                        <td className={`px-6 py-4 font-bold ${isSim ? 'text-indigo-600' : 'text-amber-600'}`}>{prod.actual_units.toLocaleString()}</td>
                        <td className="px-6 py-4">
                           <div className="flex flex-col items-center">
                              <span className={`text-xs font-black ${lGap?.gap > 0 ? 'text-rose-500' : 'text-emerald-500'}`}>
                                {lGap?.gap > 0 ? `-${lGap.gap}` : 'FULL'}
                              </span>
                              <div className="text-[8px] text-slate-400 uppercase font-bold">Heads Required</div>
                           </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase border ${
                            prod.status === 'NORMAL' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' :
                            prod.status === 'DELAY' ? 'bg-amber-50 text-amber-700 border-amber-100' :
                            'bg-rose-50 text-rose-700 border-rose-100'
                          }`}>
                            {prod.status}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Tactical Overview */}
        <div className="space-y-6">
          <div className={`rounded-3xl p-6 text-white border-t-4 shadow-2xl relative overflow-hidden ring-1 ring-white/10 ${isSim ? 'bg-indigo-950 border-indigo-600' : 'bg-slate-900 border-amber-500'}`}>
            <div className="absolute top-0 right-0 p-4 opacity-10">
               {isSim ? <Sparkles size={120}/> : <ShieldCheck size={120}/>}
            </div>
            <h3 className="text-sm font-black mb-6 flex items-center gap-2 uppercase tracking-widest relative">
              <MapIcon size={16} className={isSim ? 'text-indigo-400' : 'text-amber-500'}/> Site Operational Map
            </h3>
            <div className="grid grid-cols-3 gap-3 relative">
              {DOCK_LAYOUT.map(door => {
                const activeNode = production?.find(p => p.node_id.includes(String(door.id)) || p.node_id.includes(door.label));
                return (
                  <div 
                    key={door.id} 
                    className={`relative p-3 rounded-xl border text-center transition-all duration-500 group cursor-help ${
                      activeNode 
                        ? (isSim ? 'bg-indigo-600 border-indigo-500 text-white scale-105 shadow-lg shadow-indigo-600/30' : 'bg-amber-500 border-amber-400 text-slate-900 scale-105 shadow-lg shadow-amber-500/30') 
                        : 'bg-slate-800 border-slate-700 text-slate-500'
                    }`}
                  >
                    <div className="text-[9px] font-black uppercase mb-1">D{door.id}</div>
                    <div className={`text-[8px] font-bold truncate leading-tight ${activeNode ? (isSim ? 'text-white' : 'text-slate-900') : 'text-slate-500'}`}>
                      {door.label}
                    </div>
                    {activeNode && (
                      <div className={`absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full animate-ping opacity-75 ${isSim ? 'bg-indigo-300' : 'bg-white'}`} />
                    )}
                    {/* Tooltip-like effect */}
                    <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900/90 rounded-xl flex items-center justify-center text-[8px] font-black text-white p-1">
                       {activeNode ? `${activeNode.status} / ${activeNode.uph_actual.toFixed(0)} UPH` : 'IDLE'}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* SaaS Simulation Trigger */}
          <div className="bg-gradient-to-br from-indigo-600 to-indigo-800 rounded-3xl p-6 text-white shadow-xl group hover:shadow-2xl transition-all relative overflow-hidden">
             <div className="absolute -bottom-8 -right-8 w-32 h-32 bg-white/10 rounded-full blur-2xl group-hover:bg-white/20 transition-all"/>
             <h4 className="font-black uppercase text-[10px] tracking-widest mb-2 opacity-80 flex items-center gap-1">
               <Zap size={12}/> Scenario Lab
             </h4>
             <p className="text-xs font-bold leading-relaxed mb-4 relative">
               {isSim ? 'Simulation active. Reviewing AI-generated recovery paths.' : `Detected production variance in ${production.filter(p => p.status !== 'NORMAL').length} nodes. Run "Staff Optimization" simulation?`}
             </p>
             <button 
                onClick={() => onSimulate('labor_optimization')}
                className={`w-full font-black text-xs py-3 rounded-xl transition-all shadow-lg active:scale-95 ${isSim ? 'bg-white text-indigo-600' : 'bg-white text-indigo-600 hover:bg-slate-100'}`}
              >
               {isSim ? 'RERUN SIMULATION' : 'RUN AI SIMULATION'}
             </button>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
             <div className="flex items-center gap-2 mb-4 text-slate-400">
               <Info size={14}/>
               <span className="text-[10px] font-black uppercase tracking-widest">Platform Integrity</span>
             </div>
             <p className="text-[10px] font-medium text-slate-500 leading-relaxed">
               {isSim 
                 ? <><span className="text-indigo-600 font-bold">SYNTHESIS MODE:</span> This view displays predicted outcomes. These are not real-world telemetry signals.</>
                 : <><span className="text-amber-600 font-bold">GROUNDED MODE:</span> This view displays actual floor data derived from the ShiftOps Ontology Pack.</>
               }
             </p>
          </div>
        </div>
      </div>
    </div>
  );
}
