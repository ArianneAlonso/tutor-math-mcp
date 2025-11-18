import React from 'react';
import { Plus, Menu, ChevronLeft, MessageSquare, Palette, History, LogOut } from 'lucide-react';
import { TbMathSymbols } from "react-icons/tb";

export const Sidebar = ({
  isOpen,
  onToggle,
  onNewChat,
  onShowPizarra,
  onShowHistorial,
  showPizarra,
  conversations,
  onSelectConversation,
  onLogout,
  currentUser,
  chatsMensajes,
  onOpenChat
}) => {

  const userInitial = currentUser?.name
    ? currentUser.name[0].toUpperCase()
    : (currentUser?.email ? currentUser.email[0].toUpperCase() : 'U');

  const displayName = currentUser?.name || currentUser?.email || "Usuario";

  return (
    <>
      {!isOpen && (
        <div className="fixed top-0 left-0 h-full w-14 bg-white border-r border-slate-200 flex flex-col items-center py-4 gap-3 z-50 shadow-sm">

          <button
            onClick={onToggle}
            className="p-2.5 hover:bg-slate-100 rounded-lg text-slate-600 transition"
          >
            <Menu className="w-5 h-5" />
          </button>

          <button
            onClick={onNewChat}
            title="Nuevo Chat"
            className="p-2.5 hover:bg-slate-100 rounded-lg text-slate-600 transition"
          >
            <Plus className="w-5 h-5" />
          </button>

          <button
            onClick={onShowPizarra}
            title="Pizarra"
            className={`p-2.5 rounded-lg transition ${showPizarra ? "bg-slate-200 text-slate-800" : "text-slate-600 hover:bg-slate-100"}`}
          >
            <Palette className="w-5 h-5" />
          </button>

          <button
            onClick={onShowHistorial}
            title="Historial"
            className="p-2.5 hover:bg-slate-100 rounded-lg text-slate-600 transition"
          >
            <History className="w-5 h-5" />
          </button>

          <div className="flex-1"></div>

          <button
            onClick={onLogout}
            title="Cerrar sesión"
            className="p-2.5 hover:bg-red-100 rounded-lg text-slate-500 hover:text-red-500 transition-colors mb-2"
          >
            <LogOut className="w-5 h-5" />
          </button>

          <div
            className="w-8 h-8 bg-sky-600 rounded-full flex items-center justify-center text-white text-sm font-medium"
            title={displayName}
          >
            {userInitial}
          </div>
        </div>
      )}

      {isOpen && (
        <div className="fixed top-0 left-0 h-full w-64 bg-white border-r border-slate-200 flex flex-col z-50">

          <div className="flex items-center justify-between p-4 border-b border-slate-200">
            <span className="text-slate-700 font-semibold flex items-center gap-2">
              <TbMathSymbols />
              Math-Tutor
            </span>

            <button
              onClick={onToggle}
              className="p-2 hover:bg-slate-100 rounded-lg text-slate-600 transition"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
          </div>

          <div className="p-3 flex gap-2">
            <button
              onClick={onNewChat}
              className="flex items-center gap-2 px-3 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-700 w-full transition"
            >
              <Plus className="w-4 h-4" /> Nuevo Chat
            </button>
          </div>

          <nav className="px-2 space-y-1">

            <button
              onClick={onShowPizarra}
              className={`flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm transition ${showPizarra ? "bg-slate-200 text-slate-900" : "hover:bg-slate-100 text-slate-700"
                }`}
            >
              <Palette className="w-4 h-4" /> Pizarra
            </button>

            <button
              onClick={onShowHistorial}
              className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-sm hover:bg-slate-100 text-slate-700 transition"
            >
              <History className="w-4 h-4" /> Historial
            </button>

          </nav>

          <div className="p-3 border-t border-slate-200 mt-auto">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <div className="w-8 h-8 bg-sky-600 rounded-full flex items-center justify-center text-white font-medium">
                {userInitial}
              </div>

              <div className="flex-1 overflow-hidden">
                <div className="text-slate-800 text-sm font-medium truncate">{displayName}</div>
                {currentUser?.email && <div className="text-slate-500 text-xs truncate">{currentUser.email}</div>}
              </div>

              <button
                onClick={onLogout}
                title="Cerrar sesión"
                className="p-2 hover:bg-red-100 rounded-lg text-slate-500 hover:text-red-500 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
