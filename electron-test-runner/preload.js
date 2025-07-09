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
  // runScript: () => {
  //   const platform = os.platform();
  //   console.log("runScript() called ", platform);

  //   let scriptPath;
  //   if (platform === "win32") {
  //     scriptPath = path.join(__dirname, "script.bat");
  //   } else if (platform === "linux") {
  //     scriptPath = path.join(__dirname, "script.sh");
  //   } else {
  //     alert("Unsupported OS");
  //     return;
  //   }

  //   exec(`"${scriptPath}"`, (err, stdout, stderr) => {
  //     if (err) {
  //       alert("Error: " + err.message);
  //       return;
  //     }
  //     alert("Script Output:\n" + stdout);
  //   });
  // },
  // runLLMJudge: () => {
  //   const platform = os.platform();

  //   let scriptPath;
  //   if (platform === "win32") {
  //     scriptPath = path.join(__dirname, "./Test-Foundry/GENAI_LLMJudge_ResponseQuality_Framework/Execute.bat");
  //   } else if (platform === "linux") {
  //     scriptPath = path.join(__dirname, "./Test-Foundry/GENAI_LLMJudge_ResponseQuality_Framework/linux-execute.sh");
  //   } else {
  //     alert("Unsupported OS");
  //     return;
  //   }

  //   exec(`"${scriptPath}"`, (err, stdout, stderr) => {
  //     if (err) {
  //       alert("Error: " + err.message);
  //       return;
  //     }
  //     alert(`Script Output:\nRan Script ${scriptPath}\n${stdout}`);
  //   });
  // },
  executeTest: async (filePath) => {
    const scriptPath = await getScriptPath(filePath);
    console.log("executeTest() called ", scriptPath);
    exec(`"${scriptPath}"`, (err, stdout, stderr) => {
      if (err) {
        alert("Error: " + err.message);
        return;
      }
      alert(`Script Output:\nRan Script ${scriptPath}\n${stdout}`);
    });
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
});
