# 🍪 Sistema de Facturación - Galletas

Sistema completo de facturación para emprendimiento de venta de galletas con IA integrada.

## 📁 Estructura del Proyecto

```
galletas-system/
├── backend/                 # API con FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints de la API
│   │   ├── models/         # Modelos de base de datos
│   │   ├── services/       # Lógica de negocio
│   │   └── core/           # Configuración
│   ├── requirements.txt
│   └── main.py
│
├── frontend/               # Aplicación Electron + React
│   ├── src/
│   │   ├── components/    # Componentes React
│   │   ├── pages/         # Pantallas principales
│   │   └── services/      # Conexión con backend
│   └── package.json
│
└── database/              # Scripts y configuración DB
```

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: Electron + React + Tailwind CSS
- **Base de Datos**: PostgreSQL (Supabase)
- **IA**: Claude API (Anthropic)
- **Autenticación**: JWT

## 🚀 Instalación

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📖 Fases de Desarrollo

- [x] Fase 1: Backend básico y DB
- [ ] Fase 2: Frontend desktop
- [ ] Fase 3: Funcionalidades core
- [ ] Fase 4: Integración IA
- [ ] Fase 5: Pulido final

## 👥 Usuarios del Sistema

- **Admin**: Acceso completo, reportes, configuración
- **Vendedor**: Facturación, consulta de inventario
