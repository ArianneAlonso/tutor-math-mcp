export const VerChat = ({ chat, onClose }) => (
  <div
    className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50"
    onClick={onClose}
  >
    <div
      className="bg-white w-4/5 max-w-3xl h-4/5 p-6 rounded-xl overflow-y-auto"
      onClick={(e) => e.stopPropagation()}
    >
      <h2 className="text-xl font-bold mb-4">Chat guardado</h2>

      {chat.contenido.map((msg) => (
        <div key={msg.id} className="mb-4">
          <p className="text-xs text-slate-400">{msg.timestamp}</p>
          <div
            className={`p-3 rounded-lg mt-1 ${
              msg.sender === "user"
                ? "bg-sky-100 text-sky-900"
                : "bg-slate-200 text-slate-800"
            }`}
          >
            {msg.text}
          </div>
        </div>
      ))}
    </div>
  </div>
);
