# 🤖 ChatBot Micro Frontend (MFE)

This is a React-based Micro Frontend (MFE) that exposes a `<ChatBot />` component via [Webpack 5 Module Federation](https://webpack.js.org/concepts/module-federation/). It can be consumed by any host application supporting Webpack Module Federation.

---

## 🚀 Features

- Exposes `ChatBot` component via `remoteEntry.js`
- Built with React 18
- Runs on Webpack 5
- Can be deployed independently and consumed dynamically

---

## 📦 Scripts

```bash
# Install dependencies
npm install

# Run in development mode (serves at http://localhost:3000)
npm start

# Build for production
npm run build
```


### You generally should declare shared dependencies in ModuleFederationPlugin if:

* You're using a library in both host and remote apps (like react, react-dom, react-router, etc.)

* You want to avoid multiple versions of the same library being loaded (which can break context-based libraries like React or Redux)

* The library has global state or singletons (like @reduxjs/toolkit, Zustand, or context providers)

### Tips
* Use singleton: true to ensure one shared instance across apps.
* Use eager: true sparingly – it will bundle the dependency directly into remoteEntry.js.
* If you don’t share a library that should be singleton (like react), it can lead to bugs such as:
State loss
* Inconsistent routing
* Hooks can only be called inside function components errors
* 🧪 How to Know What to Share?
- Start simple: Just share react, react-dom, and context-based libraries.
- If a library causes issues in the host or remote runtime, try adding it to shared.
