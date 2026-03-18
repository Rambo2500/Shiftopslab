// components/RepoTree.jsx

import { useState } from "react";
import { Folder, FileCode, ChevronRight, ChevronDown } from "lucide-react";

function TreeNode({ node, name, onSelect, selectedPath }) {
  const [open, setOpen] = useState(true);

  if (node.type === "file") {
    const isSelected = selectedPath === node.path;
    return (
      <div
        onClick={() => onSelect(name, node.content, node.path)}
        className={`flex items-center gap-2 text-sm px-2 py-1.5 rounded cursor-pointer transition-colors ${
          isSelected ? "bg-blue-600/20 text-blue-400" : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
        }`}
      >
        <FileCode className={`w-4 h-4 ${isSelected ? "text-blue-400" : "text-slate-500"}`} />
        <span className="truncate">{name}</span>
      </div>
    );
  }

  return (
    <div className="text-sm">
      <div
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-2 py-1.5 text-slate-300 hover:bg-slate-800 rounded cursor-pointer transition-colors group"
      >
        {open ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-500" />}
        <Folder className="w-4 h-4 text-yellow-500/80" />
        <span className="font-medium">{name}</span>
      </div>

      {open && (
        <div className="ml-4 border-l border-slate-800 pl-1 mt-0.5">
          {Object.entries(node.children)
            .sort(([aName, aNode], [bName, bNode]) => {
              // Folders first
              if (aNode.type === "folder" && bNode.type === "file") return -1;
              if (aNode.type === "file" && bNode.type === "folder") return 1;
              return aName.localeCompare(bName);
            })
            .map(([childName, childNode]) => (
              <TreeNode
                key={childName}
                name={childName}
                node={childNode}
                onSelect={onSelect}
                selectedPath={selectedPath}
              />
            ))}
        </div>
      )}
    </div>
  );
}

export default function RepoTree({ tree, onSelect, selectedPath }) {
  return (
    <div className="space-y-0.5">
      {Object.entries(tree)
        .sort(([aName, aNode], [bName, bNode]) => {
          if (aNode.type === "folder" && bNode.type === "file") return -1;
          if (aNode.type === "file" && bNode.type === "folder") return 1;
          return aName.localeCompare(bName);
        })
        .map(([name, node]) => (
          <TreeNode 
            key={name} 
            name={name} 
            node={node} 
            onSelect={onSelect} 
            selectedPath={selectedPath}
          />
        ))}
    </div>
  );
}
