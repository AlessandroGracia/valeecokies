/**
 * Servicio de API para comunicarse con el backend FastAPI
 * 
 * Centraliza TODAS las llamadas HTTP al backend.
 * Todos los componentes DEBEN usar estos métodos en vez de fetch/axios directo.
 */

import axios from 'axios';

// URL base del backend
// En producción, buscamos la IP guardada en localStorage.
// Si no existe, usamos localhost por defecto.
const getBackendURL = () => {
  // En producción (Web), usamos la URL configurada en las variables de entorno
  if (import.meta.env.PROD && import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  const savedIP = localStorage.getItem('backend_url');
  if (savedIP) return savedIP;
  
  // En desarrollo (Vite), usamos el proxy vacío.
  if (import.meta.env.DEV) return '';
  
  // Por defecto, asumimos backend local.
  return 'http://127.0.0.1:8000';
};

const API_BASE_URL = getBackendURL();

// Instancia de axios configurada
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 segundos timeout
});

// Interceptor para agregar token de autenticación
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

// Interceptor de respuesta para manejo global de errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || '';

      // /api/auth/me lo maneja el AuthContext por su cuenta — no interferir.
      // Si lo hacemos aquí también, se produce una race condition donde un
      // token viejo en vuelo puede expulsar al usuario que YA inició sesión.
      if (url.includes('/api/auth/me')) {
        return Promise.reject(error);
      }

      console.warn('Token rechazado en:', url, '— cerrando sesión.');
      localStorage.removeItem('token');
      // Disparar evento personalizado en lugar de window.location.href
      // Así React maneja el logout sin hacer un full-reload que rompe el estado.
      window.dispatchEvent(new CustomEvent('auth:sessionExpired'));
    } else if (error.message === 'Network Error') {
      console.error('ERROR CRÍTICO DE RED:', 
        '\n- URL intentada:', error.config?.url,
        '\n- Origen actual:', window.location.href,
        '\n- Causa probable: El backend no está corriendo en 127.0.0.1:8000 o el Firewall bloquea el puerto.'
      );
    }
    return Promise.reject(error);
  }
);

// ========== PRODUCTOS ==========

export const productsAPI = {
  // Listar todos
  getAll: (params = {}) => api.get('/api/products', { params }),
  
  // Obtener uno
  getById: (id) => api.get(`/api/products/${id}`),
  
  // Crear
  create: (data) => api.post('/api/products', data),
  
  // Actualizar
  update: (id, data) => api.put(`/api/products/${id}`, data),
  
  // Eliminar
  delete: (id) => api.delete(`/api/products/${id}`),
  
  // Stock bajo
  getLowStock: () => api.get('/api/products/low-stock'),
  
  // Ajustar stock
  adjustStock: (id, adjustment) => api.patch(`/api/products/${id}/stock`, adjustment),
};

// ========== CLIENTES ==========

export const customersAPI = {
  // Listar todos
  getAll: (params = {}) => api.get('/api/customers', { params }),
  
  // Obtener uno
  getById: (id) => api.get(`/api/customers/${id}`),
  
  // Crear
  create: (data) => api.post('/api/customers', data),
  
  // Actualizar
  update: (id, data) => api.put(`/api/customers/${id}`, data),
  
  // Eliminar
  delete: (id) => api.delete(`/api/customers/${id}`),
  
  // Resumen (para dropdowns)
  getSummary: () => api.get('/api/customers/summary'),
  
  // Estadísticas
  getStats: () => api.get('/api/customers/stats'),
};

// ========== VENTAS ==========

export const salesAPI = {
  // Listar todas
  getAll: (params = {}) => api.get('/api/sales', { params }),
  
  // Obtener una
  getById: (id) => api.get(`/api/sales/${id}`),
  
  // Crear venta
  create: (data) => api.post('/api/sales', data),
  
  // Anular venta
  cancel: (id) => api.post(`/api/sales/${id}/cancel`),
  
  // Estadísticas
  getStats: (params = {}) => api.get('/api/sales/stats', { params }),
  
  // Ventas de hoy
  getToday: () => api.get('/api/sales/today'),
  
  // Ventas por fecha
  getByDate: (date) => api.get('/api/sales/daily', { params: { target_date: date } }),
};

// ========== PUNTO DE VENTA (POS) ==========

export const posAPI = {
  // Crear venta POS con cálculo de vuelto
  createSale: (data) => api.post('/api/pos/sale', data),
  
  // Calcular vuelto antes de confirmar
  calculateChange: (total, paymentReceived) => 
    api.post('/api/pos/calculate-change', null, {
      params: { total, payment_received: paymentReceived }
    }),
};

// ========== CAJA DIARIA ==========

export const cashRegisterAPI = {
  // Obtener estado de la caja (abierta/cerrada)
  getStatus: () => api.get('/api/cash-register/status'),
  
  // Obtener caja de hoy
  getToday: () => api.get('/api/cash-register/today'),
  
  // Obtener resumen completo de caja
  getSummary: () => api.get('/api/cash-register/summary'),
  
  // Abrir caja
  open: (data) => api.post('/api/cash-register/open', data),
  
  // Cerrar caja
  close: (data) => api.post('/api/cash-register/close', data),
  
  // Registrar merma
  registerShrinkage: (data) => api.post('/api/cash-register/shrinkage', data),
};

// ========== DASHBOARD ==========

export const dashboardAPI = {
  // Obtener datos del dashboard
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
    // El servidor respondió con un código de error
    return {
      message: error.response.data.detail || 'Error en el servidor',
      status: error.response.status,
      data: error.response.data,
    };
  } else if (error.request) {
    // La petición se hizo pero no hubo respuesta
    return {
      message: 'No se pudo conectar con el servidor. Verifica que el backend esté corriendo.',
      status: 0,
    };
  } else {
    // Algo pasó al configurar la petición
    return {
      message: error.message,
      status: -1,
    };
  }
};

export default api;