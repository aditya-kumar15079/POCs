const { contextBridge, ipcRenderer } = require("electron");
const { exec } = require("child_process");
const path = require("path");
const os = require("os");
const fs = require("fs/promises");
const yaml = require("js-yaml");
const platform = os.platform();

const getParentPath = async () => {
  return await ipcRenderer.invoke("get-parent-dir");
};

const getScriptPath = async (filepath) => {
  const parentPath = await getParentPath();
  if (platform === "win32") {
    return path.join(parentPath, filepath);
  } else if (platform === "linux") {
    const linuxFilePath = filepath?.replace(".bat", ".sh");
    console.log("window.api.getParentPath()", parentPath);
    return path.join(parentPath, linuxFilePath);
  } else {
    alert("Unsupported OS");
    return null;
  }
};

contextBridge.exposeInMainWorld("api", {
  executeTest: async (filePath) => {
    const scriptPath = await getScriptPath(filePath);
    const absolutePath = path.resolve(scriptPath);
    const isWindows = os.platform() === "win32";

    let terminalCommand;

    if (isWindows) {
      terminalCommand = `start cmd.exe /k "${absolutePath}"`;
    } else {
      terminalCommand = `gnome-terminal -- bash -c "chmod +x '${absolutePath}'; '${absolutePath}'; exec bash"`;
    }

    exec(
      terminalCommand,
      {
        env: { ...process.env, PYTHONIOENCODING: "utf-8" },
      },
      (err) => {
        if (err) {
          alert("Error: " + err.message);
          return;
        }
        console.log(`Script launched in terminal: ${absolutePath}`);
      }
    );
  },
  readYAML: async (filePath) => {
    const scriptPath = await getScriptPath(filePath);
    try {
      const fileContents = await fs.readFile(scriptPath, "utf8");
      const data = yaml.load(fileContents);
      return data;
    } catch (err) {
      console.error("Error reading YAML file:", err);
    }
  },
  writeYAML: async (data, filePath) => {
    const scriptPath = await getScriptPath(filePath);
    try {
      const yamlStr = yaml.dump(data);
      await fs.writeFile(scriptPath, yamlStr, "utf8");
      console.log(filePath, "YAML file written successfully");
    } catch (err) {
      console.error("Error writing YAML file:", err);
    }
  },

  listFiles: async (relativeDirPath) => {
    return await ipcRenderer.invoke("list-files", relativeDirPath);
  },
});
