import React, { useState, useEffect } from 'react';
import { Users, Plus, Edit2, Trash2, Search, Save, X, Phone, Mail, MapPin, FileText, UserCheck, UserX } from 'lucide-react';
import { customersAPI, handleAPIError } from '../services/api';

const Customers = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);

  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    id_number: '',
    address: '',
    city: '',
    notes: ''
  });

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const response = await customersAPI.getAll();
      setCustomers(response.data);
    } catch (error) {
      const errorInfo = handleAPIError(error);
      alert(errorInfo.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredCustomers = customers.filter(c =>
    c.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (c.email || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (c.phone || '').includes(searchTerm) ||
    (c.id_number || '').includes(searchTerm)
  );

  const handleOpenModal = (customer = null) => {
    if (customer) {
      setEditingCustomer(customer);
      setFormData({
        full_name: customer.full_name,
        email: customer.email || '',
        phone: customer.phone || '',
        id_number: customer.id_number || '',
        address: customer.address || '',
        city: customer.city || '',
        notes: customer.notes || ''
      });
    } else {
      setEditingCustomer(null);
      setFormData({ full_name: '', email: '', phone: '', id_number: '', address: '', city: '', notes: '' });
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingCustomer(null);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      // Limpiar campos vacíos para no enviar strings vacías como email
      const payload = { ...formData };
      Object.keys(payload).forEach(k => { if (payload[k] === '') payload[k] = null; });
      // full_name es required
      payload.full_name = formData.full_name;

      if (editingCustomer) {
        await customersAPI.update(editingCustomer.id, payload);
      } else {
        await customersAPI.create(payload);
      }
      handleCloseModal();
      loadCustomers();
    } catch (error) {
      const errorInfo = handleAPIError(error);
      alert(`Error: ${errorInfo.message}`);
    }
  };

  const handleDelete = async (customer) => {
    if (window.confirm(`¿Desactivar al cliente "${customer.full_name}"? Se conservará su historial.`)) {
      try {
        await customersAPI.delete(customer.id);
        loadCustomers();
      } catch (error) {
        const errorInfo = handleAPIError(error);
        alert(errorInfo.message);
      }
    }
  };

  const activeCount = customers.filter(c => c.is_active).length;
  const inactiveCount = customers.filter(c => !c.is_active).length;

  return (
    <div className="min-h-screen bg-[#f8f7f4] p-6 lg:p-8 overflow-auto">
      <div className="max-w-7xl mx-auto">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 font-['Poppins'] flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center text-white shadow-sm">
                <Users className="w-5 h-5" />
              </div>
              Clientes
            </h1>
            <p className="text-sm text-gray-400 mt-1">{activeCount} activos · {inactiveCount} inactivos</p>
          </div>
          <button
            onClick={() => handleOpenModal()}
            className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm flex items-center gap-2 shadow-lg shadow-violet-600/20 transition-all hover:-translate-y-0.5"
          >
            <Plus className="w-4 h-4" />
            Nuevo Cliente
          </button>
        </div>

        {/* Buscador */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 mb-6">
          <div className="relative">
            <Search className="absolute left-3.5 top-3 text-gray-300 w-5 h-5" />
            <input
              type="text"
              placeholder="Buscar por nombre, email, teléfono o cédula..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-11 pr-4 py-2.5 bg-gray-50 border border-gray-100 rounded-xl text-sm focus:outline-none focus:border-violet-300 focus:ring-2 focus:ring-violet-500/20 transition-all"
            />
          </div>
        </div>

        {/* Lista de clientes */}
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          {loading ? (
            <div className="p-12 text-center">
              <div className="animate-spin rounded-full h-10 w-10 border-2 border-violet-600 border-t-transparent mx-auto" />
            </div>
          ) : filteredCustomers.length === 0 ? (
            <div className="p-12 text-center text-gray-300">
              <Users className="w-12 h-12 mx-auto mb-3 stroke-[1.5]" />
              <p className="text-sm font-medium text-gray-400">No se encontraron clientes</p>
            </div>
          ) : (
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="px-5 py-3.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Cliente</th>
                  <th className="px-5 py-3.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Contacto</th>
                  <th className="px-5 py-3.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Cédula / RUC</th>
                  <th className="px-5 py-3.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider">Ciudad</th>
                  <th className="px-5 py-3.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider text-center">Estado</th>
                  <th className="px-5 py-3.5 text-[11px] font-semibold text-gray-400 uppercase tracking-wider text-center">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filteredCustomers.map(customer => (
                  <tr key={customer.id} className={`hover:bg-gray-50/50 transition-colors ${!customer.is_active ? 'opacity-40' : ''}`}>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-violet-100 to-purple-100 flex items-center justify-center text-violet-600 font-bold text-sm flex-shrink-0">
                          {customer.full_name.charAt(0)}
                        </div>
                        <div>
                          <p className="font-semibold text-sm text-gray-900">{customer.full_name}</p>
                          {customer.notes && <p className="text-[11px] text-gray-400 truncate max-w-[180px]">{customer.notes}</p>}
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="space-y-0.5">
                        {customer.email && (
                          <p className="text-xs text-gray-500 flex items-center gap-1.5">
                            <Mail className="w-3 h-3 text-gray-300" /> {customer.email}
                          </p>
                        )}
                        {customer.phone && (
                          <p className="text-xs text-gray-500 flex items-center gap-1.5">
                            <Phone className="w-3 h-3 text-gray-300" /> {customer.phone}
                          </p>
                        )}
                        {!customer.email && !customer.phone && <span className="text-xs text-gray-300">—</span>}
                      </div>
                    </td>
                    <td className="px-5 py-4 text-sm text-gray-600 font-mono">{customer.id_number || '—'}</td>
                    <td className="px-5 py-4 text-sm text-gray-500">{customer.city || '—'}</td>
                    <td className="px-5 py-4 text-center">
                      {customer.is_active ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                          <UserCheck className="w-3 h-3" /> Activo
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                          <UserX className="w-3 h-3" /> Inactivo
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex justify-center gap-1">
                        <button
                          onClick={() => handleOpenModal(customer)}
                          className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Editar"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        {customer.is_active && (
                          <button
                            onClick={() => handleDelete(customer)}
                            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Desactivar"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Modal Crear / Editar */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-scaleIn">
            
            {/* Header del modal */}
            <div className="bg-gradient-to-r from-violet-600 to-purple-600 p-5 text-white flex justify-between items-center">
              <h2 className="text-lg font-bold flex items-center gap-2 font-['Poppins']">
                {editingCustomer ? <Edit2 className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
                {editingCustomer ? 'Editar Cliente' : 'Nuevo Cliente'}
              </h2>
              <button onClick={handleCloseModal} className="text-white/70 hover:text-white transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleSave} className="p-6 space-y-4">
              {/* Nombre - obligatorio */}
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Nombre Completo *</label>
                <input
                  type="text" required
                  value={formData.full_name}
                  onChange={e => setFormData({...formData, full_name: e.target.value})}
                  className="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 outline-none transition-all"
                  placeholder="ej: María González"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Email</label>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={e => setFormData({...formData, email: e.target.value})}
                    className="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 outline-none transition-all"
                    placeholder="correo@ejemplo.com"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Teléfono</label>
                  <input
                    type="text"
                    value={formData.phone}
                    onChange={e => setFormData({...formData, phone: e.target.value})}
                    className="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 outline-none transition-all"
                    placeholder="0999999999"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Cédula / RUC</label>
                  <input
                    type="text"
                    value={formData.id_number}
                    onChange={e => setFormData({...formData, id_number: e.target.value})}
                    className="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 outline-none transition-all"
                    placeholder="0123456789"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Ciudad</label>
                  <input
                    type="text"
                    value={formData.city}
                    onChange={e => setFormData({...formData, city: e.target.value})}
                    className="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 outline-none transition-all"
                    placeholder="ej: Quito"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Dirección</label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={e => setFormData({...formData, address: e.target.value})}
                  className="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 outline-none transition-all"
                  placeholder="Dirección completa"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1.5 uppercase tracking-wider">Notas</label>
                <textarea
                  value={formData.notes}
                  onChange={e => setFormData({...formData, notes: e.target.value})}
                  rows={2}
                  className="w-full px-3.5 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-violet-500/30 focus:border-violet-400 outline-none transition-all resize-none"
                  placeholder="ej: Cliente frecuente, prefiere factura"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-gray-100">
                <button type="button" onClick={handleCloseModal}
                  className="px-5 py-2.5 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors">
                  Cancelar
                </button>
                <button type="submit"
                  className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm flex items-center gap-2 shadow-md transition-all">
                  <Save className="w-4 h-4" />
                  {editingCustomer ? 'Guardar Cambios' : 'Crear Cliente'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Customers;
