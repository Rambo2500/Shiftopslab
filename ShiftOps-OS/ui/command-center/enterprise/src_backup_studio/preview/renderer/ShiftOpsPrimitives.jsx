import React from 'react';

// The "iPhone" for the Showroom
export const PhoneFrame = ({ children, title }) => (
  <div className="relative mx-auto border-gray-800 bg-gray-800 border-[14px] rounded-[2.5rem] h-[600px] w-[300px] shadow-xl overflow-hidden">
    <div className="w-[148px] h-[18px] bg-gray-800 top-0 left-1/2 -translate-x-1/2 absolute rounded-b-[1rem] z-20"></div>
    <div className="h-[46px] w-[3px] bg-gray-800 absolute -left-[17px] top-[124px] rounded-l-lg"></div>
    <div className="h-[46px] w-[3px] bg-gray-800 absolute -left-[17px] top-[178px] rounded-l-lg"></div>
    <div className="h-[64px] w-[3px] bg-gray-800 absolute -right-[17px] top-[142px] rounded-r-lg"></div>
    
    <div className="bg-slate-950 h-full w-full flex flex-col">
      <div className="pt-8 pb-2 px-4 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center">
        <h1 className="text-[10px] font-bold text-blue-400 tracking-tighter uppercase">{title}</h1>
        <div className="text-[8px] text-slate-500 font-mono">LIVE_SIM_V1</div>
      </div>
      <div className="flex-1 overflow-hidden relative">
        {children}
      </div>
    </div>
  </div>
);

// High-fidelity Operational Gauge
export const Gauge = ({ label, value, unit, color = 'blue', min = 0, max = 100 }) => {
  const colors = {
    blue: 'text-blue-400 border-blue-500/30 bg-blue-500/5',
    red: 'text-red-400 border-red-500/30 bg-red-500/5',
    orange: 'text-orange-400 border-orange-500/30 bg-orange-500/5',
    emerald: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/5'
  };

  const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));

  return (
    <div className={`p-3 rounded-lg border ${colors[color] || colors.blue} flex flex-col justify-center items-center shadow-inner`}>
      <span className="text-[9px] uppercase tracking-widest opacity-60 mb-1">{label}</span>
      <div className="flex items-baseline">
        <span className="text-2xl font-black tracking-tighter">{value}</span>
        <span className="text-[10px] ml-1 opacity-50 font-mono">{unit || ''}</span>
      </div>
      <div className="w-full h-1 bg-slate-800 rounded-full mt-2 overflow-hidden">
        <div 
          className={`h-full bg-current transition-all duration-500 ease-out`} 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
};

// Haptic-Feedback Button
export const ActionButton = ({ label, icon, theme = 'primary' }) => {
  const [active, setActive] = React.useState(false);

  const triggerHaptic = () => {
    setActive(true);
    setTimeout(() => setActive(false), 150);
  };

  return (
    <button 
      onClick={triggerHaptic}
      className={`
        w-full p-4 rounded-xl border-2 font-bold text-sm uppercase tracking-wider transition-all
        ${active ? 'scale-95 translate-y-1' : 'hover:scale-[1.02]'}
        ${theme === 'primary' 
          ? 'bg-blue-600 border-blue-400 text-white shadow-[0_4px_0_rgb(30,58,138)]' 
          : 'bg-slate-800 border-slate-600 text-slate-300 shadow-[0_4px_0_rgb(30,41,59)]'}
        active:shadow-none
      `}
    >
      <div className="flex items-center justify-center space-x-2">
        {icon === 'barcode' && <span className="text-xl">⬚</span>}
        <span>{label}</span>
      </div>
    </button>
  );
};

// Data List with "Operational" feel
export const DataList = ({ title, items }) => (
  <div className="space-y-2">
    <div className="flex justify-between items-center px-1">
      <span className="text-[9px] text-slate-500 uppercase font-bold tracking-widest">{title}</span>
      <span className="text-[9px] text-blue-500/50 font-mono">COUNT: {items.length}</span>
    </div>
    <div className="space-y-1">
      {items.map((item, i) => (
        <div key={i} className="bg-slate-900 border border-slate-800 p-2 rounded flex justify-between items-center group hover:border-blue-500/50 transition-colors">
          <div className="flex flex-col">
            <span className="text-[11px] font-bold text-slate-300">{item.label || item.id}</span>
            <span className="text-[8px] text-slate-600 font-mono italic">{item.subtext || 'STABLE'}</span>
          </div>
          <div className="w-1.5 h-1.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
        </div>
      ))}
    </div>
  </div>
);
