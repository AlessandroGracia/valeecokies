/**
 * Componente de Apertura y Cierre de Caja
 * 
 * Maneja:
 * - Apertura de caja con inventario inicial
 * - Cierre de caja con cuadre
 * - Registro de mermas
 */

import React, { useState, useEffect } from 'react';
import { 
  DollarSign, 
  Package, 
  CheckCircle,
  Lock,
  Unlock,
  Banknote,
  FileText
} from 'lucide-react';
import { productsAPI, cashRegisterAPI, handleAPIError } from '../services/api';

const CashRegister = () => {
  const [cashStatus, setCashStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  const [processing, setProcessing] = useState(false);
  
  // Estados para apertura
  const [openingData, setOpeningData] = useState({
    initial_cash: '',
    inventory_items: []
  });
  
  // Estados para cierre
  const [closingData, setClosingData] = useState({
    actual_cash: '',
    closing_notes: ''
  });

  useEffect(() => {
    loadCashStatus();
    loadProducts();
  }, []);

  const loadCashStatus = async () => {
    try {
      const response = await cashRegisterAPI.getStatus();
      setCashStatus(response.data);
      
      if (response.data.is_open) {
        loadCashSummary();
      }
    } catch (error) {
      const errorInfo = handleAPIError(error);
      console.error('Error cargando estado de caja:', errorInfo);
    } finally {
      setLoading(false);
    }
  };

  const loadProducts = async () => {
    try {
      const response = await productsAPI.getAll({ is_active: true });
      setProducts(response.data);
      
      // Inicializar inventory_items con todos los productos
      setOpeningData(prev => ({
        ...prev,
        inventory_items: response.data.map(p => ({
          product_id: p.id,
          product_name: p.name,
          initial_stock: 0
        }))
      }));
    } catch (error) {
      const errorInfo = handleAPIError(error);
      console.error('Error cargando productos:', errorInfo);
    }
  };

  const loadCashSummary = async () => {
    try {
      const response = await cashRegisterAPI.getSummary();
      console.log('Resumen de caja:', response.data);
    } catch (error) {
      const errorInfo = handleAPIError(error);
      console.error('Error cargando resumen:', errorInfo);
    }
  };

  const handleOpenCash = async () => {
    if (!openingData.initial_cash) {
      alert('Ingresa el efectivo inicial');
      return;
    }

    // Validar que al menos un producto tenga stock
    const hasStock = openingData.inventory_items.some(item => item.initial_stock > 0);
    if (!hasStock) {
      alert('Debes declarar el inventario inicial de al menos un producto');
      return;
    }

    try {
      setProcessing(true);
      
      await cashRegisterAPI.open({
        initial_cash: parseFloat(openingData.initial_cash),
        inventory_items: openingData.inventory_items
          .filter(item => item.initial_stock > 0)
          .map(item => ({
            product_id: item.product_id,
            initial_stock: item.initial_stock
          }))
      });

      alert('✅ ¡Caja abierta exitosamente!');
      loadCashStatus();
      
    } catch (error) {
      const errorInfo = handleAPIError(error);
      alert(errorInfo.message);
    } finally {
      setProcessing(false);
    }
  };

  const handleCloseCash = async () => {
    if (!closingData.actual_cash) {
      alert('Ingresa el efectivo real contado');
      return;
    }

    try {
      setProcessing(true);
      
      const response = await cashRegisterAPI.close({
        actual_cash: parseFloat(closingData.actual_cash),
        closing_notes: closingData.closing_notes
      });

      const data = response.data;
      const difference = data.cash_difference;
      
      let message = '✅ ¡Caja cerrada exitosamente!\n\n';
      message += `Efectivo esperado: $${data.expected_cash}\n`;
      message += `Efectivo real: $${data.actual_cash}\n`;
      message += `Diferencia: $${Math.abs(difference).toFixed(2)}`;
      
      if (difference > 0) {
        message += ' (SOBRANTE ✓)';
      } else if (difference < 0) {
        message += ' (FALTANTE ⚠️)';
      }
      
      alert(message);
      loadCashStatus();
      setClosingData({ actual_cash: '', closing_notes: '' });
      
    } catch (error) {
      const errorInfo = handleAPIError(error);
      alert(errorInfo.message);
    } finally {
      setProcessing(false);
    }
  };

  const updateInventoryStock = (productId, value) => {
    setOpeningData(prev => ({
      ...prev,
      inventory_items: prev.inventory_items.map(item =>
        item.product_id === productId
          ? { ...item, initial_stock: parseInt(value) || 0 }
          : item
      )
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#f8f7f4]">
        <div className="text-center">
          <div className="w-14 h-14 mx-auto mb-4 rounded-2xl overflow-hidden shadow-lg animate-pulse">
             <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <p className="text-gray-500 text-sm font-medium">Cargando estado de caja...</p>
        </div>
      </div>
    );
  }

  // Pantalla de Apertura de Caja
  if (!cashStatus?.is_open) {
    return (
      <div className="min-h-screen bg-[#f8f7f4] flex items-center justify-center p-6 lg:p-8">
        <div className="w-full max-w-2xl">
          <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 sm:p-10 animate-scaleIn">
            <div className="text-center mb-10">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-emerald-100 to-green-100 rounded-2xl mb-5 shadow-sm">
                <Unlock className="w-8 h-8 text-emerald-600" />
              </div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2 font-['Poppins']">
                Apertura de Caja
              </h1>
              <p className="text-gray-500 text-sm">
                Inicia tu jornada declarando el efectivo base y tu inventario actual
              </p>
            </div>

            {/* Efectivo Inicial */}
            <div className="mb-8">
              <label className="flex items-center gap-2 text-xs font-bold text-gray-700 mb-2.5 uppercase tracking-wider">
                <Banknote className="w-4 h-4 text-emerald-500" /> 
                Efectivo Inicial en Caja
              </label>
              <div className="relative">
                <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-6 h-6" />
                <input
                  type="number"
                  value={openingData.initial_cash}
                  onChange={(e) => setOpeningData({...openingData, initial_cash: e.target.value})}
                  placeholder="0.00"
                  className="w-full pl-12 pr-4 py-4 text-2xl font-bold bg-gray-50 border border-gray-200 rounded-2xl focus:bg-white focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-400 outline-none transition-all text-gray-900 placeholder:text-gray-300"
                />
              </div>
            </div>

            {/* Inventario Inicial */}
            <div className="mb-10">
              <div className="flex items-center justify-between mb-2.5">
                <label className="flex items-center gap-2 text-xs font-bold text-gray-700 uppercase tracking-wider">
                  <Package className="w-4 h-4 text-emerald-500" /> 
                  Inventario Inicial del Día
                </label>
                <span className="text-xs font-semibold bg-emerald-50 text-emerald-600 px-2.5 py-1 rounded-full">
                  {openingData.inventory_items.length} ítems
                </span>
              </div>
              
              <div className="space-y-2 max-h-72 overflow-y-auto bg-gray-50/50 rounded-2xl p-2 border border-gray-100">
                {openingData.inventory_items.map(item => (
                  <div key={item.product_id} className="flex items-center justify-between bg-white rounded-xl p-3.5 shadow-sm border border-gray-100 hover:border-emerald-200 transition-colors">
                    <div className="flex-1 min-w-0 pr-4">
                      <p className="font-semibold text-sm text-gray-800 truncate">{item.product_name}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-gray-400">Cant.</span>
                      <input
                        type="number"
                        min="0"
                        value={item.initial_stock || ''}
                        onChange={(e) => updateInventoryStock(item.product_id, e.target.value)}
                        placeholder="0"
                        className="w-20 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-center font-bold text-gray-900 focus:bg-white focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-400 outline-none transition-all"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Botón Abrir Caja */}
            <button
              onClick={handleOpenCash}
              disabled={processing}
              className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed text-white font-bold py-4 rounded-2xl text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20 hover:shadow-emerald-500/30 transition-all hover:-translate-y-0.5 active:translate-y-0 uppercase tracking-wide"
            >
              {processing ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                  Procesando apertura...
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5" />
                  Abrir Caja y Comenzar Día
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Pantalla de Cierre de Caja
  return (
    <div className="min-h-screen bg-[#f8f7f4] flex items-center justify-center p-6 lg:p-8">
      <div className="w-full max-w-lg">
        <div className="bg-white rounded-3xl shadow-xl border border-gray-100 p-8 sm:p-10 animate-scaleIn">
          <div className="text-center mb-10">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-rose-100 to-red-100 rounded-2xl mb-5 shadow-sm">
              <Lock className="w-8 h-8 text-rose-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2 font-['Poppins']">
              Cierre de Caja
            </h1>
            <p className="text-gray-500 text-sm">
              Realiza el cuadre final e ingresa cualquier novedad del día
            </p>
          </div>

          {/* Efectivo Real Contado */}
          <div className="mb-8">
            <label className="flex items-center gap-2 text-xs font-bold text-gray-700 mb-2.5 uppercase tracking-wider">
              <Banknote className="w-4 h-4 text-rose-500" /> 
              Efectivo Real Contado
            </label>
            <div className="relative">
              <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-6 h-6" />
              <input
                type="number"
                value={closingData.actual_cash}
                onChange={(e) => setClosingData({...closingData, actual_cash: e.target.value})}
                placeholder="0.00"
                className="w-full pl-12 pr-4 py-4 text-2xl font-bold bg-gray-50 border border-gray-200 rounded-2xl focus:bg-white focus:ring-4 focus:ring-rose-500/10 focus:border-rose-400 outline-none transition-all text-gray-900 placeholder:text-gray-300"
              />
            </div>
          </div>

          {/* Notas del Cierre */}
          <div className="mb-10">
            <label className="flex items-center gap-2 text-xs font-bold text-gray-700 mb-2.5 uppercase tracking-wider">
              <FileText className="w-4 h-4 text-rose-500" />
              Notas del Cierre (Opcional)
            </label>
            <textarea
              value={closingData.closing_notes}
              onChange={(e) => setClosingData({...closingData, closing_notes: e.target.value})}
              placeholder="Ej: Todo en orden, ingreso extra por..."
              rows="3"
              className="w-full px-4 py-3.5 bg-gray-50 border border-gray-200 rounded-2xl text-sm focus:bg-white focus:ring-4 focus:ring-rose-500/10 focus:border-rose-400 outline-none transition-all resize-none text-gray-800 placeholder:text-gray-400"
            />
          </div>

          {/* Botón Cerrar Caja */}
          <button
            onClick={handleCloseCash}
            disabled={processing}
            className="w-full bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed text-white font-bold py-4 rounded-2xl text-sm flex items-center justify-center gap-2 shadow-lg shadow-rose-600/20 hover:shadow-rose-600/30 transition-all hover:-translate-y-0.5 active:translate-y-0 uppercase tracking-wide"
          >
            {processing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
                Cerrando caja...
              </>
            ) : (
              <>
                <Lock className="w-5 h-5" />
                Cerrar Caja y Finalizar Día
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default CashRegister;
