const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("api", {
  readYAML: (filePath) => ipcRenderer.invoke("read-yaml", filePath),
  writeYAML: (content, filePath) => ipcRenderer.invoke("write-yaml", content, filePath),
  listFiles: (dirPath) => ipcRenderer.invoke("list-files", dirPath),
  executeTest: (batPath) => ipcRenderer.invoke("execute-test", batPath),
});
