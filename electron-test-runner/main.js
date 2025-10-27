const { app, BrowserWindow, screen, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs/promises");
const dayjs = require("dayjs");
const yaml = require("js-yaml");
const os = require("os");
const { exec } = require("child_process");
const platform = os.platform();

const isDev = !app.isPackaged;
app.disableHardwareAcceleration();

function createWindow() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  const win = new BrowserWindow({
    width: width,
    height: height,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      enableRemoteModule: false,
      nodeIntegration: false,
    },
  });
  // win.setMenu(null);

  if (isDev) {
    setTimeout(() => {
      win.loadURL("http://localhost:5173");
    }, 2000);
  } else {
    win.loadFile(path.join(__dirname, "dist/index.html"));
  }
}

const getScriptPath = async (filepath) => {
  const parentPath = await getParentPath();
    if (platform === "win32") {
      return path.join(parentPath, filepath);
    } else if (platform === "linux") {
      const linuxFilePath = filepath?.replace(".bat", ".sh");
      return path.join(parentPath, linuxFilePath);
    } else {
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

app.whenReady().then(() => {
  createWindow();

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
      const yamlStr = yaml.dump(data);
      await fs.writeFile(scriptPath, yamlStr, "utf8");
      console.log(filePath, "YAML file written successfully");
    } catch (err) {
      console.error("Error writing YAML file:", err);
    }
  });

  ipcMain.handle("list-files", async (event, relativeDirPath) => {
    try {
      const parentDir = isDev
        ? __dirname
        : process.env.APPIMAGE
        ? path.dirname(process.env.APPIMAGE)
        : path.dirname(app.getPath("exe"));

      const dirPath = path.resolve(parentDir, relativeDirPath);
      const entries = await fs.readdir(dirPath);

      const filesWithStats = await Promise.all(
        entries.map(async (entry) => {
          const fullPath = path.join(dirPath, entry);
          const stat = await fs.stat(fullPath);
          const isFile = stat.isFile();
          if (!isFile) return null;

          const datetime = dayjs(stat.mtime).format("DD-MM-YYYY hh:mm A");

          return {
            name: entry,
            datetime: dayjs(stat.birthtime).format("DD-MM-YYYY hh:mm A"),
            createdAt: stat.birthtime, // keep original for sorting
            downloadUrl: "#",
          };
        })
      );

      const sortedFiles = filesWithStats
        .filter(Boolean)
        .sort((a, b) => b.createdAt - a.createdAt);

      return sortedFiles.map(({ name, datetime, downloadUrl }) => ({
        name,
        datetime,
        downloadUrl,
      }));
    } catch (err) {
      console.error("Error listing files:", err.message);
      return [];
    }
  });

  ipcMain.handle("execute-test", async (_, batPath) => {
    const scriptPath = await getScriptPath(batPath);
    const absolutePath = path.resolve(scriptPath);

     console.log("execute-test → batPath:", batPath);
  console.log("execute-test → scriptPath:", scriptPath);
  console.log("execute-test → absolutePath:", absolutePath);


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
          console.error("Error executing test:", err.message);
          return;
        }
        console.log(`Script launched in terminal: ${absolutePath}`);
      }
    );
  });

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
