import React, { useEffect, useRef, useState } from "react";
import { Toaster, toast } from "sonner";

const SWATCHES = [
  "#000000", "#ee3333", "#e64980", "#be4bdb", "#893200",
  "#228be6", "#3333ee", "#40c057", "#00aa00", "#fab005", "#fd7e14",
];

export const Pizarra = ({ onSave }) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [brushColor, setBrushColor] = useState("#000000");
  const [lineWidth, setLineWidth] = useState(3);

  const [latexExpressions, setLatexExpressions] = useState([]);
  const [positions, setPositions] = useState([]);
  useEffect(() => {}, [latexExpressions]);
  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    setLatexExpressions([]);
    setPositions([]);
  };
  const startDrawing = (e) => {
  setIsDrawing(true);
  const canvas = canvasRef.current;
  const ctx = canvas.getContext("2d");
  const rect = canvas.getBoundingClientRect();

  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;

  const x = (e.clientX - rect.left) * scaleX;
  const y = (e.clientY - rect.top) * scaleY;

  ctx.beginPath();
  ctx.moveTo(x, y);
  };

 const draw = (e) => {
  if (!isDrawing) return;

  const canvas = canvasRef.current;
  const ctx = canvas.getContext("2d");
  const rect = canvas.getBoundingClientRect();

  const scaleX = canvas.width / rect.width;
  const scaleY = canvas.height / rect.height;

  const x = (e.clientX - rect.left) * scaleX;
  const y = (e.clientY - rect.top) * scaleY;

  ctx.lineTo(x, y);
  ctx.strokeStyle = brushColor;
  ctx.lineWidth = lineWidth;
  ctx.lineCap = "round";
  ctx.stroke(); 
  };

  const stopDrawing = () => setIsDrawing(false);
  const processDrawing = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    console.log("CANVAS ELEMENT:", canvas);

    const dataUrl = canvas.toDataURL("image/png");
     console.log("BASE64:", dataUrl);
     
    if (typeof onSave === "function") {
      await onSave(dataUrl);
      toast.success("Dibujo enviado correctamente");
    } else {
      toast.error("Error: onSave no fue pasado desde App.jsx");
    }
  };
  const DraggableLatex = ({ latex, index }) => {
    const [pos, setPos] = useState(positions[index] || { x: 200, y: 200 });
    const offset = useRef({ x: 0, y: 0 });
    const dragging = useRef(false);

    const down = (e) => {
      dragging.current = true;
      offset.current = {
        x: e.clientX - pos.x,
        y: e.clientY - pos.y,
      };
    };

    const move = (e) => {
      if (!dragging.current) return;
      const newPos = {
        x: e.clientX - offset.current.x,
        y: e.clientY - offset.current.y,
      };
      setPos(newPos);

      const newPositions = [...positions];
      newPositions[index] = newPos;
      setPositions(newPositions);
    };

    const up = () => {
      dragging.current = false;
    };

    useEffect(() => {
      window.addEventListener("mousemove", move);
      window.addEventListener("mouseup", up);

      return () => {
        window.removeEventListener("mousemove", move);
        window.removeEventListener("mouseup", up);
      };
    }, [pos]);

    return (
      <div
        className="absolute text-slate-800 cursor-move"
        style={{ left: pos.x, top: pos.y }}
        onMouseDown={down}
      >
        <div className="latex-content">{latex}</div>
      </div>
    );
  };
  return (
    <div className="relative w-full h-full">
      <Toaster richColors />
      <div className="absolute top-0 left-0 right-0 bg-white p-3 flex items-center justify-between z-10 border-b border-slate-200 shadow-sm">
        <div className="flex gap-2">
          {SWATCHES.map((c) => (
            <button
              key={c}
              onClick={() => setBrushColor(c)}
              className={`w-8 h-8 rounded-full border-2 ${
                brushColor === c ? "border-sky-600 ring-2 ring-sky-300" : "border-slate-300"
              }`}
              style={{ backgroundColor: c }}
            />
          ))}
        </div>
        <input
          type="range"
          min="1"
          max="15"
          value={lineWidth}
          onChange={(e) => setLineWidth(e.target.value)}
          className="accent-sky-600"
        />
        <button
          onClick={clearCanvas}
          className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
        >
          Reset
        </button>
        <button
          onClick={processDrawing}
          className="bg-sky-600 text-white px-4 py-2 rounded-lg hover:bg-sky-700"
        >
          Procesar
        </button>
      </div>
      <canvas
        ref={canvasRef}
        width={1600}
        height={900}
        className="absolute top-0 left-0 w-full h-full bg-white"
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
      />
      {latexExpressions.map((latex, i) => (
        <DraggableLatex key={i} latex={latex} index={i} />
      ))}
    </div>
  );
};