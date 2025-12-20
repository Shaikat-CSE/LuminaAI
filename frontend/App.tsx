
import React, { useState, useRef, useEffect } from 'react';
import Navbar from './components/Navbar';
import FileUpload from './components/FileUpload';
import SourceCard from './components/SourceCard';
import { Message, Role, FileData, Source } from './types';
import { queryDocuments, clearAllDocuments, deleteDocument, getHealth } from './services/apiService';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: Role.MODEL,
      text: "Hello! I'm LuminaAI, your advanced AI assistant. I can help you analyze documents, extract insights, or just answer any general questions you have. How can I assist you today?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [activeFiles, setActiveFiles] = useState<FileData[]>([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [systemStatus, setSystemStatus] = useState<'healthy' | 'error' | 'checking'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Robust API path resolution
    const envApi = (import.meta as any).env?.VITE_API_URL;
    const apiBase = String(envApi || 'http://localhost:9000/api/v1').replace(/\/$/, '');
    const healthUrl = `${apiBase}/health`;

    console.log('System initialized. API Base:', apiBase);

    const checkHealth = async () => {
      try {
        const response = await fetch(healthUrl);
        if (response.ok) {
          setSystemStatus('healthy');
        } else {
          console.warn('Backend returned non-OK health status:', response.status);
          setSystemStatus('error');
        }
      } catch (err) {
        console.error('Failed to connect to backend:', err);
        setSystemStatus('error');
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  // Log active files change for debugging
  useEffect(() => {
    console.log('Active Files Updated:', activeFiles);
  }, [activeFiles]);

  const suggestedPrompts = [
    "Summarize my files",
    "Extract key metrics",
    "Compare documents",
    "Check for inconsistencies"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = async (overrideInput?: string) => {
    const textToSend = overrideInput || input;
    if ((!textToSend.trim() && activeFiles.length === 0) || isTyping) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: Role.USER,
      text: textToSend,
      timestamp: new Date(),
      files: activeFiles.length > 0 ? [...activeFiles] : undefined
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      // Use the backend API for RAG query
      const result = await queryDocuments(textToSend);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: Role.MODEL,
        text: result.answer,
        timestamp: new Date(),
        sources: result.sources // We'll need to add this to the Message type or handle it
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: Role.MODEL,
        text: `Error: ${error.message || 'Failed to get response from backend'}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const removeFile = async (index: number) => {
    const fileToRemove = activeFiles[index];
    if (fileToRemove.id) {
      try {
        await deleteDocument(fileToRemove.id);
      } catch (error) {
        console.error("Failed to delete document from backend:", error);
      }
    }
    setActiveFiles(prev => prev.filter((_, i) => i !== index));
  };

  const clearChat = async () => {
    try {
      await clearAllDocuments();
    } catch (error) {
      console.error("Failed to clear documents from backend:", error);
    }
    setMessages([
      {
        id: Date.now().toString(),
        role: Role.MODEL,
        text: "Session cleared. Ready for a new analysis!",
        timestamp: new Date()
      }
    ]);
    setActiveFiles([]);
  };

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      <Navbar onNewChat={clearChat} onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />

      {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-[60] animate-in fade-in duration-300"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar Drawer */}
      <aside className={`
        fixed left-0 top-0 bottom-0 w-72 bg-white z-[70] shadow-2xl transition-transform duration-500 ease-in-out p-6 flex flex-col gap-8
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-main">Resources</h2>
          <button onClick={() => setSidebarOpen(false)} className="p-1 hover:bg-black/5 rounded-full">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto space-y-4">
          <div className="space-y-2">
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest px-1">Active Context</p>
            {activeFiles.length === 0 ? (
              <p className="text-sm text-gray-400 italic px-1">No files uploaded yet.</p>
            ) : (
              activeFiles.map((f, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-[#F0F0E9] rounded-xl border border-black/5 group">
                  <div className="flex items-center gap-3 overflow-hidden">
                    <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center shrink-0 shadow-sm text-[#F43E01]">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M4 4a2 2 0 012-2h4.586A1 1 0 0111 2.293l4.707 4.707a1 1 0 01.293.707V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
                      </svg>
                    </div>
                    <span className="text-sm truncate text-main font-medium">{f.name}</span>
                  </div>
                  <button onClick={() => removeFile(i)} className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <button
          onClick={clearChat}
          className="w-full py-3 rounded-2xl border-2 border-red-100 text-red-500 font-bold hover:bg-red-50 transition-colors flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Clear All Data
        </button>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 md:px-8 pt-28 pb-40 space-y-8">
        {messages.map((msg, index) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === Role.USER ? 'items-end' : 'items-start'} animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out`}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div className={`
              max-w-[88%] md:max-w-[75%] p-5 md:p-6 rounded-[2rem] shadow-sm relative group
              ${msg.role === Role.USER
                ? 'bg-[#F43E01] text-white rounded-tr-none'
                : 'bg-white text-[#332F33] rounded-tl-none border border-black/5'
              }
            `}>
              {msg.files && msg.files.length > 0 && (
                <div className="mb-4 flex flex-wrap gap-2">
                  {msg.files.map((f, i) => (
                    <div key={i} className={`text-[11px] font-bold px-3 py-1.5 rounded-full flex items-center gap-2 border ${msg.role === Role.USER ? 'bg-white/10 border-white/20' : 'bg-black/5 border-black/10'}`}>
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      {f.name}
                    </div>
                  ))}
                </div>
              )}
              <div className="whitespace-pre-wrap leading-relaxed text-[15px] md:text-[17px] tracking-wide font-medium">
                {msg.text}
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-6 pt-6 border-t border-black/5">
                  <button
                    onClick={() => {
                      const el = document.getElementById(`sources-${msg.id}`);
                      if (el) el.classList.toggle('hidden');
                      const arrow = document.getElementById(`arrow-${msg.id}`);
                      if (arrow) arrow.classList.toggle('rotate-180');
                    }}
                    className="flex items-center justify-between w-full group hover:opacity-80 transition-opacity"
                  >
                    <div className="flex items-center gap-2">
                      <svg id={`arrow-${msg.id}`} className="w-4 h-4 text-gray-400 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                      <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Supporting Evidence</p>
                    </div>
                    <span className="text-[10px] font-bold text-[#F43E01] bg-[#F43E01]/5 px-2 py-0.5 rounded-full">
                      {msg.sources.length} Sources
                    </span>
                  </button>
                  <div id={`sources-${msg.id}`} className="hidden mt-4 space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pb-2">
                      {msg.sources.slice(0, 4).map((source, i) => (
                        <SourceCard key={i} source={source} />
                      ))}
                    </div>
                  </div>
                </div>
              )}

              <div className={`text-[11px] mt-3 font-semibold opacity-40 uppercase tracking-widest ${msg.role === Role.USER ? 'text-white' : 'text-[#332F33]'}`}>
                {msg.timestamp instanceof Date ? msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Just now'}
              </div>
            </div>

            {msg.role === Role.MODEL && index === messages.length - 1 && !isTyping && (
              <div className="flex gap-2 mt-4 px-2">
                <button className="p-2 rounded-full border border-black/5 hover:bg-white transition-colors text-gray-400 hover:text-main">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" /></svg>
                </button>
                <button className="p-2 rounded-full border border-black/5 hover:bg-white transition-colors text-gray-400 hover:text-green-500">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" /></svg>
                </button>
              </div>
            )}
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white p-5 rounded-[2rem] rounded-tl-none border border-black/5 shadow-sm">
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 bg-[#F43E01]/30 rounded-full animate-bounce"></div>
                <div className="w-2.5 h-2.5 bg-[#F43E01]/50 rounded-full animate-bounce [animation-delay:-.3s]"></div>
                <div className="w-2.5 h-2.5 bg-[#F43E01] rounded-full animate-bounce [animation-delay:-.5s]"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      {/* Suggestion Bar & Input */}
      <div className="fixed bottom-0 left-0 right-0 z-40 p-4 bg-gradient-to-t from-[#F0F0E9] via-[#F0F0E9]/95 to-transparent">
        <div className="max-w-4xl mx-auto w-full space-y-4">

          {/* Suggested Prompts */}
          {messages.length < 3 && !isTyping && (
            <div className="flex gap-2 overflow-x-auto pb-2 px-1 no-scrollbar">
              {suggestedPrompts.map((p, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(p)}
                  className="shrink-0 px-4 py-2 rounded-full bg-white border border-black/5 text-sm font-bold text-main hover:border-[#F43E01] hover:text-[#F43E01] transition-all shadow-sm"
                >
                  {p}
                </button>
              ))}
            </div>
          )}

          {/* Active File Pills (Above Input) */}
          {activeFiles.length > 0 && (
            <div className="flex flex-wrap gap-2 animate-in slide-in-from-bottom-2">
              {activeFiles.map((file, idx) => (
                <div key={idx} className="bg-[#F43E01] text-white px-3 py-1 rounded-full text-[11px] font-bold flex items-center gap-2 shadow-md">
                  <span className="truncate max-w-[150px]">{file.name}</span>
                  <button onClick={() => removeFile(idx)} className="hover:scale-125 transition-transform">
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" /></svg>
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Enhanced Input Box */}
          <div className="bg-white rounded-[2.5rem] shadow-2xl border border-black/5 p-3 flex items-end gap-3 transition-all focus-within:ring-4 focus-within:ring-[#F43E01]/10">
            <FileUpload
              onFilesSelected={setActiveFiles}
              selectedFiles={activeFiles}
            />

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Message LuminaAI..."
              className="flex-1 bg-transparent border-none focus:ring-0 resize-none py-3 text-[16px] text-[#332F33] max-h-40 min-h-[48px] font-medium placeholder:text-gray-400"
              rows={1}
            />

            <button
              onClick={() => handleSend()}
              disabled={(!input.trim() && activeFiles.length === 0) || isTyping}
              className={`
                w-12 h-12 rounded-full transition-all duration-300 flex items-center justify-center shrink-0
                ${(!input.trim() && activeFiles.length === 0) || isTyping
                  ? 'bg-gray-100 text-gray-300'
                  : 'primary-btn shadow-lg hover:scale-105 active:scale-95'
                }
              `}
            >
              <svg className="w-6 h-6 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>

          <div className="flex justify-between items-center px-4">
            <span className="text-[10px] text-gray-400 font-bold uppercase tracking-[0.2em] hidden md:block">End-to-end Encrypted Analysis</span>
            <div className="flex items-center gap-6">
              <span className="text-[10px] text-gray-400 font-bold uppercase tracking-[0.2em]">Created by Shaikat S.</span>
              <div className="flex items-center gap-4">
                <a
                  href="https://linkedin.com/in/shaikatsk"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-[#0077B5] transition-colors"
                  title="LinkedIn"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" />
                  </svg>
                </a>
                <a
                  href="https://github.com/shaikat-cse"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-black transition-colors"
                  title="GitHub"
                >
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;
