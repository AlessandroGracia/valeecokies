import React, { useState, useEffect } from 'react';
import { Package, Plus, Edit2, PauseCircle, PlayCircle, Search, Save, X } from 'lucide-react';
import { productsAPI, handleAPIError } from '../services/api';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  
  // Estado del formulario
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    description: '',
    category: 'cookies',
    cost_price: '',
    sale_price: '',
    stock_quantity: 0,
    min_stock: 10,
    unit: 'unidad'
  });

  const categories = [
    { id: 'cookies', name: 'Cookies', icon: '🍪', color: 'bg-amber-100 text-amber-800' },
    { id: 'postres', name: 'Postres', icon: '🍰', color: 'bg-pink-100 text-pink-800' },
    { id: 'bebidas', name: 'Bebidas', icon: '🥤', color: 'bg-cyan-100 text-cyan-800' }
  ];

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      // Cargar TODOS los productos, incluso los pausados, para administrarlos
      const response = await productsAPI.getAll(); 
      setProducts(response.data);
    } catch (error) {
      const errorInfo = handleAPIError(error);
      alert(errorInfo.message);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryInfo = (catId) => {
    return categories.find(c => c.id === catId) || categories[0];
  };

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase()) || p.code.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = filterCategory === 'all' || p.category === filterCategory;
    return matchesSearch && matchesCategory;
  });

  const handleOpenModal = (product = null) => {
    if (product) {
      setEditingProduct(product);
      setFormData({
        code: product.code,
        name: product.name,
        description: product.description || '',
        category: product.category,
        cost_price: product.cost_price,
        sale_price: product.sale_price,
        stock_quantity: product.stock_quantity,
        min_stock: product.min_stock,
        unit: product.unit
      });
    } else {
      setEditingProduct(null);
      setFormData({
        code: `PROD-${Math.floor(1000 + Math.random() * 9000)}`,
        name: '',
        description: '',
        category: 'cookies',
        cost_price: '',
        sale_price: '',
        stock_quantity: 0,
        min_stock: 10,
        unit: 'unidad'
      });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingProduct(null);
  };

  const handleSaveProduct = async (e) => {
    e.preventDefault();
    try {
      // Parsear numéricos
      const payload = {
        ...formData,
        cost_price: parseFloat(formData.cost_price),
        sale_price: parseFloat(formData.sale_price),
        stock_quantity: parseInt(formData.stock_quantity),
        min_stock: parseInt(formData.min_stock)
      };

      if (editingProduct) {
        await productsAPI.update(editingProduct.id, payload);
        alert('Producto actualizado exitosamente');
      } else {
        await productsAPI.create(payload);
        alert('Producto creado exitosamente');
      }
      
      handleCloseModal();
      loadProducts();
    } catch (error) {
      const errorInfo = handleAPIError(error);
      alert(`Error: ${errorInfo.message}`);
    }
  };

  const toggleProductStatus = async (product) => {
    const newStatus = !product.is_active;
    const actionText = newStatus ? 'Reactivar' : 'Pausar';
    
    if (window.confirm(`¿Estás seguro de que quieres ${actionText} el producto ${product.name}?`)) {
      try {
        await productsAPI.update(product.id, { is_active: newStatus });
        loadProducts(); // Recargar para ver el cambio
      } catch (error) {
        const errorInfo = handleAPIError(error);
        alert(`Error al cambiar estado: ${errorInfo.message}`);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4 lg:p-8 pt-20 lg:pt-8 overflow-auto">
      <div className="max-w-7xl mx-auto">
        {/* Encabezado */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 flex items-center gap-3">
              <Package className="w-8 h-8 text-amber-600" />
              Gestión de Inventario
            </h1>
            <p className="text-sm text-gray-500 mt-1">Administra tus galletas, postres y bebidas</p>
          </div>
          <button 
            onClick={() => handleOpenModal()}
            className="w-full sm:w-auto bg-amber-600 hover:bg-amber-700 text-white px-6 py-3 rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg transition-transform hover:-translate-y-1"
          >
            <Plus className="w-5 h-5" />
            NUEVO PRODUCTO
          </button>
        </div>

        {/* Filtros */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-gray-400 w-5 h-5" />
            <input 
              type="text" 
              placeholder="Buscar por código o nombre..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
            />
          </div>
          <div className="flex bg-gray-100 p-1 rounded-lg overflow-x-auto no-scrollbar shrink-0">
            <button 
              onClick={() => setFilterCategory('all')}
              className={`whitespace-nowrap px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${filterCategory === 'all' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-600 hover:text-gray-900'}`}
            >
              Todos
            </button>
            {categories.map(cat => (
              <button 
                key={cat.id}
                onClick={() => setFilterCategory(cat.id)}
                className={`whitespace-nowrap flex items-center gap-1 px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${filterCategory === cat.id ? 'bg-white shadow-sm text-gray-900' : 'text-gray-600 hover:text-gray-900'}`}
              >
                <span>{cat.icon}</span> {cat.name}
              </button>
            ))}
          </div>
        </div>

        {/* Tabla */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-x-auto">
          {loading ? (
             <div className="p-12 pl-4 text-center">
               <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600 mx-auto"></div>
             </div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-50 border-b border-gray-100">
                  <th className="p-4 font-semibold text-gray-600">Código</th>
                  <th className="p-4 font-semibold text-gray-600">Producto</th>
                  <th className="p-4 font-semibold text-gray-600">Categoría</th>
                  <th className="p-4 font-semibold text-gray-600 text-right">Bodega Principal</th>
                  <th className="p-4 font-semibold text-gray-600 text-right">Costo</th>
                  <th className="p-4 font-semibold text-gray-600 text-right">Venta</th>
                  <th className="p-4 font-semibold text-gray-600 text-center">Estado</th>
                  <th className="p-4 font-semibold text-gray-600 text-center">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filteredProducts.map(product => {
                  const catInfo = getCategoryInfo(product.category);
                  const isLowStock = product.stock_quantity <= product.min_stock;
                  
                  return (
                    <tr key={product.id} className={`hover:bg-gray-50 transition-colors ${!product.is_active ? 'opacity-50 bg-gray-100' : ''}`}>
                      <td className="p-4 font-mono text-sm text-gray-500">{product.code}</td>
                      <td className="p-4 font-medium text-gray-900">{product.name}</td>
                      <td className="p-4">
                        <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${catInfo.color}`}>
                          {catInfo.icon} {catInfo.name}
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <span className={`inline-flex items-center justify-center min-w-[3rem] px-2 py-1 rounded-lg text-sm font-bold ${isLowStock ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'}`}>
                          {product.stock_quantity}
                        </span>
                      </td>
                      <td className="p-4 text-right text-gray-500">${parseFloat(product.cost_price).toFixed(2)}</td>
                      <td className="p-4 text-right font-bold text-amber-700">${parseFloat(product.sale_price).toFixed(2)}</td>
                      <td className="p-4 text-center">
                        {product.is_active ? (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">Activo</span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-200 text-gray-600">Pausado</span>
                        )}
                      </td>
                      <td className="p-4">
                        <div className="flex justify-center gap-2">
                          <button 
                            onClick={() => handleOpenModal(product)}
                            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="Editar"
                          >
                            <Edit2 className="w-5 h-5" />
                          </button>
                          <button 
                            onClick={() => toggleProductStatus(product)}
                            className={`p-1.5 rounded-lg transition-colors ${product.is_active ? 'text-amber-600 hover:bg-amber-50' : 'text-green-600 hover:bg-green-50'}`}
                            title={product.is_active ? "Pausar Producto" : "Reactivar Producto"}
                          >
                            {product.is_active ? <PauseCircle className="w-5 h-5" /> : <PlayCircle className="w-5 h-5" />}
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
                {filteredProducts.length === 0 && (
                  <tr>
                     <td colSpan="8" className="p-8 text-center text-gray-500">
                        No se encontraron productos que coincidan con la búsqueda.
                     </td>
                  </tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Modal de Crear/Editar */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl overflow-hidden animate-fade-in">
            <div className="bg-gradient-to-r from-amber-600 to-orange-600 p-6 text-white flex justify-between items-center">
              <h2 className="text-2xl font-bold flex items-center gap-2">
                {editingProduct ? <Edit2 className="w-6 h-6" /> : <Plus className="w-6 h-6" />}
                {editingProduct ? 'Editar Producto' : 'Nuevo Producto'}
              </h2>
              <button onClick={handleCloseModal} className="text-white/80 hover:text-white transition-colors">
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <form onSubmit={handleSaveProduct} className="p-6">
              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Código</label>
                  <input type="text" required value={formData.code} onChange={e => setFormData({...formData, code: e.target.value})} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Nombre Comercial</label>
                  <input type="text" required value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500" />
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-1">Categoría</label>
                <div className="flex gap-4">
                  {categories.map(cat => (
                    <label key={cat.id} className={`flex-1 flex justify-center items-center gap-2 border-2 rounded-xl py-3 cursor-pointer transition-all ${formData.category === cat.id ? 'border-amber-600 bg-amber-50 text-amber-800 font-bold' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
                      <input type="radio" name="category" value={cat.id} checked={formData.category === cat.id} onChange={(e) => setFormData({...formData, category: e.target.value})} className="hidden" />
                      <span className="text-2xl">{cat.icon}</span> {cat.name}
                    </label>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Costo de Producción ($)</label>
                  <input type="number" step="0.01" min="0" required value={formData.cost_price} onChange={e => setFormData({...formData, cost_price: e.target.value})} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500 bg-gray-50 text-gray-600 font-mono" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Precio de Venta al Público ($)</label>
                  <input type="number" step="0.01" min="0" required value={formData.sale_price} onChange={e => setFormData({...formData, sale_price: e.target.value})} className="w-full px-3 py-2 border-2 border-amber-300 rounded-lg focus:ring-amber-500 focus:border-amber-500 font-bold font-mono text-amber-700 text-lg" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6 mb-8">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Inventario Bodega Principal</label>
                  <input type="number" min="0" required value={formData.stock_quantity} onChange={e => setFormData({...formData, stock_quantity: e.target.value})} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500" />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">Alerta Stock Mínimo (<span className="text-red-500">Mermas/Falta</span>)</label>
                  <input type="number" min="0" required value={formData.min_stock} onChange={e => setFormData({...formData, min_stock: e.target.value})} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-amber-500 focus:border-amber-500" />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                <button type="button" onClick={handleCloseModal} className="px-6 py-2.5 rounded-lg text-gray-700 font-medium hover:bg-gray-100 transition-colors">
                  Cancelar
                </button>
                <button type="submit" className="bg-amber-600 hover:bg-amber-700 text-white px-6 py-2.5 rounded-lg font-bold flex items-center gap-2 transition-colors">
                  <Save className="w-5 h-5" />
                  {editingProduct ? 'Guardar Cambios' : 'Crear Producto'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Products;
