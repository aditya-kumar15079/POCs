const { app, BrowserWindow, screen, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs/promises");
const fssync = require("fs");
const dayjs = require("dayjs");

const isDev = !app.isPackaged;
app.disableHardwareAcceleration();

function createWindow() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  const win = new BrowserWindow({
    width: width,
    height: height,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
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

app.whenReady().then(() => {
  createWindow();

  ipcMain.handle("get-parent-dir", () => {
    if (!isDev) {
      if (process.env.APPIMAGE) {
        return path.dirname(process.env.APPIMAGE);
      } else {
        return path.dirname(app.getPath("exe"));
      }
    } else {
      return __dirname;
    }
  });

  ipcMain.handle("list-files", async (event, relativeDirPath) => {
    try {
      const parentDir = isDev ? __dirname : process.env.APPIMAGE ? path.dirname(process.env.APPIMAGE) : path.dirname(app.getPath("exe"));

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

      const sortedFiles = filesWithStats.filter(Boolean).sort((a, b) => b.createdAt - a.createdAt);

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

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
