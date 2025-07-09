const { app, BrowserWindow, screen, ipcMain } = require("electron");
const path = require("path");
const isDev = !app.isPackaged;

function createWindow() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.workAreaSize;

  const win = new BrowserWindow({
    width: width,
    height: height,
    webPreferences: {
      nodeIntegration: true,
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
  // win.loadFile(path.join(__dirname, "renderer/dist/index.html"));
}

app.whenReady().then(() => {
  createWindow();

  ipcMain.handle("get-parent-dir", () => {
    if (!isDev) {
      if (process.env.APPIMAGE) {
        console.log("Running as AppImage from:", process.env.APPIMAGE);
        return path.dirname(process.env.APPIMAGE);
      } else {
        return path.dirname(app.getPath("exe"));
      }
    } else {
      return __dirname;
    }
  });

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
