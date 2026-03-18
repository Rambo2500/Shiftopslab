import React from 'react';
import SurfaceProjector from "../preview/SurfaceProjector";
import { ShieldCheck, Server, Zap, LayoutDashboard } from 'lucide-react';

export default function PreviewView({ snapshot }) {
  if (!snapshot) return (
    <div className="p-20 flex flex-col items-center justify-center text-slate-500 bg-slate-900/50 h-full">
      <LayoutDashboard className="w-12 h-12 mb-4 opacity-10" />
      <p className="italic uppercase font-black text-[10px] tracking-widest">Awaiting System Synthesis...</p>
    </div>
  );

  return (
    <div className="h-full overflow-hidden bg-[#0d1117] flex flex-col">
      {/* Showroom Header */}
      <header className="px-12 py-6 border-b border-slate-800 bg-slate-950/30 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-blue-600 rounded-xl shadow-lg shadow-blue-600/20">
            <LayoutDashboard className="text-white w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-tight text-white uppercase italic">{snapshot.id}</h1>
              <span className="px-2 py-0.5 bg-blue-500/10 text-blue-400 text-[8px] font-black rounded-full border border-blue-500/20 uppercase tracking-widest">Projection_Lens</span>
            </div>
            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">High-Fidelity Product Showroom</p>
          </div>
        </div>
        
        <div className="flex items-center gap-8">
           <div className="flex flex-col items-end">
              <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">Confidence</span>
              <span className="text-xs font-bold text-blue-400">{(snapshot.diagnostics?.confidence * 100).toFixed(1)}%</span>
           </div>
           <div className="w-px h-6 bg-slate-800" />
           <div className="flex flex-col items-end pr-4">
              <span className="text-[9px] font-black text-slate-600 uppercase tracking-widest">Visual Status</span>
              <span className="text-xs font-bold text-green-500 flex items-center gap-1.5 uppercase italic">
                 Live_Hologram
              </span>
           </div>
        </div>
      </header>

      {/* THE HERO: The Surface Projector (Phone/Blueprint) */}
      <div className="flex-1 overflow-y-auto custom-scrollbar bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:32px_32px]">
        <div className="max-w-5xl mx-auto py-12">
          <SurfaceProjector manifest={snapshot.surface_manifest} state={snapshot.simulation_state || {}} />
          
          {/* Narrative Summary Overlay */}
          <div className="mt-12 mx-12 p-8 bg-slate-900/80 backdrop-blur-md rounded-3xl border border-slate-800 shadow-2xl">
             <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-blue-500/10 rounded-lg">
                   <ShieldCheck className="w-5 h-5 text-blue-400" />
                </div>
                <h3 className="text-[10px] font-black text-white uppercase tracking-[0.3em]">Architect Narrative</h3>
             </div>
             <p className="text-xs text-slate-400 leading-relaxed font-mono italic">
                "{snapshot.narrative_summary || "System architecture verified. Projecting product surface for stakeholder review."}"
             </p>
             
             <div className="mt-8 pt-6 border-t border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-6">
                   <div className="flex -space-x-3">
                      <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-900 flex items-center justify-center">
                         <ShieldCheck className="w-4 h-4 text-blue-500" />
                      </div>
                      <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-900 flex items-center justify-center">
                         <Server className="w-4 h-4 text-purple-500" />
                      </div>
                   </div>
                   <div className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Validation Layers: Active</div>
                </div>
                <button className="px-6 py-2.5 bg-blue-600 text-white font-black text-[10px] uppercase tracking-[0.2em] rounded-xl hover:bg-blue-500 shadow-lg shadow-blue-600/30 transition-all">
                   Deploy System
                </button>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
