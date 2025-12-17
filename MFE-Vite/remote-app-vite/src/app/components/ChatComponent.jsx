import { useEffect } from "react";
import BottomBar from "./BottomBar";
import TopBar from "./TopBar";
import { useDispatch, useSelector } from "react-redux";
import { setMessages } from "../reducers/chatSlice";

export default function ChatComponent() {
  const { messages } = useSelector((state) => state.chat);
  const dispatch = useDispatch();

  useEffect(() => {
    if (messages.length === 0) {
      dispatch( setMessages([{ text: "Hello! How can I assist you today?", sender: "bot" }]));
    }
  }, [dispatch, messages.length]);

  return (
    <div className="flex flex-col h-screen w-full max-w-3xl mx-auto border border-gray-300 md:rounded-xl">
      <TopBar />

      <div className="flex-1 overflow-y-auto p-4 bg-white space-y-3">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`max-w-[75%] p-3 rounded-xl text-sm ${
              msg.sender === "user" ? "bg-sky-600 text-white ml-auto" : "bg-gray-200 text-gray-800"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <BottomBar />
    </div>
  );
}
