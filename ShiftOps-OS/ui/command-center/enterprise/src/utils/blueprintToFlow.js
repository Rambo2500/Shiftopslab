import { layoutGraph } from './layoutGraph';

export function blueprintToFlow(blueprint) {
  if (!blueprint || !blueprint.graph) return { nodes: [], edges: [] };

  const rawNodes = blueprint.graph.nodes.map((node) => ({
    id: node.id,
    data: { 
      label: node.id,
      type: node.type,
      traits: node.traits 
    },
    style: { 
      background: '#1e293b', 
      color: '#fff', 
      borderRadius: '8px',
      border: '1px solid #334155',
      padding: '10px',
      fontSize: '12px',
      width: 180,
      textAlign: 'center'
    }
  }));

  const edges = (blueprint.graph.edges || []).map((edge, index) => ({
    id: `e-${index}`,
    source: edge.from,
    target: edge.to,
    animated: true,
    style: { stroke: '#1a66ff', strokeWidth: 2 }
  }));

  const nodes = layoutGraph(rawNodes, edges);
  return { nodes, edges };
}
