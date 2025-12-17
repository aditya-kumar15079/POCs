import { Mic, Plus, SendHorizonal } from 'lucide-react';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { addMessage } from '../reducers/chatSlice';

const BottomBar = () => {
  const [input, setInput] = useState("");
  const [inputDisabled, setInputDisabled] = useState(false);
  const dispatch = useDispatch();
  const [rows, setRows] = useState(1);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (input.trim()) {
        sendMessage();
        setInput("");
      }
    } else if (e.key === "Enter" && e.shiftKey && rows < 3) {
      setRows(rows + 1);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    dispatch(addMessage({ text: input, sender: "user" }));
    setInput("");
    setRows(1);
    setInputDisabled(true);

    // Simulate bot response delay
    setTimeout(() => {
      dispatch(addMessage({ text: "Hello! How can I assist you today?", sender: "bot" }));
      setInputDisabled(false);
    }, 1000);
  };

  return (
    <div className="pt-4 pb-8 px-1 border-t border-gray-300 bg-bg flex items-center mr-1">
      <button disabled={inputDisabled} className="bg-primary w-10 h-10 rounded-full text-white flex justify-center items-center mr-2">
        <Plus className="w-8 h-8 rounded-full text-white" />
      </button>
      <button disabled={inputDisabled} className="bg-primary w-10 h-10 rounded-full text-white flex justify-center items-center mr-2">
        <Mic className="w-8 h-8 rounded-full text-white" />
      </button>
      <textarea
        rows={rows}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        type="text"
        disabled={inputDisabled}
        placeholder={`${inputDisabled ? "Please wait" : `Ask Me Anything...`}`}
        className="flex-1 bg-white rounded-lg px-2 py-3 outline-none resize-none
          placeholder:text-gray-500 disabled:bg-gray-200 mr-2"
      />

      <button
        onClick={sendMessage}
        disabled={inputDisabled}
        className="bg-primary w-10 h-10 rounded-lg text-white flex justify-center items-center mr-2"
      >
        <SendHorizonal className="w-8 h-6 rounded-full text-white" />
      </button>
    </div>
  );
};

export default BottomBar;