import React, { useState } from 'react';
import { api } from '../services/api';
import { Bot, Send, X, Sparkles, Loader2, BookOpen, User } from 'lucide-react';

export const AIChatCopilot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'ai',
      text: 'Hello! I am RouteAI Copilot. Ask me about route optimization, fleet status, ETA predictions, or logistics SOPs.',
      rag_sources: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await api.post('/ai/chat', {
        prompt: userMsg,
        include_rag: true
      });
      setMessages(prev => [
        ...prev,
        {
          sender: 'ai',
          text: res.data.reply,
          rag_sources: res.data.rag_sources || []
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'ai',
          text: 'Apologies, I encountered an issue processing your query. Please try again.',
          rag_sources: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 p-4 rounded-full bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-600 text-white shadow-2xl shadow-indigo-600/50 hover:scale-105 transition-all duration-300 group"
        title="Open RouteAI Copilot Assistant"
      >
        <Bot className="w-7 h-7 animate-pulse" />
      </button>

      {/* Floating Chat Window Drawer */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] h-[520px] glass-panel rounded-3xl border border-indigo-500/30 shadow-2xl flex flex-col overflow-hidden animate-fadeIn">
          {/* Header */}
          <div className="p-4 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white shadow-md">
                <Sparkles className="w-4 h-4 text-amber-300" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-100 font-heading">RouteAI Copilot</h4>
                <p className="text-[10px] text-indigo-400 font-medium">Google Gemini LLM + RAG Active</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3.5 text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`p-3.5 rounded-2xl max-w-[85%] leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-indigo-600 text-white font-medium rounded-br-none shadow-md shadow-indigo-600/20'
                      : 'bg-slate-900/80 text-slate-200 border border-slate-800 rounded-bl-none shadow-sm'
                  }`}
                >
                  {m.text}
                </div>
                {m.rag_sources && m.rag_sources.length > 0 && (
                  <div className="mt-1 flex items-center space-x-1 text-[10px] text-indigo-400">
                    <BookOpen className="w-3 h-3" />
                    <span>Sources: {m.rag_sources.join(', ')}</span>
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex items-center space-x-2 text-slate-400 text-xs p-2">
                <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                <span>RouteAI Copilot is reasoning...</span>
              </div>
            )}
          </div>

          {/* Input Footer Form */}
          <form onSubmit={handleSend} className="p-3 border-t border-slate-800 bg-slate-950/60 flex items-center space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask RouteAI Assistant..."
              className="flex-1 bg-slate-900/80 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-slate-100 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white disabled:opacity-50 transition-opacity shadow-md"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
};
