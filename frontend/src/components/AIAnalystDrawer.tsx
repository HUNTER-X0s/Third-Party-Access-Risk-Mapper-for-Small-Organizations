import React, { useState } from 'react';
import { Bot, Shield, AlertTriangle, CheckCircle, FileText, X, ArrowRight, CornerDownLeft, Lock } from 'lucide-react';
import { SEVERITY_STYLES } from '../designTokens';

interface Claim {
  claim: string;
  evidence_ids: string[];
}

interface SecurityObjectRef {
  type: string;
  id: string;
  display_name?: string;
}

interface Recommendation {
  action: string;
  source: string; // DETERMINISTIC_RECOMMENDATION or AI_SUGGESTION
}

interface AIAnalysisResponse {
  answer: string;
  summary: string;
  severity: string;
  confidence: string;
  claims: Claim[];
  security_objects: SecurityObjectRef[];
  recommendations: Recommendation[];
  limitations: string[];
  model_metadata?: {
    provider?: string;
    model?: string;
    mode?: string;
    latency_ms?: number;
  };
}

interface AIAnalystDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  initialQuestion?: string;
  contextType?: string; // GENERAL, APPLICATION, FINDING, DATA_ASSET, PATH, SNAPSHOT
  entityId?: string;
  entityName?: string;
}

export const AIAnalystDrawer: React.FC<AIAnalystDrawerProps> = ({
  isOpen,
  onClose,
  initialQuestion = 'Provide a high-level security risk overview.',
  contextType = 'GENERAL',
  entityId,
  entityName,
}) => {
  const [question, setQuestion] = useState(initialQuestion);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<AIAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleAnalyze = async (queryText?: string) => {
    const q = queryText || question;
    if (!q.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/v1/ai/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: q,
          context_type: contextType,
          entity_id: entityId,
          mode: 'TECHNICAL',
        }),
      });

      if (!res.ok) {
        throw new Error(`AI Request failed with status ${res.status}`);
      }

      const data: AIAnalysisResponse = await res.json();
      setResponse(data);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to AI Security Analyst service.');
    } finally {
      setLoading(false);
    }
  };

  const sevStyle = response ? (SEVERITY_STYLES[response.severity] || SEVERITY_STYLES.Info) : SEVERITY_STYLES.Info;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/30 flex justify-end">
      <div className="w-full max-w-2xl bg-white border-l border-slate-200 text-slate-900 h-full flex flex-col shadow-2xl font-sans">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-md bg-blue-50 border border-blue-200 text-blue-600">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-bold text-slate-900">Security Analyst Copilot</h2>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                  Read-Only Advisory
                </span>
              </div>
              <p className="text-xs text-slate-500">
                {entityName ? `Context: ${entityName}` : 'Grounded Security Intelligence & Investigation'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Query Bar */}
          <div className="space-y-2.5">
            <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Investigation Prompt
            </label>
            <div className="relative">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={2}
                placeholder="Ask analyst about risk factors, evidence, or attack paths..."
                className="w-full bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 resize-none transition-all shadow-xs"
              />
              <button
                onClick={() => handleAnalyze()}
                disabled={loading}
                className="absolute right-3 bottom-3 px-3 py-1.5 rounded-md bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium flex items-center gap-1.5 transition-colors disabled:opacity-50 cursor-pointer shadow-xs"
              >
                {loading ? 'Analyzing...' : 'Run Query'}
                <CornerDownLeft className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Suggested Queries */}
            <div className="flex flex-wrap gap-1.5 pt-1">
              {[
                'Why is this critical risk?',
                'What evidence grounds this finding?',
                'What happens if compromised?',
                'Which remediation to prioritize?',
              ].map((sq) => (
                <button
                  key={sq}
                  onClick={() => {
                    setQuestion(sq);
                    handleAnalyze(sq);
                  }}
                  className="text-xs px-2.5 py-1 rounded-md bg-slate-50 border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors cursor-pointer"
                >
                  {sq}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 shrink-0 text-red-600" />
              <span>{error}</span>
            </div>
          )}

          {response && (
            <div className="space-y-6">
              {/* Status & Model Banner */}
              <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase border ${sevStyle.bg} ${sevStyle.text} ${sevStyle.border}`}>
                    {response.severity} Risk
                  </span>
                  <span className="text-slate-500">Confidence: <strong className="text-slate-800">{response.confidence}</strong></span>
                </div>
                <div className="text-slate-400 font-mono text-[11px]">
                  Model: {response.model_metadata?.model || 'gemini-2.5-flash'} ({response.model_metadata?.latency_ms || 0}ms)
                </div>
              </div>

              {/* Main Answer Card */}
              <div className="p-4 rounded-lg bg-white border border-slate-200 shadow-xs space-y-3">
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <FileText className="w-4 h-4 text-blue-600" />
                  <span>Analyst Findings & Evidence Interpretation</span>
                </h3>
                <div className="text-xs text-slate-700 leading-relaxed space-y-2 whitespace-pre-wrap">
                  {response.answer}
                </div>
              </div>

              {/* Claims & Evidence Grounding */}
              {response.claims && response.claims.length > 0 && (
                <div className="space-y-2.5">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Grounded Factual Claims ({response.claims.length})
                  </h4>
                  <div className="space-y-2">
                    {response.claims.map((c, i) => (
                      <div key={i} className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs text-xs space-y-1.5">
                        <p className="text-slate-800 font-medium">{c.claim}</p>
                        {c.evidence_ids && c.evidence_ids.length > 0 && (
                          <div className="flex items-center gap-1.5 pt-1">
                            <span className="text-slate-400 font-mono text-[11px]">Evidence Citations:</span>
                            {c.evidence_ids.map((eid) => (
                              <span key={eid} className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-700 font-mono text-[10px]">
                                {eid}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {response.recommendations && response.recommendations.length > 0 && (
                <div className="space-y-2.5">
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Action Guidance</h4>
                  <div className="space-y-2">
                    {response.recommendations.map((rec, i) => (
                      <div key={i} className="p-3.5 rounded-lg bg-white border border-slate-200 shadow-xs flex items-start gap-3 text-xs">
                        <ArrowRight className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
                        <div className="flex-1">
                          <p className="text-slate-800 font-medium">{rec.action}</p>
                          <span className={`inline-block mt-1.5 text-[10px] font-medium px-2 py-0.5 rounded border ${
                            rec.source === 'DETERMINISTIC_RECOMMENDATION'
                              ? 'bg-blue-50 border-blue-200 text-blue-700'
                              : 'bg-emerald-50 border-emerald-200 text-emerald-700'
                          }`}>
                            {rec.source === 'DETERMINISTIC_RECOMMENDATION' ? 'Authoritative Engine' : 'AI Advisory Suggestion'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Limitations & Safeguards */}
              {response.limitations && response.limitations.length > 0 && (
                <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1">
                  <span className="text-slate-500 font-semibold text-[11px] uppercase block">Security Safeguards & Governance</span>
                  <ul className="list-disc list-inside text-slate-500 space-y-0.5 text-[11px]">
                    {response.limitations.map((lim, i) => (
                      <li key={i}>{lim}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500 font-mono">
          <div className="flex items-center gap-1.5">
            <Lock className="w-3.5 h-3.5 text-emerald-600" />
            <span>Sandboxed Read-Only Governance</span>
          </div>
          <span>AccessGuard v1.5.0</span>
        </div>
      </div>
    </div>
  );
};
