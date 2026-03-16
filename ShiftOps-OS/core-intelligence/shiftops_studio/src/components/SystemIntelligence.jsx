// components/SystemIntelligence.jsx
import React from "react";
import HealthGauge from "./HealthGauge";
import { ShieldCheck, AlertTriangle, Info, Zap, TrendingUp } from "lucide-react";

export default function SystemIntelligence({ snapshot, simulationMetrics }) {
  if (!snapshot) return null;

  const { diagnostics } = snapshot;
  const resilienceScore = diagnostics?.fitness_score || 0;

  return (
    <aside className="w-80 border-l border-slate-800 bg-[#0d1117] p-6 flex flex-col gap-8 overflow-y-auto scrollbar-hide">
      <header>
        <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-6">
          System Intelligence
        </h3>
        <HealthGauge resilienceScore={resilienceScore} />
      </header>

      <div className="space-y-6">
        <section>
          <div className="flex items-center gap-2 mb-3">
            <ShieldCheck className="w-4 h-4 text-blue-500" />
            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
              Reasoning Signals
            </h4>
          </div>
          <ul className="space-y-3">
            {(diagnostics?.reasons || [
              "Standard service topology validated",
              "Redundant data layers detected",
              "Integrated monitoring active"
            ]).map((reason, i) => (
              <li key={i} className="flex gap-2 text-xs text-slate-500 font-medium leading-relaxed">
                <span className="text-blue-500/50">•</span>
                {reason}
              </li>
            ))}
          </ul>
        </section>

        <section>
          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">
              Risk Signals
            </h4>
          </div>
          <ul className="space-y-3">
            {(diagnostics?.warnings || [
              "Single instance of primary gateway detected",
              "Potential bottleneck in analytics routing"
            ]).map((warning, i) => (
              <li key={i} className="flex gap-2 text-xs text-amber-500/70 font-medium leading-relaxed bg-amber-500/5 p-2 rounded-lg border border-amber-500/10">
                <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" />
                {warning}
              </li>
            ))}
          </ul>
        </section>

        <section className="p-4 bg-slate-900/50 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
              Simulation Telemetry
            </h4>
            <div className="flex gap-1">
              <div className="w-1 h-1 rounded-full bg-blue-500 animate-ping" />
            </div>
          </div>
          <div className="space-y-4">
             <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-slate-600 uppercase">Throughput</span>
                <span className="text-xs font-mono text-blue-400 font-bold">{simulationMetrics?.throughput || 0} req/s</span>
             </div>
             <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-slate-600 uppercase">Avg Latency</span>
                <span className="text-xs font-mono text-purple-400 font-bold">{simulationMetrics?.latency || '0ms'}</span>
             </div>
             <div className="flex items-center justify-between">
                <span className="text-[10px] font-bold text-slate-600 uppercase">Scalability</span>
                <div className="flex items-center gap-2">
                   <TrendingUp className="w-3 h-3 text-green-500" />
                   <span className="text-xs font-mono text-green-500 font-bold">{diagnostics?.scalability_index?.toFixed(1) || 0.0}</span>
                </div>
             </div>
          </div>
        </section>
      </div>

      <footer className="mt-auto pt-6 border-t border-slate-800/50">
         <div className="p-4 bg-blue-600/10 rounded-xl border border-blue-500/20 text-center">
            <p className="text-[10px] font-bold text-blue-400 uppercase leading-relaxed">
               Architecture is verified for materialization
            </p>
         </div>
      </footer>
    </aside>
  );
}
