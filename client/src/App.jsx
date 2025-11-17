import React, { useState, useEffect } from 'react';
import { Chat } from './components/chat';
import { Historial } from './components/historial';
import { Pizarra } from './components/pizarra';
import { Sidebar } from './components/sidebar';
import { VerDibujo } from './components/chatPreview';
import LoginRegister from './components/loginregister';

export const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showPizarra, setShowPizarra] = useState(false);
  const [showHistorial, setShowHistorial] = useState(false);
  const [messages, setMessages] = useState([]);
  const [drawings, setDrawings] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [inputMessage, setInputMessage] = useState("");
  const [pizarraWidth, setPizarraWidth] = useState(50);
  const [isResizing, setIsResizing] = useState(false);
  const [chatsMensajes, setChatsMensajes] = useState([]);
  const [chatsDibujos, setChatsDibujos] = useState([]);
  const [selectedChat, setSelectedChat] = useState(null);
  const [selectedDibujo, setSelectedDibujo] = useState(null);


  useEffect(() => {
    const token = localStorage.getItem('user_token');
    if (token) fetchUserData(token);
  }, []);

  const guardarChatDeMensajes = () => {
    if (messages.length === 0) return;

    const nuevoChat = {
      id: Date.now(),
      contenido: [...messages],
      timestamp: new Date().toLocaleTimeString(),
    };

    setChatsMensajes(prev => [...prev, nuevoChat]);
  };

  const fetchUserData = async (token) => {
    try {
      const response = await fetch('http://localhost:3000/users/me', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error();
      const userData = await response.json();
      setCurrentUser(userData);
      setIsAuthenticated(true);
      fetchConversations(token);
    } catch {
      localStorage.removeItem('user_token');
      setIsAuthenticated(false);
      setCurrentUser(null);
    }
  };

  const fetchConversations = async (token) => {
    try {
      const response = await fetch('http://localhost:3000/conversations', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error();
      const data = await response.json();
      setConversations(data);
    } catch { }
  };

  const handleNewChat = () => {
    guardarChatDeMensajes();
    setMessages([]);
    setShowPizarra(false);
    setCurrentConversationId(null);
  };

  const handleSelectConversation = (id) => {
    setCurrentConversationId(id);
    setMessages([
      { id: 1, sender: 'bot', text: `Cargando mensajes del chat ${id}...`, timestamp: new Date().toLocaleTimeString() }
    ]);
  };

  const handleClearHistory = () => {
    setMessages([]);
    setDrawings([]);
    setShowHistorial(false);
  };

  const handleLoginSuccess = (token) => {
    localStorage.setItem('user_token', token);
    fetchUserData(token);
  };

  const handleLogout = () => {
    localStorage.removeItem('user_token');
    setIsAuthenticated(false);
    setCurrentUser(null);
    setMessages([]);
    setDrawings([]);
    setConversations([]);
    setCurrentConversationId(null);
    setShowPizarra(false);
    setShowHistorial(false);
    setSidebarOpen(false);
  };

  const handleSendMessage = async (msg) => {
    if (!msg.trim()) return;

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text: msg,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");

    const extraerExpresion = (text) => {
      const expr = text.replace(/[^0-9+\-*/().^xX= ]/g, '');
      const contiene = /[+\-*/=]/.test(expr);
      return contiene ? expr.trim() : null;
    };

    const expresion = extraerExpresion(msg);

    if (!expresion) {
      const botMessage = {
        id: Date.now() + 1,
        sender: "ai",
        text: "Hola, puedo ayudarte a resolver operaciones o ecuaciones. Escríbeme una expresión matemática.",
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, botMessage]);
      return;
    }

    let tool = "realizar_operacion";
    if (/x\^2|x²/.test(expresion)) tool = "resolver_ecuacion_cuadratica";
    else if (/x/.test(expresion) && /=/.test(expresion)) tool = "resolver_ecuacion_lineal";

    const payload = {
      jsonrpc: "2.0",
      id: crypto.randomUUID(),
      method: "tools/call",
      params: {
        name: tool,
        arguments:
          tool === "realizar_operacion"
            ? { expresion }
            : tool === "resolver_ecuacion_lineal"
              ? { m: 2, b: 3 }
              : { a: 1, b: 2, c: 1 }
      }
    };

    try {
      const response = await fetch("http://localhost:3000/mcp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      const aiText =
        data?.result?.content?.[0]?.text ??
        data?.error?.message ??
        "No pude procesar la expresión.";

      const botMessage = {
        id: Date.now() + 1,
        sender: "ai",
        text: aiText,
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, botMessage]);

    } catch {
      const botMessage = {
        id: Date.now() + 2,
        sender: "ai",
        text: "Error al contactar el servidor MCP.",
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, botMessage]);
    }
  };

  const handleAnalyzeAndSaveDrawing = (drawingData) => {
    const newDrawing = {
      id: Date.now(),
      image: drawingData,
      timestamp: new Date().toLocaleTimeString()
    };

    setChatsDibujos(prev => [...prev, newDrawing]);
  };


  const startResize = () => {
    setIsResizing(true);
  };

  const doResize = (e) => {
    if (!isResizing) return;


    const newWidth = ((window.innerWidth - e.clientX) / window.innerWidth) * 100;

    setPizarraWidth(Math.min(80, Math.max(20, newWidth)));
  };

  const stopResize = () => {
    setIsResizing(false);
  };

  useEffect(() => {
    window.addEventListener("mousemove", doResize);
    window.addEventListener("mouseup", stopResize);
    return () => {
      window.removeEventListener("mousemove", doResize);
      window.removeEventListener("mouseup", stopResize);
    };
  }, [isResizing]);

  const toggleHistorial = () => setShowHistorial(prev => !prev);

  return (
    <div className="w-full h-screen bg-slate-100 overflow-hidden">
      {!isAuthenticated ? (
        <LoginRegister onLoginSuccess={handleLoginSuccess} />
      ) : (
        <>
          <Sidebar
            isOpen={sidebarOpen}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
            onNewChat={handleNewChat}
            onShowPizarra={() => setShowPizarra(!showPizarra)}
            onShowHistorial={toggleHistorial}
            showPizarra={showPizarra}
            conversations={conversations}
            chatsMensajes={chatsMensajes}     
            onOpenChat={(chat) => {           
              setMessages(chat.contenido);
              setShowHistorial(false);
            }}
            onSelectConversation={handleSelectConversation}
            onLogout={handleLogout}
            currentUser={currentUser}
          />

          <div className={`h-full transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-14'} flex`}>

            <div
              style={{ width: showPizarra ? `${100 - pizarraWidth}%` : "100%" }}
              className="border-r border-slate-200"
            >
              <Chat
                messages={messages}
                onSendMessage={handleSendMessage}
                inputMessage={inputMessage}
                setInputMessage={setInputMessage}
                sidebarOpen={sidebarOpen}
                showPizarra={showPizarra}
              />
            </div>

            {showPizarra && (
              <div
                onMouseDown={startResize}
                className="w-2 cursor-ew-resize bg-slate-300 hover:bg-slate-400"
              />
            )}

            {showPizarra && (
              <div style={{ width: `${pizarraWidth}%` }} className="h-full">
                <Pizarra onSave={handleAnalyzeAndSaveDrawing} />
              </div>
            )}
          </div>

          {showHistorial && (
            <Historial
              chatsMensajes={chatsMensajes}
              chatsDibujos={chatsDibujos}
              sidebarOpen={sidebarOpen}
              onClose={toggleHistorial}
              onOpenChat={(chat) => {
                setMessages(chat.contenido);   
                setShowHistorial(false);       
              }}
              onOpenDibujo={(dibujo) => setSelectedDibujo(dibujo)}
            />
          )}

          {selectedDibujo && (
            <VerDibujo dibujo={selectedDibujo} onClose={() => setSelectedDibujo(null)} />
          )}
        </>
      )}
    </div>
  );
};