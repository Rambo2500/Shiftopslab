// components/HealthGauge.jsx
import React from "react";

export default function HealthGauge({ resilienceScore }) {
  // Map the 0-100 score to a rotation between -90 and 90 degrees
  const rotation = (resilienceScore / 100) * 180 - 90;
  
  const getColor = (score) => {
    if (score > 85) return '#22c55e'; // Green
    if (score > 60) return '#f59e0b'; // Amber
    return '#ef4444'; // Red
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <svg width="240" height="140" viewBox="0 0 200 120">
          {/* The Track */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="#1e293b"
            strokeWidth="12"
            strokeLinecap="round"
          />
          {/* The Colored Indicator */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke={getColor(resilienceScore)}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray="251.2"
            strokeDashoffset={251.2 - (resilienceScore / 100) * 251.2}
            className="transition-all duration-1000 ease-out"
          />
          {/* The Needle */}
          <line
            x1="100" y1="100"
            x2="100" y2="40"
            stroke="white"
            strokeWidth="3"
            strokeLinecap="round"
            style={{ 
                transform: `rotate(${rotation}deg)`, 
                transformOrigin: '100px 100px'
            }}
            className="transition-all duration-700 ease-in-out"
          />
          {/* Needle Center Point */}
          <circle cx="100" cy="100" r="5" fill="white" />
        </svg>
        
        <div className="absolute top-[85px] left-0 right-0 text-center">
            <div className="text-3xl font-black tracking-tighter" style={{ color: getColor(resilienceScore) }}>
                {Math.round(resilienceScore)}%
            </div>
            <div className="text-[10px] font-black text-slate-500 uppercase tracking-widest mt-1">
                Resilience Index
            </div>
        </div>
      </div>
    </div>
  );
}
