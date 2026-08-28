import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { api } from '../services/api';
import { SeverityBadge } from './SeverityBadge';
import { PotentialAttackPath } from '../types';
import { Network, Database, Box, Shield, Filter, Zap, Layers, AlertTriangle, ArrowRight, X, ChevronRight, GripVertical } from 'lucide-react';

export const AccessGraphView: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  const [attackPaths, setAttackPaths] = useState<PotentialAttackPath[]>([]);
  const [selectedPath, setSelectedPath] = useState<PotentialAttackPath | null>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [selectedEdgeMeta, setSelectedEdgeMeta] = useState<any>(null);
  const [filterMode, setFilterMode] = useState<string>('ALL');
  const [graphMode, setGraphMode] = useState<'CURRENT' | 'DELTA' | 'BASELINE'>('DELTA');
  const [deltaSummary, setDeltaSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showAttackPaths, setShowAttackPaths] = useState(true);

  // Draggable legend state — default to top-right (we'll place via absolute with right/top)
  const legendRef = useRef<HTMLDivElement>(null);
  const dragOffset = useRef<{ x: number; y: number }>({ x: 0, y: 0 });
  const [legendPos, setLegendPos] = useState<{ right: number; top: number } | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [legendFixed, setLegendFixed] = useState<{ left: number; top: number } | null>(null);

  const canvasRef = useRef<HTMLDivElement>(null);

  const onLegendPointerDown = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.currentTarget.setPointerCapture(e.pointerId);
    const legendEl = legendRef.current;
    if (!legendEl) return;
    const bRect = legendEl.getBoundingClientRect();
    dragOffset.current = { x: e.clientX - bRect.left, y: e.clientY - bRect.top };
    setIsDragging(true);
  }, []);

  const onLegendPointerMove = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    const container = canvasRef.current;
    if (!container) return;
    const cRect = container.getBoundingClientRect();
    const newLeft = Math.max(0, Math.min(e.clientX - cRect.left - dragOffset.current.x, cRect.width - 180));
    const newTop = Math.max(0, Math.min(e.clientY - cRect.top - dragOffset.current.y, cRect.height - 120));
    setLegendFixed({ left: newLeft, top: newTop });
  }, [isDragging]);

  const onLegendPointerUp = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    e.currentTarget.releasePointerCapture(e.pointerId);
    setIsDragging(false);
  }, []);

  const loadGraph = () => {
    setLoading(true);
    const graphPromise = graphMode === 'DELTA' ? api.getAccessGraphDelta() : api.getAccessGraph();

    Promise.all([
      graphPromise,
      api.getPotentialAttackPaths().catch(() => [])
    ]).then(([graphData, paths]) => {
      setAttackPaths(paths);
      if (paths.length > 0) setSelectedPath(paths[0]);
      if (graphData.delta_summary) setDeltaSummary(graphData.delta_summary);

      const formattedNodes = (graphData.nodes || []).map((node: any) => {
        const isCrownJewel = node.type === 'data_asset' && node.data.is_crown_jewel;
        const isOrg = node.type === 'organization';

        return {
          id: node.id,
          type: 'default',
          position: node.position,
          data: {
            label: (
              <div className="p-3 text-left space-y-1.5 font-sans">
                <div className="flex items-center space-x-1.5 font-semibold text-xs text-slate-900">
                  {isOrg && <Shield className="w-3.5 h-3.5 text-blue-600" />}
                  {node.type === 'application' && <Box className="w-3.5 h-3.5 text-slate-500" />}
                  {node.type === 'data_asset' && <Database className="w-3.5 h-3.5 text-slate-500" />}
                  <span className="truncate">{node.data.label}</span>
                </div>

                {node.data.risk_severity && (
                  <div className="flex items-center space-x-1.5">
                    <SeverityBadge severity={node.data.risk_severity} showDot />
                    <span className="text-[10px] font-mono text-slate-500">{node.data.risk_score} pts</span>
                  </div>
                )}

                {isCrownJewel && (
                  <span className="bg-red-50 text-red-700 border border-red-200 text-[10px] px-1.5 py-0.2 rounded font-medium inline-block">
                    Crown Jewel
                  </span>
                )}
              </div>
            )
          },
          style: {
            background: isCrownJewel ? '#FFF5F5' : '#FFFFFF',
            color: '#0F172A',
            border: isCrownJewel ? '1px solid #FECACA' : '1px solid #E2E8F0',
            borderRadius: '6px',
            width: 190,
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.05)',
            fontSize: '12px'
          },
          rawNode: node
        };
      });

      const formattedEdges = (graphData.edges || []).map((edge: any) => {
        let stroke = edge.style?.stroke || '#94A3B8';
        let strokeDasharray = edge.style?.strokeDasharray;

        if (graphMode === 'DELTA' && edge.change_status) {
          if (edge.change_status === 'NEW') stroke = '#16803C';
          else if (edge.change_status === 'CHANGED') stroke = '#B54708';
          else if (edge.change_status === 'REMOVED') {
            stroke = '#B42318';
            strokeDasharray = '4 4';
          }
        }

        return {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.label || '',
          animated: edge.animated || edge.change_status === 'NEW',
          style: {
            ...edge.style,
            stroke,
            strokeDasharray,
            strokeWidth: edge.change_status && edge.change_status !== 'UNCHANGED' ? 2 : 1.5,
            cursor: edge.change_metadata ? 'pointer' : 'default'
          },
          markerEnd: { type: MarkerType.ArrowClosed, color: stroke },
          rawEdge: edge
        };
      });

      setNodes(formattedNodes);
      setEdges(formattedEdges);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadGraph();
  }, [graphMode]);

  const filteredNodes = nodes.filter(node => {
    if (filterMode === 'ALL') return true;
    if (filterMode === 'CROWN_JEWELS') return node.rawNode.data?.is_crown_jewel || node.rawNode.type === 'organization';
    if (filterMode === 'HIGH_RISK') return node.rawNode.data?.risk_severity === 'Critical' || node.rawNode.data?.risk_severity === 'High' || node.rawNode.type === 'organization';
    return true;
  });

  const handleEdgeClick = (_: any, edge: any) => {
    if (edge.rawEdge?.change_metadata) {
      setSelectedEdgeMeta({
        edgeId: edge.id,
        label: edge.label,
        ...edge.rawEdge.change_metadata
      });
    }
  };

  return (
    <div className="h-full w-full flex flex-col bg-white border border-slate-200 rounded-lg shadow-xs relative font-sans overflow-hidden">
      {/* Control & Filter Header */}
      <div className="p-3 sm:p-3.5 bg-white border-b border-slate-200 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs">
        <div className="flex flex-wrap items-center gap-3 sm:gap-4">
          <div className="flex items-center space-x-2 font-bold text-slate-900">
            <Network className="w-4 h-4 text-blue-600" />
            <span>Access Topology & Attack Graph</span>
          </div>

          {/* Graph Mode Segmented Control */}
          <div className="flex items-center space-x-1 pl-2 sm:pl-4 border-l border-slate-200">
            <Layers className="w-3.5 h-3.5 text-slate-400 mr-1 hidden xs:inline" />
            {(['DELTA', 'CURRENT', 'BASELINE'] as const).map(mode => (
              <button
                key={mode}
                onClick={() => setGraphMode(mode)}
                className={`px-2 sm:px-2.5 py-1 rounded-md text-[11px] font-medium transition-colors cursor-pointer ${
                  graphMode === mode
                    ? 'bg-blue-50 text-blue-700 border border-blue-200 font-semibold'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                {mode === 'DELTA' ? 'Delta Mode' : mode}
              </button>
            ))}
          </div>

          <div className="flex items-center space-x-1.5 pl-2 sm:pl-4 border-l border-slate-200 text-xs">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filterMode}
              onChange={(e) => setFilterMode(e.target.value)}
              className="bg-white border border-slate-200 rounded-md px-2 py-1 text-slate-700 text-xs focus:outline-none focus:border-blue-500 cursor-pointer shadow-xs"
            >
              <option value="ALL">All Nodes & Relationships</option>
              <option value="CROWN_JEWELS">Crown Jewels Reachability</option>
              <option value="HIGH_RISK">High/Critical Risk Paths</option>
            </select>
          </div>
        </div>

        <div className="text-slate-500 text-xs flex flex-wrap items-center gap-2 sm:gap-3 self-stretch sm:self-auto justify-between sm:justify-end">
          {graphMode === 'DELTA' && deltaSummary && (
            <div className="flex items-center space-x-2 text-[11px] font-medium">
              <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">+{deltaSummary.new_edges_count} New</span>
              <span className="text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">~{deltaSummary.changed_edges_count} Changed</span>
              <span className="text-slate-500 hidden sm:inline">{deltaSummary.unchanged_edges_count} Unchanged</span>
            </div>
          )}
          <span className="text-slate-300 hidden sm:inline">|</span>
          <span className="text-slate-600 font-medium">Engine: <span className="text-emerald-700 font-bold">Deterministic Graph</span></span>
        </div>
      </div>

      {/* Main Container: Canvas + Attack Path Panel */}
      <div className="flex-1 flex overflow-hidden relative min-h-0">
        {/* React Flow Canvas — always fills remaining space */}
        <div
          ref={canvasRef}
          className="flex-1 min-w-0 min-h-0 h-full relative bg-[#F8FAFC]"
        >
          {loading ? (
            <div className="flex items-center justify-center h-full text-slate-400 text-xs">
              Loading graph topology...
            </div>
          ) : (
            <ReactFlow
              nodes={filteredNodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={(_, node) => setSelectedNode(node.rawNode || null)}
              onEdgeClick={handleEdgeClick}
              fitView
            >
              <Background color="#CBD5E1" gap={18} size={1} />
              <Controls />
            </ReactFlow>
          )}

          {/* Draggable Graph Legend — default top-right */}
          <div
            data-legend-wrap="true"
            ref={legendRef}
            style={legendFixed
              ? { position: 'absolute', left: legendFixed.left, top: legendFixed.top, right: 'auto', cursor: isDragging ? 'grabbing' : 'default' }
              : { position: 'absolute', right: 12, top: 12, left: 'auto', cursor: isDragging ? 'grabbing' : 'default' }
            }
            className="bg-white/95 border border-slate-200 rounded-lg shadow-md text-[11px] text-slate-700 z-20 select-none"
          >
            {/* Drag handle */}
            <div
              className="flex items-center justify-between px-2.5 pt-2 pb-1 border-b border-slate-100 cursor-grab active:cursor-grabbing"
              onPointerDown={onLegendPointerDown}
              onPointerMove={onLegendPointerMove}
              onPointerUp={onLegendPointerUp}
            >
              <span className="font-semibold text-slate-900 text-xs">Graph Legend</span>
              <GripVertical className="w-3.5 h-3.5 text-slate-400" />
            </div>
            <div className="grid grid-cols-2 gap-x-3 gap-y-1 p-2.5">
              <div className="flex items-center space-x-1.5">
                <span className="w-3 h-0.5 bg-slate-400 inline-block" />
                <span>Unchanged</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-3 h-0.5 bg-emerald-600 inline-block" />
                <span className="text-emerald-700 font-medium">New</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-3 h-0.5 bg-amber-600 inline-block" />
                <span className="text-amber-700 font-medium">Changed</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-3 h-0.5 bg-red-600 inline-block" />
                <span className="text-red-700">Removed</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" />
                <span>Crown Jewel</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block" />
                <span>High Risk</span>
              </div>
            </div>
          </div>

          {/* Attack path toggle button — visible only on small screens when panel is hidden */}
          {!selectedEdgeMeta && attackPaths.length > 0 && (
            <button
              onClick={() => setShowAttackPaths(p => !p)}
              className="absolute bottom-4 right-4 z-20 lg:hidden flex items-center space-x-1.5 bg-white border border-slate-200 shadow-md rounded-lg px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 cursor-pointer transition-colors"
            >
              <Zap className="w-3.5 h-3.5 text-blue-600" />
              <span>{showAttackPaths ? 'Hide' : 'Show'} Paths ({attackPaths.length})</span>
            </button>
          )}
        </div>

        {/* Changed Edge Detail Drawer */}
        {selectedEdgeMeta && (
          <div className="fixed inset-y-0 right-0 w-full sm:w-80 md:w-96 max-w-full bg-white border-l border-slate-200 p-4 sm:p-5 flex flex-col space-y-4 text-xs overflow-y-auto shadow-xl z-30">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span className="font-bold text-slate-900 text-xs uppercase">Relationship Change</span>
              </div>
              <button
                onClick={() => setSelectedEdgeMeta(null)}
                className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-slate-400 uppercase text-[10px] block font-medium">Change Type</span>
                <span className="font-semibold text-slate-900 text-sm">{selectedEdgeMeta.change_type}</span>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-md space-y-1.5">
                <span className="text-slate-400 uppercase text-[10px] block font-medium">Access Transition</span>
                <div className="flex items-center space-x-2 text-xs">
                  <span className="text-slate-600 bg-white px-2 py-0.5 rounded border border-slate-200">{selectedEdgeMeta.before}</span>
                  <ArrowRight className="w-3.5 h-3.5 text-amber-600" />
                  <span className="text-amber-800 bg-amber-50 px-2 py-0.5 rounded border border-amber-200 font-semibold">{selectedEdgeMeta.after}</span>
                </div>
              </div>

              <div>
                <span className="text-slate-400 uppercase text-[10px] block font-medium">Risk Impact</span>
                <p className="text-slate-700 text-xs leading-relaxed mt-1">{selectedEdgeMeta.risk_impact}</p>
              </div>

              {selectedEdgeMeta.evidence_refs?.length > 0 && (
                <div>
                  <span className="text-slate-400 uppercase text-[10px] block font-medium">Evidence References</span>
                  <div className="flex flex-wrap gap-1.5 mt-1.5">
                    {selectedEdgeMeta.evidence_refs.map((ref: string) => (
                      <span key={ref} className="px-2 py-0.5 bg-slate-50 border border-slate-200 text-slate-600 font-mono text-[11px] rounded">
                        {ref}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Attack Path Panel — always visible on lg+, collapsible on smaller screens */}
        {!selectedEdgeMeta && attackPaths.length > 0 && (
          <div
            className={[
              'bg-white border-l border-slate-200 flex-col space-y-3 text-xs shadow-xs overflow-y-auto',
              'lg:flex lg:w-72 xl:w-80 lg:p-4',
              showAttackPaths
                ? 'flex fixed inset-y-0 right-0 w-80 max-w-[90vw] z-30 p-4 lg:static lg:z-auto'
                : 'hidden lg:flex'
            ].join(' ')}
          >
            <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <span className="font-bold text-slate-900 text-xs flex items-center space-x-1.5">
                <Zap className="w-4 h-4 text-blue-600" />
                <span>Attack Paths ({attackPaths.length})</span>
              </span>
              {/* Close button on mobile */}
              <button
                onClick={() => setShowAttackPaths(false)}
                className="lg:hidden p-1 rounded-md text-slate-400 hover:text-slate-600 cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-2.5 overflow-y-auto flex-1">
              {attackPaths.map((path) => (
                <div
                  key={path.path_id}
                  onClick={() => { setSelectedPath(path); setShowAttackPaths(false); }}
                  className={`p-3 rounded-lg border cursor-pointer transition-all space-y-2 ${
                    selectedPath?.path_id === path.path_id
                      ? 'bg-blue-50/50 border-blue-300 text-slate-900 shadow-xs'
                      : 'bg-white border-slate-200 text-slate-600 hover:border-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-900 text-xs truncate max-w-[140px]">{path.entry_application}</span>
                    <span className="font-mono text-red-600 font-bold text-xs ml-1">{path.path_risk_score} pts</span>
                  </div>

                  <p className="text-xs text-slate-600 line-clamp-2">
                    Target: <strong className="text-slate-900">{path.target_data_asset}</strong>
                  </p>

                  <div className="flex items-center justify-between text-[11px] pt-1.5 border-t border-slate-100">
                    <span className="text-emerald-700 font-medium">{path.confidence_percentage}% Confidence</span>
                    <span className="text-slate-500 uppercase text-[10px]">{path.verification_state}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
