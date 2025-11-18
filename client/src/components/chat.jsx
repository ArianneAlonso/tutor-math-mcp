import { useRef, useEffect } from "react";
import { Plus, MessageSquare, Send } from "lucide-react";

export const Chat = ({
  messages,
  onSendMessage,
  inputMessage,
  setInputMessage,
  sidebarOpen,
  showPizarra,
  isBotThinking
}) => {

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = () => {
    if (inputMessage.trim() && !isBotThinking) {
      onSendMessage(inputMessage);
      setInputMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-100">

      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center px-4">
          <div className="text-sky-600 mb-4">
            <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" />
            </svg>
          </div>
          <h1 className="text-3xl font-light text-slate-700 mb-2">Bienvenido a tu tutor de matemáticas</h1>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-2xl px-4 py-3 rounded-lg ${
                  msg.sender === 'user'
                    ? 'bg-sky-600 text-white'
                    : 'bg-white text-slate-700 shadow-sm border border-slate-100'
                }`}
              >
                <div
                  className="text-sm whitespace-pre-wrap"
                  dangerouslySetInnerHTML={{
                    __html: msg.text.replace(
                      /```json\n([\s\S]*?)\n```/g,
                      '<pre class="bg-slate-100 p-2 rounded-md text-xs text-slate-800">$1</pre>'
                    )
                  }}
                />
                <span className={`text-xs mt-2 block ${
                  msg.sender === 'user' ? 'text-sky-100' : 'text-slate-400'
                }`}>
                  {msg.timestamp}
                </span>
              </div>
            </div>
          ))}
          {isBotThinking && (
            <div className="flex justify-start">
              <div className="max-w-2xl px-4 py-3 rounded-lg bg-white text-slate-700 shadow-sm border border-slate-100">
                <div className="flex items-center gap-2 text-sm">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                  <span className="text-slate-500">El tutor está pensando...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      )}

      <div className="p-4 bg-slate-100">
        <div className="max-w-3xl mx-auto">
          <div className="relative bg-blue-100 rounded-xl border border-slate-200 shadow-sm h-[70px]">

            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                showPizarra
                  ? 'Escribe variables JSON aquí (ej: {"x":5})'
                  : '¿Cómo puedo ayudarle hoy?'
              }
              rows="2"
              className="w-full px-4 py-3 bg-transparent text-slate-800 focus:outline-none resize-none placeholder-slate-400"
              disabled={isBotThinking}
            />

            <div className="flex items-center justify-between px-4 py-2">
              <div className="flex items-center gap-2 text-xs text-slate-400">
              </div>

              <button
                onClick={handleSubmit}
                className="p-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-[-100px]"
                disabled={!inputMessage.trim() || isBotThinking}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};