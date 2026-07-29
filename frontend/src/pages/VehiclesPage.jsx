import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { DataTable } from '../components/DataTable';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';
import { api } from '../services/api';
import { Plus, Edit2, Trash2, Truck, Gauge, Fuel } from 'lucide-react';

export const VehiclesPage = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    license_plate: '',
    vehicle_model: '',
    capacity_kg: 1500.0,
    volume_m3: 12.5,
    fuel_type: 'DIESEL',
    max_range_km: 650.0,
    status: 'AVAILABLE'
  });

  const fetchVehicles = async () => {
    setLoading(true);
    try {
      const params = { page, page_size: 10 };
      const res = await api.get('/vehicles', { params });
      setVehicles(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error('Error fetching vehicles', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVehicles();
  }, [page]);

  const handleOpenCreate = () => {
    setEditingId(null);
    setFormData({
      license_plate: '',
      vehicle_model: '',
      capacity_kg: 1500.0,
      volume_m3: 12.5,
      fuel_type: 'DIESEL',
      max_range_km: 650.0,
      status: 'AVAILABLE'
    });
    setIsModalOpen(true);
  };

  const handleOpenEdit = (vehicle) => {
    setEditingId(vehicle.id);
    setFormData({
      license_plate: vehicle.license_plate,
      vehicle_model: vehicle.vehicle_model,
      capacity_kg: vehicle.capacity_kg,
      volume_m3: vehicle.volume_m3,
      fuel_type: vehicle.fuel_type,
      max_range_km: vehicle.max_range_km,
      status: vehicle.status
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/vehicles/${editingId}`, formData);
      } else {
        await api.post('/vehicles', formData);
      }
      setIsModalOpen(false);
      fetchVehicles();
    } catch (err) {
      alert(err.message || 'Operation failed');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete vehicle from fleet?')) {
      try {
        await api.delete(`/vehicles/${id}`);
        fetchVehicles();
      } catch (err) {
        alert(err.message || 'Delete failed');
      }
    }
  };

  const columns = [
    {
      header: 'Vehicle Specification',
      accessor: 'license_plate',
      render: (row) => (
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <Truck className="w-5 h-5" />
          </div>
          <div>
            <div className="font-bold text-slate-100 font-heading">{row.vehicle_model}</div>
            <div className="text-xs font-mono text-indigo-400">{row.license_plate}</div>
          </div>
        </div>
      )
    },
    {
      header: 'Payload Capacity',
      accessor: 'capacity_kg',
      render: (row) => (
        <div className="text-xs space-y-1">
          <div className="text-slate-200 font-medium">{row.capacity_kg.toLocaleString()} kg</div>
          <div className="text-slate-400">{row.volume_m3} m³ volume</div>
        </div>
      )
    },
    {
      header: 'Fuel & Range',
      accessor: 'fuel_type',
      render: (row) => (
        <div className="text-xs space-y-1">
          <div className="text-slate-300 flex items-center">
            <Fuel className="w-3 h-3 mr-1 text-amber-400" />
            {row.fuel_type}
          </div>
          <div className="text-slate-400 flex items-center">
            <Gauge className="w-3 h-3 mr-1 text-cyan-400" />
            {row.max_range_km} km max
          </div>
        </div>
      )
    },
    {
      header: 'Fleet Status',
      accessor: 'status',
      render: (row) => <StatusBadge status={row.status} />
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
        title="Fleet Vehicles"
        subtitle="Manage logistics cargo vehicles, volume capacities, and maintenance schedules"
      />

      <div className="p-8 max-w-7xl mx-auto space-y-6">
        <DataTable
          columns={columns}
          data={vehicles}
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
              <span>Add Fleet Vehicle</span>
            </button>
          }
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingId ? 'Edit Vehicle Specification' : 'Add New Fleet Vehicle'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">License Plate *</label>
              <input
                type="text"
                required
                value={formData.license_plate}
                onChange={(e) => setFormData({ ...formData, license_plate: e.target.value })}
                placeholder="IL-ROUTE-99"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Vehicle Model *</label>
              <input
                type="text"
                required
                value={formData.vehicle_model}
                onChange={(e) => setFormData({ ...formData, vehicle_model: e.target.value })}
                placeholder="Ford Transit Cargo Van"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Capacity (kg) *</label>
              <input
                type="number"
                step="any"
                required
                value={formData.capacity_kg}
                onChange={(e) => setFormData({ ...formData, capacity_kg: parseFloat(e.target.value) })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Volume (m³) *</label>
              <input
                type="number"
                step="any"
                required
                value={formData.volume_m3}
                onChange={(e) => setFormData({ ...formData, volume_m3: parseFloat(e.target.value) })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Fuel Type</label>
              <select
                value={formData.fuel_type}
                onChange={(e) => setFormData({ ...formData, fuel_type: e.target.value })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              >
                <option value="DIESEL">DIESEL</option>
                <option value="ELECTRIC">ELECTRIC</option>
                <option value="GASOLINE">GASOLINE</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Status</label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              >
                <option value="AVAILABLE">AVAILABLE</option>
                <option value="IN_TRANSIT">IN_TRANSIT</option>
                <option value="MAINTENANCE">MAINTENANCE</option>
              </select>
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
              {editingId ? 'Save Vehicle' : 'Add Vehicle'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
