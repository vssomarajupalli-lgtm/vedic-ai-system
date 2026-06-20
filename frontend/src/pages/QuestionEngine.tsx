import { useState, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Send, User, Bot, Loader2 } from 'lucide-react';
import { useChartStore } from '../store/useChartStore';
import { apiService } from '../api/backend';

interface ChatMessage {
  id: string;
  role: 'user' | 'bot';
  content: string;
  yogas?: string[];
}

export default function QuestionEngine() {
  const { rawOutputs } = useChartStore();
  const location = useLocation();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (!initialized && location.state) {
      const { initialQuestionId, initialQuestionText } = location.state;
      if (initialQuestionId || initialQuestionText) {
        setInitialized(true);
        handleSendPredefined(initialQuestionText || "Astrological Query", initialQuestionId);
      }
    }
  }, [location.state, initialized]);

  // Guard clause
  if (!rawOutputs) {
    return <Navigate to="/upload" replace />;
  }

  const handleSendPredefined = async (text: string, id: string | null) => {
    if (loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text
    };

    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await apiService.askQuestion(text, id, rawOutputs);
      
      const botMessage: ChatMessage = {
        id: response.question_id,
        role: 'bot',
        content: response.answer_text,
        yogas: response.referenced_yogas
      };
      
      setMessages(prev => [...prev, botMessage]);
    } catch (err: any) {
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'bot',
        content: `Error: ${err.response?.data?.detail || err.message}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const text = input.trim();
    setInput('');
    await handleSendPredefined(text, null);
  };

  return (
    <div className="max-w-4xl mx-auto h-[80vh] flex flex-col bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
      
      {/* Header */}
      <div className="bg-indigo-600 text-white p-4">
        <h2 className="text-lg font-bold flex items-center">
          <Bot className="w-5 h-5 mr-2" />
          Vedic-AI Interpreter
        </h2>
        <p className="text-indigo-100 text-sm">Ask natural language questions grounded in your calculated chart.</p>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50">
        {messages.length === 0 && (
          <div className="text-center text-slate-500 mt-10">
            <p>No questions asked yet. Try asking about career, wealth, or current dashas!</p>
          </div>
        )}
        
        {messages.map(msg => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              
              <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-indigo-100 ml-3' : 'bg-white border border-slate-200 mr-3'}`}>
                {msg.role === 'user' ? <User className="w-4 h-4 text-indigo-600" /> : <Bot className="w-4 h-4 text-slate-600" />}
              </div>
              
              <div className={`px-4 py-3 rounded-2xl ${msg.role === 'user' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none shadow-sm'}`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
                
                {msg.yogas && msg.yogas.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-slate-100 flex flex-wrap gap-2">
                    {msg.yogas.map(yoga => (
                      <span key={yoga} className="text-xs font-semibold px-2 py-1 bg-indigo-50 text-indigo-700 rounded border border-indigo-100">
                        {yoga}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 px-4 py-3 rounded-2xl rounded-tl-none shadow-sm flex items-center text-slate-500">
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Synthesizing...
            </div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <div className="p-4 bg-white border-t border-slate-200">
        <form onSubmit={handleSend} className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={loading}
            className="flex-1 px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-slate-50 disabled:text-slate-500 outline-none transition-shadow"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="inline-flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-indigo-300 transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
