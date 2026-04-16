/**
 * Contexto de Autenticación
 *
 * Maneja la sesión del usuario usando localStorage.
 * El token JWT y los datos del usuario se persisten juntos,
 * evitando llamadas de red al iniciar la app (sin race conditions).
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [loading, setLoading] = useState(false);

  // Inicialización SINCRÓNICA desde localStorage — sin llamada de red al backend.
  // Esto elimina la race condition donde un token viejo en vuelo
  // podía expulsar al usuario que ya había iniciado sesión con un token nuevo.
  const [user, setUser] = useState(() => {
    try {
      const token = localStorage.getItem('token');
      const savedUser = localStorage.getItem('user');
      if (token && savedUser) {
        return JSON.parse(savedUser);
      }
    } catch {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    return null;
  });

  // Escucha el evento que dispara el interceptor de axios en caso de 401.
  // Usa un evento personalizado para evitar window.location.href (full-reload).
  useEffect(() => {
    const handleSessionExpired = () => {
      console.warn('Sesión expirada — cerrando sesión.');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
    };
    window.addEventListener('auth:sessionExpired', handleSessionExpired);
    return () => window.removeEventListener('auth:sessionExpired', handleSessionExpired);
  }, []);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const { access_token, user: userData } = response.data;

      // Guardar token Y datos del usuario en localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);

    } catch (err) {
      let errorMsg = 'Error al conectar con el servidor';
      if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err.message === 'Network Error') {
        errorMsg = 'No se puede conectar al servidor. Verifica que el backend esté corriendo.';
      }
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const value = {
    user,
    userId: user?.id,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin' || user?.role === 'ADMIN',
    login,
    logout,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
};
