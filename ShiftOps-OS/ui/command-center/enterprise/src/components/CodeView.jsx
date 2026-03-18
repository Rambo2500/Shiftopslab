// components/CodeView.jsx

import { useState, useMemo } from "react";
import RepoTree from "./RepoTree";
import { buildRepoTree } from "../utils/buildRepoTree";
import { Terminal, Copy, Check, FileCode, Search } from "lucide-react";

export default function CodeView({ snapshot }) {
  const [selectedFile, setSelectedFile] = useState({ name: "", content: "", path: "" });
  const [copied, setCopied] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [viewMode, setViewMode] = useState("tree"); // 'tree' or 'terminal'

  // Filtered repo based on search term
  const filteredRepo = useMemo(() => {
    if (!snapshot?.repo) return {};
    if (!searchTerm) return snapshot.repo;
    
    return Object.keys(snapshot.repo)
      .filter(path => path.toLowerCase().includes(searchTerm.toLowerCase()))
      .reduce((obj, key) => {
        obj[key] = snapshot.repo[key];
        return obj;
      }, {});
  }, [snapshot, searchTerm]);

  const tree = useMemo(() => {
    return buildRepoTree(filteredRepo);
  }, [filteredRepo]);

  // Set initial file
  useMemo(() => {
    if (snapshot?.repo && !selectedFile.path) {
      const firstPath = Object.keys(snapshot.repo)[0];
      if (firstPath) {
        setSelectedFile({
          name: firstPath.split("/").pop(),
          content: snapshot.repo[firstPath],
          path: firstPath
        });
      }
    }
  }, [snapshot, selectedFile.path]);

  const handleCopy = () => {
    navigator.clipboard.writeText(selectedFile.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!snapshot?.repo) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500 italic bg-slate-900/50">
        No implementation artifacts generated yet.
      </div>
    );
  }

  return (
    <div className="flex h-full bg-[#0d1117] overflow-hidden">
      {/* 1. Virtual Repo Tree Sidebar */}
      <aside className="w-72 border-r border-slate-800 flex flex-col bg-[#161b22]">
        <div className="p-4 border-b border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
              Project Explorer
            </h3>
            <div className="flex bg-slate-900 rounded-md p-0.5 border border-slate-800">
              <button 
                onClick={() => setViewMode("tree")}
                className={`px-2 py-0.5 text-[9px] font-bold uppercase rounded ${viewMode === 'tree' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
              >
                Tree
              </button>
              <button 
                onClick={() => setViewMode("terminal")}
                className={`px-2 py-0.5 text-[9px] font-bold uppercase rounded ${viewMode === 'terminal' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
              >
                ls
              </button>
            </div>
          </div>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-500" />
            <input 
              type="text"
              placeholder="Filter files..."
              className="w-full bg-slate-900/50 border border-slate-800 rounded-md py-1.5 pl-8 pr-3 text-xs text-slate-300 focus:outline-none focus:border-blue-500/50 transition-colors"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 scrollbar-hide">
          {viewMode === "tree" ? (
            <RepoTree
              tree={tree}
              selectedPath={selectedFile.path}
              onSelect={(name, content, path) => setSelectedFile({ name, content, path })}
            />
          ) : (
            <div className="space-y-1 font-mono text-[11px] p-2">
              <div className="text-slate-500 mb-2">$ ls -R .</div>
              {Object.keys(filteredRepo).sort().map(path => (
                <div
                  key={path}
                  onClick={() => setSelectedFile({ name: path.split('/').pop(), content: filteredRepo[path], path })}
                  className={`cursor-pointer px-2 py-1 rounded truncate transition-colors ${
                    selectedFile.path === path ? 'bg-blue-600/20 text-blue-400' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'
                  }`}
                >
                  <span className="opacity-40 mr-1">{path.includes('/') ? path.split('/').slice(0,-1).join('/') + '/' : ''}</span>
                  <span className="font-bold">{path.split('/').pop()}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-3 border-t border-slate-800 bg-slate-900/30">
          <div className="flex items-center gap-2 text-[10px] text-slate-500">
            <Terminal className="w-3 h-3" />
            <span>Virtual FS Layer Active</span>
          </div>
        </div>
      </aside>

      {/* 2. Code Editor Preview */}
      <main className="flex-1 flex flex-col min-w-0 bg-[#0d1117]">
        {selectedFile.path ? (
          <>
            <div className="h-10 border-b border-slate-800 flex items-center justify-between px-4 bg-[#161b22]/50">
              <div className="flex items-center gap-2 text-xs font-mono text-slate-400 truncate">
                <FileCode className="w-3.5 h-3.5 text-blue-400" />
                <span className="opacity-50">{selectedFile.path.split('/').slice(0, -1).join(' / ')} /</span>
                <span className="text-slate-200 font-bold">{selectedFile.name}</span>
              </div>
              <button 
                onClick={handleCopy}
                className="p-1.5 hover:bg-slate-800 rounded transition-colors text-slate-500 hover:text-slate-300"
                title="Copy Code"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
            </div>
            
            <div className="flex-1 overflow-auto bg-[#0d1117] relative">
              {/* Line Numbers */}
              <div className="absolute left-0 top-0 bottom-0 w-12 bg-slate-900/20 border-r border-slate-800/50 flex flex-col items-center pt-6 text-[10px] font-mono text-slate-600 select-none">
                {selectedFile.content.split('\n').map((_, i) => (
                  <div key={i} className="leading-6">{i + 1}</div>
                ))}
              </div>
              
              <pre className="p-6 pl-16 font-mono text-sm text-slate-300 leading-6 whitespace-pre">
                <code>{selectedFile.content}</code>
              </pre>
            </div>
            
            <footer className="h-8 border-t border-slate-800 bg-[#161b22] px-4 flex items-center justify-between text-[10px] text-slate-500">
              <div className="flex items-center gap-4">
                <span>UTF-8</span>
                <span>{selectedFile.name.split('.').pop()?.toUpperCase() || 'Text'}</span>
              </div>
              <div>{selectedFile.content.split('\n').length} Lines</div>
            </footer>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-600">
             <FileCode className="w-12 h-12 mb-4 opacity-10" />
             <p className="text-sm italic">Select a file to preview implementation</p>
          </div>
        )}
      </main>
    </div>
  );
}
