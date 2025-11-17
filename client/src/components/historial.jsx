import React, { useState } from 'react';
import { History, MessageSquare, Palette } from 'lucide-react';

export const Historial = ({
  chatsMensajes,
  chatsDibujos,
  sidebarOpen,
  onClose,
  onOpenChat,
  onOpenDibujo,
}) => {
  const [tab, setTab] = useState("mensajes");

  return (
    <div
      className={`fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50 ${sidebarOpen ? 'ml-64' : 'ml-14'}`}
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl w-11/12 h-5/6 max-w-5xl flex flex-col border border-slate-200 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="bg-white p-5 border-b">
          <div className="flex items-center gap-3">
            <History className="w-6 h-6 text-sky-600" />
            <h2 className="text-xl font-semibold text-slate-800">Historial</h2>
          </div>
        </div>

        <div className="flex gap-6 px-6 py-3 border-b bg-slate-50">
          <button
            className={`pb-2 ${
              tab === "mensajes"
                ? "text-sky-600 border-b-2 border-sky-600 font-semibold"
                : "text-slate-500"
            }`}
            onClick={() => setTab("mensajes")}
          >
            Chats ({chatsMensajes.length})
          </button>

          <button
            className={`pb-2 ${
              tab === "dibujos"
                ? "text-sky-600 border-b-2 border-sky-600 font-semibold"
                : "text-slate-500"
            }`}
            onClick={() => setTab("dibujos")}
          >
            Dibujos ({chatsDibujos.length})
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 bg-slate-50">
          {tab === "mensajes" && (
            <div className="space-y-4">
              {chatsMensajes.length === 0 ? (
                <p className="text-slate-500">No hay chats guardados</p>
              ) : (
                chatsMensajes.map((chat) => (
                  <div
                    key={chat.id}
                    className="bg-white p-4 rounded-lg border shadow-sm cursor-pointer hover:bg-slate-100"
                    onClick={() => onOpenChat(chat)}
                  >
                    <div className="flex justify-between">
                      <h3 className="font-medium">{chat.contenido.length} mensajes</h3>
                      <span className="text-xs text-slate-400">{chat.timestamp}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {tab === "dibujos" && (
            <div className="grid grid-cols-3 gap-4">
              {chatsDibujos.length === 0 ? (
                <p className="text-slate-500 col-span-3">No hay dibujos guardados</p>
              ) : (
                chatsDibujos.map((dibujo) => (
                  <div
                    key={dibujo.id}
                    className="bg-white p-3 border rounded-lg shadow-sm cursor-pointer hover:bg-slate-100"
                    onClick={() => onOpenDibujo(dibujo)}
                  >
                    <img src={dibujo.image} className="rounded h-40 w-full object-cover" />
                    <p className="text-xs text-slate-400 mt-1">{dibujo.timestamp}</p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
