import React, { useState, useEffect } from 'react';
import { 
  Zap, 
  Layout, 
  Activity, 
  Phone, 
  Layers, 
  Settings, 
  Navigation, 
  MapPin, 
  AlertCircle,
  ChevronRight,
  Bell,
  Search,
  Cpu,
  MessageSquare,
  Code2,
  Sparkles,
  Maximize2,
  Minimize2,
  Send,
  Terminal,
  FileJson,
  ClipboardCheck,
  Download,
  CheckCircle2,
  BarChart3,
  Folder,
  FileCode,
  FileText,
  ChevronDown,
  Box,
  Share2,
  ListChecks,
  Milestone
} from 'lucide-react';

import SurfaceProjector from "./preview/SurfaceProjector";

// --- Domain: Generic Operational UI Component (Demo/Fallback) ---
const GenericOperationsApp = () => {
  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100 font-sans overflow-hidden">
      <div className="h-6 flex justify-between px-6 items-center text-[10px] opacity-60">
        <span>9:41</span>
        <div className="flex gap-1 items-center">
          <Activity size={10} />
          <div className="w-4 h-2 border border-white/40 rounded-sm" />
        </div>
      </div>

      <header className="p-4 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white">System Monitor</h2>
          <p className="text-xs text-blue-400 flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
            Core Systems Active
          </p>
        </div>
        <div className="bg-slate-800 p-2 rounded-full relative">
          <Settings size={18} />
        </div>
      </header>

      <div className="flex-1 px-4 py-2 flex flex-col gap-4 overflow-y-auto pb-20 scrollbar-hide">
        <div className="bg-gradient-to-br from-blue-600/20 to-slate-900 border border-blue-500/30 rounded-2xl p-4 relative overflow-hidden shadow-lg">
          <div className="flex justify-between items-start mb-2">
            <span className="bg-blue-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">Status: Nominal</span>
            <span className="text-[10px] opacity-60 font-mono">ID: #000-SYS</span>
          </div>
          <h3 className="text-lg font-semibold leading-tight text-white">Baseline Operations</h3>
          <p className="text-sm opacity-70 mb-4 flex items-center gap-1">
            <Layers size={12} /> Global Infrastructure Node
          </p>
          <div className="flex gap-2">
            <button className="flex-1 bg-blue-600 hover:bg-blue-500 text-white font-bold py-2 rounded-xl transition-colors text-sm shadow-lg shadow-blue-900/20">
              Refresh Data
            </button>
            <button className="px-3 bg-slate-800 border border-slate-700 rounded-xl">
              <Activity size={16} />
            </button>
          </div>
        </div>

        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-widest text-slate-500">Service Nodes</h4>
          {[
            { id: 'NODE-01', status: 'Active', load: '12%', color: 'bg-emerald-500' },
            { id: 'NODE-02', status: 'Standby', load: '0%', color: 'bg-slate-500' },
            { id: 'NODE-03', status: 'Active', load: '45%', color: 'bg-blue-500' }
          ].map((unit, i) => (
            <div key={i} className="bg-slate-900/50 border border-slate-800 rounded-xl p-3 flex justify-between items-center group cursor-pointer hover:bg-slate-800/50 transition-all">
              <div className="flex items-center gap-3">
                <div className={`w-1.5 h-8 rounded-full ${unit.color}`} />
                <div>
                  <div className="text-sm font-medium">{unit.id}</div>
                  <div className="text-[10px] opacity-50">{unit.status}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs font-mono">{unit.load}</div>
                <ChevronRight size={14} className="opacity-30 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </div>

      <nav className="absolute bottom-4 left-4 right-4 h-16 bg-slate-900/80 backdrop-blur-xl border border-white/10 rounded-2xl flex justify-around items-center px-6">
        <Activity className="text-blue-400" size={20} />
        <Layers className="text-slate-500" size={20} />
        <Search className="text-slate-500" size={20} />
        <Settings className="text-slate-500" size={20} />
      </nav>
    </div>
  );
};

// --- Repository Tree Item Component ---
const RepoItem = ({ icon: Icon, label, depth = 0, isFolder = false, isOpen = true, color = "text-slate-400", onClick, isSelected }) => (
  <div 
    onClick={onClick}
    className={`flex items-center gap-2 py-1 px-2 rounded-md hover:bg-white/5 cursor-pointer transition-colors text-xs font-mono group ${isSelected ? 'bg-indigo-500/10 border-l-2 border-indigo-500' : ''}`}
    style={{ paddingLeft: `${depth * 16 + 8}px` }}
  >
    {isFolder && <ChevronDown size={12} className={`text-slate-600 ${!isOpen && '-rotate-90'}`} />}
    <Icon size={14} className={isFolder ? "text-blue-500" : color} />
    <span className={isFolder ? "text-slate-200" : "text-slate-400 group-hover:text-white"}>{label}</span>
  </div>
);

// --- Repo Tree Renderer (Dynamic) ---
const RepoTreeRenderer = ({ repo, onFileSelect, selectedFile }) => {
  if (!repo) return null;
  const paths = Object.keys(repo).sort();
  
  return (
    <div className="space-y-0.5">
      {paths.map((path, i) => {
        const parts = path.split('/');
        const name = parts[parts.length - 1];
        const depth = parts.length - 1;
        // Simple folder detection: if the path has a slash and there are files inside it
        const isFolder = paths.some(p => p.startsWith(path + '/') && p !== path);
        
        // Skip rendering folder entries directly if they are just prefixes of other files
        // (unless they are empty folders, which our hologram doesn't really have)
        
        const icon = isFolder ? Folder : (name.endsWith('.json') ? FileJson : FileCode);
        const color = name.endsWith('.json') ? "text-yellow-500" : (name.endsWith('.jsx') || name.endsWith('.js') || name.endsWith('.py') ? "text-blue-400" : "text-slate-400");
        
        return (
          <RepoItem 
            key={i} 
            icon={icon} 
            label={name} 
            depth={depth} 
            isFolder={isFolder} 
            color={color} 
            isSelected={selectedFile === path}
            onClick={() => !isFolder && onFileSelect(path)}
          />
        );
      })}
    </div>
  );
};

// --- Main Studio Layout ---
const App = () => {
  const [activeTab, setActiveTab] = useState('User Experience');
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [isCanvasOpen, setIsCanvasOpen] = useState(true);
  const [chatInput, setChatInput] = useState("");
  const [copied, setCopied] = useState(false);
  const [snapshot, setSnapshot] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  
  const [messages, setMessages] = useState([
    { role: 'system', text: 'ShiftOps-OS / Canvas 2.0 Connected to ArchitectureEngine.' },
    { role: 'ai', text: 'Synthesis ready. I can architect logistics networks, satellite telemetry systems, or emergency response platforms.' }
  ]);

  const handleFileSelect = (path) => {
    setSelectedFile(path);
    setActiveTab('Source Code');
  };

  const handleSynthesize = async (e) => {
    if (e) e.preventDefault();
    if (!chatInput.trim()) return;

    const intent = chatInput;
    setChatInput("");
    setIsSynthesizing(true);
    setMessages(prev => [...prev, { role: 'user', text: intent }, { role: 'system', text: 'Synthesizing Architecture...' }]);

    try {
      const res = await fetch('http://localhost:8000/architect/snapshot', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal: "Project Synthesis", request: intent })
      });
      const data = await res.json();
      if (data.status === "success") {
        setSnapshot(data.snapshot);
        setSelectedFile("README.md"); // Default to README
        setMessages(prev => [...prev, { role: 'ai', text: `Synthesis complete. System Fitness: ${data.snapshot.diagnostics.fitness_score}%. Surface manifest projected.` }]);
        setActiveTab('User Experience');
      }
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'system', text: 'Synthesis Error. Check Engine Logs.' }]);
    } finally {
      setIsSynthesizing(false);
    }
  };

  const handleCopy = () => {
    const textToCopy = (snapshot && selectedFile) ? snapshot.repo[selectedFile] : JSON.stringify(snapshot?.surface_manifest, null, 2);
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExport = async () => {
    if (!snapshot) return;
    try {
      const res = await fetch('http://localhost:8000/export', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal: snapshot.id, repo: snapshot.repo })
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${snapshot.id}.zip`;
      a.click();
    } catch (err) {
      console.error("Export failed", err);
    }
  };

  return (
    <div className="h-screen bg-[#050507] text-slate-300 flex flex-col font-sans selection:bg-blue-500/30 overflow-hidden">
      
      {/* Top Header */}
      <header className="h-14 border-b border-white/5 bg-slate-950/80 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-50">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-tr from-indigo-600 to-purple-600 p-1.5 rounded-lg">
            <Sparkles size={16} className="text-white" />
          </div>
          <h1 className="text-sm font-bold text-white tracking-tight flex items-center gap-2 uppercase tracking-widest">
            SHIFTOPS-OS <span className="text-white/30">/</span> CANVAS 
          </h1>
        </div>

        <div className="flex items-center gap-4">
          <button 
            onClick={() => setIsCanvasOpen(!isCanvasOpen)}
            className="p-2 hover:bg-white/5 rounded-lg transition-colors text-slate-400 hover:text-white"
          >
            {isCanvasOpen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </button>
        </div>
      </header>

      {/* Workspace Area */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Side: Collaborative Agent */}
        <div className={`transition-all duration-500 ease-in-out border-r border-white/5 flex flex-col bg-[#0a0a0c] ${isCanvasOpen ? 'w-[380px]' : 'w-0 opacity-0'}`}>
          <div className="p-4 border-b border-white/5 bg-slate-900/20 flex items-center gap-2 text-xs font-bold text-slate-100 uppercase tracking-tighter">
            <MessageSquare size={14} className="text-indigo-400" />
            Agent Workspace
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`max-w-[90%] rounded-2xl p-3 text-xs leading-relaxed shadow-sm ${
                  msg.role === 'user' 
                  ? 'bg-indigo-600 text-white shadow-indigo-500/10' 
                  : msg.role === 'system'
                  ? 'bg-white/5 text-slate-500 italic border border-white/5 font-mono'
                  : 'bg-slate-900 text-slate-300 border border-white/10'
                }`}>
                  {msg.text}
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 bg-slate-900/30 border-t border-white/5">
            <form onSubmit={handleSynthesize} className="relative">
              <input 
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Modify build steps..."
                className="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-3 pr-12 text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500/50 placeholder:text-slate-600"
              />
              <button className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-indigo-500 hover:text-indigo-400 transition-colors">
                <Send size={18} />
              </button>
            </form>
          </div>
        </div>

        {/* Right Side: Hollywood Stage */}
        <div className="flex-1 flex flex-col bg-[#050507] relative">
          
          {/* Navigation Tabs */}
          <div className="flex items-center justify-between px-6 h-12 border-b border-white/5 bg-slate-950/20 shrink-0">
             <div className="flex h-full">
               {['Architecture', 'User Experience', 'Build Summary', 'Source Code'].map(tab => (
                 <button 
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`h-full px-4 text-xs font-medium transition-all relative ${
                    activeTab === tab ? 'text-white' : 'text-slate-500 hover:text-slate-300'
                  }`}
                 >
                   {tab}
                   {activeTab === tab && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-500" />}
                 </button>
               ))}
             </div>
             <div className="flex gap-2">
                <button 
                    className="flex items-center gap-1.5 bg-white/5 border border-white/10 hover:bg-white/10 text-white px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all"
                >
                    <Share2 size={12} /> Share
                </button>
                <button 
                    onClick={() => handleSynthesize()}
                    className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all shadow-lg shadow-blue-600/20"
                >
                    <Zap size={12} fill="currentColor" /> Synthesize
                </button>
             </div>
          </div>

          {/* Tab Content Rendering */}
          <section className="flex-1 overflow-hidden relative">
            
            {/* 1. Architecture View (Repo Layout) */}
            {activeTab === 'Architecture' && (
              <div className="w-full h-full flex flex-col p-8 overflow-y-auto bg-[#0a0a0c] custom-scrollbar">
                <div className="max-w-4xl mx-auto w-full">
                  <div className="flex items-center justify-between mb-8">
                     <div>
                        <h3 className="text-lg font-bold text-white mb-1">Repository Architecture</h3>
                        <p className="text-xs text-slate-500">High-level structure generated by ArchitectureEngine.</p>
                     </div>
                     <button className="flex items-center gap-2 bg-slate-900 border border-white/10 px-4 py-2 rounded-xl text-[10px] font-bold text-slate-400 hover:text-white transition-all">
                        <Box size={14} /> Open in IDE
                     </button>
                  </div>

                  <div className="bg-slate-950/50 border border-white/5 rounded-2xl overflow-hidden shadow-2xl">
                    <div className="flex items-center gap-4 bg-slate-900/50 px-4 py-3 border-b border-white/5">
                        <div className="flex gap-1.5">
                            <div className="w-2.5 h-2.5 rounded-full bg-red-500/20" />
                            <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/20" />
                            <div className="w-2.5 h-2.5 rounded-full bg-green-500/20" />
                        </div>
                        <span className="text-[10px] font-mono text-slate-500">project_root / {snapshot?.id || "waiting_for_synthesis"}</span>
                    </div>
                    <div className="p-4 bg-slate-950 min-h-[400px]">
                        {snapshot ? (
                          <RepoTreeRenderer 
                            repo={snapshot.repo} 
                            onFileSelect={handleFileSelect} 
                            selectedFile={selectedFile} 
                          />
                        ) : (
                          <div className="flex flex-col items-center justify-center h-full py-20 text-slate-700 text-xs italic font-mono uppercase tracking-widest">
                            Awaiting Architecture Synthesis...
                          </div>
                        )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 2. User Experience View */}
            {activeTab === 'User Experience' && (
              <div className="w-full h-full flex items-center justify-center p-8 bg-[radial-gradient(circle_at_center,_#1a1b2e_0%,_#050507_100%)]">
                {isSynthesizing ? (
                  <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 border-2 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
                    <span className="text-xs font-mono text-slate-500">Synthesizing Surface...</span>
                  </div>
                ) : snapshot ? (
                  <SurfaceProjector manifest={snapshot.surface_manifest} state={{ metrics: { docks: 12, trailers: 4, health: 98 } }} />
                ) : (
                  <div className="relative w-full max-w-[320px] aspect-[9/19.5] bg-slate-900 rounded-[2.5rem] p-2 border-[4px] border-slate-800 shadow-2xl">
                    <div className="w-full h-full bg-slate-950 rounded-[2rem] overflow-hidden">
                      <GenericOperationsApp />
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 3. Build Summary View */}
            {activeTab === 'Build Summary' && (
              <div className="w-full h-full p-8 overflow-y-auto custom-scrollbar">
                <div className="max-w-4xl mx-auto space-y-8">
                  {/* Header & Confidence */}
                  <div className="flex justify-between items-end border-b border-white/5 pb-6">
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-2 tracking-tight">Build Analysis: {snapshot?.id || "Snapshot Pending"}</h2>
                      <p className="text-slate-400 text-sm">Comprehensive breakdown of synthesized infrastructure.</p>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Confidence Rating</div>
                      <div className="flex items-center gap-3">
                         <div className="w-32 h-2 bg-slate-800 rounded-full overflow-hidden">
                            <div className="h-full bg-emerald-500 transition-all duration-1000" style={{ width: `${(snapshot?.diagnostics.confidence * 100) || 0}%` }} />
                         </div>
                         <span className="text-xl font-mono font-bold text-emerald-400">{(snapshot?.diagnostics.confidence * 100).toFixed(0) || 0}%</span>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Project Roadmap / Steps */}
                    <div className="lg:col-span-2 space-y-6">
                      <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-6">
                        <h3 className="text-white text-xs font-bold uppercase tracking-widest mb-6 flex items-center gap-2">
                          <Milestone size={14} className="text-blue-400" /> Project Roadmap
                        </h3>
                        <div className="space-y-6 relative">
                          <div className="absolute left-4 top-2 bottom-2 w-px bg-slate-800" />
                          {snapshot?.diagnostics.roadmap ? snapshot.diagnostics.roadmap.map((item, i) => (
                            <div key={i} className="relative pl-10 group">
                              <div className="absolute left-2.5 top-1.5 w-3 h-3 rounded-full bg-slate-950 border-2 border-blue-500 z-10 group-hover:scale-125 transition-transform" />
                              <div className="text-[10px] font-mono text-blue-500 mb-1">{item.step}</div>
                              <h4 className="text-sm font-bold text-slate-100 mb-1">{item.title}</h4>
                              <p className="text-xs text-slate-500 leading-relaxed">{item.desc}</p>
                            </div>
                          )) : (
                            <div className="text-xs text-slate-600 italic py-10 text-center">Awaiting Synthesis Roadmap...</div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Technical & Realism Boxes */}
                    <div className="space-y-6">
                      <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-6">
                        <h3 className="text-white text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
                          <Layers size={14} className="text-indigo-400" /> System Integrity
                        </h3>
                        <ul className="text-xs text-slate-400 space-y-4">
                          <li className="flex gap-2">
                            <span className="text-indigo-500 font-bold">Â»</span>
                            Fitness Score: {snapshot?.diagnostics.fitness_score || 0}%
                          </li>
                          <li className="flex gap-2">
                            <span className="text-indigo-500 font-bold">Â»</span>
                            Scalability Index: {snapshot?.diagnostics.scalability_index || 0}
                          </li>
                          <li className="flex gap-2">
                            <span className="text-indigo-500 font-bold">Â»</span>
                            Resilience Score: {snapshot?.diagnostics.resilience_score || 0}
                          </li>
                        </ul>
                      </div>

                      <div className="bg-slate-900/40 border border-white/5 rounded-2xl p-6">
                        <h3 className="text-white text-xs font-bold uppercase tracking-widest mb-4 flex items-center gap-2">
                          <BarChart3 size={14} className="text-purple-400" /> Synthesis Rationale
                        </h3>
                        <div className="space-y-4">
                          {snapshot?.diagnostics.reasons ? snapshot.diagnostics.reasons.map((reason, i) => (
                            <div key={i} className="flex gap-2 text-[10px]">
                              <span className="text-purple-500 font-bold">â€¢</span>
                              <span className="text-slate-500">{reason}</span>
                            </div>
                          )) : (
                            <div className="text-[10px] text-slate-700 italic">No rationale data.</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* 4. Source Code View */}
            {activeTab === 'Source Code' && (
              <div className="w-full h-full flex flex-col p-6 bg-slate-950">
                <div className="flex justify-between items-center mb-4">
                   <div className="flex gap-2">
                      <div className="px-3 py-1 bg-slate-900 border border-white/10 rounded-lg text-[10px] font-mono text-slate-100">{selectedFile || "synthesis_snapshot.json"}</div>
                   </div>
                   <div className="flex gap-2">
                      <button 
                        onClick={handleCopy}
                        className="flex items-center gap-2 bg-white/5 hover:bg-white/10 text-white px-4 py-1.5 rounded-lg text-[10px] font-bold transition-all border border-white/5"
                      >
                        {copied ? <CheckCircle2 size={12} className="text-emerald-400" /> : <ClipboardCheck size={12} />}
                        {copied ? 'Copied' : 'Copy Content'}
                      </button>
                      <button 
                        onClick={handleExport}
                        className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-1.5 rounded-lg text-[10px] font-bold transition-all"
                      >
                        <Download size={12} /> Export Project
                      </button>
                   </div>
                </div>
                <div className="flex-1 bg-slate-900/50 rounded-2xl border border-white/5 p-6 font-mono text-[10px] overflow-auto text-blue-300 custom-scrollbar">
                  <pre className="leading-relaxed whitespace-pre-wrap">
                    {snapshot ? (selectedFile ? snapshot.repo[selectedFile] : JSON.stringify(snapshot, null, 2)) : "// Awaiting synthesis..."}
                  </pre>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>

      <footer className="h-6 bg-[#050507] border-t border-white/5 flex items-center justify-between px-4 z-50">
        <div className="flex items-center gap-4 text-[8px] font-mono tracking-widest text-slate-600 uppercase">
          <span>Confidence: {snapshot ? "HIGH" : "WAITING"}</span>
          <span className="text-indigo-500/50">â€¢</span>
          <span>Build Snapshot: {snapshot?.id || "N/A"}</span>
        </div>
        <div className="flex items-center gap-1.5 text-[8px] font-mono text-slate-600 uppercase">
          <Terminal size={10} /> Hollywood_Set_Production_Active
        </div>
      </footer>
    </div>
  );
};

export default App;

