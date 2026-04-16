/**
 * Servicio de API para comunicarse con el backend FastAPI
 */

import axios from 'axios';

const getBackendURL = () => {
  // PRIORIDAD 1: Forzar la URL de Render si estamos en la web
  // Esto evita que el localStorage o variables viejas nos bloqueen
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return 'https://valeecokies.onrender.com';
  }

  // PRIORIDAD 2: LocalStorage (para desarrollo local en red)
  const savedIP = localStorage.getItem('backend_url');
  if (savedIP) return savedIP;
  
  // PRIORIDAD 3: Localhost por defecto
  return 'http://127.0.0.1:8000';
};

const API_BASE_URL = getBackendURL();
console.log('Conectando a Backend en:', API_BASE_URL);

// Instancia de axios configurada
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000, // Aumentamos a 15 segundos porque Render free es lento al despertar
});

// Interceptor para agregar token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Manejo global de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.dispatchEvent(new CustomEvent('auth:sessionExpired'));
    }
    return Promise.reject(error);
  }
);

export const handleAPIError = (error) => {
  if (error.response) {
    return {
      message: error.response.data.detail || 'Error en el servidor',
      status: error.response.status
    };
  } else if (error.request) {
    return {
      message: 'No se pudo conectar con el servidor de Render. (Posible tiempo de espera agotado)',
      status: 0
    };
  }
  return { message: error.message, status: -1 };
};

export default api;