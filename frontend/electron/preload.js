/**
 * Preload script para Electron.
 * 
 * Este script se ejecuta antes del renderer y permite
 * exponer APIs seguras al frontend via contextBridge.
 */

const { contextBridge } = require('electron');

// Exponer APIs seguras al renderer
contextBridge.exposeInMainWorld('electronAPI', {
  // Información de la plataforma
  platform: process.platform,
  
  // Puedes agregar más funciones seguras aquí
  // Ejemplo: abrir diálogos, leer archivos, etc.
});
