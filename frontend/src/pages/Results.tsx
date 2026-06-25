import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useChartStore } from '../store/useChartStore';
import { Award, User, Target, Activity, HelpCircle, Calendar, ChevronDown, ChevronRight, Database } from 'lucide-react';

const CollapsibleSection = ({ title, icon: Icon, children, defaultOpen = false }: { title: string, icon: any, children: React.ReactNode, defaultOpen?: boolean }) => {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mt-8">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-6 bg-slate-50 hover:bg-slate-100 transition-colors text-left"
      >
        <h3 className="text-xl font-bold text-slate-900 flex items-center">
          <Icon className="w-5 h-5 mr-2 text-indigo-600" />
          {title}
        </h3>
        {isOpen ? <ChevronDown className="w-6 h-6 text-slate-500" /> : <ChevronRight className="w-6 h-6 text-slate-500" />}
      </button>
      {isOpen && (
        <div className="p-6 border-t border-slate-200">
          {children}
        </div>
      )}
    </div>
  );
};

export default function Results() {
  const report = useChartStore((state) => state.report);

  // Guard clause if user navigates here without uploading
  if (!report) {
    return <Navigate to="/upload" replace />;
  }

  const {
    client_profile,
    master_probability,
    executive_summary,
    yoga_analysis,
    natal_promise_analysis,
    question_responses
  } = report;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      
      {/* Client Header */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 flex items-center">
            <User className="w-6 h-6 mr-2 text-indigo-600" />
            {client_profile?.name || 'Anonymous Client'}
          </h2>
          <p className="text-slate-500 mt-1">DOB: {client_profile?.dob || 'Unknown'} | TOB: {client_profile?.tob || 'Unknown'} | POB: {client_profile?.pob || 'Unknown'}</p>
        </div>
        <div className="text-right">
          <div className="inline-flex items-center justify-center px-4 py-2 bg-indigo-50 border border-indigo-100 rounded-lg">
            <Award className="w-5 h-5 text-indigo-600 mr-2" />
            <span className="font-bold text-indigo-900">
              Score: {master_probability.data_points?.final_score?.toFixed(1) || '0.0'}
            </span>
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <h3 className="text-xl font-bold text-slate-900 mb-4 flex items-center">
          <Target className="w-5 h-5 mr-2 text-indigo-600" />
          {executive_summary.title}
        </h3>
        <p className="text-lg text-slate-700 leading-relaxed">
          {executive_summary.summary_text}
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Natal Promise */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-indigo-600" />
            {natal_promise_analysis.title}
          </h3>
          <div className="space-y-4">
            {Object.entries(natal_promise_analysis.data_points || {}).map(([domain, details]: [string, any]) => (
              <div key={domain} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-100">
                <span className="font-semibold text-slate-700 capitalize">{domain}</span>
                <div className="flex items-center space-x-3">
                  <span className="text-sm font-medium text-slate-500">Score: {details.score}</span>
                  <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-indigo-100 text-indigo-800">
                    {details.grade}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Yogas */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
          <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
            <SparklesIcon className="w-5 h-5 mr-2 text-indigo-600" />
            {yoga_analysis.title}
          </h3>
          <p className="text-slate-600 mb-4">{yoga_analysis.summary_text}</p>
          <div className="space-y-3">
            {Object.entries(yoga_analysis.data_points?.summary_map || {}).map(([yoga, strength]: [string, any]) => (
              <div key={yoga} className="flex items-center justify-between border-b border-slate-100 pb-2 last:border-0">
                <span className="font-medium text-slate-800">{yoga}</span>
                <span className="text-sm text-indigo-600 font-semibold bg-indigo-50 px-2 py-1 rounded">Strength: {strength}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Question Results */}
      {question_responses && question_responses.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mt-8">
          <h3 className="text-xl font-bold text-slate-900 mb-6 flex items-center">
            <HelpCircle className="w-5 h-5 mr-2 text-indigo-600" />
            Question Results
          </h3>
          <div className="space-y-8">
            {question_responses.map((qr, idx) => (
              <div key={idx} className="border border-slate-200 rounded-lg overflow-hidden">
                <div className="bg-slate-50 p-4 border-b border-slate-200">
                  <h4 className="font-bold text-lg text-slate-800 capitalize">{qr.domain || 'Query'}: {qr.question}</h4>
                </div>
                <div className="p-4 bg-white">
                  <p className="text-slate-700 mb-6">{qr.answer_text}</p>
                  
                  {/* Top 5 Future Opportunity Windows */}
                  {qr.top_opportunities && qr.top_opportunities.length > 0 && (
                    <div>
                      <h5 className="font-bold text-slate-800 mb-3 flex items-center">
                        <Calendar className="w-4 h-4 mr-2 text-indigo-500" />
                        Top 5 Future Opportunity Windows
                      </h5>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-slate-200 border border-slate-200 rounded text-sm">
                          <thead className="bg-slate-50">
                            <tr>
                              <th className="px-3 py-2 text-left font-semibold text-slate-700">Period</th>
                              <th className="px-3 py-2 text-left font-semibold text-slate-700">MD</th>
                              <th className="px-3 py-2 text-left font-semibold text-slate-700">AD</th>
                              <th className="px-3 py-2 text-left font-semibold text-slate-700">PD</th>
                              <th className="px-3 py-2 text-right font-semibold text-slate-700">Prob. %</th>
                              <th className="px-3 py-2 text-center font-semibold text-slate-700">Grade</th>
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-slate-100">
                            {qr.top_opportunities.map((opp: any, oidx: number) => {
                              const [from, to] = (opp.period || "Unknown to Unknown").split(" to ");
                              return (
                                <tr key={oidx} className="hover:bg-slate-50">
                                  <td className="px-3 py-2 whitespace-nowrap text-slate-800">
                                    <span className="block font-medium">{from}</span>
                                    <span className="block text-xs text-slate-500">to {to}</span>
                                  </td>
                                  <td className="px-3 py-2 capitalize text-slate-600">{opp.md}</td>
                                  <td className="px-3 py-2 capitalize text-slate-600">{opp.ad}</td>
                                  <td className="px-3 py-2 capitalize text-slate-600">{opp.pd}</td>
                                  <td className="px-3 py-2 text-right font-mono font-bold text-indigo-600">{opp.final_probability_pct}%</td>
                                  <td className="px-3 py-2 text-center">
                                    <span className="px-2 py-1 text-xs font-bold rounded-full bg-indigo-100 text-indigo-800">
                                      {opp.grade}
                                    </span>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Technical Analysis */}
      {master_probability?.data_points?.lifetime_projection && (
        <CollapsibleSection title="Technical Analysis: Lifetime MD-AD-PD Strength Analysis" icon={Database}>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 border border-slate-200 rounded text-sm text-center">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-3 py-2 font-semibold text-slate-700 text-left">Period</th>
                  <th className="px-3 py-2 font-semibold text-slate-700 border-l border-slate-200">MD</th>
                  <th className="px-3 py-2 font-semibold text-slate-700">Strength</th>
                  <th className="px-3 py-2 font-semibold text-slate-700 border-l border-slate-200">AD</th>
                  <th className="px-3 py-2 font-semibold text-slate-700">Strength</th>
                  <th className="px-3 py-2 font-semibold text-slate-700 border-l border-slate-200">PD</th>
                  <th className="px-3 py-2 font-semibold text-slate-700">Strength</th>
                  <th className="px-3 py-2 font-semibold text-slate-700 border-l border-slate-200">Activation</th>
                  <th className="px-3 py-2 font-semibold text-indigo-700 bg-indigo-50 border-l border-slate-200">Prob. %</th>
                  <th className="px-3 py-2 font-semibold text-slate-700">Grade</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-100">
                {master_probability.data_points.lifetime_projection.map((proj: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="px-3 py-2 whitespace-nowrap text-slate-800 text-left">
                      <span className="block font-medium">{proj.start_date || 'Unknown'}</span>
                      <span className="block text-xs text-slate-500">to {proj.end_date || 'Unknown'}</span>
                    </td>
                    <td className="px-3 py-2 capitalize text-slate-600 border-l border-slate-100">{proj.md}</td>
                    <td className="px-3 py-2 font-mono text-slate-500">{proj.md_planet_strength?.toFixed(1) ?? '-'}</td>
                    <td className="px-3 py-2 capitalize text-slate-600 border-l border-slate-100">{proj.ad}</td>
                    <td className="px-3 py-2 font-mono text-slate-500">{proj.ad_planet_strength?.toFixed(1) ?? '-'}</td>
                    <td className="px-3 py-2 capitalize text-slate-600 border-l border-slate-100">{proj.pd}</td>
                    <td className="px-3 py-2 font-mono text-slate-500">{proj.pd_planet_strength?.toFixed(1) ?? '-'}</td>
                    <td className="px-3 py-2 font-mono text-emerald-600 font-medium border-l border-slate-100">{proj.activation_pct?.toFixed(1)}%</td>
                    <td className="px-3 py-2 font-mono font-bold text-indigo-700 bg-indigo-50/30 border-l border-slate-100">{proj.final_probability_pct?.toFixed(1)}%</td>
                    <td className="px-3 py-2 text-center">
                      <span className="px-2 py-1 text-[10px] uppercase font-bold rounded bg-slate-100 text-slate-700">
                        {proj.grade}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CollapsibleSection>
      )}

    </div>
  );
}

// Temporary icon to avoid adding too many imports
function SparklesIcon(props: any) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
  );
}
