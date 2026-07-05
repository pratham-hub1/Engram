import React, { useEffect, useRef, useState } from 'react';
import GlassCard from '../components/GlassCard';
import * as d3 from 'd3';
import { Zap } from 'lucide-react';

export default function MemorySummaryGraph() {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const simulationRef = useRef(null);
  const nodesRef = useRef([]);
  const linksRef = useRef([]);
  
  const [ingestionCount, setIngestionCount] = useState(0);
  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;
    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    const initGraph = async () => {
      // Initial Data Fetch
      if (nodesRef.current.length === 0) {
        try {
          const res = await fetch('http://127.0.0.1:8000/api/graph/summary');
          if (res.ok) {
            const data = await res.json();
            nodesRef.current = data.nodes || [];
            linksRef.current = data.links || [];
          }
        } catch (e) {
          console.error("Failed to fetch graph summary:", e);
        }
        
        // Fallback if empty or failed
        if (nodesRef.current.length === 0) {
          nodesRef.current = [
            { id: 'Project Core', group: 1, radius: 24 },
            { id: 'Backend API', group: 2, radius: 16 },
            { id: 'Frontend UI', group: 2, radius: 16 },
            { id: 'Memory Orchestrator', group: 3, radius: 12 },
            { id: 'Observer Service', group: 3, radius: 12 },
            { id: 'Cognee Graph', group: 4, radius: 20 },
            { id: 'LLM Extraction', group: 3, radius: 12 },
            { id: 'SQLite Log', group: 4, radius: 12 },
            { id: 'LanceDB', group: 4, radius: 12 },
            { id: 'KuzuDB', group: 4, radius: 12 },
            { id: 'Dashboard', group: 5, radius: 16 },
            { id: 'MCP Server', group: 5, "radius": 16 },
          ];
          linksRef.current = [
            { source: 'Project Core', target: 'Backend API', value: 2 },
            { source: 'Project Core', target: 'Frontend UI', value: 2 },
            { source: 'Backend API', target: 'Memory Orchestrator', value: 1 },
            { source: 'Backend API', target: 'Observer Service', value: 1 },
            { source: 'Observer Service', target: 'LLM Extraction', value: 1 },
            { source: 'LLM Extraction', target: 'Cognee Graph', value: 3 },
            { source: 'Memory Orchestrator', target: 'Cognee Graph', value: 3 },
            { source: 'Cognee Graph', target: 'SQLite Log', value: 1 },
            { source: 'Cognee Graph', target: 'LanceDB', value: 1 },
            { source: 'Cognee Graph', target: 'KuzuDB', value: 1 },
            { source: 'Frontend UI', target: 'Dashboard', value: 2 },
            { source: 'Dashboard', target: 'Memory Orchestrator', value: 2 },
            { source: 'Backend API', target: 'MCP Server', value: 2 },
            { source: 'MCP Server', target: 'Memory Orchestrator', value: 2 },
          ];
        }
      }

      const svg = d3.select(svgRef.current)
        .attr('width', width)
        .attr('height', height);
      
      svg.selectAll('*').remove();

    // Defs for organic shadows
    const defs = svg.append('defs');
    const filter = defs.append('filter')
      .attr('id', 'soft-shadow')
      .attr('x', '-20%').attr('y', '-20%').attr('width', '140%').attr('height', '140%');
    filter.append('feDropShadow')
      .attr('dx', '0').attr('dy', '4').attr('stdDeviation', '6').attr('flood-color', 'rgba(45,49,66,0.1)');

    // Master container for pan and zoom
    const mainContainer = svg.append('g').attr('class', 'main-container');

    // Setup zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.2, 4]) // Allow zooming out to 20% and in to 400%
      .on('zoom', (event) => {
        mainContainer.attr('transform', event.transform);
      });

    // Apply zoom to the SVG
    svg.call(zoom);

    const linkGroup = mainContainer.append('g').attr('class', 'links');
    const nodeGroup = mainContainer.append('g').attr('class', 'nodes');

    const simulation = d3.forceSimulation()
      .force('link', d3.forceLink().id(d => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(d => d.radius + 20));
      
    simulationRef.current = simulation;

    const update = () => {
      const nodes = nodesRef.current;
      const links = linksRef.current;

      // Update links with elegant Bezier curves
      const link = linkGroup.selectAll('path')
        .data(links, d => `${d.source.id || d.source}-${d.target.id || d.target}`);
      
      const linkEnter = link.enter().append('path')
        .attr('fill', 'none')
        .attr('stroke', 'rgba(45, 49, 66, 0.15)')
        .attr('stroke-width', d => Math.sqrt(d.value) * 1.5)
        .style('opacity', 0)
        .transition().duration(800)
        .style('opacity', 1);

      const linkUpdate = linkGroup.selectAll('path');

      // Update nodes
      const node = nodeGroup.selectAll('g.node')
        .data(nodes, d => d.id);

      const nodeEnter = node.enter().append('g')
        .attr('class', 'node')
        .call(d3.drag()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended));

      nodeEnter.append('circle')
        .attr('r', 0)
        .attr('fill', d => {
          if (d.group === 1) return '#ffffff';
          if (d.group === 4) return 'var(--accent-primary)';
          if (d.group === 6) return 'var(--accent-success)'; // New injected nodes
          return 'rgba(255, 255, 255, 0.8)';
        })
        .attr('stroke', d => {
          if (d.group === 1) return 'var(--text-main)';
          if (d.group === 4) return 'var(--accent-primary)';
          if (d.group === 6) return 'var(--accent-success)';
          return 'rgba(45, 49, 66, 0.2)';
        })
        .attr('stroke-width', 2)
        .style('filter', 'url(#soft-shadow)')
        .transition().duration(800)
        .attr('r', d => d.radius);

      nodeEnter.append('text')
        .text(d => d.id)
        .attr('x', d => d.radius + 12)
        .attr('y', 4)
        .attr('fill', d => d.group === 4 || d.group === 6 ? 'var(--accent-primary)' : 'var(--text-main)')
        .style('font-family', 'var(--font-mono)')
        .style('font-size', '12px')
        .style('font-weight', d => d.group === 1 ? '700' : '500')
        .style('pointer-events', 'none')
        .style('opacity', 0)
        .transition().duration(800)
        .style('opacity', 1);

      const nodeUpdate = nodeGroup.selectAll('g.node');

      simulation
        .nodes(nodes)
        .on('tick', () => {
          linkUpdate.attr('d', d => {
            const dx = d.target.x - d.source.x;
            const dy = d.target.y - d.source.y;
            const dr = Math.sqrt(dx * dx + dy * dy) * 1.5; // Curvature
            return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
          });
          nodeUpdate.attr('transform', d => `translate(${d.x},${d.y})`);
        });

      simulation.force('link').links(links);
      simulation.alpha(1).restart();
    };

    update();
    
    window.__updateD3Graph = update;

    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }
  };

  initGraph();

    return () => {
      if (simulationRef.current) {
        simulationRef.current.stop();
      }
      delete window.__updateD3Graph;
    };
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', position: 'relative' }}>
      
      {/* Floating Header */}
      <div style={{ position: 'absolute', top: '2rem', left: '2rem', right: '2rem', zIndex: 10, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', pointerEvents: 'none' }}>
        <div>
          <h2 className="heading-primary" style={{ margin: 0, fontSize: '2rem' }}>The Neural Graph</h2>
          <div className="text-mono" style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>Live Organic Vector Representation</div>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '1rem', pointerEvents: 'auto' }}>

          {/* Legend Panel */}
          <div className="glass-panel" style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', background: 'rgba(255,255,255,0.6)', minWidth: '200px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: '#ffffff', border: '2px solid var(--text-main)' }}></div>
              <span className="text-mono" style={{ fontSize: '0.8rem', color: 'var(--text-main)', fontWeight: 600 }}>Core Architecture</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: 'var(--accent-primary)', border: '2px solid var(--accent-primary)' }}></div>
              <span className="text-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Databases & Storage</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: 'var(--accent-success)', border: '2px solid var(--accent-success)' }}></div>
              <span className="text-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Live Injections</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <div style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: 'rgba(255, 255, 255, 0.8)', border: '2px solid rgba(45, 49, 66, 0.2)' }}></div>
              <span className="text-mono" style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Standard Services</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Full Bleed Graph */}
      <div ref={containerRef} style={{ flex: 1, width: '100%', height: '100%', background: 'transparent' }}>
        <svg ref={svgRef} style={{ width: '100%', height: '100%' }} />
      </div>
      
    </div>
  );
}
