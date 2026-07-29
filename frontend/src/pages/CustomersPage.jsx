import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { DataTable } from '../components/DataTable';
import { Modal } from '../components/Modal';
import { api } from '../services/api';
import { Plus, Edit2, Trash2, MapPin, Mail, Phone, Building } from 'lucide-react';

export const CustomersPage = () => {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    company_name: '',
    email: '',
    phone: '',
    address: '',
    latitude: 41.8781,
    longitude: -87.6298,
    notes: ''
  });

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const params = { page, page_size: 10 };
      if (search) params.q = search;
      const res = await api.get('/customers', { params });
      setCustomers(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error('Error fetching customers', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [page, search]);

  const handleOpenCreate = () => {
    setEditingId(null);
    setFormData({
      name: '',
      company_name: '',
      email: '',
      phone: '',
      address: '',
      latitude: 41.8781,
      longitude: -87.6298,
      notes: ''
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (customer) => {
    setEditingId(customer.id);
    setFormData({
      name: customer.name,
      company_name: customer.company_name || '',
      email: customer.email,
      phone: customer.phone,
      address: customer.address,
      latitude: customer.latitude,
      longitude: customer.longitude,
      notes: customer.notes || ''
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/customers/${editingId}`, formData);
      } else {
        await api.post('/customers', formData);
      }
      setIsModalOpen(false);
      fetchCustomers();
    } catch (err) {
      alert(err.message || 'Operation failed');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this customer account?')) {
      try {
        await api.delete(`/customers/${id}`);
        fetchCustomers();
      } catch (err) {
        alert(err.message || 'Delete failed');
      }
    }
  };

  const columns = [
    {
      header: 'Customer Name',
      accessor: 'name',
      render: (row) => (
        <div>
          <div className="font-semibold text-slate-100">{row.name}</div>
          {row.company_name && (
            <div className="text-xs text-slate-400 flex items-center mt-0.5">
              <Building className="w-3 h-3 mr-1 text-slate-500" />
              {row.company_name}
            </div>
          )}
        </div>
      )
    },
    {
      header: 'Contact Info',
      accessor: 'email',
      render: (row) => (
        <div className="text-xs space-y-0.5">
          <div className="text-slate-300 flex items-center">
            <Mail className="w-3 h-3 mr-1 text-indigo-400" />
            {row.email}
          </div>
          <div className="text-slate-400 flex items-center">
            <Phone className="w-3 h-3 mr-1 text-slate-500" />
            {row.phone}
          </div>
        </div>
      )
    },
    {
      header: 'Delivery Address',
      accessor: 'address',
      render: (row) => (
        <div className="text-xs text-slate-300 max-w-xs truncate flex items-center">
          <MapPin className="w-3.5 h-3.5 mr-1 text-rose-400 flex-shrink-0" />
          <span className="truncate">{row.address}</span>
        </div>
      )
    },
    {
      header: 'Coordinates',
      accessor: 'latitude',
      render: (row) => (
        <span className="text-xs font-mono text-slate-400 bg-slate-900/60 px-2 py-1 rounded border border-slate-800">
          {row.latitude.toFixed(4)}, {row.longitude.toFixed(4)}
        </span>
      )
    },
    {
      header: 'Actions',
      accessor: 'id',
      render: (row) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleOpenEdit(row)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-indigo-400 hover:bg-slate-800 transition-colors"
          >
            <Edit2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleDelete(row.id)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      )
    }
  ];

  return (
    <div className="flex-1 pb-12">
      <Header
        title="Customer Directory"
        subtitle="Manage client shipping accounts, delivery locations, and contact coordinates"
      />

      <div className="p-8 max-w-7xl mx-auto space-y-6">
        <DataTable
          columns={columns}
          data={customers}
          loading={loading}
          searchQuery={search}
          onSearchChange={setSearch}
          page={page}
          totalPages={totalPages}
          totalItems={totalItems}
          onPageChange={setPage}
          actionButton={
            <button
              onClick={handleOpenCreate}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold text-xs flex items-center space-x-2 shadow-lg shadow-indigo-500/20 hover:opacity-90 transition-opacity"
            >
              <Plus className="w-4 h-4" />
              <span>Add New Customer</span>
            </button>
          }
        />
      </div>

      {/* Add / Edit Customer Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingId ? 'Edit Customer Account' : 'Add New Customer Account'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Customer Name *</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Acme Logistics Corp"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Company Name</label>
              <input
                type="text"
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                placeholder="Acme Corp"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Email Address *</label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="contact@acme.com"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Phone Number *</label>
              <input
                type="text"
                required
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                placeholder="+1-555-0199"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Delivery Address *</label>
            <textarea
              required
              rows={2}
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
              placeholder="100 Warehouse Way, Chicago, IL"
              className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Latitude</label>
              <input
                type="number"
                step="any"
                required
                value={formData.latitude}
                onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Longitude</label>
              <input
                type="number"
                step="any"
                required
                value={formData.longitude}
                onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-medium hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30"
            >
              {editingId ? 'Save Changes' : 'Create Account'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
