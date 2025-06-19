---

## 📘 `host-app/README.md` – Host App

```md
# 🏠 Host App for ChatBot MFE

This is a React application that **dynamically loads a ChatBot component** from a remote Micro Frontend (MFE) via [Webpack 5 Module Federation](https://webpack.js.org/concepts/module-federation/).

---

## 🚀 Features

- Loads remote ChatBot from `chatbot_mfe@http://localhost:3000/remoteEntry.js` (make sure to run mfe-chatbot-modulefederation present in this POC)
- Uses React + React.lazy + Suspense
- Fully decoupled: no hard dependency on ChatBot’s source code

---

## 📦 Scripts

```bash
# Install dependencies
npm install

# Run the host app (http://localhost:3001)
npm start

# Build for production
npm run build
```

### How to run

- gotomfe-chatbot-modulefederation (cd ../mfe-chatbot-modulefederation)
- npm run start
- new terminal (should be at ./host-app)
- npm start
