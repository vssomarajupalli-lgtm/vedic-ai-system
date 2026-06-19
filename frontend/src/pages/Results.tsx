import { Navigate } from 'react-router-dom';
import { useChartStore } from '../store/useChartStore';
import { Award, User, Target, Activity } from 'lucide-react';

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
    natal_promise_analysis
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
