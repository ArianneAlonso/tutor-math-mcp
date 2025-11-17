import React, { useState, useEffect } from 'react';
import { Chat } from './components/chat';
import { Historial } from './components/historial';
import { Pizarra } from './components/pizarra';
import { Sidebar } from './components/sidebar';
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

  useEffect(() => {
    const token = localStorage.getItem('user_token');
    if (token) {
      fetchUserData(token);
    }
  }, []);

  const fetchUserData = async (token) => {
    try {
      const response = await fetch('http://localhost:3000/users/me', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!response.ok) throw new Error('Sesión inválida o expirada');
      const userData = await response.json();
      setCurrentUser(userData);
      setIsAuthenticated(true);
      fetchConversations(token);
    } catch (error) {
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
      if (!response.ok) throw new Error('No se pudieron cargar las conversaciones');
      const data = await response.json();
      setConversations(data);
    } catch (error) {
      console.error(error);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setShowPizarra(false);
    setCurrentConversationId(null);
  };

  const handleSelectConversation = async (id) => {
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

  const handleSendMessage = (msg) => {
    if (!msg.trim()) return;
    const newMsg = { id: Date.now(), sender: "user", text: msg, timestamp: new Date().toLocaleTimeString() };
    setMessages(prev => [...prev, newMsg]);
    setInputMessage("");

    setTimeout(() => {
      const botResponse = { id: Date.now() + 1, sender: "bot", text: "Respuesta temporal del bot.", timestamp: new Date().toLocaleTimeString() };
      setMessages(prev => [...prev, botResponse]);
    }, 600);
  };

  const handleAnalyzeAndSaveDrawing = (drawingData) => {
    const newDrawing = { id: Date.now(), data: drawingData, timestamp: new Date().toLocaleTimeString() };
    setDrawings(prev => [...prev, newDrawing]);
  };

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
            onSelectConversation={handleSelectConversation}
            onLogout={handleLogout}
            currentUser={currentUser}
          />

          <div className={`h-full transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-14'} flex`}>
            <div className={showPizarra ? "w-1/2 border-r border-slate-200" : "w-full"}>
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
              <div className="w-1/2 h-full">
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