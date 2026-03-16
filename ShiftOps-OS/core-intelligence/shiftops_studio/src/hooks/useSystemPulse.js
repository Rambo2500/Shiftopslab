// hooks/useSystemPulse.js
import { useState, useEffect } from "react";

export function useSystemPulse(snapshot, isRunning) {
  const [activeEdge, setActiveEdge] = useState(null);
  const [activeNode, setActiveNode] = useState(null);
  const [metrics, setMetrics] = useState({ throughput: 0, latency: '24ms' });
  const [nodeHeat, setNodeHeat] = useState({});

  useEffect(() => {
    if (!isRunning || !snapshot?.architecture?.edges || snapshot.architecture.edges.length === 0) return;

    const interval = setInterval(() => {
      const edges = snapshot.architecture.edges;
      const pulseEdge = edges[Math.floor(Math.random() * edges.length)];
      
      setActiveEdge(pulseEdge.id);
      setActiveNode(pulseEdge.to); // Pulse hits the target node
      
      // Update Heat Map
      setNodeHeat(prev => ({
        ...prev,
        [pulseEdge.to]: (prev[pulseEdge.to] || 0) + 1
      }));

      // Temporal Entropy: Add ±5% jitter to the metrics
      const baseThroughput = (snapshot.diagnostics?.scalability_index || 10) * 20;
      const demandMultiplier = 1.0; // In a real scenario, this comes from the active scenario
      const targetThroughput = baseThroughput * demandMultiplier;
      const jitter = targetThroughput * 0.05; // 5% jitter
      const actualThroughput = targetThroughput + (Math.random() * jitter * 2) - jitter;

      const baseLatency = 20;
      const latencyJitter = baseLatency * 0.1; // 10% jitter for latency
      const actualLatency = baseLatency + (Math.random() * latencyJitter * 2) - latencyJitter;

      setMetrics({
        throughput: Math.floor(actualThroughput),
        latency: `${Math.floor(actualLatency)}ms`
      });

      // Decay heat over time
      setTimeout(() => {
        setActiveEdge(null);
        setActiveNode(null);
      }, 400);

    }, 1200);

    // Occasional heat decay
    const decayInterval = setInterval(() => {
      setNodeHeat(prev => {
        const next = { ...prev };
        Object.keys(next).forEach(nodeId => {
          if (next[nodeId] > 0) next[nodeId] -= 0.5;
        });
        return next;
      });
    }, 2000);

    return () => {
      clearInterval(interval);
      clearInterval(decayInterval);
    };
  }, [snapshot, isRunning]);

  return { activeEdge, activeNode, metrics, nodeHeat };
}
