import { BotMessageSquare, Menu, SendHorizontal } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";
import MessageCard from "./MessageCard";
import { BASE_URL, mockChatResponse } from "../utils/Constants";
import useApi from "../hooks/useApi";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const { POST, loading } = useApi();
  const endOfMessagesRef = useRef(null);
  const inputRef = useRef(null);
  const [newSession, setNewSession] = useState(false);
  const [sessionId, setSessionId] = useState("1");

  const handleSend = async () => {
    const text = input.trim()?.toLocaleLowerCase();
    if (!text) return;

    if (messages?.[messages?.length - 1]?.extracted_keywords?.length > 0) {
      if (
        text === "yes" ||
        text === "ya" ||
        text === "y" ||
        text === "yup" ||
        text === "sure" ||
        text === "yes please"
      ) {
        setMessages((prev) => {
          if (prev.length === 0) return prev;
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            clicked: {
              type: "yes",
              text,
            },
          };
          return updated;
        });
        setInput("");
        return;
      }

      if (text === "confirm") {
        setMessages((prev) => {
          if (prev.length === 0) return prev;
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            clicked: {
              type: "confirm",
              text,
            },
          };
          return updated;
        });
        setInput("");
        return;
      }
    }

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [
      ...prev,
      userMessage,
      { role: "bot", loading: true },
    ]);
    setInput("");
    const { text_response, xml_rule, extracted_keywords } = BASE_URL
      ? await fetchChatResponse(input)
      : await fetchStaticResponse();

    const botResponse = {
      role: "bot",
      text_response,
      xml_rule,
      extracted_keywords,
      sessionId,
    };

    setMessages((prev) => [...prev.slice(0, -1), botResponse]);
  };

  const fetchChatResponse = async (payload) => {
    const data = await POST("chat", {
      user_id: "1",
      session_id: sessionId,
      user_input: payload,
    });
    return data;
  };

  const fetchStaticResponse = async () => {
    return mockChatResponse[0];
  };

  useEffect(() => {
    const welcomeMessage = {
      role: "welcome",
      text: "Hi, This is your Smart Rules Builder assistant, let me know how can I help you?",
    };
    setMessages([welcomeMessage]);
  }, []);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if(!loading){
      inputRef?.current?.focus();
    }
  }, [loading]);

  const handleClearChat = () => {
    handleNewSession();
  };

  const handleNewSession = () => {
    const newSessionId = Math.floor(100000 + Math.random() * 900000).toString();
    setSessionId(newSessionId);
    setMessages([]);
    setNewSession(false);
  }

  return (
    <>
      <div className="fixed flex flex-col flex-col-reverse bottom-10 right-10 z-50 h-9/10 transition-all duration-500 ease-out transform animate-chat-open">
        {isOpen ? (
          <div className="mt-2 w-180 min-h-8/10 bg-white rounded-xl shadow-2xl flex flex-col overflow-hidden border border-gray-200">
            <div className="flex justify-between bg-hexblue">
              <span className="text-white p-3 font-semibold">Rule Builder</span>
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="bg-hexblue px-3 m-1 text-l rounded-full shadow-lg hover:bg-blue-800 transition"
              >
                ❌
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-3 bg-gray-100">
              {messages.length === 0 && (
                <p className="text-gray-400 text-sm text-center">
                  Ask me something!
                </p>
              )}

              {messages.map((msg, index) => (
                <MessageCard key={index} message={msg} setNewSession={setNewSession} />
              ))}
              <div ref={endOfMessagesRef} />
            </div>

            {/* Input Section */}
            {!newSession ? <div className="p-3 flex items-center bg-white">
              <div className="relative">
                <button
                  onClick={() => setMenuOpen(!menuOpen)}
                  className="px-2 py-1 rounded cursor-pointer hover:bg-gray-200"
                >
                  <Menu className="" />
                </button>
                {menuOpen && (
                  <div className="absolute bottom-10 left-0 bg-white border border-gray-200 rounded shadow-md w-32 text-sm z-10">
                    <button
                      onClick={handleClearChat}
                      className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                    >
                      Clear Chat
                    </button>
                  </div>
                )}
              </div>

              <input
                type="text"
                value={input}
                onFocus={() => setMenuOpen(false)}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSend()}
                className="flex-1 ml-1 border border-gray-300 rounded-md rounded-r-none px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-hexblue"
                placeholder="Type your query..."
                disabled={loading}
                ref={inputRef}
              />
              <button
                onClick={handleSend}
                disabled={loading}
                className="bg-hexblue text-white px-6 py-2 text-sm rounded-md rounded-l-none hover:bg-blue-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <SendHorizontal />
              </button>
            </div> :
            <div className="p-3 flex items-center bg-white">
              <button className="bg-hexblue w-full text-white px-6 py-2 text-sm rounded-md hover:bg-blue-800 transition" onClick={handleNewSession}>Start new session</button>
            </div>}
          </div>
        ) : (
          <div className="fixed flex flex-col flex-col-reverse bottom-10 right-10 z-50 h-8/10">
            <div className="relative group">
              {/* Tooltip */}
              <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 text-sm font-semibold rounded px-2 py-1 w-60 text-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                Chat with us
              </div>

              {/* Chat Button */}
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="bg-hexblue text-red-500 px-4 py-2 font-bold text-2xl rounded-full shadow-lg transition transform hover:-translate-y-1 hover:scale-105 hover:bg-blue-800 animate-bounce-once"
              >
                💬
              </button>
            </div>
          </div>
        )}
      </div>
      <style>
        {`
          @keyframes bounceOnce {
            0% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0); }
          }

          .animate-bounce-once:hover {
            animation: bounceOnce 0.4s ease-in-out;
          }
          
          @keyframes chatOpen {
            0% {
              opacity: 0;
              transform: scale(0.2) translateY(200px);
            }
            100% {
              opacity: 1;
              transform: scale(1) translateY(0);
            }
          }

          .animate-chat-open {
            animation: chatOpen 0.3s ease-out;
          }
        `}
      </style>
    </>
  );
};

export default Chatbot;
