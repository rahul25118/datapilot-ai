"use client";

import React, { useState } from 'react';

interface ChatInterfaceProps {
  datasetId: string;
}

export function ChatInterface({ datasetId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'system', text: string, details?: string[] }>>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [lang, setLang] = useState<'en' | 'hi'>('en');

  async function handleSend() {
    if (!input.trim()) return;
    const currentQuery = input;
    setMessages(prev => [...prev, { role: 'user', text: currentQuery }]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem("datapilot_token");
      const res = await fetch("http://localhost:8000/api/query/chat", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          dataset_id: datasetId,
          prompt: currentQuery,
          language: lang
        })
      });
      
      const data = await res.json();
      setMessages(prev => [...prev, { 
        role: 'system', 
        text: data.response_text,
        details: data.strategic_recommendations 
      }]);
    } catch (err) {
      console.error("Critical conversational data pipeline error:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full justify-between p-4 h-[550px]">
      <div className="flex justify-between items-center border-b border-slate-800 pb-2 mb-2">
        <span className="text-xs uppercase font-semibold text-slate-400 tracking-wider">AI Business Analyst</span>
        <select 
          value={lang} 
          onChange={(e: any) => setLang(e.target.value)}
          className="bg-slate-800 text-xs text-white border border-slate-700 rounded p-1"
        >
          <option value="en">English (EN)</option>
          <option value="hi">Hindi (HI)</option>
        </select>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 my-2 pr-2">
        {messages.map((m, idx) => (
          <div key={idx} className={`p-3 rounded-lg max-w-[85%] text-sm ${m.role === 'user' ? 'bg-indigo-600 text-white ml-auto' : 'bg-slate-800 text-slate-200'}`}>
            <p className="font-normal leading-relaxed">{m.text}</p>
            {m.details && m.details.length > 0 && (
              <div className="mt-2 pt-2 border-t border-slate-700 space-y-1">
                <p className="text-xs text-indigo-400 font-bold">Actionable Next Steps:</p>
                {m.details.map((detail, dIdx) => (
                  <p key={dIdx} className="text-xs text-slate-300">• {detail}</p>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-slate-500 text-xs animate-pulse">Running data analysis algorithms...</div>}
      </div>

      <div className="flex gap-2 pt-2 border-t border-slate-800">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about trend, profitability, or churn..."
          className="bg-slate-950 border border-slate-800 rounded-md p-2 flex-1 text-sm focus:outline-none focus:border-indigo-500 text-white"
        />
        <button onClick={handleSend} className="bg-indigo-600 hover:bg-indigo-500 text-white text-sm px-4 rounded-md transition-colors">Execute</button>
      </div>
    </div>
  );
}
