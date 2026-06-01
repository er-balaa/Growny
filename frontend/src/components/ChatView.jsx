import React, { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../services/api';

const BADGE = {
  FINANCE: { label: 'Logged',    cls: 'badge-finance'  },
  TASK:    { label: 'Saved',      cls: 'badge-task'     },
  ERROR:   { label: 'Error',      cls: 'badge-error'    },
  GENERAL: null,
};

// Web Speech API Initialization
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const mic = SpeechRecognition ? new SpeechRecognition() : null;
if (mic) {
  mic.continuous = false;
  mic.interimResults = true;
  mic.lang = 'en-US';
}

const ChatView = ({ onDataRefresh, user }) => {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'agent',
      text: "Hi! I'm Growny. I can help manage your money, tasks, and knowledge. What can I help you with?",
      type: 'GENERAL',
      steps: [],
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [thinkingStep, setThinkingStep] = useState(0);
  const messagesEndRef = useRef(null);
  const thinkingRef = useRef(null);

  const THINKING_LABELS = [
    'Thinking…',
    'Routing to agent…',
    'Running crew…',
    'Finalising response…',
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => { scrollToBottom(); }, [messages, isTyping]);

  useEffect(() => {
    if (isTyping) {
      setThinkingStep(0);
      thinkingRef.current = setInterval(() => {
        setThinkingStep(prev => (prev + 1) % THINKING_LABELS.length);
      }, 900);
    } else {
      clearInterval(thinkingRef.current);
    }
    return () => clearInterval(thinkingRef.current);
  }, [isTyping]);

  // Voice Recognition Setup
  useEffect(() => {
    if (!mic) return;
    
    mic.onstart = () => setIsListening(true);
    
    mic.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0])
        .map(result => result.transcript)
        .join('');
      setInput(transcript);
    };

    mic.onerror = (event) => {
      console.error("Speech recognition error", event.error);
      setIsListening(false);
    };

    mic.onend = () => setIsListening(false);
    
    return () => {
      if (isListening) mic.stop();
    };
  }, []);

  const toggleVoice = () => {
    if (!mic) {
      alert("Voice recognition is not supported in this browser. Try Chrome or Safari.");
      return;
    }
    if (isListening) {
      mic.stop();
    } else {
      setInput(''); // Clear input before dictating
      mic.start();
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isTyping) return;
    
    if (isListening && mic) {
      mic.stop();
    }

    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      text: input,
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const history = messages
        .filter(m => m.id !== 'welcome')
        .slice(-10)
        .map(m => ({
          role: m.sender === 'user' ? 'user' : 'assistant',
          content: m.text,
        }));

      const response = await chatAPI.sendMessage(userMsg.text, history);

      const agentMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: response.reply,
        type: response.action_type,
        steps: response.data?.steps || [],
      };

      setMessages(prev => [...prev, agentMsg]);

      if (['FINANCE', 'TASK'].includes(response.action_type)) {
        onDataRefresh();
      }

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: 'Sorry, I ran into an issue connecting to the server.',
        type: 'ERROR',
        steps: [],
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-view">
      <div className="chat-messages">
        {messages.map(msg => {
          const badge = BADGE[msg.type] || null;
          return (
            <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
              {msg.sender === 'agent' && (
                <div className="agent-avatar">M</div>
              )}
              <div className={`message-bubble ${msg.sender} ${msg.type ? msg.type.toLowerCase() : ''}`}>
                <p>{msg.text}</p>

                {/* Action-type badge */}
                {badge && msg.sender === 'agent' && (
                  <span className={`message-badge ${badge.cls}`}>{badge.label}</span>
                )}

                {/* Agent steps trace */}
                {msg.steps && msg.steps.length > 0 && (
                  <div className="agent-steps">
                    {msg.steps.map((step, i) => (
                      <span key={i} className="agent-step-item">{step}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Agent Thinking Indicator */}
        {isTyping && (
          <div className="message-wrapper agent">
            <div className="agent-avatar">M</div>
            <div className="message-bubble agent thinking-bubble">
              <div className="thinking-dots">
                <span /><span /><span />
              </div>
              <span className="thinking-label">{THINKING_LABELS[thinkingStep]}</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container-unified">
        <form onSubmit={handleSend} className={`chat-form ${isListening ? 'listening-mode' : ''}`}>
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={isListening ? "Listening... Speak now" : "Log an expense, add a task, or ask a question…"}
            disabled={isTyping}
            className="unified-chat-input"
          />
          <button 
            type="button" 
            onClick={toggleVoice} 
            className={`voice-btn ${isListening ? 'listening' : ''}`}
            title="Use Voice Typing"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill={isListening ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
              <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
              <line x1="12" x2="12" y1="19" y2="22" />
            </svg>
          </button>
          <button type="submit" disabled={!input.trim() || isTyping} className="unified-submit-btn">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatView;
