import React from 'react';

export interface StructuredQuestionResult {
  question_title: string;
  promise_assessment: {
    promise_score: string;
    promise_grade: string;
    interpretation: string;
  };
  dasha_activation: {
    mahadasha: string;
    mahadasha_start?: string;
    mahadasha_end?: string;
    antardasha: string;
    antardasha_start?: string;
    antardasha_end?: string;
    pratyantardasha: string;
    pratyantardasha_start?: string;
    pratyantardasha_end?: string;
    activation_index: string;
    activation_grade: string;
  };
  final_conclusion: {
    promise_status: string;
    dasha_support: string;
    assessment: string;
  };
  timing_window: {
    mahadasha: string;
    antardasha: string;
    pratyantardasha: string;
    most_supportive_period: string;
  };
  supporting_factors: string[];
  attention_factors: string[];
  mandali_commentary: string;
}

interface Props {
  result: StructuredQuestionResult;
}

export const QuestionResultCard: React.FC<Props> = ({ result }) => {
  return (
    <div className="w-full bg-white shadow-lg rounded-xl overflow-hidden mb-6 border border-gray-200">
      {/* Header */}
      <div className="bg-blue-900 p-4 text-white">
        <h2 className="text-xl font-bold">Question: {result.question_title}</h2>
      </div>

      <div className="p-6 space-y-8 text-gray-800">
        {/* A. Promise Assessment */}
        <section className="border-b border-gray-200 pb-4">
          <h3 className="text-lg font-bold text-blue-800 mb-3 border-b-2 border-blue-200 inline-block">A. Promise Assessment</h3>
          <div className="grid grid-cols-2 gap-4">
            <div><span className="font-semibold text-gray-600">Promise Score:</span> <br/>{result.promise_assessment.promise_score}</div>
            <div><span className="font-semibold text-gray-600">Promise Grade:</span> <br/>{result.promise_assessment.promise_grade}</div>
          </div>
          <div className="mt-3">
            <span className="font-semibold text-gray-600">Interpretation:</span><br/>
            {result.promise_assessment.interpretation}
          </div>
        </section>

        {/* B. Current Dasha Activation */}
        <section className="border-b border-gray-200 pb-4">
          <h3 className="text-lg font-bold text-blue-800 mb-3 border-b-2 border-blue-200 inline-block">B. Current Dasha Activation</h3>
          <div className="space-y-4">
            {/* Mahadasha */}
            <div>
              <div className="font-semibold text-gray-600">Mahadasha</div>
              <div className="mb-2">{result.dasha_activation.mahadasha}</div>
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-700">
                <div><span className="font-semibold text-gray-500">Start Date:</span><br/>{result.dasha_activation.mahadasha_start || 'Unknown'}</div>
                <div><span className="font-semibold text-gray-500">End Date:</span><br/>{result.dasha_activation.mahadasha_end || 'Unknown'}</div>
              </div>
            </div>
            <hr className="border-gray-100" />
            {/* Antardasha */}
            <div>
              <div className="font-semibold text-gray-600">Antardasha</div>
              <div className="mb-2">{result.dasha_activation.antardasha}</div>
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-700">
                <div><span className="font-semibold text-gray-500">Start Date:</span><br/>{result.dasha_activation.antardasha_start || 'Unknown'}</div>
                <div><span className="font-semibold text-gray-500">End Date:</span><br/>{result.dasha_activation.antardasha_end || 'Unknown'}</div>
              </div>
            </div>
            <hr className="border-gray-100" />
            {/* Pratyantardasha */}
            <div>
              <div className="font-semibold text-gray-600">Pratyantardasha</div>
              <div className="mb-2">{result.dasha_activation.pratyantardasha}</div>
              <div className="grid grid-cols-2 gap-4 text-sm text-gray-700">
                <div><span className="font-semibold text-gray-500">Start Date:</span><br/>{result.dasha_activation.pratyantardasha_start || 'Unknown'}</div>
                <div><span className="font-semibold text-gray-500">End Date:</span><br/>{result.dasha_activation.pratyantardasha_end || 'Unknown'}</div>
              </div>
            </div>
            <hr className="border-gray-100" />
            {/* Activation Index */}
            <div>
              <div className="font-semibold text-gray-600">Activation Index</div>
              <div>{result.dasha_activation.activation_index}</div>
            </div>
          </div>
        </section>

        {/* C. Final Conclusion */}
        <section className="border-b border-gray-200 pb-4">
          <h3 className="text-lg font-bold text-blue-800 mb-3 border-b-2 border-blue-200 inline-block">C. Final Conclusion</h3>
          <div className="grid grid-cols-3 gap-4">
            <div><span className="font-semibold text-gray-600">Promise Status:</span><br/>{result.final_conclusion.promise_status}</div>
            <div><span className="font-semibold text-gray-600">Current Dasha Support:</span><br/>{result.final_conclusion.dasha_support}</div>
            <div><span className="font-semibold text-gray-600">Assessment:</span><br/>
              <span className={`font-bold ${result.final_conclusion.assessment === 'FAVORABLE' ? 'text-green-600' : result.final_conclusion.assessment === 'UNFAVORABLE' ? 'text-red-600' : 'text-yellow-600'}`}>
                {result.final_conclusion.assessment}
              </span>
            </div>
          </div>
        </section>

        {/* D. Timing Window */}
        <section className="border-b border-gray-200 pb-4">
          <h3 className="text-lg font-bold text-blue-800 mb-3 border-b-2 border-blue-200 inline-block">D. Timing Window</h3>
          <div className="grid grid-cols-2 gap-y-4 gap-x-8">
            <div><span className="font-semibold text-gray-600">Mahadasha:</span><br/>{result.timing_window.mahadasha}</div>
            <div><span className="font-semibold text-gray-600">Antardasha:</span><br/>{result.timing_window.antardasha}</div>
            <div><span className="font-semibold text-gray-600">Pratyantardasha:</span><br/>{result.timing_window.pratyantardasha}</div>
            <div><span className="font-semibold text-gray-600">Most Supportive Period:</span><br/>{result.timing_window.most_supportive_period}</div>
          </div>
        </section>

        {/* E. Supporting Factors */}
        <section className="border-b border-gray-200 pb-4">
          <h3 className="text-lg font-bold text-green-700 mb-3 border-b-2 border-green-200 inline-block">E. Supporting Factors</h3>
          {result.supporting_factors.length > 0 ? (
            <ul className="list-disc pl-5 space-y-1">
              {result.supporting_factors.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          ) : (
            <p className="text-gray-500 italic">No supporting factors found.</p>
          )}
        </section>

        {/* F. Attention Factors */}
        <section className="border-b border-gray-200 pb-4">
          <h3 className="text-lg font-bold text-red-700 mb-3 border-b-2 border-red-200 inline-block">F. Attention Factors</h3>
          {result.attention_factors.length > 0 ? (
            <ul className="list-disc pl-5 space-y-1">
              {result.attention_factors.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          ) : (
            <p className="text-gray-500 italic">No attention factors found.</p>
          )}
        </section>

        {/* G. Mandali Commentary */}
        <section>
          <h3 className="text-lg font-bold text-purple-800 mb-3 border-b-2 border-purple-200 inline-block">G. Mandali Commentary</h3>
          <p className="text-gray-500 italic bg-gray-50 p-4 rounded border border-gray-100">
            {result.mandali_commentary}
          </p>
        </section>
      </div>
    </div>
  );
};
