import React, { useState, useEffect } from 'react';
import { FileSpreadsheet, Calendar, Search, Filter, PieChart, ShoppingBag } from 'lucide-react';
import { salesAPI, handleAPIError } from '../services/api';

const Reports = () => {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dateFilter, setDateFilter] = useState('');
  
  useEffect(() => {
    loadDetailedSales();
  }, [dateFilter]);

  const loadDetailedSales = async () => {
    try {
      setLoading(true);
      // Pedimos las ventas con 'detailed=true' para que el backend incluya qué compraron
      const response = await salesAPI.getAll({ detailed: true, date_from: dateFilter || undefined, date_to: dateFilter || undefined });
      setSales(response.data);
    } catch (error) {
      const errorInfo = handleAPIError(error);
      alert(`Error al cargar las ventas: ${errorInfo.message}`);
    } finally {
      setLoading(false);
    }
  };

  const exportToCSV = () => {
    if (sales.length === 0) {
      alert("No hay ventas para exportar");
      return;
    }
    
    // Configurar cabeceras del CSV
    const headers = [
      "ID VENTA",
      "NUMERO FACTURA",
      "FECHA",
      "HORA",
      "VENDEDOR",
      "METODO DE PAGO",
      "ESTADO",
      "TOTAL VENTA ($)",
      "PRODUCTO COMPRADO",
      "CANTIDAD",
      "PRECIO UNITARIO ($)",
      "SUBTOTAL ITEM ($)"
    ];
    
    // Crear las filas
    const rows = [];
    
    sales.forEach(sale => {
      const saleDate = new Date(sale.sale_date);
      const dateStr = saleDate.toLocaleDateString();
      const timeStr = saleDate.toLocaleTimeString();
      const seller = sale.user_name || 'Desconocido';
      
      // Si la venta tiene items, generamos una fila por cada item para el desglose
      if (sale.items && sale.items.length > 0) {
        sale.items.forEach(item => {
          rows.push([
            sale.id,
            sale.invoice_number,
            dateStr,
            timeStr,
            seller,
            String(sale.payment_method).toUpperCase(),
            String(sale.status).toUpperCase(),
            parseFloat(sale.total || 0).toFixed(2),
            `"${item.product_name || 'Producto'}"`, 
            item.quantity,
            parseFloat(item.unit_price || 0).toFixed(2),
            parseFloat(item.total || 0).toFixed(2)
          ]);
        });
      } else {
        // En caso excepcional que una venta no tenga items registrados (error)
        rows.push([
          sale.id,
          sale.invoice_number,
          dateStr,
          timeStr,
          seller,
          String(sale.payment_method).toUpperCase(),
          String(sale.status).toUpperCase(),
          parseFloat(sale.total || 0).toFixed(2),
          "SIN ITEMS",
          0,
          0,
          0
        ]);
      }
    });
    
    // Convertir a string CSV
    const csvContent = [
      headers.join(","),
      ...rows.map(r => r.join(","))
    ].join("\n");
    
    // Insertar BOM para que Excel detecte UTF-8 (tildes, eñes)
    const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    // Crear enlace oculto y forzar descarga
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `Reporte_Ventas_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Cabecera */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <PieChart className="w-8 h-8 text-amber-600" />
              Reportes Contables
            </h1>
            <p className="text-gray-500 mt-1">Historial detallado de todas tus ventas</p>
          </div>
          
          <button 
            onClick={exportToCSV}
            disabled={sales.length === 0}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-bold py-3 px-6 rounded-xl flex items-center gap-2 shadow-lg transition-transform hover:-translate-y-1"
          >
            <FileSpreadsheet className="w-6 h-6" />
            Descargar a Excel (CSV)
          </button>
        </div>

        {/* Filtros */}
        <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex gap-4 mb-6 items-center">
          <Calendar className="text-gray-400 w-6 h-6" />
          <div className="flex flex-col">
            <span className="text-sm text-gray-500 font-semibold">Filtrar por Fecha Específica:</span>
            <input 
              type="date" 
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="border border-gray-300 rounded px-3 py-1 mt-1 focus:outline-none focus:border-amber-500"
            />
          </div>
          {dateFilter && (
            <button 
              onClick={() => setDateFilter('')}
              className="ml-2 text-sm text-amber-600 hover:underline mt-4"
            >
              Ver Todas
            </button>
          )}
        </div>

        {/* Tabla visualizadora */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          {loading ? (
             <div className="p-12 text-center">
               <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mx-auto"></div>
             </div>
          ) : sales.length === 0 ? (
             <div className="p-12 text-center text-gray-500">
               No hay ventas registradas para este periodo.
             </div>
          ) : (
             <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-100 text-sm">
                    <th className="p-4 font-semibold text-gray-600">Factura</th>
                    <th className="p-4 font-semibold text-gray-600">Fecha</th>
                    <th className="p-4 font-semibold text-gray-600">Método Pago</th>
                    <th className="p-4 font-semibold text-gray-600">Items (Resumen)</th>
                    <th className="p-4 font-semibold text-gray-600 text-right">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {sales.map(sale => (
                    <tr key={sale.id} className="hover:bg-gray-50 transition-colors">
                      <td className="p-4 font-mono font-medium text-gray-700">{sale.invoice_number}</td>
                      <td className="p-4 text-gray-600">
                        {new Date(sale.sale_date).toLocaleDateString()} a las {new Date(sale.sale_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                      </td>
                      <td className="p-4 text-gray-600 capitalize">
                         <span className="bg-blue-50 text-blue-800 px-2.5 py-0.5 rounded-full text-xs font-semibold">
                           {String(sale.payment_method)}
                         </span>
                      </td>
                      <td className="p-4">
                        <div className="text-sm text-gray-500 max-w-xs truncate">
                           {(sale.items || []).map(i => `${i.quantity} ${i.product_name || 'Producto'}`).join(', ') || 'N/A'}
                        </div>
                      </td>
                      <td className="p-4 text-right font-bold text-gray-900">${parseFloat(sale.total || 0).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
             </table>
          )}
        </div>

      </div>
    </div>
  );
};

export default Reports;
