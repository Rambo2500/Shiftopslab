// components/ArchitectureView.jsx

import { useMemo } from "react";
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap 
} from "reactflow";
import "reactflow/dist/style.css";
import { blueprintToFlow } from "../utils/blueprintToFlow";

export default function ArchitectureView({ snapshot }) {
  const { nodes, edges } = useMemo(() => {
    if (!snapshot?.architecture) return { nodes: [], edges: [] };
    
    // Convert to React Flow format
    const flowData = blueprintToFlow({
      graph: {
        nodes: snapshot.architecture.nodes.map(n => ({
          id: n.id,
          type: n.type,
          traits: n.traits
        })),
        edges: snapshot.architecture.edges
      }
    });
    
    return flowData;
  }, [snapshot]);

  if (!nodes.length) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500 italic bg-slate-900/50">
        No architecture graph generated yet.
      </div>
    );
  }

  return (
    <div className="h-full bg-[#0d1117] relative">
      <div className="absolute top-6 left-6 z-10 flex items-center gap-2">
         <span className="px-3 py-1 bg-blue-600/10 text-blue-400 border border-blue-500/20 text-[10px] font-black rounded uppercase tracking-widest">Topology View</span>
         <span className="text-xs text-slate-500 font-bold">{nodes.length} Components Resolved</span>
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        style={{ background: '#0d1117' }}
      >
        <Background color="#1e293b" gap={20} size={1} />
        <Controls showInteractive={false} className="!bg-slate-900 !border-slate-800 !fill-slate-400" />
        <MiniMap 
          style={{ background: '#161b22', border: '1px solid #1e293b' }}
          nodeColor="#1e293b"
          maskColor="#0d1117"
        />
      </ReactFlow>
    </div>
  );
}
