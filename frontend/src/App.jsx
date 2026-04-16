/**
 * Componente principal de la aplicación
 * 
 * Maneja las rutas y navegación entre componentes
 * usando React Router para URLs reales y deep linking.
 */

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ShoppingCart, 
  Package, 
  Users, 
  CreditCard,
  LogOut,
  PieChart,
  Menu as MenuIcon,
  X as XIcon
} from 'lucide-react';

// Contexto
import { useAuth } from './context/AuthContext';

// Componentes
import Dashboard from './components/Dashboard';
import POS from './components/POS';
import CashRegister from './components/CashRegister';
import Products from './components/Products';
import Reports from './components/Reports';
import Customers from './components/Customers';

// Componente temporal "Próximamente"
const ComingSoon = ({ title }) => (
  <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
    <div className="text-center">
      <div className="text-6xl mb-4">🚧</div>
      <h2 className="text-3xl font-bold text-gray-800 mb-2">{title}</h2>
      <p className="text-gray-600">Esta sección está en desarrollo</p>
    </div>
  </div>
);

// Componente de item de menú con NavLink
const MenuItem = ({ icon, label, to }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      `group w-full flex items-center gap-3 px-4 py-3 rounded-xl mb-1 transition-all duration-200 ${
        isActive
          ? 'bg-white/15 shadow-lg shadow-black/10 text-white font-semibold'
          : 'text-amber-200/70 hover:bg-white/10 hover:text-white'
      }`
    }
  >
    {({ isActive }) => (
      <>
        <div className={`w-5 h-5 transition-transform duration-200 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`}>{icon}</div>
        <span className="text-sm">{label}</span>
        {isActive && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />}
      </>
    )}
  </NavLink>
);

// Componente de navegación lateral
const Sidebar = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  // Cerrar sidebar al navegar (en móvil)
  React.useEffect(() => {
    if (isOpen) onClose();
  }, [location.pathname]);
  
  return (
    <div className={`
      fixed inset-y-0 left-0 z-50 w-64 bg-gradient-to-b from-[#3d1c00] via-[#4a2200] to-[#2d1500] text-white flex flex-col shadow-2xl transition-transform duration-300 transform
      lg:static lg:translate-x-0 ${isOpen ? 'translate-x-0' : '-translate-x-full'}
    `}>
      {/* Logo */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl overflow-hidden shadow-lg ring-2 ring-white/20 flex-shrink-0 hover:ring-amber-400/50 transition-all duration-300 flex items-center justify-center">
            <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <div>
            <h1 className="text-lg font-bold font-['Poppins'] tracking-tight">Valeecokies</h1>
            <p className="text-[11px] text-amber-400/80 font-medium tracking-wider uppercase">Sistema POS</p>
          </div>
        </div>
      </div>

      {/* Menú de navegación */}
      <nav className="flex-1 p-3 overflow-y-auto">
        <p className="text-[10px] text-amber-300/40 font-semibold uppercase tracking-widest px-4 mb-2 mt-2">Operaciones</p>
        <MenuItem icon={<ShoppingCart />} label="Punto de Venta" to="/pos" />
        <MenuItem icon={<CreditCard />} label="Abrir/Cerrar Caja" to="/caja" />
        
        <p className="text-[10px] text-amber-300/40 font-semibold uppercase tracking-widest px-4 mb-2 mt-5">Gestión</p>
        <MenuItem icon={<LayoutDashboard />} label="Dashboard" to="/dashboard" />
        <MenuItem icon={<Package />} label="Productos" to="/productos" />
        <MenuItem icon={<Users />} label="Clientes" to="/clientes" />
        <MenuItem icon={<PieChart />} label="Reportes" to="/reportes" />
      </nav>

      {/* Usuario y configuración */}
      <div className="p-4 border-t border-white/10 bg-black/10">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-amber-700 rounded-full flex items-center justify-center font-bold overflow-hidden ring-2 ring-amber-500/30 relative text-sm shadow-inner shrink-0 text-amber-100">
             {user?.full_name?.charAt(0) || 'U'}
             <img 
               src={user?.username ? `/${user.username}.png` : '/vendedor1.png'} 
               alt={user?.full_name} 
               className="w-full h-full object-cover absolute inset-0 z-10" 
               onError={(e) => { e.target.style.display = 'none'; }} 
             />
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-sm truncate">{user?.full_name || 'Usuario'}</p>
            <p className="text-[11px] text-amber-400/70 capitalize">{user?.role || 'vendedor'}</p>
          </div>
        </div>
        <button 
          onClick={logout}
          className="w-full bg-white/10 hover:bg-red-600/80 rounded-lg py-2 text-sm flex items-center justify-center gap-2 transition-all duration-300 text-amber-200 hover:text-white"
        >
          <LogOut className="w-4 h-4" />
          Cerrar Sesión
        </button>
      </div>
    </div>
  );
};

import Login from './components/Login';

function AppContent() {
  const { isAuthenticated } = useAuth();
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  // Título dinámico basado en la ruta
  const getPageTitle = () => {
    const path = location.pathname;
    if (path === '/pos') return 'Punto de Venta';
    if (path === '/caja') return 'Caja Diaria';
    if (path === '/dashboard') return 'Dashboard';
    if (path === '/productos') return 'Inventario';
    if (path === '/clientes') return 'Clientes';
    if (path === '/reportes') return 'Reportes';
    return 'Valeecokies';
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Overlay para móvil */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden backdrop-blur-sm"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <Sidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header móvil */}
        <header className="lg:hidden h-16 bg-[#3d1c00] text-white flex items-center justify-between px-4 shrink-0 shadow-md z-30">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setSidebarOpen(true)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
            >
              <MenuIcon className="w-6 h-6" />
            </button>
            <h1 className="font-bold text-lg truncate">{getPageTitle()}</h1>
          </div>
          <div className="w-10 h-10 bg-amber-700 rounded-xl flex items-center justify-center font-bold overflow-hidden ring-2 ring-amber-500/30 shadow-inner">
             <img 
               src={useAuth().user?.username ? `/${useAuth().user.username}.png` : '/vendedor1.png'} 
               alt="User" 
               className="w-full h-full object-cover" 
               onError={(e) => { e.target.style.display = 'none'; }} 
             />
          </div>
        </header>

        <div className="flex-1 overflow-auto relative">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/pos" element={<POS />} />
            <Route path="/caja" element={<CashRegister />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/productos" element={<Products />} />
            <Route path="/reportes" element={<Reports />} />
            <Route path="/clientes" element={<Customers />} />
            {/* Si intenta ir a login estando logueado, lo mandamos al dashboard */}
            <Route path="/login" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;
