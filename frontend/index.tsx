
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

interface SpeechSynthesisErrorEvent extends Event {
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

interface CalendarEvent {
  id: string;
  time: string;
  title: string;
}

interface EmailItem {
  id: string;
  sender: string;
  subject: string;
  snippet: string;
}

const initialCalendarEvents: CalendarEvent[] = [
];

interface WeatherInfo {
  currentTime: string;
  timeZone: { id: string };
  isDaytime: boolean;
  weatherCondition: {
    iconBaseUri: string;
    description: { text: string; languageCode: string };
    type: string;
  };
  temperature: { degrees: number; unit: string };
  feelsLikeTemperature: { degrees: number; unit: string };
  dewPoint: { degrees: number; unit: string };
  heatIndex: { degrees: number; unit: string };
  windChill: { degrees: number; unit: string };
  relativeHumidity: number;
  uvIndex: number;
  precipitation: {
    probability: { percent: number; type: string };
    snowQpf: { quantity: number; unit: string };
    qpf: { quantity: number; unit: string };
  };
  thunderstormProbability: number;
  airPressure: { meanSeaLevelMillibars: number };
  wind: {
    direction: { degrees: number; cardinal: string };
    speed: { value: number; unit: string };
    gust: { value: number; unit: string };
  };
  visibility: { distance: number; unit: string };
  cloudCover: number;
  currentConditionsHistory: {
    temperatureChange: { degrees: number; unit: string };
    maxTemperature: { degrees: number; unit: string };
    minTemperature: { degrees: number; unit: string };
    snowQpf: { quantity: number; unit: string };
    qpf: { quantity: number; unit: string };
  };
}

const App: React.FC = () => {
  const [chatHistory, setChatHistory] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState<string>('');
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isBotThinking, setIsBotThinking] = useState<boolean>(false);
  const [assistantVolume, setAssistantVolume] = useState<number>(0.7); 

  const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>(initialCalendarEvents);
  const [emailItems, setEmailItems] = useState<EmailItem[]>([]);
  const [isCalendarLoading, setIsCalendarLoading] = useState<boolean>(false);
  const [isEmailLoading, setIsEmailLoading] = useState<boolean>(false);

  const speechRecognitionRef = useRef<SpeechRecognition | null>(null);
  const chatHistoryRef = useRef<HTMLDivElement>(null);

  const [weatherInfo, setWeatherInfo] = useState<WeatherInfo | null>(null);
  const [isWeatherLoading, setIsWeatherLoading] = useState<boolean>(false);

  const speakText = useCallback((text: string) => {
    if (assistantVolume > 0 && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window) {
      const utterance = new window.SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.volume = assistantVolume;
      window.speechSynthesis.speak(utterance);
    } else if (assistantVolume === 0) {
        console.log("Assistant audio is muted.");
    } else {
      console.warn('Text-to-Speech API not supported in this browser.');
    }
  }, [assistantVolume]);


  const fetchCalendarEvents = async () => {
    setIsCalendarLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/fetch_calendar_events");
      const data = await response.json();
      if (data && Array.isArray(data.events)) {
        const newEvents: CalendarEvent[] = data.events.map((event: any, idx: number) => ({
          id: event.id || `cal-api-${idx}-${Date.now()}`,
          time: event.time || event.start?.dateTime || event.start?.date || "Unknown Time",
          title: event.title || event.summary || "No Title",
        }));
        setCalendarEvents(newEvents);
      } else {
        setCalendarEvents([]);
      }
    } catch (error) {
      console.error("Failed to fetch calendar events:", error);
      setCalendarEvents([]);
    }
    setIsCalendarLoading(false);
  };

  useEffect(() => {
    fetchCalendarEvents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const fetchWeather = async () => {
      setIsWeatherLoading(true);
      try {
        const response = await fetch("http://127.0.0.1:8000/fetch_weather");
        const data = await response.json();
        setWeatherInfo(data.weather || null);
      } catch (error) {
        console.error("Failed to fetch weather:", error);
        setWeatherInfo(null);
      }
      setIsWeatherLoading(false);
    };
    fetchWeather();
  }, []);

  useEffect(() => {
    const fetchInitialEmails = async () => {
      setIsEmailLoading(true);
      try {
        const response = await fetch("http://127.0.0.1:8000/fetch_latest_emails");
        const data = await response.json();
        if (data && Array.isArray(data.emails)) {
          const newEmails: EmailItem[] = data.emails.map((email: any, idx: number) => ({
            id: email.id || `mail-api-${idx}-${Date.now()}`,
            sender: email.from || email.sender || "Unknown Sender",
            subject: email.subject || "No Subject",
            snippet: email.snippet || "",
          }));
          setEmailItems(newEmails);
        } else {
          setEmailItems([]);
        }
      } catch (error) {
        console.error("Failed to fetch emails:", error);
        setEmailItems([]);
      }
      setIsEmailLoading(false);
    };

    fetchInitialEmails();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const welcomeMessageText = "Hello! I'm your AI assistant. How can I help you today? You can toggle my audio response using the switch in the top-left corner.";
    const initialBotMessage: Message = {
        id: `bot-initial-${Date.now()}`,
        text: welcomeMessageText,
        sender: 'bot'
    };
    setChatHistory([initialBotMessage]);
    speakText(welcomeMessageText);
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
            if (isListening) {
                 speechRecognitionRef.current.stop();
            }
        }
    };
  }, [isListening]);

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
      setIsListening(false);
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const toggleAssistantAudio = () => {
    setAssistantVolume(prevVolume => prevVolume > 0 ? 0 : 0.7);
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

    // Simulate API call
    try {
      const response = await fetch("http://127.0.0.1:8000/agent/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: textToSend }),
      });
      const data = await response.json();
      const botResponseText = data.response;

      const newBotMessage: Message = { id: `bot-${Date.now()}`, text: botResponseText, sender: 'bot' };
      setChatHistory(prev => prev.map(msg => msg.id === loadingBotMessageId ? newBotMessage : msg ));
      speakText(botResponseText);
    } catch (error) {
      console.error("Error communicating with the assistant:", error);
    } finally {
      setIsBotThinking(false);
    }
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
  // Preserve line breaks and whitespace from backend
  return (
    <span style={{ whiteSpace: 'pre-line' }}>
      {message.text}
    </span>
  );
};

  const handleRefreshCalendar = () => {
    setIsCalendarLoading(true);
    try {
      fetchCalendarEvents();
    }
    catch (error) {
        console.error("Failed to fetch emails:", error);
        setCalendarEvents([]);
    }
    setIsCalendarLoading(false);
  };

  const handleRefreshEmail = async () => {
    setIsEmailLoading(true);
    try {
        const response = await fetch("http://127.0.0.1:8000/fetch_latest_emails");
        const data = await response.json();
        if (data && Array.isArray(data.emails)) {
            // Map backend dicts to EmailItem type if needed
            const newEmails: EmailItem[] = data.emails.map((email: any, idx: number) => ({
                id: email.id || `mail-api-${idx}-${Date.now()}`,
                sender: email.from || email.sender || "Unknown Sender",
                subject: email.subject || "No Subject",
                snippet: email.snippet || "",
            }));
            setEmailItems(newEmails);
        } else {
            setEmailItems([]);
        }
    } catch (error) {
        console.error("Failed to fetch emails:", error);
        setEmailItems([]);
    }
    setIsEmailLoading(false);
  };


  return (
    <div className="app-container" role="main">
           <aside className="dashboard-panel" aria-label="Information Dashboard">
        <div className="dashboard-content">
            <div className="dashboard-column">
                <div className="widget fixed-height" role="region" aria-labelledby="weather-widget-heading">
                    <h3 id="weather-widget-heading"><span className="widget-icon" aria-hidden="true">☀️</span>Weather</h3>
                    {isWeatherLoading ? (
                <p>Loading weather...</p>
              ) : weatherInfo ? (
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <img
                      src={weatherInfo.weatherCondition.iconBaseUri + ".svg"}
                      alt={weatherInfo.weatherCondition.description.text}
                      style={{ width: 36, height: 36 }}
                    />
                    <span style={{ fontWeight: 300, fontSize: "1.1em" }}>
                      {weatherInfo.weatherCondition.description.text}
                    </span>
                  </div>
                  <div style={{ marginTop: 8 }}>
                    <span>
                      <strong>{weatherInfo.temperature.degrees}°{weatherInfo.temperature.unit === "CELSIUS" ? "C" : "F"}</strong>
                      {" "} (feels like {weatherInfo.feelsLikeTemperature.degrees}°{weatherInfo.feelsLikeTemperature.unit === "CELSIUS" ? "C" : "F"})
                    </span>
                    <br />
                    <span>
                      Humidity: {weatherInfo.relativeHumidity}% | Wind: {weatherInfo.wind.speed.value} km/h
                    </span>
                    <br />
                    <span>
                      High: {weatherInfo.currentConditionsHistory.maxTemperature.degrees}°{weatherInfo.currentConditionsHistory.maxTemperature.unit === "CELSIUS" ? "C" : "F"}
                      {" "} | Low: {weatherInfo.currentConditionsHistory.minTemperature.degrees}°{weatherInfo.currentConditionsHistory.minTemperature.unit === "CELSIUS" ? "C" : "F"}
                    </span>
                    <br />
                    <span>
                      Cloud Cover: {weatherInfo.cloudCover}% | UV Index: {weatherInfo.uvIndex}
                    </span>
                  </div>
                </div>
              ) : (
                <p>Weather information is unavailable.</p>
              )}
                </div>
                <div className="widget grow-widget" role="region" aria-labelledby="calendar-list-heading">
                    <div className="widget-header">
                        <h3 id="calendar-list-heading"><span className="widget-icon" aria-hidden="true">🗓️</span>Calendar Events</h3>
                        <button 
                            className="widget-refresh-button" 
                            onClick={handleRefreshCalendar} 
                            disabled={isCalendarLoading}
                            aria-label="Refresh calendar events"
                            title="Refresh calendar events"
                        >
                            <svg className={isCalendarLoading ? 'spinning' : ''} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18px" height="18px">
                                <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                            </svg>
                        </button>
                    </div>
                    <p className="calendar-list-description">Your upcoming schedule. Scroll to see more.</p>
                    <div className="list-content-wrapper" aria-label="List of calendar events">
                      {calendarEvents.length === 0 && !isCalendarLoading ? (
                          <div className="calendar-event-item" style={{ color: 'var(--secondary-text-color)' }}>
                              You are all clear today!
                          </div>
                      ) : (
                          calendarEvents.map(event => (
                              <div key={event.id} className="calendar-event-item">
                                  <strong>{event.time}</strong> - {event.title}
                              </div>
                          ))
                      )}
                      {isCalendarLoading && <div className="widget-loading-text">Loading events...</div>}
                  </div>
                </div>
            </div>
            <div className="dashboard-column">
                <div className="widget grow-widget" role="region" aria-labelledby="email-list-heading">
                     <div className="widget-header">
                        <h3 id="email-list-heading"><span className="widget-icon" aria-hidden="true">✉️</span>Email List</h3>
                        <button 
                            className="widget-refresh-button" 
                            onClick={handleRefreshEmail} 
                            disabled={isEmailLoading}
                            aria-label="Refresh email list"
                            title="Refresh email list"
                        >
                             <svg className={isEmailLoading ? 'spinning' : ''} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18px" height="18px">
                                <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                            </svg>
                        </button>
                    </div>
                    <p className="email-list-description">Recent messages from your inbox. Scroll for more.</p>
                    <div className="list-content-wrapper" aria-label="List of emails">
                        {emailItems.map(email => (
                            <div key={email.id} className="email-item">
                                <strong>{email.sender}</strong> - {email.subject}
                                <p style={{fontSize: '0.8em', color: 'var(--secondary-text-color)', margin: '4px 0 0'}}>{email.snippet}</p>
                            </div>
                        ))}
                        {isEmailLoading && <div className="widget-loading-text">Loading emails...</div>}
                    </div>
                </div>
            </div>
        </div>
      </aside>
      <section className="chat-panel" aria-label="Chat Panel">
        <div className="chat-panel-header">
            <button
                onClick={toggleAssistantAudio}
                className={`audio-toggle-switch ${assistantVolume > 0 ? 'on' : 'off'}`}
                aria-pressed={assistantVolume > 0}
                aria-label={assistantVolume > 0 ? "Mute assistant audio" : "Unmute assistant audio"}
                title={assistantVolume > 0 ? "Mute assistant audio" : "Unmute assistant audio"}
            >
                <span className="audio-toggle-label">Assistant Audio:</span>
                <span className="audio-toggle-icon" aria-hidden="true">
                    {assistantVolume > 0 ? (
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18px" height="18px">
                          <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                        </svg>
                    ) : (
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" width="18px" height="18px">
                          <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L7 9H3v6h4l5 5V4z"/>
                        </svg>
                    )}
                </span>
                <div className="switch-track">
                    <div className="switch-knob"></div>
                </div>
            </button>
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
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.85C16.52 14.24 14.47 16 12 16s-4.52-1.76-4.93-4.15c-.08-.49-.49-.85-.98-.85-.55 0-1 .45-1 1 0 2.73 2.04 4.98 4.75 5.42V21H9.75c-.41 0-.75.34-.75.75s.34.75.75.75h4.5c.41 0 .75-.34.75-.75s-.34-.75-.75-.75H13v-1.58c2.71-.44 4.75-2.69 4.75-5.42 0-.55-.45-1-1-1z"/>
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
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24px" height="24px">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
      </section>
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
