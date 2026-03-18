import React from 'react';

export default function BlueprintProjector({ manifest, state }) {
  const { layers = [] } = manifest;

  // Render spatial elements (Walls, Zones, Parts)
  const renderSpatial = (element, i) => {
    switch (element.type) {
      case 'rect':
        return (
          <rect 
            key={i} 
            x={element.x} y={element.y} width={element.w} height={element.h} 
            className={`fill-slate-900 stroke-2 ${element.className || 'stroke-blue-500/50'}`}
          />
        );
      case 'zone':
        return (
          <g key={i}>
            <rect 
              x={element.x} y={element.y} width={element.w} height={element.h} 
              className="fill-blue-500/10 stroke-1 stroke-blue-500/20 stroke-dasharray-4"
            />
            <text x={element.x + 5} y={element.y + 15} className="fill-blue-500/50 text-[8px] font-mono uppercase">
              {element.label}
            </text>
          </g>
        );
      case 'part':
        return (
          <circle 
            key={i} cx={element.x} cy={element.y} r={element.r || 5} 
            className="fill-blue-400 stroke-blue-200 stroke-1 shadow-lg"
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="blueprint-engine w-full h-full bg-slate-950 flex flex-col p-6">
      {/* Schematic Header */}
      <div className="mb-4 flex justify-between items-end border-b border-blue-900/30 pb-2">
        <div>
          <h2 className="text-blue-400 text-xs font-black tracking-widest uppercase">
            {manifest.title} // TECHNICAL_SPEC
          </h2>
          <div className="text-[8px] text-slate-500 font-mono mt-1">
            REF_ID: {Math.random().toString(36).substr(2, 9).toUpperCase()} // SCALE: 1:100
          </div>
        </div>
        <div className="text-right">
          <span className="text-[10px] text-blue-900 font-mono">RENDER_LENS: BLUEPRINT_2D</span>
        </div>
      </div>

      {/* The Drawing Canvas */}
      <div className="flex-1 relative bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:20px_20px] border border-blue-900/20 rounded-lg overflow-hidden shadow-inner">
        <svg className="w-full h-full" viewBox="0 0 800 500">
          {/* Grid lines or coordinate markers */}
          <line x1="0" y1="250" x2="800" y2="250" className="stroke-blue-900/10 stroke-1" />
          <line x1="400" y1="0" x2="400" y2="500" className="stroke-blue-900/10 stroke-1" />

          {/* Layers and Elements */}
          {layers.map((layer) => (
            <g key={layer.id} className="blueprint-layer">
              {layer.elements?.map(renderSpatial)}
            </g>
          ))}
        </svg>

        {/* Dynamic Telemetry Overlays */}
        <div className="absolute top-4 right-4 space-y-2 pointer-events-none">
          {state?.metrics && Object.entries(state.metrics).map(([key, val]) => (
            <div key={key} className="bg-slate-950/80 border border-blue-500/30 p-2 rounded backdrop-blur-sm">
              <div className="text-[8px] text-blue-400 uppercase font-bold">{key.replace('_', ' ')}</div>
              <div className="text-sm font-mono text-white leading-none">{val}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Blueprint Footer/Legend */}
      <div className="mt-4 grid grid-cols-4 gap-4">
        <div className="border-l-2 border-blue-500 pl-2">
           <div className="text-[8px] text-slate-600 uppercase">System Status</div>
           <div className="text-[10px] text-blue-400 font-bold">STABLE_NOMINAL</div>
        </div>
        <div className="border-l-2 border-slate-700 pl-2">
           <div className="text-[8px] text-slate-600 uppercase">Hardware Delta</div>
           <div className="text-[10px] text-slate-400 font-bold">+0.002ms</div>
        </div>
        <div className="col-span-2 text-right flex flex-col justify-end">
           <div className="text-[8px] text-blue-900 font-mono">PROJECTED_BY_SHIFTOPS-OS_SURFACE</div>
        </div>
      </div>
    </div>
  );
}

