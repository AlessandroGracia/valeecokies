# Guía de Despliegue: Galletas System 🍪

Esta guía te ayudará a subir tu proyecto a la web paso a paso.

## 1. Crear Repositorio en GitHub

1. Entra en [github.com](https://github.com) e inicia sesión.
2. Haz clic en el botón **"New"** para crear un nuevo repositorio.
3. Ponle un nombre (ej: `galletas-system-web`) y déjalo como **Public** o **Private**.
4. **IMPORTANTE**: No marques "Initialize this repository with a README", ya lo tenemos localmente.
5. Haz clic en **"Create repository"**.
6. GitHub te mostrará una pantalla con comandos. Copia la URL que termina en `.git` (ej: `https://github.com/tu-usuario/nombre-repo.git`).

---

## 2. Subir el Código (desde tu terminal)

Abre una terminal en la carpeta raíz del proyecto y ejecuta estos comandos (reemplaza la URL):

```bash
# Inicializar Git
git init

# Agregar todos los archivos preparados
git add .

# Primer commit
git commit -m "Preparado para despliegue web"

# Conectar con GitHub
git branch -M main
git remote add origin https://github.com/tu-usuario/tu-repo.git

# Subir por primera vez
git push -u origin main
```

---

## 3. Desplegar el Backend (Render)

1. Ve a [dashboard.render.com](https://dashboard.render.com) y conecta tu cuenta de GitHub.
2. Haz clic en **"New"** -> **"Web Service"**.
3. Selecciona tu repositorio de GitHub.
4. Configuración:
   - **Name**: `galletas-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: (Ya lo configuramos en el `Procfile`, Render debería detectarlo automáticamente). Si no, usa: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`
5. Haz clic en **"Advanced"** -> **"Add Environment Variable"**:
   - `DATABASE_URL`: (Tu URL de Supabase)
   - `SECRET_KEY`: (Una clave segura, puedes usar la que tienes en el `.env` local)
   - `DEBUG`: `False`
6. Haz clic en **"Create Web Service"**.
7. Una vez termine, copia la URL que te da Render (ej: `https://galletas-backend.onrender.com`).

---

## 4. Desplegar el Frontend (Vercel)

1. Ve a [vercel.com](https://vercel.com) e inicia sesión con GitHub.
2. Haz clic en **"Add New"** -> **"Project"**.
3. Selecciona tu repositorio.
4. Configuración:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite` (debería autodetectarse)
5. Haz clic en **"Environment Variables"**:
   - **Name**: `VITE_API_URL`
   - **Value**: (La URL que copiaste de Render en el paso anterior)
6. Haz clic en **"Deploy"**.

---

## 5. ¡Listo! 🚀

Ahora tu sistema estará accesible desde la URL que te asigne Vercel. Puedes entrar desde tu celular o cualquier computadora.

> [!TIP]
> Si en algún momento cambias algo en el código, simplemente haz `git add .`, `git commit -m "cambio"` y `git push`. La web se actualizará sola.
