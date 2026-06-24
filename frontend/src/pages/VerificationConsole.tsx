import React, { useState } from 'react';
import { useChartStore } from '../store/useChartStore';
import { ChevronDown, ChevronRight, Activity, Database } from 'lucide-react';

const StatusBadge = ({ status }: { status: 'LIVE DATA' | 'NOT EXPOSED' }) => {
  if (status === 'LIVE DATA') {
    return (
      <span className="inline-flex items-center gap-1 bg-emerald-100 text-emerald-800 px-2.5 py-0.5 rounded text-xs font-bold border border-emerald-200">
        <Activity className="w-3 h-3" />
        {status}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 bg-amber-100 text-amber-800 px-2.5 py-0.5 rounded text-xs font-bold border border-amber-200">
      <Database className="w-3 h-3" />
      {status}
    </span>
  );
};

const SectionHeader = ({ title, source, status, isOpen, onToggle }: { title: string, source: string, status: 'LIVE DATA' | 'NOT EXPOSED', isOpen: boolean, onToggle: () => void }) => (
  <button 
    onClick={onToggle}
    className="w-full flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 bg-slate-50 hover:bg-slate-100 transition-colors rounded-t-lg gap-4"
  >
    <div className="flex flex-col items-start gap-1">
      <div className="flex items-center gap-3">
        <h2 className="text-lg font-bold text-slate-800">{title}</h2>
        <StatusBadge status={status} />
      </div>
      <p className="text-xs text-slate-500 font-mono bg-slate-200 px-2 py-0.5 rounded mt-1">
        Source: {source}
      </p>
    </div>
    {isOpen ? <ChevronDown className="w-5 h-5 text-slate-500 flex-shrink-0" /> : <ChevronRight className="w-5 h-5 text-slate-500 flex-shrink-0" />}
  </button>
);

const CollapsibleSection = ({ title, source, status, children, defaultOpen = false }: { title: string, source: string, status: 'LIVE DATA' | 'NOT EXPOSED', children: React.ReactNode, defaultOpen?: boolean }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div className="border border-slate-200 rounded-lg mb-4 bg-white shadow-sm">
      <SectionHeader title={title} source={source} status={status} isOpen={isOpen} onToggle={() => setIsOpen(!isOpen)} />
      {isOpen && (
        <div className="p-4 border-t border-slate-200">
          {children}
        </div>
      )}
    </div>
  );
};

const JsonViewer = ({ data }: { data: any }) => (
  <pre className="bg-slate-900 text-emerald-400 p-4 rounded-lg overflow-x-auto text-sm font-mono border border-slate-800">
    {JSON.stringify(data, null, 2)}
  </pre>
);

export default function VerificationConsole() {
  const { rawOutputs, questionResults } = useChartStore();

  if (!rawOutputs || !rawOutputs.breakdown) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <h1 className="text-2xl font-bold text-slate-800 mb-2">Formula Verification Console</h1>
        <p className="text-slate-500">Please process a chart first to view the verification trace.</p>
      </div>
    );
  }

  const engineOutputs = rawOutputs.breakdown.engine_outputs || {};
  const natalPromise = engineOutputs.natal_promise || {};
  const planets = engineOutputs.planets || {};
  const houses = engineOutputs.houses || {};
  const dashas = engineOutputs.dashas || {};
  
  const latestResult = questionResults && questionResults.length > 0 
    ? questionResults[questionResults.length - 1] 
    : null;
  const isolatedSignals = latestResult?.isolated_signals || null;

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      <div className="bg-slate-900 text-white p-6 rounded-xl shadow-lg border border-slate-800">
        <h1 className="text-3xl font-bold mb-2">Formula Verification Console</h1>
        <p className="text-slate-300">Internal diagnostics and deterministic formula validation.</p>
      </div>

      {/* A. Domain Formula Trace */}
      <CollapsibleSection 
        title="B. Domain Formula Trace" 
        source="breakdown.engine_outputs.natal_promise" 
        status="LIVE DATA" 
        defaultOpen
      >
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 border border-slate-200 rounded-lg overflow-hidden">
            <thead className="bg-slate-100">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">Domain</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">Bhava</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">Bhavadhipati</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">Karaka</th>
                <th className="px-4 py-3 text-left text-xs font-bold text-slate-700 uppercase tracking-wider">Varga</th>
                <th className="px-4 py-3 text-left text-xs font-black text-indigo-900 uppercase tracking-wider bg-indigo-50">Final Score</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {Object.entries(natalPromise).map(([domain, data]: [string, any]) => {
                const bd = data.breakdown || {};
                return (
                  <tr key={domain} className="hover:bg-slate-50">
                    <td className="px-4 py-3 whitespace-nowrap font-bold text-slate-900 capitalize">{domain}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-slate-600 font-mono">{bd.bhava ?? '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-slate-600 font-mono">{bd.bhavadhipati ?? '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-slate-600 font-mono">{bd.karaka ?? '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-slate-600 font-mono">{bd.varga ?? '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap font-black text-indigo-700 font-mono bg-indigo-50/30">{data.score ?? '-'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </CollapsibleSection>

      {/* C. Planet Strength Breakdown */}
      <CollapsibleSection 
        title="C. Planet Strength Breakdown" 
        source="breakdown.engine_outputs.planets" 
        status="LIVE DATA"
      >
        <div className="space-y-3">
          {Object.entries(planets).map(([planet, data]: [string, any]) => {
            const bd = data.breakdown || {};
            return (
              <details key={planet} className="group bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
                <summary className="flex cursor-pointer items-center justify-between p-4 hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-4">
                    <span className="capitalize text-lg font-bold text-slate-800 w-24">{planet}</span>
                    <span className="bg-indigo-100 text-indigo-900 border border-indigo-200 px-3 py-1 rounded text-sm font-bold shadow-sm">
                      Final Score: {data.final_score}
                    </span>
                  </div>
                  <ChevronDown className="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform" />
                </summary>
                <div className="p-4 bg-white border-t border-slate-200 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">Dignity</span>
                    <span className="font-mono text-slate-800">{bd.dignity ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">House Placement</span>
                    <span className="font-mono text-slate-800">{bd.house_placement ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">Aspects</span>
                    <span className="font-mono text-slate-800">{bd.aspects ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">Conjunctions</span>
                    <span className="font-mono text-slate-800">{bd.conjunctions ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">Combustion</span>
                    <span className="font-mono text-slate-800">{bd.combustion ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">Retrogression</span>
                    <span className="font-mono text-slate-800">{bd.retrogression ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">Shadbala</span>
                    <span className="font-mono text-slate-800">{bd.shadbala?.toFixed(2) ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">BAV Modifier</span>
                    <span className="font-mono text-slate-800">{data.bav_modifier ?? '-'}</span>
                  </div>
                </div>
              </details>
            );
          })}
        </div>
      </CollapsibleSection>

      {/* D. House Strength Breakdown */}
      <CollapsibleSection 
        title="D. House Strength Breakdown" 
        source="breakdown.engine_outputs.houses" 
        status="LIVE DATA"
      >
        <div className="space-y-3">
          {Object.entries(houses).map(([house, data]: [string, any]) => {
            const bd = data.breakdown || {};
            return (
              <details key={house} className="group bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
                <summary className="flex cursor-pointer items-center justify-between p-4 hover:bg-slate-100 transition-colors">
                  <div className="flex items-center gap-4">
                    <span className="text-lg font-bold text-slate-800 w-24">House {house}</span>
                    <span className="bg-emerald-100 text-emerald-900 border border-emerald-200 px-3 py-1 rounded text-sm font-bold shadow-sm">
                      Final Score: {data.final_score}
                    </span>
                  </div>
                  <ChevronDown className="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform" />
                </summary>
                <div className="p-4 bg-white border-t border-slate-200 grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">SAV</span>
                    <span className="font-mono text-slate-800">{bd.sav ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">Occupants</span>
                    <span className="font-mono text-slate-800">{bd.occupants ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">Benefic Aspects</span>
                    <span className="font-mono text-slate-800">{bd.benefic_aspects ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">Malefic Aspects</span>
                    <span className="font-mono text-slate-800">{bd.malefic_aspects ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">House Type</span>
                    <span className="font-mono text-slate-800">{bd.house_type ?? '-'}</span>
                  </div>
                  <div className="bg-slate-50 p-3 rounded shadow-sm border border-slate-100">
                    <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">House Yogas</span>
                    <span className="font-mono text-slate-800">{bd.house_yogas ?? '-'}</span>
                  </div>
                </div>
              </details>
            );
          })}
        </div>
      </CollapsibleSection>

      {/* E. Dasha Formula Console */}
      <CollapsibleSection 
        title="E. Dasha Formula Console" 
        source="breakdown.engine_outputs.dashas.synthesis" 
        status="LIVE DATA"
      >
        {dashas.synthesis ? (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white border border-amber-200 p-6 rounded-xl shadow-sm text-center relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-amber-400"></div>
              <h3 className="text-amber-800 font-bold mb-1 text-xs uppercase tracking-wider">Current Mahadasha</h3>
              <p className="text-2xl font-black capitalize text-slate-800">{dashas.synthesis.active_md}</p>
              <div className="mt-3 bg-slate-50 py-2 rounded border border-slate-100">
                <p className="text-slate-500 text-xs uppercase font-bold">MD Strength</p>
                <p className="font-mono font-bold text-lg text-slate-700">{dashas.synthesis.md_strength}</p>
              </div>
            </div>
            
            <div className="bg-white border border-blue-200 p-6 rounded-xl shadow-sm text-center relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-blue-400"></div>
              <h3 className="text-blue-800 font-bold mb-1 text-xs uppercase tracking-wider">Current Antardasha</h3>
              <p className="text-2xl font-black capitalize text-slate-800">{dashas.synthesis.active_ad}</p>
              <div className="mt-3 bg-slate-50 py-2 rounded border border-slate-100">
                <p className="text-slate-500 text-xs uppercase font-bold">AD Strength</p>
                <p className="font-mono font-bold text-lg text-slate-700">{dashas.synthesis.ad_strength}</p>
              </div>
            </div>
            
            <div className="bg-white border border-purple-200 p-6 rounded-xl shadow-sm text-center relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-purple-400"></div>
              <h3 className="text-purple-800 font-bold mb-1 text-xs uppercase tracking-wider">Current Pratyantardasha</h3>
              <p className="text-2xl font-black capitalize text-slate-800">{dashas.synthesis.active_pd}</p>
              <div className="mt-3 bg-slate-50 py-2 rounded border border-slate-100">
                <p className="text-slate-500 text-xs uppercase font-bold">PD Strength</p>
                <p className="font-mono font-bold text-lg text-slate-700">{dashas.synthesis.pd_strength}</p>
              </div>
            </div>
            
            <div className="bg-white border border-emerald-200 p-6 rounded-xl shadow-sm text-center relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-emerald-400"></div>
              <h3 className="text-emerald-800 font-bold mb-1 text-xs uppercase tracking-wider">Activation Index</h3>
              <div className="flex items-center justify-center h-full pb-4">
                <p className="text-4xl font-black text-emerald-600 font-mono">{dashas.synthesis.dasha_strength}%</p>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-slate-500 italic p-4 text-center">No temporal activation data found.</p>
        )}
      </CollapsibleSection>

      {/* F. Signal Trace Console */}
      <CollapsibleSection 
        title="F. Signal Trace Console" 
        source="isolated_signals" 
        status="LIVE DATA"
        defaultOpen
      >
        {!latestResult ? (
          <div className="bg-amber-50 border border-amber-200 p-8 rounded-lg text-center flex flex-col items-center justify-center">
            <Database className="w-12 h-12 text-amber-300 mb-4" />
            <h3 className="text-lg font-bold text-amber-900 mb-2">Signal Trace requires an active query.</h3>
            <p className="text-amber-700 max-w-lg">
              Ask a structured question in the Question Browser to hydrate the signal trace.
            </p>
          </div>
        ) : !isolatedSignals || Object.keys(isolatedSignals).length === 0 ? (
          <div className="bg-slate-50 border border-slate-200 p-8 rounded-lg text-center">
            <p className="text-slate-500">No signals isolated for "{latestResult.question_title}".</p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="bg-indigo-50 border border-indigo-100 p-4 rounded-lg mb-4">
              <p className="text-indigo-900 font-bold text-sm">Target Formula: <span className="font-normal">{latestResult.question_title}</span></p>
            </div>
            {Object.entries(isolatedSignals).map(([signalKey, signalData]: [string, any]) => {
              const bd = signalData.breakdown || {};
              const meta = signalData.metadata || {};
              
              return (
                <details key={signalKey} className="group bg-white rounded-lg border border-slate-200 overflow-hidden shadow-sm">
                  <summary className="flex cursor-pointer items-center justify-between p-4 hover:bg-slate-50 transition-colors">
                    <div className="flex items-center gap-4">
                      <span className="capitalize text-lg font-bold text-slate-800 w-32">
                        {signalKey.replace(/_/g, ' ')}
                      </span>
                      {signalData.final_score !== undefined && (
                        <span className={`px-3 py-1 rounded text-sm font-bold shadow-sm ${signalData.final_score >= 50 ? 'bg-emerald-100 text-emerald-900 border border-emerald-200' : 'bg-red-100 text-red-900 border border-red-200'}`}>
                          Score: {signalData.final_score}
                        </span>
                      )}
                    </div>
                    <ChevronDown className="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform" />
                  </summary>
                  <div className="p-4 bg-slate-50 border-t border-slate-200">
                    
                    {/* Metadata Row */}
                    <div className="flex gap-4 mb-4">
                      <span className="bg-slate-200 text-slate-700 text-xs px-2 py-1 rounded font-mono uppercase tracking-wider">
                        Type: {meta.entity_type || 'Unknown'}
                      </span>
                      <span className="bg-slate-200 text-slate-700 text-xs px-2 py-1 rounded font-mono uppercase tracking-wider">
                        ID: {meta.entity_id || signalKey}
                      </span>
                    </div>

                    {/* Breakdown Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      {Object.entries(bd).map(([k, v]: [string, any]) => (
                        <div key={k} className="bg-white p-3 rounded shadow-sm border border-slate-100">
                          <span className="text-slate-500 block mb-1 text-xs uppercase font-bold tracking-wider">
                            {k.replace(/_/g, ' ')}
                          </span>
                          <span className="font-mono text-slate-800">
                            {typeof v === 'number' && !Number.isInteger(v) ? v.toFixed(2) : String(v)}
                          </span>
                        </div>
                      ))}
                    </div>
                    
                    {/* Confidence Flags */}
                    {signalData.confidence_flags && signalData.confidence_flags.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-slate-200">
                        <span className="text-slate-500 block mb-2 text-xs uppercase font-bold tracking-wider">Confidence Flags</span>
                        <div className="flex flex-wrap gap-2">
                          {signalData.confidence_flags.map((flag: string, idx: number) => (
                            <span key={idx} className="bg-amber-100 text-amber-800 border border-amber-200 px-2 py-1 rounded text-xs font-bold">
                              {flag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </details>
              );
            })}
          </div>
        )}
      </CollapsibleSection>

      {/* G. Engine Output Snapshot */}
      <CollapsibleSection 
        title="G. Engine Output Snapshot" 
        source="breakdown" 
        status="LIVE DATA"
      >
        <JsonViewer data={rawOutputs.breakdown} />
      </CollapsibleSection>

    </div>
  );
}
