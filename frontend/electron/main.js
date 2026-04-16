const { app, BrowserWindow, session } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,       // Seguridad: no exponer Node al renderer
      contextIsolation: true,       // Seguridad: aislar contextos
      preload: path.join(__dirname, 'preload.js'),
    },
    icon: path.join(__dirname, '../build/icon.png'),
    title: 'Valeecokies POS',
  });

  // Permitir llamadas HTTP al backend (local o remoto)
  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    callback({
      responseHeaders: {
        ...details.responseHeaders,
        'Content-Security-Policy': [
          "default-src 'self' 'unsafe-inline' 'unsafe-eval' http://127.0.0.1:5173 http://localhost:5173 http://127.0.0.1:8000 https://hlqkclscqeyinukrhtaq.supabase.co; " +
          "connect-src 'self' http://* https://* ws://*;"
        ]
      }
    });
  });

  // Cargar la app
  const isDev = process.env.NODE_ENV !== 'production';

  if (isDev) {
    // En desarrollo, cargar desde Vite (el proxy de Vite redirige /api → backend)
    mainWindow.loadURL('http://127.0.0.1:5173');
    // DevTools desactivado para evitar que congele el renderer durante el login.
    // Descomenta la línea de abajo solo si necesitas depurar:
    // mainWindow.webContents.openDevTools();
  } else {
    // En producción, cargar desde dist
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});