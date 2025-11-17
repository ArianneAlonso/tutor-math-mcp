import React from 'react';
import { Trash2, History, MessageSquare, Palette } from 'lucide-react';

export const Historial = ({ messages, drawings, onClearHistory, sidebarOpen }) => {
  return (
    <div className={`fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 ${sidebarOpen ? 'ml-64' : 'ml-14'}`}>
      
      <div className="bg-white rounded-xl w-11/12 h-5/6 max-w-5xl flex flex-col border border-slate-200 shadow-2xl">
        
        <div className="bg-white p-5 border-b border-slate-200 rounded-t-xl">
          <div className="flex items-center gap-3">
            <History className="w-6 h-6 text-sky-600" />
            <h2 className="text-xl font-semibold text-slate-800">Historial</h2>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 bg-slate-50">
          <div className="space-y-8">

            <div>
              <h3 className="text-slate-700 font-semibold mb-4 text-lg flex items-center gap-2">
                <MessageSquare className="w-5 h-5" />
                Mensajes ({messages.length})
              </h3>
              <div className="space-y-3">
                {messages.length === 0 ? (
                  <p className="text-slate-500 text-sm">No hay mensajes aún</p> 
                ) : (
                  messages.map((msg) => (
                    <div key={msg.id} className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                      <div className="flex justify-between items-start mb-2">
                        <span className={`text-xs font-semibold px-2 py-1 rounded ${
                          msg.sender === 'user' ? 'bg-sky-600 text-white' : 'bg-slate-200 text-slate-700' 
                        }`}>
                          {msg.sender === 'user' ? 'Tú' : 'Bot'}
                        </span>
                        <span className="text-xs text-slate-400">{msg.timestamp}</span> 
                      </div>
                      <p className="text-sm text-slate-600">{msg.text}</p> 
                    </div>
                  ))
                )}
              </div>
            </div>

            <div>
              <h3 className="text-slate-700 font-semibold mb-4 text-lg flex items-center gap-2">
                <Palette className="w-5 h-5" />
                Dibujos guardados ({drawings.length})
              </h3>
              <div className="grid grid-cols-3 gap-4">
                {drawings.length === 0 ? (
                  <p className="text-slate-500 text-sm col-span-3">No hay dibujos guardados</p> 
                ) : (
                  drawings.map((drawing, idx) => (
                    <div key={idx} className="bg-white p-3 rounded-lg border border-slate-200 hover:border-slate-300 transition-colors shadow-sm">
                      <img 
                        src={drawing.dataUrl} 
                        alt={`Dibujo ${idx + 1}`}
                        className="w-full h-48 object-cover rounded mb-2 bg-white"
                      />
                      <p className="text-xs text-slate-400">{drawing.timestamp}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};
