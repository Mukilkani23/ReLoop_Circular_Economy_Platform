/**
 * ChatbotWidget Component — Floating chatbot with WebSocket connection.
 */
import { useState, useEffect, useRef } from 'react';
import { WS_URL, chatAPI } from '../services/api';
import CryptoService from '../services/cryptoService';
import { useAuth } from '../context/AuthContext';

export default function ChatbotWidget() {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [ws, setWs] = useState(null);
  const [roomId, setRoomId] = useState('bot');
  const [roomInfo, setRoomInfo] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const handleOpenChat = async (e) => {
      if (!user) return;
      const newRoomId = e.detail.roomId;
      setRoomId(newRoomId);
      setIsOpen(true);
      setMessages([]); // Clear previous messages

      if (newRoomId.startsWith('chat_')) {
        const requestId = newRoomId.replace('chat_', '');
        try {
          // 1. Fetch Room Info (Participants & Public Keys)
          const infoRes = await chatAPI.getRoomInfo(requestId);
          setRoomInfo(infoRes.data);

          // 2. Fetch Historical Encrypted Messages
          const msgsRes = await chatAPI.getMessages(newRoomId);
          
          // 3. Decrypt History
          const mySecretKeyBase64 = localStorage.getItem(`reloop_sec_${user.id}`);
          if (!mySecretKeyBase64) return;
          const mySecretKey = CryptoService.base64ToKey(mySecretKeyBase64);
          
          const decodedHistory = msgsRes.data.map(m => {
            try {
              const otherPubKeyBase64 = m.sender_id === user.id ? 
                (user.id === infoRes.data.buyer_id ? infoRes.data.seller_public_key : infoRes.data.buyer_public_key) :
                (m.sender_id === infoRes.data.buyer_id ? infoRes.data.buyer_public_key : infoRes.data.seller_public_key);
              
              const otherPubKey = CryptoService.base64ToKey(otherPubKeyBase64);
              const text = CryptoService.decrypt(m.encrypted_message, mySecretKey, otherPubKey);
              return { sender: m.sender_id === user.id ? 'user' : 'bot', text };
            } catch (err) {
              return { sender: 'bot', text: '🔒 [Encrypted Message — Decryption Failed]' };
            }
          });
          setMessages(decodedHistory);
        } catch (err) {
          console.error("Failed to load chat history:", err);
        }
      }
    };
    window.addEventListener('open-chat', handleOpenChat);
    return () => window.removeEventListener('open-chat', handleOpenChat);
  }, [user]);

  // Connect WebSocket
  useEffect(() => {
    if (!user) return;
    if (isOpen && !ws) {
      const token = localStorage.getItem('reloop_token') || '';
      const socket = new WebSocket(`${WS_URL}?room_id=${roomId}&token=${token}`);

      socket.onopen = () => console.log('🤖 Chat connected');
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.sender === 'system') {
            setMessages((prev) => [...prev, { sender: 'bot', text: `⚙️ ${data.message}` }]);
            return;
          }

          // If room is E2EE, decrypt incoming message
          if (roomId.startsWith('chat_') && roomInfo && data.sender !== 'user') {
            try {
              const mySecretKey = CryptoService.base64ToKey(localStorage.getItem(`reloop_sec_${user.id}`));
              const otherPubKeyBase64 = user.id === roomInfo.buyer_id ? roomInfo.seller_public_key : roomInfo.buyer_public_key;
              const otherPubKey = CryptoService.base64ToKey(otherPubKeyBase64);
              
              const decrypted = CryptoService.decrypt(data.message, mySecretKey, otherPubKey);
              setMessages((prev) => [...prev, { sender: 'bot', text: decrypted }]);
            } catch (err) {
              setMessages((prev) => [...prev, { sender: 'bot', text: '🔒 [Encrypted Message]' }]);
            }
          } else {
            setMessages((prev) => [...prev, { sender: data.sender || 'bot', text: data.message }]);
          }
        } catch {
          setMessages((prev) => [...prev, { sender: 'bot', text: event.data }]);
        }
      };

      socket.onclose = () => {
        console.log('🤖 Chat disconnected');
        setWs(null);
      };

      setWs(socket);
      return () => {
        socket.close();
        setWs(null);
      };
    }
  }, [isOpen, roomId, roomInfo, user]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = () => {
    if (!user || !input.trim() || !ws || ws.readyState !== WebSocket.OPEN) return;
    const msg = input.trim();
    let payload = msg;

    if (roomId.startsWith('chat_') && roomInfo) {
      try {
        const mySecretKey = CryptoService.base64ToKey(localStorage.getItem(`reloop_sec_${user.id}`));
        const otherPubKeyBase64 = user.id === roomInfo.buyer_id ? roomInfo.seller_public_key : roomInfo.buyer_public_key;
        const otherPubKey = CryptoService.base64ToKey(otherPubKeyBase64);
        payload = CryptoService.encrypt(msg, mySecretKey, otherPubKey);
      } catch (err) {
        console.error("Encryption failed:", err);
        return;
      }
    }

    setMessages((prev) => [...prev, { sender: 'user', text: msg }]);
    ws.send(JSON.stringify({ message: payload, sender: 'user' }));
    setInput('');
  };


  const handleKeyPress = (e) => { if (e.key === 'Enter') sendMessage(); };

  return (
    <>
      <button className="chatbot-toggle" onClick={() => setIsOpen(!isOpen)}>{isOpen ? '✕' : '💬'}</button>
      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <h3>{roomId === 'bot' ? '🤖 ReLoop Assistant' : '🔒 E2EE Negotiation'}</h3>
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>
          <div className="chatbot-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-message ${msg.sender === 'user' ? 'user' : 'bot'}`}>{msg.text}</div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <div className="chatbot-input">
            <input type="text" placeholder="Type a message..." value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={handleKeyPress} />
            <button onClick={sendMessage}>➤</button>
          </div>
        </div>
      )}
    </>
  );
}
