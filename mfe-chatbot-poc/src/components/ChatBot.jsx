import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { addMessage } from "../store";

export default function ChatBot() {
  const messages = useSelector((state) => state?.chat?.messages);
  const dispatch = useDispatch();
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (input.trim() !== "") {
      dispatch(addMessage({ sender: "user", text: input }));
      dispatch(addMessage({ sender: "bot", text: `Echo: ${input}` }));
      setInput("");
    }
  };

  return (
    <div className="w-[500px] max-w-md border rounded-xl shadow-lg p-4 bg-red-300">
      <div className="h-[700px] overflow-y-auto border rounded p-2 mb-2 bg-gray-100">
        {messages?.map((msg, i) => (
          <div key={i} className={`mb-1 ${msg.sender === "user" ? "text-right" : "text-left"}`}>
            <span
              className={`inline-block px-3 py-1 rounded-full text-sm ${msg?.sender === "user" ? "bg-blue-500 text-white" : "bg-gray-300"}`}
            >
              {msg?.text}
            </span>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded p-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type a message..."
        />
        <button onClick={handleSend} className="bg-blue-500 text-white px-4 rounded">
          Send
        </button>
      </div>
    </div>
  );
}
