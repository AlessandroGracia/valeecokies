/**
 * Servicio de API para comunicarse con el backend FastAPI
 * 
 * Centraliza TODAS las llamadas HTTP al backend.
 * Todos los componentes DEBEN usar estos métodos en vez de fetch/axios directo.
 */

import axios from 'axios';

const getBackendURL = () => {
  // PRIORIDAD 1: Forzar la URL de Render si estamos en la web
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return 'https://valeecokies.onrender.com';
  }

  // PRIORIDAD 2: Variables de entorno de Vite
  if (import.meta.env.PROD && import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  // PRIORIDAD 3: LocalStorage (para desarrollo local)
  const savedIP = localStorage.getItem('backend_url');
  if (savedIP) return savedIP;
  
  // PRIORIDAD 4: Localhost por defecto
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
  timeout: 15000, 
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
      const url = error.config?.url || '';
      if (url.includes('/api/auth/me')) {
        return Promise.reject(error);
      }
      localStorage.removeItem('token');
      window.dispatchEvent(new CustomEvent('auth:sessionExpired'));
    }
    return Promise.reject(error);
  }
);

// ========== PRODUCTOS ==========
export const productsAPI = {
  getAll: (params = {}) => api.get('/api/products', { params }),
  getById: (id) => api.get(`/api/products/${id}`),
  create: (data) => api.post('/api/products', data),
  update: (id, data) => api.put(`/api/products/${id}`, data),
  delete: (id) => api.delete(`/api/products/${id}`),
  getLowStock: () => api.get('/api/products/low-stock'),
  adjustStock: (id, adjustment) => api.patch(`/api/products/${id}/stock`, adjustment),
};

// ========== CLIENTES ==========
export const customersAPI = {
  getAll: (params = {}) => api.get('/api/customers', { params }),
  getById: (id) => api.get(`/api/customers/${id}`),
  create: (data) => api.post('/api/customers', data),
  update: (id, data) => api.put(`/api/customers/${id}`, data),
  delete: (id) => api.delete(`/api/customers/${id}`),
  getSummary: () => api.get('/api/customers/summary'),
  getStats: () => api.get('/api/customers/stats'),
};

// ========== VENTAS ==========
export const salesAPI = {
  getAll: (params = {}) => api.get('/api/sales', { params }),
  getById: (id) => api.get(`/api/sales/${id}`),
  create: (data) => api.post('/api/sales', data),
  cancel: (id) => api.post(`/api/sales/${id}/cancel`),
  getStats: (params = {}) => api.get('/api/sales/stats', { params }),
  getToday: () => api.get('/api/sales/today'),
  getByDate: (date) => api.get('/api/sales/daily', { params: { target_date: date } }),
};

// ========== PUNTO DE VENTA (POS) ==========
export const posAPI = {
  createSale: (data) => api.post('/api/pos/sale', data),
  calculateChange: (total, paymentReceived) => 
    api.post('/api/pos/calculate-change', null, {
      params: { total, payment_received: paymentReceived }
    }),
};

// ========== CAJA DIARIA ==========
export const cashRegisterAPI = {
  getStatus: () => api.get('/api/cash-register/status'),
  getToday: () => api.get('/api/cash-register/today'),
  getSummary: () => api.get('/api/cash-register/summary'),
  open: (data) => api.post('/api/cash-register/open', data),
  close: (data) => api.post('/api/cash-register/close', data),
  registerShrinkage: (data) => api.post('/api/cash-register/shrinkage', data),
};

// ========== DASHBOARD ==========
export const dashboardAPI = {
  getData: async () => {
    const [productsStats, customersStats, salesStats, todaySales] = await Promise.all([
      api.get('/api/products'),
      customersAPI.getStats(),
      salesAPI.getStats(),
      salesAPI.getToday(),
    ]);
    
    return {
      products: productsStats.data,
      customers: customersStats.data,
      sales: salesStats.data,
      today: todaySales.data,
    };
  },
};

// ========== MANEJO DE ERRORES ==========
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