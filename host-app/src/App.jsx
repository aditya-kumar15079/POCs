import React, { Suspense } from "react";

const ChatBot = React.lazy(() => import("chatbot_mfe/ChatBot"));

export default function App() {
  return (
    <div style={{ padding: 20 }}>
      <h1>Host App</h1>
      <Suspense fallback={<div>Loading ChatBot...</div>}>
        <ChatBot />
      </Suspense>
    </div>
  );
}
