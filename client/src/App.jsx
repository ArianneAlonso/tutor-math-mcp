import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'sonner';

import { Chat } from './components/chat';
import { Historial } from './components/historial';
import { Pizarra } from './components/pizarra';
import { Sidebar } from './components/sidebar';
import LoginRegister from './components/loginregister';

const API_URL = 'http://localhost:3000';

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
  const [isBotThinking, setIsBotThinking] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('user_token');
    if (token) {
        fetchUserData(token);
    } else {
        setMessages([{
            id: 'welcome-guest',
            sender: 'ai',
            text: '¡Hola! Inicia sesión o regístrate para comenzar.',
            timestamp: new Date().toLocaleTimeString()
        }]);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && currentUser && messages.length <= 1) {
        setMessages([{
            id: 'welcome-user',
            sender: 'ai',
            text: `¡Hola ${currentUser.name}! Soy tu tutor de matemáticas. ¿En qué te puedo ayudar hoy? 🚀`,
            timestamp: new Date().toLocaleTimeString()
        }]);
    }
  }, [isAuthenticated, currentUser]);

  const fetchUserData = async (token) => {
    try {
      const response = await fetch(`${API_URL}/users/me`, {
        method: 'GET',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      if (!response.ok) throw new Error("Sesión inválida");
      const userData = await response.json();
      setCurrentUser(userData);
      setIsAuthenticated(true);
      fetchConversations(token);
    } catch(error) {
      localStorage.removeItem('user_token');
      setIsAuthenticated(false);
      setCurrentUser(null);
      toast.error(error.message || "Tu sesión expiró. Inicia sesión de nuevo.");
      setMessages([{
        id: 'session-expired',
        sender: 'ai',
        text: 'Tu sesión expiró. Por favor, inicia sesión de nuevo.',
        timestamp: new Date().toLocaleTimeString()
      }]);
    }
  };

  const fetchConversations = async (token) => {
    try {
      const response = await fetch(`${API_URL}/conversations`, {
        method: 'GET',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al cargar conversaciones");
      }
      
      const data = await response.json();
      setConversations(data);
    } catch (error) {
      console.error("Error fetching conversations:", error);
      toast.error(error.message || "No se pudieron cargar las conversaciones.");
    }
  };

  const handleNewChat = async () => {
    const token = localStorage.getItem('user_token');
    if (!token) {
      toast.error("Debes iniciar sesión para crear un chat.");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/conversations/new`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error creando nueva conversación");
      }

      const data = await response.json();
      
      setMessages([{
        id: 'new-chat',
        sender: 'ai',
        text: `¡Claro! Empecemos de nuevo. ¿Cuál es tu consulta matemática?`,
        timestamp: new Date().toLocaleTimeString()
      }]);
      
      setCurrentConversationId(data.conversation_id);
      setShowPizarra(false);
      fetchConversations(token);
      toast.success("Nuevo chat iniciado");

    } catch (error) {
      toast.error(error.message || "Error al crear nuevo chat");
      console.error("New chat error:", error);
    }
  };

  const handleSelectConversation = async (id) => {
    const token = localStorage.getItem('user_token');
    if (!token) return;

    try {
      setCurrentConversationId(id);
      setMessages([{
        id: 1,
        sender: 'ai', 
        text: `Conversación seleccionada. Esta funcionalidad está en desarrollo.`,
        timestamp: new Date().toLocaleTimeString()
      }]);
      
      toast.info(`Conversación ${id} seleccionada`);
    } catch (error) {
      toast.error("Error al cargar la conversación");
    }
  };

  const handleClearHistory = () => {
    setMessages([]);
    setDrawings([]);
    toast.success("Historial local borrado");
  };

  const handleLoginSuccess = (token) => {
    localStorage.setItem('user_token', token);
    fetchUserData(token);
  };

  const handleLogout = () => {
    localStorage.removeItem('user_token');
    setIsAuthenticated(false);
    setCurrentUser(null);
    setMessages([{
        id: 'logout',
        sender: 'ai',
        text: '¡Hasta pronto! Vuelve cuando quieras.',
        timestamp: new Date().toLocaleTimeString()
    }]);
    setDrawings([]);
    setConversations([]);
    setCurrentConversationId(null);
    setShowPizarra(false);
    setShowHistorial(false);
    setSidebarOpen(false);
  };

  const handleSendMessage = async (msg) => {
    if (!msg.trim() || isBotThinking) return;

    const token = localStorage.getItem('user_token');
    if (!token) {
        toast.error("Debes iniciar sesión para chatear.");
        return;
    }

    const userMessage = {
      id: Date.now(),
      sender: "user",
      text: msg,
      timestamp: new Date().toLocaleTimeString()
    };

    const historyForBackend = messages
      .filter(m => m.sender !== 'ai' || !m.text.includes('Analizando tu dibujo'))
      .map(m => ({
        sender: m.sender,
        text: m.text
      }));

    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setIsBotThinking(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: msg,
          history: historyForBackend,
          conversation_id: currentConversationId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error en la respuesta del servidor");
      }

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        sender: "ai",
        text: data.response,
        timestamp: new Date().toLocaleTimeString()
      };
      
      setMessages(prev => [...prev, botMessage]);
      if (data.conversation_id && !currentConversationId) {
        setCurrentConversationId(data.conversation_id);
        fetchConversations(token);
      }

    } catch (error) {
      console.error("Chat error:", error);
      toast.error(`Error: ${error.message}`);
      
      const botMessage = {
        id: Date.now() + 2,
        sender: "ai",
        text: `Lo siento, tuve un problema: ${error.message}`,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, botMessage]);
    } finally {
      setIsBotThinking(false);
    }
  };

  const handleAnalyzeAndSaveDrawing = async (drawingData) => {
    const token = localStorage.getItem('user_token');
    if (!token) {
        toast.error("Debes iniciar sesión para analizar dibujos.");
        return;
    }

    const newDrawing = { 
      id: Date.now(), 
      dataUrl: drawingData, 
      timestamp: new Date().toLocaleTimeString() 
    };
    setDrawings(prev => [...prev, newDrawing]);

    const processingMessage = {
        id: Date.now() + 1,
        sender: "ai",
        text: "Analizando tu dibujo... ",
        timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, processingMessage]);
    setIsBotThinking(true);

    try {
        const response = await fetch(`${API_URL}/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                image: drawingData,
                dict_of_vars: {}
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Error en la respuesta del servidor');
        }

        const result = await response.json();
        
        const resultText = result.data.map(item =>
            `**Expresión detectada:** ${item.expr}  ➔  **Resultado:** ${item.result}`
        ).join('\n');

        const botMessage = {
            id: Date.now() + 2,
            sender: "ai",
            text: `¡He analizado tu dibujo!\n\n${resultText}`,
            timestamp: new Date().toLocaleTimeString()
        };
        
        setMessages(prev => prev.filter(msg => msg.id !== processingMessage.id));
        setMessages(prev => [...prev, botMessage]);

        fetchConversations(token);
        toast.success("Dibujo analizado con éxito");

    } catch (error) {
        console.error("Error al analizar el dibujo:", error);
        toast.error(`Error al analizar: ${error.message}`);
        
        setMessages(prev => prev.filter(msg => msg.id !== processingMessage.id));
        setMessages(prev => [...prev, {
            id: Date.now() + 3,
            sender: "ai",
            text: `Hubo un error al analizar el dibujo: ${error.message}`,
            timestamp: new Date().toLocaleTimeString()
        }]);
    } finally {
        setIsBotThinking(false);
    }
  };

  const startResize = () => setIsResizing(true);

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
        <Toaster richColors position="top-right" />
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
                isBotThinking={isBotThinking}
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
              messages={messages}
              drawings={drawings}
              onClearHistory={handleClearHistory}
              onClose={toggleHistorial}
              sidebarOpen={sidebarOpen}
            />
          )}
        </>
      )}
    </div>
  );
};

export default App;