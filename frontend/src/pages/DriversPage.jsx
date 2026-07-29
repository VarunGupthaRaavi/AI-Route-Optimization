import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { DataTable } from '../components/DataTable';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';
import { api } from '../services/api';
import { Plus, Edit2, Trash2, UserCheck, Phone, Shield, Star } from 'lucide-react';

export const DriversPage = () => {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    license_number: '',
    phone: '',
    status: 'IDLE',
    rating: 5.0
  });

  const fetchDrivers = async () => {
    setLoading(true);
    try {
      const params = { page, page_size: 10 };
      const res = await api.get('/drivers', { params });
      setDrivers(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error('Error fetching drivers', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDrivers();
  }, [page]);

  const handleOpenCreate = () => {
    setEditingId(null);
    setFormData({
      license_number: '',
      phone: '',
      status: 'IDLE',
      rating: 5.0
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (driver) => {
    setEditingId(driver.id);
    setFormData({
      license_number: driver.license_number,
      phone: driver.phone,
      status: driver.status,
      rating: driver.rating
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/drivers/${editingId}`, formData);
      } else {
        await api.post('/drivers', formData);
      }
      setIsModalOpen(false);
      fetchDrivers();
    } catch (err) {
      alert(err.message || 'Operation failed');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete driver profile?')) {
      try {
        await api.delete(`/drivers/${id}`);
        fetchDrivers();
      } catch (err) {
        alert(err.message || 'Delete failed');
      }
    }
  };

  const columns = [
    {
      header: 'Commercial License',
      accessor: 'license_number',
      render: (row) => (
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <UserCheck className="w-4 h-4" />
          </div>
          <div>
            <div className="font-bold text-slate-100 font-mono">{row.license_number}</div>
            <div className="text-xs text-slate-400 flex items-center mt-0.5">
              <Phone className="w-3 h-3 mr-1 text-slate-500" />
              {row.phone}
            </div>
          </div>
        </div>
      )
    },
    {
      header: 'Duty Status',
      accessor: 'status',
      render: (row) => <StatusBadge status={row.status} />
    },
    {
      header: 'Driver Rating',
      accessor: 'rating',
      render: (row) => (
        <div className="flex items-center space-x-1.5 text-amber-400 text-xs font-semibold">
          <Star className="w-4 h-4 fill-amber-400" />
          <span>{row.rating.toFixed(1)} / 5.0</span>
        </div>
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
        title="Fleet Drivers"
        subtitle="Manage commercial drivers, license qualifications, and duty statuses"
      />

      <div className="p-8 max-w-7xl mx-auto space-y-6">
        <DataTable
          columns={columns}
          data={drivers}
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
              <span>Register New Driver</span>
            </button>
          }
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingId ? 'Edit Driver Profile' : 'Register New Fleet Driver'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Commercial License Number *</label>
            <input
              type="text"
              required
              value={formData.license_number}
              onChange={(e) => setFormData({ ...formData, license_number: e.target.value })}
              placeholder="CDL-99887766"
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
              placeholder="+1-555-0144"
              className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Duty Status</label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              >
                <option value="IDLE">IDLE (Available)</option>
                <option value="ON_ROUTE">ON_ROUTE (Active)</option>
                <option value="OFF_DUTY">OFF_DUTY (Inactive)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Rating</label>
              <input
                type="number"
                step="0.1"
                min="1.0"
                max="5.0"
                value={formData.rating}
                onChange={(e) => setFormData({ ...formData, rating: parseFloat(e.target.value) })}
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
              {editingId ? 'Save Driver' : 'Register Driver'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
