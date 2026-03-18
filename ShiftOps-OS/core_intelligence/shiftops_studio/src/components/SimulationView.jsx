// components/SimulationView.jsx
import React, { useState, useMemo, useEffect } from "react";
import ReactFlow, { Background, EdgeText } from "reactflow";
import "reactflow/dist/style.css";
import { Play, Pause, Zap, Server, Database, Globe, Shield, Activity, Terminal as TerminalIcon } from "lucide-react";
import { useSystemPulse } from "../hooks/useSystemPulse";
import { blueprintToFlow } from "../utils/blueprintToFlow";

const SCENARIOS = [
  {
    id: "normal",
    label: "Normal Ops",
    description: "Standard system baseline load.",
    modifiers: { demandMultiplier: 1.0, outageNodes: [] }
  },
  {
    id: "peak",
    label: "Peak Demand",
    description: "2.5x traffic surge across all services.",
    modifiers: { demandMultiplier: 2.5, outageNodes: [] }
  },
  {
    id: "outage",
    label: "Outage Recovery",
    description: "Loss of primary data ingestion node.",
    modifiers: { demandMultiplier: 1.2, outageNodes: ["data_intake"] }
  }
];

export default function SimulationView({ snapshot, onMetricsUpdate }) {
  const [isRunning, setIsRunning] = useState(true);
  const [activeScenario, setActiveScenario] = useState(SCENARIOS[0]);

  const { nodes: initialNodes, edges: initialEdges } = useMemo(() => {
    if (!snapshot?.architecture) return { nodes: [], edges: [] };
    return blueprintToFlow(snapshot.architecture);
  }, [snapshot]);

  const { activeEdge, activeNode, metrics, nodeHeat } = useSystemPulse(snapshot, isRunning);

  // Notify parent of metric changes for the Intelligence Sidebar
  useEffect(() => {
    if (onMetricsUpdate) onMetricsUpdate(metrics);
  }, [metrics, onMetricsUpdate]);

  const flowNodes = useMemo(() => {
    return initialNodes.map(node => {
      const heat = nodeHeat[node.id] || 0;
      const isActive = activeNode === node.id;
      
      return {
        ...node,
        data: {
          ...node.data,
          heat,
          isActive
        },
        style: {
          ...node.style,
          background: heat > 10 ? 'rgba(249, 115, 22, 0.1)' : heat > 5 ? 'rgba(59, 130, 246, 0.1)' : 'rgba(30, 41, 59, 0.5)',
          borderColor: isActive ? '#3b82f6' : heat > 10 ? '#f59e0b' : '#334155',
          boxShadow: isActive ? '0 0 20px rgba(59, 130, 246, 0.4)' : heat > 10 ? '0 0 15px rgba(245, 158, 11, 0.2)' : 'none',
          transition: 'all 0.5s ease'
        }
      };
    });
  }, [initialNodes, nodeHeat, activeNode]);

  const flowEdges = useMemo(() => {
    return initialEdges.map(edge => {
      const isActive = activeEdge === edge.id;
      return {
        ...edge,
        animated: isRunning,
        style: {
          ...edge.style,
          stroke: isActive ? '#3b82f6' : '#1e293b',
          strokeWidth: isActive ? 4 : 2,
          opacity: isActive ? 1 : 0.3,
          transition: 'all 0.3s ease'
        }
      };
    });
  }, [initialEdges, activeEdge, isRunning]);

  if (!flowNodes.length) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500 italic bg-slate-900/50">
        Awaiting system architecture to begin simulation.
      </div>
    );
  }

  return (
    <div className="flex h-full bg-[#0d1117] overflow-hidden">
      {/* 1. Simulation Sidebar */}
      <aside className="w-80 border-r border-slate-800 flex flex-col bg-[#161b22]/50 z-10">
        <div className="p-6 border-b border-slate-800/50">
           <div className="flex items-center justify-between mb-8">
              <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Metabolism Control</h3>
              <div className="flex gap-2">
                <button 
                  onClick={() => setIsRunning(!isRunning)}
                  className={`p-2 rounded-xl transition-all ${isRunning ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'}`}
                >
                  {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
                <button 
                  onClick={() => {
                    const randomNode = flowNodes[Math.floor(Math.random() * flowNodes.length)];
                    alert(`CHAOS INJECTED: Node ${randomNode.id} forcefully terminated. Engine rerouting...`);
                  }}
                  className="p-2 bg-amber-500/10 text-amber-500 rounded-xl hover:bg-amber-500/20 transition-all border border-amber-500/20"
                >
                  <TerminalIcon className="w-4 h-4" />
                </button>
              </div>
           </div>
           
           <div className="space-y-3">
              <h4 className="text-[10px] font-black text-slate-600 uppercase mb-4 tracking-widest">Operational Scenarios</h4>
              {SCENARIOS.map(s => (
                 <button
                    key={s.id}
                    onClick={() => setActiveScenario(s)}
                    className={`w-full text-left p-4 rounded-2xl border transition-all ${
                       activeScenario.id === s.id 
                        ? 'bg-blue-600/10 border-blue-500/50 text-blue-400' 
                        : 'bg-slate-900/40 border-slate-800 text-slate-500 hover:border-slate-700'
                    }`}
                 >
                    <div className="text-[10px] font-black uppercase mb-1">{s.label}</div>
                    <div className="text-[10px] opacity-60 leading-relaxed">{s.description}</div>
                 </button>
              ))}
           </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
           <div>
              <h4 className="text-[10px] font-black text-slate-600 uppercase mb-4 tracking-widest">Behavioral Metrics</h4>
              <div className="grid grid-cols-1 gap-3">
                 <div className="p-4 bg-slate-900/50 rounded-2xl border border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                       <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Throughput</span>
                       <Activity className="w-3.5 h-3.5 text-blue-500/50" />
                    </div>
                    <div className="text-xl font-mono text-blue-400 font-bold">
                       {isRunning ? Math.floor(metrics.throughput * (activeScenario.modifiers.demandMultiplier)) : 0} 
                       <span className="text-[10px] text-slate-600 ml-2">req/s</span>
                    </div>
                 </div>
                 <div className="p-4 bg-slate-900/50 rounded-2xl border border-slate-800">
                    <div className="flex items-center justify-between mb-2">
                       <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Latent Delay</span>
                       <Zap className="w-3.5 h-3.5 text-purple-500/50" />
                    </div>
                    <div className="text-xl font-mono text-purple-400 font-bold">
                       {isRunning ? metrics.latency : '--'}
                    </div>
                 </div>
              </div>
           </div>

           <div className="flex-1 min-h-0 flex flex-col">
              <h4 className="text-[10px] font-black text-slate-600 uppercase mb-4 tracking-widest">Simulated Logs</h4>
              <div className="flex-1 bg-black/40 rounded-xl p-3 font-mono text-[9px] text-slate-500 overflow-y-auto scrollbar-hide space-y-1.5 border border-slate-800/50">
                 <div className="text-blue-500/80">[SYSTEM] Metabolism Engine Online...</div>
                 <div className="text-slate-600">[{new Date().toLocaleTimeString()}] TRACE: Handshake established.</div>
                 {isRunning && activeNode && (
                   <div className="animate-pulse text-blue-400/80">[{new Date().toLocaleTimeString()}] PULSE: Interaction detected on {activeNode}</div>
                 )}
                 <div className="opacity-40 italic">Waiting for state mutation...</div>
              </div>
           </div>
        </div>
      </aside>

      {/* 2. Kinetic Visualizer Canvas */}
      <main className="flex-1 relative bg-[#0d1117] overflow-hidden">
         <ReactFlow
            nodes={flowNodes}
            edges={flowEdges}
            fitView
            style={{ background: '#0d1117' }}
            proOptions={{ hideAttribution: true }}
         >
            <Background color="#1e293b" gap={20} size={1} />
         </ReactFlow>

         {/* Bottom Legend */}
         <div className="absolute bottom-10 left-10 flex items-center gap-6 bg-[#161b22]/80 backdrop-blur-xl border border-slate-800 px-6 py-3 rounded-full z-10">
            <div className="flex items-center gap-2">
               <div className="w-2 h-2 rounded-full bg-slate-800 border border-slate-700" />
               <span className="text-[10px] font-bold text-slate-500 uppercase">Idle</span>
            </div>
            <div className="flex items-center gap-2">
               <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
               <span className="text-[10px] font-bold text-blue-400 uppercase">Processing</span>
            </div>
            <div className="flex items-center gap-2">
               <div className="w-2 h-2 rounded-full bg-orange-500" />
               <span className="text-[10px] font-bold text-orange-500 uppercase">High Load</span>
            </div>
         </div>
      </main>
    </div>
  );
}
