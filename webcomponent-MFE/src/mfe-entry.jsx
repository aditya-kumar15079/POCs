import React from "react";
import ReactDOM from "react-dom/client";
import ChatBot from "./components/ChatBot";
import { Provider } from "react-redux";
import store from "./store";
import "./index.css";

class ChatBotElement extends HTMLElement {
  connectedCallback() {
    console.log("[ChatBot] connectedCallback called");
    const root = ReactDOM.createRoot(this);
    root.render(
      <Provider store={store}>
        <ChatBot />
      </Provider>
    );
  }
}

customElements.define("chat-bot", ChatBotElement);
