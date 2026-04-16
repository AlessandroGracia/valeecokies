/**
 * Componente POS (Punto de Venta)
 * 
 * Interfaz completa para realizar ventas con:
 * - Grid de productos
 * - Carrito de compra
 * - Calculadora de efectivo
 * - Cálculo de vuelto
 * - Resumen de caja
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ShoppingCart,
  Trash2,
  Plus,
  Minus,
  Package,
  CheckCircle,
  Clock,
  Banknote,
  CreditCard,
  Smartphone,
  Receipt,
  Printer,
  X
} from 'lucide-react';
import { productsAPI, posAPI, cashRegisterAPI, handleAPIError } from '../services/api';

const POS = () => {
  // Estados
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [cashRegisterOpen, setCashRegisterOpen] = useState(false);
  const [cashSummary, setCashSummary] = useState(null);

  // Estados para el pago
  const [paymentReceived, setPaymentReceived] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('efectivo');

  // Estado para la factura (ticket)
  const [showReceipt, setShowReceipt] = useState(false);
  const [lastSaleData, setLastSaleData] = useState(null);

  // Cargar datos iniciales
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);

      const [productsRes, cashStatusRes] = await Promise.all([
        productsAPI.getAll({ is_active: true }),
        cashRegisterAPI.getStatus().catch(() => ({ data: { is_open: false } })),
      ]);

      setProducts(productsRes.data);
      setCashRegisterOpen(cashStatusRes.data.is_open);

      if (cashStatusRes.data.is_open) {
        try {
          const summaryRes = await cashRegisterAPI.getSummary();
          setCashSummary(summaryRes.data);

          const dailyInventoryList = summaryRes.data.inventory_details || [];
          const dailyStockMap = {};

          dailyInventoryList.forEach(item => {
            dailyStockMap[item.product_id] = item.current_stock;
          });

          setProducts(productsRes.data.map(p => ({
            ...p,
            stock_quantity: dailyStockMap[p.id] !== undefined ? dailyStockMap[p.id] : 0,
            in_daily_inventory: dailyStockMap[p.id] !== undefined
          })));

        } catch (e) {
          console.warn('No se pudo cargar resumen de caja:', e);
        }
      } else {
        setProducts(productsRes.data);
      }

    } catch (error) {
      const errorInfo = handleAPIError(error);
      console.error('Error cargando datos:', errorInfo);
    } finally {
      setLoading(false);
    }
  };

  // Agregar producto al carrito
  const addToCart = (product) => {
    const existingItem = cart.find(item => item.product_id === product.id);

    if (existingItem) {
      if (existingItem.quantity < product.stock_quantity) {
        setCart(cart.map(item =>
          item.product_id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        ));
      } else {
        alert(`Stock insuficiente. Disponible: ${product.stock_quantity}`);
      }
    } else {
      if (product.stock_quantity > 0) {
        setCart([...cart, {
          product_id: product.id,
          product_name: product.name,
          unit_price: parseFloat(product.sale_price),
          quantity: 1,
          stock_available: product.stock_quantity
        }]);
      } else {
        alert('Producto sin stock');
      }
    }
  };

  const removeFromCart = (productId) => {
    const item = cart.find(i => i.product_id === productId);
    if (item.quantity > 1) {
      setCart(cart.map(i =>
        i.product_id === productId
          ? { ...i, quantity: i.quantity - 1 }
          : i
      ));
    } else {
      setCart(cart.filter(i => i.product_id !== productId));
    }
  };

  const deleteFromCart = (productId) => {
    setCart(cart.filter(i => i.product_id !== productId));
  };

  const calculateTotal = () => {
    return cart.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
  };

  const calculateChange = () => {
    const total = calculateTotal();
    const received = parseFloat(paymentReceived) || 0;
    return received - total;
  };

  const processSale = async () => {
    const total = calculateTotal();
    const received = parseFloat(paymentReceived) || 0;

    if (received < total) {
      alert('El pago recibido es menor al total');
      return;
    }

    if (cart.length === 0) {
      alert('El carrito está vacío');
      return;
    }

    try {
      setProcessing(true);

      const saleData = {
        items: cart.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity
        })),
        payment_method: paymentMethod,
        payment_received: received,
        notes: "Venta desde POS"
      };

      const response = await posAPI.createSale(saleData);
      const result = response.data;
      // En vez de un alert sencillo, mostramos el ticket de la factura
      setLastSaleData({
        invoice_number: result.invoice_number,
        total: total,
        received: received,
        change: result.change,
        items: [...cart], // guardamos copia del carrito
        date: new Date().toLocaleString(),
        payment_method: paymentMethod
      });

      setShowReceipt(true);

      setCart([]);
      setPaymentReceived('');
      loadInitialData();

    } catch (error) {
      const errorInfo = handleAPIError(error);
      alert(errorInfo.message);
    } finally {
      setProcessing(false);
    }
  };

  // Categorías
  const categories = [
    { id: 'all', name: 'Todos', icon: '🏪' },
    { id: 'cookies', name: 'Cookies', icon: '🍪' },
    { id: 'postres', name: 'Postres', icon: '🍰' },
    { id: 'bebidas', name: 'Bebidas', icon: '🥤' },
  ];

  const paymentMethods = [
    { id: 'efectivo', label: 'Efectivo', icon: <Banknote className="w-4 h-4" /> },
    { id: 'tarjeta', label: 'Tarjeta', icon: <CreditCard className="w-4 h-4" /> },
    { id: 'transferencia', label: 'Transfer', icon: <Smartphone className="w-4 h-4" /> },
    { id: 'credito', label: 'Crédito', icon: <Receipt className="w-4 h-4" /> },
  ];

  const total = calculateTotal();
  const change = calculateChange();
  const totalItemsInCart = cart.reduce((sum, item) => sum + item.quantity, 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#f8f7f4]">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl overflow-hidden shadow-lg animate-pulse">
            <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <p className="text-amber-800 font-semibold text-sm">Cargando Punto de Venta...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#e8e4dc] relative">

      {/* Overlay si la caja está cerrada */}
      {!cashRegisterOpen && !loading && (
        <div className="absolute inset-0 z-50 bg-black/60 backdrop-blur-md flex items-center justify-center">
          <div className="bg-white p-10 rounded-3xl shadow-2xl max-w-md text-center animate-scaleIn">
            <div className="w-20 h-20 bg-red-50 text-red-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-inner">
              <span className="text-4xl">🔒</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3 font-['Poppins']">Caja Cerrada</h2>
            <p className="text-gray-500 mb-8 text-sm leading-relaxed">
              Debes realizar la apertura de caja e ingresar el inventario inicial antes de poder procesar ventas.
            </p>
            <Link
              to="/caja"
              className="block w-full bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-bold py-3.5 rounded-xl text-sm shadow-lg hover:shadow-xl transition-all hover:-translate-y-0.5"
            >
              Ir a Abrir Caja →
            </Link>
          </div>
        </div>
      )}

      {/* ===== SIDEBAR CATEGORÍAS ===== */}
      <div className="w-[88px] bg-white border-r border-gray-200 flex flex-col items-center py-5 gap-1 shadow-md">
        <div className="w-12 h-12 rounded-xl overflow-hidden shadow-md mb-5 ring-2 ring-amber-100">
          <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
        </div>

        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`w-[68px] flex flex-col items-center gap-1 py-3 rounded-xl transition-all duration-200 ${selectedCategory === cat.id
                ? 'bg-amber-50 text-amber-700 shadow-sm ring-1 ring-amber-200'
                : 'text-gray-400 hover:bg-gray-50 hover:text-gray-600'
              }`}
          >
            <span className="text-2xl">{cat.icon}</span>
            <span className="text-[10px] font-semibold tracking-wide">{cat.name}</span>
          </button>
        ))}

        <div className="mt-auto">
          <Link to="/caja" className="w-[68px] flex flex-col items-center gap-1 py-3 rounded-xl text-gray-400 hover:bg-red-50 hover:text-red-500 transition-all">
            <Clock className="w-5 h-5" />
            <span className="text-[10px] font-semibold">Caja</span>
          </Link>
        </div>
      </div>

      {/* ===== GRID DE PRODUCTOS ===== */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header del grid */}
        <div className="px-6 pt-5 pb-3 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900 font-['Poppins']">Punto de Venta</h1>
            <p className="text-xs text-gray-400 mt-0.5">
              {products.filter(p => selectedCategory === 'all' || p.category === selectedCategory).length} productos disponibles
            </p>
          </div>
          {cashSummary && (
            <div className="flex items-center gap-4 text-xs">
              <div className="bg-white px-3 py-1.5 rounded-lg shadow-sm border border-gray-100">
                <span className="text-gray-400">Ventas turno: </span>
                <span className="font-bold text-gray-800">${parseFloat(cashSummary.total_sales_amount || 0).toFixed(2)}</span>
              </div>
              <div className="bg-white px-3 py-1.5 rounded-lg shadow-sm border border-gray-100">
                <span className="text-gray-400">Stock: </span>
                <span className="font-bold text-gray-800">{cashSummary.total_current_stock || 0}</span>
              </div>
            </div>
          )}
        </div>

        {/* Productos */}
        <div className="flex-1 px-6 pb-4 overflow-y-auto">
          <div className="grid grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-3">
            {products
              .filter(product => selectedCategory === 'all' || product.category === selectedCategory)
              .map(product => {
                const isOutOfStock = product.stock_quantity <= 0;
                const isLowStock = product.stock_quantity > 0 && product.stock_quantity <= product.min_stock;
                const categoryGradient = product.category === 'bebidas'
                  ? 'from-sky-50 to-cyan-50'
                  : product.category === 'postres'
                    ? 'from-rose-50 to-pink-50'
                    : 'from-amber-50 to-orange-50';
                const categoryEmoji = product.category === 'bebidas' ? '🥤' : product.category === 'postres' ? '🍰' : '🍪';
                const cartItem = cart.find(i => i.product_id === product.id);

                return (
                  <button
                    key={product.id}
                    onClick={() => addToCart(product)}
                    disabled={isOutOfStock}
                    className={`group relative bg-white rounded-2xl border transition-all duration-200 text-left overflow-hidden shadow-md ${isOutOfStock
                        ? 'opacity-40 cursor-not-allowed border-gray-300'
                        : 'border-gray-200 hover:border-amber-400 hover:shadow-xl hover:-translate-y-1 active:translate-y-0 active:shadow-lg cursor-pointer'
                      }`}
                  >
                    {/* Badge si está en el carrito */}
                    {cartItem && (
                      <div className="absolute top-2 right-2 z-10 w-6 h-6 bg-amber-600 text-white rounded-full flex items-center justify-center text-xs font-bold shadow-md animate-scaleIn">
                        {cartItem.quantity}
                      </div>
                    )}

                    {/* Visual del producto */}
                    <div className={`h-24 flex items-center justify-center bg-gradient-to-br ${categoryGradient} relative`}>
                      <span className="text-5xl transition-transform duration-300 group-hover:scale-110 group-active:scale-95">{categoryEmoji}</span>
                      {isOutOfStock && (
                        <div className="absolute inset-0 bg-white/60 backdrop-blur-sm flex items-center justify-center">
                          <span className="bg-gray-800 text-white text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider">Agotado</span>
                        </div>
                      )}
                      {isLowStock && !isOutOfStock && (
                        <div className="absolute top-1.5 left-1.5">
                          <span className="bg-amber-500 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-md">Bajo</span>
                        </div>
                      )}
                    </div>

                    {/* Info */}
                    <div className="p-3">
                      <h3 className="font-semibold text-gray-800 text-sm leading-tight mb-1.5 truncate">
                        {product.name}
                      </h3>
                      <div className="flex items-end justify-between">
                        <p className="text-lg font-bold text-amber-700">
                          ${parseFloat(product.sale_price).toFixed(2)}
                        </p>
                        <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded ${isOutOfStock ? 'bg-gray-100 text-gray-400'
                            : isLowStock ? 'bg-amber-100 text-amber-700'
                              : 'bg-gray-100 text-gray-500'
                          }`}>
                          {product.stock_quantity} uds
                        </span>
                      </div>
                    </div>
                  </button>
                );
              })}
          </div>
        </div>
      </div>

      {/* ===== PANEL DERECHO: CARRITO ===== */}
      <div className="w-[380px] bg-white border-l border-gray-200 flex flex-col shadow-xl">

        {/* Header del carrito */}
        <div className="px-5 pt-5 pb-3 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-gray-900 flex items-center gap-2 font-['Poppins']">
              <ShoppingCart className="w-5 h-5 text-amber-600" />
              Venta Actual
            </h2>
            {totalItemsInCart > 0 && (
              <span className="bg-amber-100 text-amber-700 text-xs font-bold px-2.5 py-1 rounded-full">
                {totalItemsInCart} {totalItemsInCart === 1 ? 'item' : 'items'}
              </span>
            )}
          </div>
        </div>

        {/* Items del carrito - scrollable */}
        <div className="flex-1 overflow-y-auto px-4 py-3 min-h-0">
          {cart.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-300 py-12">
              <Package className="w-12 h-12 mb-3 stroke-[1.5]" />
              <p className="text-sm font-medium">Carrito vacío</p>
              <p className="text-xs mt-1">Toca un producto para agregarlo</p>
            </div>
          ) : (
            <div className="space-y-2">
              {cart.map(item => (
                <div key={item.product_id} className="bg-gray-50 rounded-xl p-3 flex items-center gap-3 group hover:bg-gray-100 transition-colors">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-gray-800 truncate">{item.product_name}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      ${item.unit_price.toFixed(2)} × {item.quantity}
                    </p>
                  </div>
                  <p className="font-bold text-sm text-gray-900 whitespace-nowrap">
                    ${(item.unit_price * item.quantity).toFixed(2)}
                  </p>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={(e) => { e.stopPropagation(); removeFromCart(item.product_id); }}
                      className="w-7 h-7 rounded-lg bg-white border border-gray-200 hover:bg-red-50 hover:border-red-200 hover:text-red-600 flex items-center justify-center text-gray-400 transition-all"
                    >
                      <Minus className="w-3.5 h-3.5" />
                    </button>
                    <span className="w-6 text-center font-bold text-xs text-gray-700">{item.quantity}</span>
                    <button
                      onClick={(e) => { e.stopPropagation(); addToCart(products.find(p => p.id === item.product_id)); }}
                      className="w-7 h-7 rounded-lg bg-white border border-gray-200 hover:bg-green-50 hover:border-green-200 hover:text-green-600 flex items-center justify-center text-gray-400 transition-all"
                    >
                      <Plus className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); deleteFromCart(item.product_id); }}
                      className="w-7 h-7 rounded-lg hover:bg-red-50 hover:text-red-500 flex items-center justify-center text-gray-300 transition-all opacity-0 group-hover:opacity-100"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* ===== SECCIÓN DE PAGO (fija abajo) ===== */}
        <div className="border-t border-gray-100 bg-white">

          {/* Subtotal */}
          <div className="px-5 py-3 flex justify-between items-center text-sm">
            <span className="text-gray-500">Subtotal</span>
            <span className="font-bold text-gray-900 text-lg">${total.toFixed(2)}</span>
          </div>

          {/* Método de pago */}
          <div className="px-5 pb-3">
            <div className="grid grid-cols-4 gap-1.5 bg-gray-100 p-1 rounded-xl">
              {paymentMethods.map(method => (
                <button
                  key={method.id}
                  onClick={() => setPaymentMethod(method.id)}
                  className={`flex flex-col items-center gap-0.5 py-2 rounded-lg text-[10px] font-semibold transition-all duration-200 ${paymentMethod === method.id
                      ? 'bg-white text-amber-700 shadow-sm'
                      : 'text-gray-400 hover:text-gray-600'
                    }`}
                >
                  {method.icon}
                  {method.label}
                </button>
              ))}
            </div>
          </div>

          {/* Input de efectivo + teclado */}
          <div className="px-5 pb-3">
            <div className="bg-gray-50 rounded-xl p-3 border border-gray-100">
              <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1">Monto recibido</p>
              <input
                type="number"
                value={paymentReceived}
                onChange={(e) => setPaymentReceived(e.target.value)}
                placeholder="0.00"
                className="w-full bg-transparent text-right text-2xl font-bold outline-none text-gray-900 placeholder:text-gray-300"
              />
            </div>
          </div>

          {/* Numpad */}
          <div className="px-5 pb-3">
            <div className="grid grid-cols-4 gap-1.5">
              {[1, 2, 3, 'C', 4, 5, 6, '.', 7, 8, 9, 0].map(num => (
                <button
                  key={num}
                  onClick={() => {
                    if (num === 'C') {
                      setPaymentReceived('');
                    } else if (num === '.') {
                      if (!paymentReceived.includes('.')) {
                        setPaymentReceived(paymentReceived + '.');
                      }
                    } else {
                      setPaymentReceived(paymentReceived + num);
                    }
                  }}
                  className={`py-2.5 rounded-xl font-bold text-sm transition-all duration-150 active:scale-95 ${num === 'C'
                      ? 'bg-red-50 text-red-500 hover:bg-red-100'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                >
                  {num}
                </button>
              ))}
            </div>
          </div>

          {/* Vuelto */}
          {paymentReceived && (
            <div className={`mx-5 mb-3 rounded-xl p-3 flex items-center justify-between ${change >= 0
                ? 'bg-emerald-50 border border-emerald-100'
                : 'bg-red-50 border border-red-100'
              }`}>
              <span className={`text-xs font-semibold ${change >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                {change >= 0 ? 'Vuelto' : 'Falta'}
              </span>
              <span className={`text-xl font-bold ${change >= 0 ? 'text-emerald-700' : 'text-red-700'}`}>
                ${Math.abs(change).toFixed(2)}
              </span>
            </div>
          )}

          {/* Procesar Venta */}
          <div className="px-5 pb-5">
            <button
              onClick={processSale}
              disabled={!paymentReceived || cart.length === 0 || processing || change < 0}
              className="w-full bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed text-white rounded-xl py-3.5 font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-lg shadow-amber-600/20 hover:shadow-amber-600/30 disabled:shadow-none hover:-translate-y-0.5 disabled:translate-y-0 active:translate-y-0"
            >
              {processing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                  Procesando...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Cobrar ${total.toFixed(2)}
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* MODAL DE FACTURA (TICKET) */}
      {showReceipt && lastSaleData && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm print:bg-white print:backdrop-blur-none">
          <div className="bg-white rounded-3xl overflow-hidden shadow-2xl w-[400px] max-w-full flex flex-col animate-scaleIn print:shadow-none print:w-[80mm] print:rounded-none">

            {/* Cabecera NO imprimible */}
            <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50 print:hidden">
              <h3 className="font-bold text-gray-800 flex items-center gap-2">
                <Receipt className="w-5 h-5 text-amber-600" />
                Factura Generada
              </h3>
              <button
                onClick={() => setShowReceipt(false)}
                className="p-2 hover:bg-gray-200 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* Contenido Imprimible del Ticket */}
            <div id="print-ticket" className="p-6 bg-white flex-1 overflow-auto print:p-0 print:overflow-visible">
              <div className="text-center mb-6">
                <img src="/logo.png" alt="Logo Valeecokies" className="w-16 h-16 mx-auto mb-3 object-contain" />
                <h2 className="text-xl font-black text-gray-900 uppercase tracking-widest mb-1">Valeecokies</h2>
                <p className="text-xs text-gray-500 mb-1">Sistema POS & Pastelería</p>
                <p className="text-xs text-gray-500 mb-3">Fecha: {lastSaleData.date}</p>
                <div className="inline-block px-3 py-1 bg-gray-100 rounded-md text-sm font-bold text-gray-700 tracking-wider">
                  {lastSaleData.invoice_number}
                </div>
              </div>

              <div className="border-t border-dashed border-gray-300 py-4 mb-4">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-gray-500 text-xs border-b border-dashed border-gray-300">
                      <th className="text-left pb-2 font-normal">CANT</th>
                      <th className="text-left pb-2 font-normal">DESCRIPCIÓN</th>
                      <th className="text-right pb-2 font-normal">TOTAL</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-800">
                    {lastSaleData.items.map((item, index) => (
                      <tr key={index}>
                        <td className="py-2 align-top font-medium">{item.quantity}</td>
                        <td className="py-2 pr-2">
                          {item.product_name}
                          <div className="text-[10px] text-gray-400">${parseFloat(item.unit_price).toFixed(2)} c/u</div>
                        </td>
                        <td className="py-2 text-right align-top font-bold">
                          ${(item.quantity * item.unit_price).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="space-y-1 text-sm">
                <div className="flex justify-between text-gray-600">
                  <span>Subtotal</span>
                  <span>${lastSaleData.total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-black text-lg py-2 border-y border-dashed border-gray-300 my-2">
                  <span>TOTAL</span>
                  <span>${lastSaleData.total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-600">
                  <span className="capitalize">Pago ({lastSaleData.payment_method})</span>
                  <span>${lastSaleData.received.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-gray-600 font-bold">
                  <span>Cambio/Vuelto</span>
                  <span>${lastSaleData.change.toFixed(2)}</span>
                </div>
              </div>

              <div className="text-center mt-8 text-xs text-gray-400 italic">
                ¡Gracias por su compra!<br />Vuelva pronto
              </div>
            </div>

            {/* Acciones NO imprimibles */}
            <div className="p-4 bg-gray-50 flex gap-3 print:hidden">
              <button
                onClick={() => setShowReceipt(false)}
                className="flex-1 px-4 py-3 bg-white border border-gray-200 text-gray-700 font-bold rounded-xl hover:bg-gray-50 transition-colors shadow-sm"
              >
                Nueva Venta
              </button>
              <button
                onClick={() => window.print()}
                className="flex-1 px-4 py-3 bg-amber-600 text-white font-bold rounded-xl hover:bg-amber-700 transition-colors shadow-md flex justify-center items-center gap-2"
              >
                <Printer className="w-5 h-5" />
                Imprimir
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default POS;
