@echo off
REM Script para corregir TODOS los errores de configuracion
REM Ejecuta este archivo en la carpeta frontend/

echo ========================================
echo   CORRECTOR AUTOMATICO DE ERRORES
echo   Sistema POS Valeecc
echo ========================================
echo.

echo Este script va a:
echo 1. Organizar archivos en carpetas correctas
echo 2. Corregir postcss.config.js
echo 3. Crear archivos faltantes
echo.
pause

echo.
echo [1/5] Creando estructura de carpetas...
if not exist "src" mkdir src
if not exist "src\components" mkdir src\components
if not exist "src\services" mkdir src\services
if not exist "electron" mkdir electron

echo [2/5] Moviendo archivos de componentes...
if exist "Dashboard.jsx" move /Y Dashboard.jsx src\components\ >nul
if exist "POS.jsx" move /Y POS.jsx src\components\ >nul
if exist "CashRegister.jsx" move /Y CashRegister.jsx src\components\ >nul
if exist "App.jsx" move /Y App.jsx src\ >nul
if exist "main.jsx" move /Y main.jsx src\ >nul
if exist "index.css" move /Y index.css src\ >nul
if exist "api.js" move /Y api.js src\services\ >nul

echo [3/5] Corrigiendo postcss.config.js...
(
echo module.exports = {
echo   plugins: {
echo     tailwindcss: {},
echo     autoprefixer: {},
echo   },
echo }
) > postcss.config.js
echo   ✓ postcss.config.js corregido

echo [4/5] Verificando package.json...
if exist "package.json" (
    echo   ✓ package.json existe
) else (
    echo   ✗ FALTA package.json - copialo manualmente
)

echo [5/5] Verificando estructura final...
echo.
echo === ESTRUCTURA FINAL ===
if exist "src\components\Dashboard.jsx" (echo ✓ src\components\Dashboard.jsx) else (echo ✗ FALTA Dashboard.jsx)
if exist "src\components\POS.jsx" (echo ✓ src\components\POS.jsx) else (echo ✗ FALTA POS.jsx)
if exist "src\components\CashRegister.jsx" (echo ✓ src\components\CashRegister.jsx) else (echo ✗ FALTA CashRegister.jsx)
if exist "src\App.jsx" (echo ✓ src\App.jsx) else (echo ✗ FALTA App.jsx)
if exist "src\main.jsx" (echo ✓ src\main.jsx) else (echo ✗ FALTA main.jsx)
if exist "src\index.css" (echo ✓ src\index.css) else (echo ✗ FALTA index.css)
if exist "src\services\api.js" (echo ✓ src\services\api.js) else (echo ✗ FALTA api.js)
if exist "postcss.config.js" (echo ✓ postcss.config.js) else (echo ✗ FALTA postcss.config.js)
if exist "tailwind.config.js" (echo ✓ tailwind.config.js) else (echo ✗ FALTA tailwind.config.js)
if exist "vite.config.js" (echo ✓ vite.config.js) else (echo ✗ FALTA vite.config.js)

echo.
echo ========================================
echo   CORRECCION COMPLETADA
echo ========================================
echo.
echo SIGUIENTES PASOS:
echo 1. Si aun no instalaste dependencias: npm install
echo 2. Ejecuta el servidor: npm run dev
echo 3. Abre en navegador: http://localhost:5173
echo.
echo Si hay errores, lee el archivo: SOLUCION_ERROR_POSTCSS.md
echo.
pause
