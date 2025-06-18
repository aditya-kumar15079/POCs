import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { Provider } from "react-redux";
import store from "./store";
import ChatBot from "./components/ChatBot";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <Provider store={store}>
      <ChatBot />
    </Provider>
  </StrictMode>
);
