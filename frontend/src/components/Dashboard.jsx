/**
 * Dashboard Principal
 * 
 * Muestra un resumen general del negocio:
 * - Ventas del día
 * - Estadísticas generales
 * - Productos con stock bajo
 * - Acceso rápido a módulos
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShoppingCart, 
  Users, 
  Package, 
  DollarSign, 
  TrendingUp,
  AlertTriangle,
  ArrowUpRight,
  ArrowRight,
  Banknote,
  CreditCard,
  Smartphone,
  PieChart,
  BarChart3,
  Clock
} from 'lucide-react';
import { dashboardAPI, productsAPI, handleAPIError } from '../services/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    today: null,
    sales: null,
    customers: null,
    products: [],
  });
  const [lowStockProducts, setLowStockProducts] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      const dashboardData = await dashboardAPI.getData();
      setData(dashboardData);
      
      const lowStock = await productsAPI.getLowStock();
      setLowStockProducts(lowStock.data);
      
    } catch (error) {
      const errorInfo = handleAPIError(error);
      console.error('Error cargando dashboard:', errorInfo);
    } finally {
      setLoading(false);
    }
  };

  const todayDate = new Date().toLocaleDateString('es-ES', { 
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#f8f7f4]">
        <div className="text-center">
          <div className="w-14 h-14 mx-auto mb-4 rounded-2xl overflow-hidden shadow-lg animate-pulse">
            <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <p className="text-gray-500 text-sm font-medium">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  const todaySales = data.today?.total_amount || 0;
  const todayTransactions = data.today?.total_sales || 0;
  const avgSale = data.sales?.average_sale || 0;
  const totalCompleted = data.sales?.completed_sales || 0;

  return (
    <div className="min-h-screen bg-[#f8f7f4] p-6 lg:p-8 overflow-auto">
      <div className="max-w-7xl mx-auto">

        {/* ===== HEADER ===== */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 font-['Poppins']">Dashboard</h1>
          <p className="text-sm text-gray-400 mt-0.5 capitalize">{todayDate}</p>
        </div>

        {/* ===== STAT CARDS ===== */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
          
          {/* Ventas de Hoy - Card destacada */}
          <div className="bg-gradient-to-br from-amber-600 to-orange-600 rounded-2xl p-5 text-white shadow-lg shadow-amber-600/20 relative overflow-hidden">
            <div className="absolute -right-4 -bottom-4 w-24 h-24 bg-white/10 rounded-full blur-xl" />
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-3">
                <p className="text-amber-100 text-xs font-semibold uppercase tracking-wider">Ventas Hoy</p>
                <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                  <DollarSign className="w-4 h-4" />
                </div>
              </div>
              <p className="text-3xl font-bold">${parseFloat(todaySales).toFixed(2)}</p>
              <p className="text-amber-200 text-xs mt-1">{todayTransactions} transacciones</p>
            </div>
          </div>

          {/* Productos */}
          <StatCard
            title="Productos Activos"
            value={data.products?.length || 0}
            subtitle={`${lowStockProducts.length} con stock bajo`}
            icon={<Package className="w-4 h-4" />}
            accentColor="bg-blue-500"
            subtitleColor={lowStockProducts.length > 0 ? "text-amber-600" : "text-gray-400"}
          />

          {/* Promedio por Venta */}
          <StatCard
            title="Promedio x Venta"
            value={`$${parseFloat(avgSale).toFixed(2)}`}
            subtitle={`${totalCompleted} ventas completadas`}
            icon={<BarChart3 className="w-4 h-4" />}
            accentColor="bg-emerald-500"
          />

          {/* Clientes */}
          <StatCard
            title="Clientes"
            value={data.customers?.total || 0}
            subtitle={`${data.customers?.active || 0} activos`}
            icon={<Users className="w-4 h-4" />}
            accentColor="bg-violet-500"
          />
        </div>

        {/* ===== SEGUNDA FILA ===== */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
          
          {/* Ventas por Método de Pago */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-sm font-bold text-gray-900 font-['Poppins']">Ventas por Método de Pago</h2>
              <span className="text-xs text-gray-400">Hoy</span>
            </div>
            <div className="space-y-4">
              <PaymentMethodRow
                method="Efectivo"
                icon={<Banknote className="w-4 h-4 text-emerald-500" />}
                amount={data.today?.cash_sales || 0}
                total={data.today?.total_amount || 1}
                barColor="bg-emerald-500"
              />
              <PaymentMethodRow
                method="Tarjeta"
                icon={<CreditCard className="w-4 h-4 text-blue-500" />}
                amount={data.today?.card_sales || 0}
                total={data.today?.total_amount || 1}
                barColor="bg-blue-500"
              />
              <PaymentMethodRow
                method="Transferencia"
                icon={<Smartphone className="w-4 h-4 text-violet-500" />}
                amount={data.today?.transfer_sales || 0}
                total={data.today?.total_amount || 1}
                barColor="bg-violet-500"
              />
            </div>
          </div>

          {/* Productos con Stock Bajo */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold text-gray-900 flex items-center gap-2 font-['Poppins']">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                Stock Bajo
              </h2>
              <span className="text-[10px] font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
                {lowStockProducts.length}
              </span>
            </div>
            <div className="space-y-1 max-h-52 overflow-y-auto">
              {lowStockProducts.length === 0 ? (
                <div className="text-center py-8 text-gray-300">
                  <CheckMark />
                  <p className="text-xs mt-2 text-gray-400">Todo en orden</p>
                </div>
              ) : (
                lowStockProducts.map((product) => (
                  <div
                    key={product.id}
                    className="flex justify-between items-center py-2.5 px-3 rounded-xl hover:bg-gray-50 transition-colors"
                  >
                    <div className="min-w-0">
                      <p className="font-semibold text-sm text-gray-800 truncate">{product.name}</p>
                      <p className="text-[10px] text-gray-400 font-mono">{product.code}</p>
                    </div>
                    <div className="text-right flex-shrink-0 ml-3">
                      <p className="text-sm font-bold text-red-600">
                        {product.stock_quantity}
                      </p>
                      <p className="text-[10px] text-gray-400">
                        mín: {product.min_stock}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* ===== ACCESO RÁPIDO ===== */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <h2 className="text-sm font-bold text-gray-900 mb-4 font-['Poppins']">Acceso Rápido</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <QuickAccessButton
              icon={<ShoppingCart className="w-5 h-5" />}
              text="Punto de Venta"
              desc="Abrir POS"
              color="from-amber-500 to-orange-500"
              onClick={() => navigate('/pos')}
            />
            <QuickAccessButton
              icon={<Package className="w-5 h-5" />}
              text="Productos"
              desc="Gestionar inventario"
              color="from-blue-500 to-cyan-500"
              onClick={() => navigate('/productos')}
            />
            <QuickAccessButton
              icon={<Users className="w-5 h-5" />}
              text="Clientes"
              desc="Base de datos"
              color="from-violet-500 to-purple-500"
              onClick={() => navigate('/clientes')}
            />
            <QuickAccessButton
              icon={<PieChart className="w-5 h-5" />}
              text="Reportes"
              desc="Exportar a Excel"
              color="from-emerald-500 to-teal-500"
              onClick={() => navigate('/reportes')}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

// ========== SUB-COMPONENTES ==========

const CheckMark = () => (
  <div className="w-10 h-10 mx-auto rounded-full bg-emerald-50 flex items-center justify-center">
    <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  </div>
);

const StatCard = ({ title, value, subtitle, icon, accentColor, subtitleColor = "text-gray-400" }) => (
  <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 hover:shadow-md transition-shadow">
    <div className="flex items-center justify-between mb-3">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">{title}</p>
      <div className={`w-8 h-8 ${accentColor} rounded-lg flex items-center justify-center text-white shadow-sm`}>
        {icon}
      </div>
    </div>
    <p className="text-2xl font-bold text-gray-900">{value}</p>
    <p className={`text-xs mt-1 font-medium ${subtitleColor}`}>{subtitle}</p>
  </div>
);

const PaymentMethodRow = ({ method, icon, amount, total, barColor }) => {
  const percentage = total > 0 ? (amount / total) * 100 : 0;
  
  return (
    <div className="flex items-center gap-4">
      <div className="w-8 h-8 bg-gray-50 rounded-lg flex items-center justify-center flex-shrink-0">
        {icon}
      </div>
      <div className="flex-1">
        <div className="flex justify-between mb-1.5">
          <span className="text-sm font-semibold text-gray-700">{method}</span>
          <span className="text-sm font-bold text-gray-900">${parseFloat(amount).toFixed(2)}</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-1.5">
          <div
            className={`${barColor} h-1.5 rounded-full transition-all duration-500 ease-out`}
            style={{ width: `${Math.max(percentage, 1)}%` }}
          />
        </div>
      </div>
    </div>
  );
};

const QuickAccessButton = ({ icon, text, desc, color, onClick }) => (
  <button
    onClick={onClick}
    className="group relative bg-gray-50 hover:bg-gray-100 border border-gray-100 hover:border-gray-200 rounded-2xl p-4 text-left transition-all duration-200 hover:-translate-y-0.5 overflow-hidden"
  >
    <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${color} text-white flex items-center justify-center shadow-sm mb-3 transition-transform group-hover:scale-110`}>
      {icon}
    </div>
    <p className="text-sm font-bold text-gray-800">{text}</p>
    <p className="text-[11px] text-gray-400 mt-0.5">{desc}</p>
    <ArrowRight className="absolute top-4 right-4 w-4 h-4 text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity" />
  </button>
);

export default Dashboard;
