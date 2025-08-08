const { app, BrowserWindow, screen, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs/promises");
const dayjs = require("dayjs");
const yaml = require("js-yaml");
const os = require("os");
const { exec } = require("child_process");
const platform = os.platform();

const isDev = !app.isPackaged;

let mainWindow;

// function createWindow() {
//   const primaryDisplay = screen.getPrimaryDisplay();
//   const { width, height } = primaryDisplay.workAreaSize;

//   const win = new BrowserWindow({
//     width: width,
//     height: height,
//     webPreferences: {
//       preload: path.join(__dirname, "preload.js"),
//       contextIsolation: true,
//       enableRemoteModule: false,
//       nodeIntegration: false,
//     },
//   });
//   // win.setMenu(null);

//   if (isDev) {
//     setTimeout(() => {
//       win.loadURL("http://localhost:5173");
//     }, 2000);
//   } else {
//     win.loadFile(path.join(__dirname, "dist/index.html"));
//   }
// }

  function createWindow() {
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workAreaSize;

    mainWindow = new BrowserWindow({
      width: width,
      height: height,
      webPreferences: {
        preload: path.join(__dirname, "preload.js"),
        contextIsolation: true,
        nodeIntegration: false,
      },
    });
    if (isDev) {
      mainWindow.loadURL("http://localhost:5173");
      mainWindow.webContents.openDevTools();
    } else {
      mainWindow.loadFile(path.join(__dirname, "dist/index.html"));
    }

    mainWindow.on("closed", () => {
      mainWindow = null;
    });
  }

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

const getParentPath = async () => {
   if (!isDev) {
      if (process.env.APPIMAGE) {
        return path.dirname(process.env.APPIMAGE);
      } else {
        return path.dirname(app.getPath("exe"));
      }
    } else {
      return __dirname;
    }
};

function registerIpcHandlers() {
  ipcMain.handle("read-yaml", async (_, filePath) => {
    const scriptPath = await getScriptPath(filePath);
    try {
      const fileContents = await fs.readFile(scriptPath, "utf8");
      const data = yaml.load(fileContents);
      return data;
    } catch (err) {
      console.error("Error reading YAML file:", err);
    }
  });

  ipcMain.handle("write-yaml", async (_, content, filePath) => {
    const scriptPath = await getScriptPath(filePath);
    try {
      const yamlStr = yaml.dump(content);
      await fs.writeFile(scriptPath, yamlStr, "utf8");
      console.log(filePath, "YAML file written successfully");
    } catch (err) {
      console.error("Error writing YAML file:", err);
    }
  });

  if (!ipcMain.listenerCount("list-files")) {
    ipcMain.handle("list-files", async (event, relativeDirPath) => {
      try {
        const parentDir = isDev ? __dirname : process.env.APPIMAGE ? path.dirname(process.env.APPIMAGE) : path.dirname(app.getPath("exe"));

        const dirPath = path.resolve(parentDir, relativeDirPath);
        const entries = await fs.readdir(dirPath);

        const filesWithStats = await Promise.all(
          entries.map(async (entry) => {
            const fullPath = path.join(dirPath, entry);
            const stat = await fs.stat(fullPath);
            if (!stat.isFile()) return null;

            const createdAt = stat.birthtimeMs && stat.birthtimeMs > 0 ? stat.birthtime : stat.mtime;

            return {
              name: entry,
              createdAt,
              datetime: dayjs(createdAt).format("DD-MM-YYYY hh:mm A"),
              downloadUrl: "#",
            };
          })
        );

        return filesWithStats
          .filter(Boolean)
          .sort((a, b) => b.createdAt - a.createdAt)
          .map(({ name, datetime, downloadUrl }) => ({ name, datetime, downloadUrl }));
      } catch (err) {
        console.error("Error listing files:", err.message);
        return [];
      }
    });
  }

  ipcMain.handle("execute-test", async (_, batPath) => {
    const scriptPath = await getScriptPath(batPath);
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
  });

}

app.whenReady().then(() => {
  createWindow();
  registerIpcHandlers();
  

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
