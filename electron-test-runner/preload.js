const { contextBridge, ipcRenderer } = require("electron");

const getParentPath = async () => {
  return await ipcRenderer.invoke("get-parent-dir");
};
exports.getParentPath = getParentPath;

const getScriptPath = async (filepath) => {
  return await ipcRenderer.invoke("get-script-path", filepath);
};
exports.getScriptPath = getScriptPath;

contextBridge.exposeInMainWorld("api", {
  readYAML: (filePath) => ipcRenderer.invoke("read-yaml", filePath),
  writeYAML: (content, filePath) => ipcRenderer.invoke("write-yaml", content, filePath),
  listFiles: (dirPath) => ipcRenderer.invoke("list-files", dirPath),
  executeTest: (batPath) => ipcRenderer.invoke("execute-test", batPath),
});
