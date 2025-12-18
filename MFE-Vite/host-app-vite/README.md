# 🤖 ChatBot Micro Frontend (MFE) -using Vite

This is a React-based app that consumes a remote component coming from http://localhost:4173. We import the remote component as `remoteApp`(check vite.config.js) The component which is exported by remoteApp is `<ChatRoot />`. Now we can use the ChatRoot component anywhere in our App by `import Chatbot from "remoteApp/ChatRoot";`

---

## 🚀 Features

- imports `remoteApp` via `http://localhost:4173/assets/remoteEntry.js`
- Built with React 18
- Runs on Vite
- Can be deployed independently and used just like a React App.

---

## 📦 Scripts

```bash
# Install dependencies
npm install

# serves the app
npm run dev
```

NOTE: ChatRoot component is available only if the remote is also running. In this POC it should be running at http://localhost:4173 and http://localhost:4173/assets/remoteEntry.js is also reachable.


### You generally should declare shared dependencies in ModuleFederationPlugin if:

* You're using a library in both host and remote apps (like react, react-dom, react-router, etc.)

* You want to avoid multiple versions of the same library being loaded (which can break context-based libraries like React or Redux)

* The library has global state or singletons (like @reduxjs/toolkit, Zustand, or context providers)

### Tips
* Use singleton: true to ensure one shared instance across apps.
* Use eager: false
* If you don’t share a library that should be singleton (like react), it can lead to bugs such as:
State loss
* Inconsistent routing
* Hooks can only be called inside function components errors
* 🧪 How to Know What to Share?
- Start simple: Just share react, react-dom, and context-based libraries.
- If a library causes issues in the host or remote runtime, try adding it to shared.
