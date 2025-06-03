
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createRoot } from 'react-dom/client';

// --- Web Speech API Type Definitions ---
interface SpeechRecognitionEventMap {
    "audiostart": Event;
    "soundstart": Event;
    "speechstart": Event;
    "speechend": Event;
    "soundend": Event;
    "audioend": Event;
    "result": SpeechRecognitionEvent;
    "nomatch": SpeechRecognitionEvent;
    "error": SpeechRecognitionErrorEvent;
    "start": Event;
    "end": Event;
}

interface SpeechRecognition extends EventTarget {
    grammars: SpeechGrammarList;
    lang: string;
    continuous: boolean;
    interimResults: boolean;
    maxAlternatives: number;
    serviceURI: string;

    start(): void;
    stop(): void;
    abort(): void;

    onaudiostart: ((this: SpeechRecognition, ev: Event) => any) | null;
    onsoundstart: ((this: SpeechRecognition, ev: Event) => any) | null;
    onspeechstart: ((this: SpeechRecognition, ev: Event) => any) | null;
    onspeechend: ((this: SpeechRecognition, ev: Event) => any) | null;
    onsoundend: ((this: SpeechRecognition, ev: Event) => any) | null;
    onaudioend: ((this: SpeechRecognition, ev: Event) => any) | null;
    onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
    ennomatch: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
    onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => any) | null;
    onstart: ((this: SpeechRecognition, ev: Event) => any) | null;
    onend: ((this: SpeechRecognition, ev: Event) => any) | null;

    addEventListener<K extends keyof SpeechRecognitionEventMap>(type: K, listener: (this: SpeechRecognition, ev: SpeechRecognitionEventMap[K]) => any, options?: boolean | AddEventListenerOptions): void;
    addEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | AddEventListenerOptions): void;
    removeEventListener<K extends keyof SpeechRecognitionEventMap>(type: K, listener: (this: SpeechRecognition, ev: SpeechRecognitionEventMap[K]) => any, options?: boolean | EventListenerOptions): void;
    removeEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | EventListenerOptions): void;
}

declare var SpeechRecognition: {
    prototype: SpeechRecognition;
    new(): SpeechRecognition;
};

declare var webkitSpeechRecognition: { // For Safari/Chrome legacy
    prototype: SpeechRecognition;
    new(): SpeechRecognition;
};

interface SpeechRecognitionEvent extends Event {
    readonly resultIndex: number;
    readonly results: SpeechRecognitionResultList;
    readonly interpretation?: any; 
    readonly emma?: Document | null; 
}

interface SpeechRecognitionResultList {
    readonly length: number;
    item(index: number): SpeechRecognitionResult;
    [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
    readonly isFinal: boolean;
    readonly length: number;
    item(index: number): SpeechRecognitionAlternative;
    [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
    readonly transcript: string;
    readonly confidence: number;
}

interface SpeechRecognitionErrorEvent extends Event {
    readonly error: string; 
    readonly message: string; 
}

interface SpeechGrammar {
    src: string;
    weight?: number;
}
declare var SpeechGrammar: {
    prototype: SpeechGrammar;
    new(): SpeechGrammar;
};

interface SpeechGrammarList {
    readonly length: number;
    item(index: number): SpeechGrammar;
    [index: number]: SpeechGrammar;
    addFromString(string: string, weight?: number): void;
    addFromURI(src: string, weight?: number): void;
}
declare var SpeechGrammarList: {
    prototype: SpeechGrammarList;
    new(): SpeechGrammarList;
};

// --- Speech Synthesis API Type Definitions ---
interface SpeechSynthesisUtterance extends EventTarget {
    text: string;
    lang: string;
    voice: SpeechSynthesisVoice | null;
    volume: number; // 0 to 1
    rate: number;   // 0.1 to 10
    pitch: number;  // 0 to 2
    onstart: ((this: SpeechSynthesisUtterance, ev: SpeechSynthesisEvent) => any) | null;
    onend: ((this: SpeechSynthesisUtterance, ev: SpeechSynthesisEvent) => any) | null;
    onerror: ((this: SpeechSynthesisUtterance, ev: SpeechSynthesisErrorEvent) => any) | null;
    onpause: ((this: SpeechSynthesisUtterance, ev: SpeechSynthesisEvent) => any) | null;
    onresume: ((this: SpeechSynthesisUtterance, ev: SpeechSynthesisEvent) => any) | null;
    onmark: ((this: SpeechSynthesisUtterance, ev: SpeechSynthesisEvent) => any) | null;
    onboundary: ((this: SpeechSynthesisUtterance, ev: SpeechSynthesisEvent) => any) | null;
}
declare var SpeechSynthesisUtterance: {
    prototype: SpeechSynthesisUtterance;
    new(text?: string): SpeechSynthesisUtterance;
};

interface SpeechSynthesisVoice {
    readonly voiceURI: string;
    readonly name: string;
    readonly lang: string;
    readonly localService: boolean;
    readonly default: boolean;
}

interface SpeechSynthesis extends EventTarget {
    readonly pending: boolean;
    readonly speaking: boolean;
    readonly paused: boolean;
    onvoiceschanged: ((this: SpeechSynthesis, ev: Event) => any) | null;
    speak(utterance: SpeechSynthesisUtterance): void;
    cancel(): void;
    pause(): void;
    resume(): void;
    getVoices(): SpeechSynthesisVoice[];
}

interface SpeechSynthesisEvent extends Event {
    readonly charIndex: number;
    readonly elapsedTime: number;
    readonly name: string;
}

interface SpeechSynthesisErrorEvent extends Event { // Renamed from SpeechSynthesisErrorEvent to avoid conflict if globally defined
    readonly error: string; 
}

declare global {
    interface Window {
        SpeechRecognition?: typeof SpeechRecognition;
        webkitSpeechRecognition?: typeof SpeechRecognition;
        SpeechSynthesisUtterance: typeof SpeechSynthesisUtterance;
    }
}

// --- App Code ---
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  isLoading?: boolean;
}

const DEFAULT_VOLUME = 0.7;

const App: React.FC = () => {
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState<string>('');
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isBotThinking, setIsBotThinking] = useState<boolean>(false);
  const [assistantVolume, setAssistantVolume] = useState<number>(DEFAULT_VOLUME);
  
  const speechRecognitionRef = useRef<SpeechRecognition | null>(null);
  const chatHistoryRef = useRef<HTMLDivElement>(null);
  const speechSynthesisSupported = useRef(false);
  const previousVolumeRef = useRef<number>(DEFAULT_VOLUME);


  useEffect(() => {
    speechSynthesisSupported.current = 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
  }, []);

  const speakText = useCallback((text: string) => {
    if (!speechSynthesisSupported.current || assistantVolume === 0) {
      console.log('Speech synthesis skipped (not supported, volume is 0, or no text).');
      return;
    }
    window.speechSynthesis.cancel(); 
    const utterance = new window.SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.volume = assistantVolume;
    window.speechSynthesis.speak(utterance);
  }, [assistantVolume]);

  useEffect(() => {
    const welcomeMessageText = "Hi! I'm your AI assistant. My responses are read aloud by default. You can toggle my voice using the audio switch at the top.";
    const welcomeMessage: Message = {
      id: `bot-welcome-${Date.now()}`,
      text: welcomeMessageText,
      sender: 'bot',
    };
    setChatHistory([welcomeMessage]);
    
    if (speechSynthesisSupported.current && assistantVolume > 0) {
        // Small delay to ensure the message is in the DOM and the user is ready.
        setTimeout(() => {
            const utterance = new window.SpeechSynthesisUtterance(welcomeMessageText);
            utterance.lang = 'en-US';
            utterance.volume = assistantVolume; 
            window.speechSynthesis.speak(utterance);
        }, 100);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); 

  useEffect(() => {
    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognitionAPI) {
      if (!speechRecognitionRef.current) {
        speechRecognitionRef.current = new SpeechRecognitionAPI();
      }
      const recognitionInstance = speechRecognitionRef.current;
      
      recognitionInstance.continuous = false;
      recognitionInstance.interimResults = true; 
      recognitionInstance.lang = 'en-US';

      recognitionInstance.onresult = (event: SpeechRecognitionEvent) => {
        let interimTranscript = '';
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }
        setUserInput(finalTranscript || interimTranscript); 
      };

      recognitionInstance.onerror = (event: SpeechRecognitionErrorEvent) => {
        console.error('Speech recognition error:', event.error, event.message);
        setIsListening(false);
      };
      
      recognitionInstance.onend = () => {
        setIsListening(false); 
      };

    } else {
      console.warn('Speech Recognition API not supported in this browser.');
    }
    return () => {
        if (speechRecognitionRef.current) {
            speechRecognitionRef.current.onresult = null;
            speechRecognitionRef.current.onerror = null;
            speechRecognitionRef.current.onend = null;
        }
    };
  }, []);

  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const startListening = () => {
    if (speechRecognitionRef.current && !isListening) {
      try {
        setUserInput(''); 
        speechRecognitionRef.current.start();
        setIsListening(true);
      } catch (e) {
        console.error("Error starting speech recognition:", e);
        setIsListening(false); 
      }
    }
  };

  const stopListening = () => {
    if (speechRecognitionRef.current && isListening) {
      speechRecognitionRef.current.stop();
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };
  
  const handleSendMessage = async (messageText?: string) => {
    const textToSend = (messageText || userInput).trim();
    if (!textToSend) return;

    if (isListening) {
        stopListening();
    }

    const newUserMessage: Message = { id: `user-${Date.now()}`, text: textToSend, sender: 'user' };
    setChatHistory(prev => [...prev, newUserMessage]);
    setUserInput('');
    setIsBotThinking(true);
    
    const loadingBotMessageId = `bot-loading-${Date.now()}`;
    const loadingBotMessage: Message = { 
        id: loadingBotMessageId, 
        text: 'Thinking', 
        sender: 'bot',
        isLoading: true 
    };
    setChatHistory(prev => [...prev, loadingBotMessage]);

    setTimeout(() => {
      const botResponseText = `You said: "${textToSend}"`;
      const newBotMessage: Message = { id: `bot-${Date.now()}`, text: botResponseText, sender: 'bot' };
      
      setChatHistory(prev => prev.map(msg => msg.id === loadingBotMessageId ? newBotMessage : msg ));
      speakText(botResponseText);
      setIsBotThinking(false);
    }, 2000);
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(event.target.value);
  };

  const handleInputKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !isBotThinking && !isListening) {
      handleSendMessage();
    }
  };

  const renderMessageContent = (message: Message) => {
    if (message.isLoading && message.text === "Thinking") {
      return (
        <>
          {message.text}
          <span className="loading-ellipsis">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </>
      );
    }
    return message.text;
  };

  const toggleMute = () => {
    if (assistantVolume > 0) {
      previousVolumeRef.current = assistantVolume; 
      setAssistantVolume(0);
    } else {
      setAssistantVolume(previousVolumeRef.current > 0 ? previousVolumeRef.current : DEFAULT_VOLUME);
    }
  };

  const getVolumeIcon = () => {
    return assistantVolume === 0 ? '🔇' : '🔊';
  };

  const mockCalendarEvents = [
    { id: 'cal1', time: '09:00 AM', title: 'Daily Stand-up' },
    { id: 'cal2', time: '10:00 AM', title: 'Client Onboarding Call' },
    { id: 'cal3', time: '11:30 AM', title: 'Design Review Session' },
    { id: 'cal4', time: '01:00 PM', title: 'Lunch Break' },
    { id: 'cal5', time: '02:00 PM', title: 'Feature Planning Meeting' },
    { id: 'cal6', time: '03:30 PM', title: 'Code Refactoring Session' },
    { id: 'cal7', time: '05:00 PM', title: 'End of Day Sync' },
    { id: 'cal8', time: '06:00 PM', title: 'Gym Session' },
  ];

  const mockEmails = [
    { id: 'mail1', sender: 'HR Department', subject: 'Important: Company Policy Update', snippet: 'Please review the updated company policies...' },
    { id: 'mail2', sender: 'John Doe', subject: 'Project Alpha - Feedback', snippet: 'Here is my feedback on the latest designs...' },
    { id: 'mail3', sender: 'Tech Weekly', subject: 'Your Weekly Tech Digest', snippet: 'Latest news in AI, Web Development, and more...' },
    { id: 'mail4', sender: 'Support Team', subject: 'Re: Your recent inquiry', snippet: 'We have an update regarding your ticket...' },
    { id: 'mail5', sender: 'Marketing Team', subject: 'Upcoming Webinar Announcement', snippet: 'Join us for an exciting webinar next week...' },
    { id: 'mail6', sender: 'Cloud Services', subject: 'Your monthly invoice is ready', snippet: 'Please find your latest invoice attached...' },
    { id: 'mail7', sender: 'Jane Smith', subject: 'Quick Question', snippet: 'Could we chat for a few minutes today?' },
  ];
  
  const isAudioOn = assistantVolume > 0;

  return (
    <div className="app-container" role="main">
      <section className="chat-panel" aria-labelledby="chat-panel-heading">
        <div className="chat-panel-header">
            <h2 id="chat-panel-heading" className="sr-only">Chat with AI Assistant</h2>
            {speechSynthesisSupported.current && (
                <button
                    className="audio-control-switch-container"
                    onClick={toggleMute}
                    title={isAudioOn ? "Turn off assistant audio" : "Turn on assistant audio"}
                    aria-label={isAudioOn ? "Turn off assistant audio" : "Turn on assistant audio"}
                    aria-pressed={isAudioOn}
                >
                    <span className="audio-control-icon" aria-hidden="true">{getVolumeIcon()}</span>
                    <span className="audio-control-label">Assistant Audio</span>
                    <div className={`audio-switch-track ${isAudioOn ? 'on' : 'off'}`}>
                        <div className="audio-switch-knob"></div>
                    </div>
                </button>
            )}
        </div>
        <div className="chat-history" ref={chatHistoryRef} aria-live="polite">
          {chatHistory.map((msg) => (
            <div
              key={msg.id}
              className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'bot-message'} ${msg.isLoading ? 'loading' : ''}`}
              aria-label={`${msg.sender === 'user' ? 'User' : 'Bot'} message: ${msg.isLoading ? msg.text + ' loading' : msg.text }`}
            >
              {renderMessageContent(msg)}
            </div>
          ))}
        </div>
        <div className="chat-input-area">
          <button 
            onClick={toggleListening} 
            className={`mic-button ${isListening ? 'listening' : ''}`}
            aria-pressed={isListening}
            aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
            title={isListening ? 'Stop voice input' : 'Start voice input'}
            disabled={!speechRecognitionRef.current || isBotThinking}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="22px" height="22px">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.24 14.47 16 12 16s-4.52-1.76-4.93-4.15c-.08-.49-.49-.85-.98-.85-.55 0-1 .45-1 1 0 2.73 2.04 4.98 4.75 5.42V21H9.75c-.41 0-.75.34-.75.75s.34.75.75.75h4.5c.41 0 .75-.34.75-.75s-.34-.75-.75-.75H13v-1.58c2.71-.44 4.75-2.69 4.75-5.42 0-.55-.45-1-1-1z M9 5c0-1.66 1.34-3 3-3s3 1.34 3 5v6c0 1.66-1.34 3-3 3s-3-1.34-3-5V5z"/>
            </svg>
          </button>
          <input
            type="text"
            value={userInput}
            onChange={handleInputChange}
            onKeyPress={handleInputKeyPress}
            placeholder={isListening ? "Listening..." : "Type or use mic..."}
            aria-label="Chat input"
            disabled={isListening || isBotThinking}
          />
          <button 
            onClick={() => handleSendMessage()} 
            className="send-button"
            disabled={!userInput.trim() || isBotThinking }
            aria-label="Send message"
            title="Send message"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20px" height="20px">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
      </section>

      <aside className="dashboard-panel" aria-label="Information dashboard">
        <div className="dashboard-content">
            <div className="dashboard-column">
                <div className="widget fixed-height" role="region" aria-labelledby="weather-widget-heading">
                    <h3 id="weather-widget-heading"><span className="widget-icon" aria-hidden="true">☀️</span>Weather</h3>
                    <p>Current weather information will appear here.</p>
                </div>
                <div className="widget grow-widget" role="region" aria-labelledby="calendar-list-heading">
                    <h3 id="calendar-list-heading"><span className="widget-icon" aria-hidden="true">🗓️</span>Calendar Events</h3>
                    <p className="calendar-list-description">Your upcoming schedule. Scroll to see more.</p>
                    <div className="list-content-wrapper" aria-label="List of calendar events">
                        {mockCalendarEvents.map(event => (
                            <div key={event.id} className="calendar-event-item">
                                <strong>{event.time}</strong> - {event.title}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
            <div className="dashboard-column">
                <div className="widget grow-widget" role="region" aria-labelledby="email-list-heading">
                    <h3 id="email-list-heading"><span className="widget-icon" aria-hidden="true">✉️</span>Email List</h3>
                    <p className="email-list-description">Recent messages from your inbox. Scroll for more.</p>
                    <div className="list-content-wrapper" aria-label="List of emails">
                        {mockEmails.map(email => (
                            <div key={email.id} className="email-item">
                                <strong>{email.sender}</strong> - {email.subject}
                                <p style={{fontSize: '0.8em', color: 'var(--secondary-text-color)', margin: '4px 0 0'}}>{email.snippet}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
      </aside>
    </div>
  );
};

const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<React.StrictMode><App /></React.StrictMode>);
} else {
  console.error('Root element not found');
}
