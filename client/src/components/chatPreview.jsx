export const VerDibujo = ({ dibujo, onClose }) => (
  <div
    className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50"
    onClick={onClose}
  >
    <div
      className="bg-white p-4 rounded-xl shadow-xl max-w-3xl"
      onClick={(e) => e.stopPropagation()}
    >
      <img src={dibujo.image} className="rounded max-h-[75vh]" />
      <p className="text-center text-xs text-slate-500 mt-2">{dibujo.timestamp}</p>
    </div>
  </div>
);
