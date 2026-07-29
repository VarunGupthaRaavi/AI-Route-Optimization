import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { DataTable } from '../components/DataTable';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';
import { api } from '../services/api';
import { Plus, Trash2, Package, MapPin, Play, CheckCircle2, XCircle, RotateCcw } from 'lucide-react';

export const DeliveriesPage = () => {
  const [deliveries, setDeliveries] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    customer_id: '',
    pickup_address: 'Hub Depot, Chicago, IL',
    delivery_address: '',
    pickup_lat: 41.8781,
    pickup_lng: -87.6298,
    delivery_lat: 41.8900,
    delivery_lng: -87.6240,
    weight_kg: 100.0,
    volume_m3: 0.5,
    priority: 'MEDIUM',
    notes: ''
  });

  const fetchDeliveries = async () => {
    setLoading(true);
    try {
      const params = { page, page_size: 10 };
      const res = await api.get('/deliveries', { params });
      setDeliveries(res.data.items);
      setTotalPages(res.data.total_pages);
      setTotalItems(res.data.total);
    } catch (err) {
      console.error('Error fetching deliveries', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      const res = await api.get('/customers?page_size=50');
      setCustomers(res.data.items || []);
      if (res.data.items?.length > 0 && !formData.customer_id) {
        setFormData(prev => ({ ...prev, customer_id: res.data.items[0].id }));
      }
    } catch (err) {
      console.error('Error fetching customers for select', err);
    }
  };

  useEffect(() => {
    fetchDeliveries();
    fetchCustomers();
  }, [page]);

  const handleOpenCreate = () => {
    setEditingId(null);
    setFormData({
      customer_id: customers[0]?.id || '',
      pickup_address: 'Hub Depot, Chicago, IL',
      delivery_address: '',
      pickup_lat: 41.8781,
      pickup_lng: -87.6298,
      delivery_lat: 41.8900,
      delivery_lng: -87.6240,
      weight_kg: 100.0,
      volume_m3: 0.5,
      priority: 'MEDIUM',
      notes: ''
    });
    setIsModalOpen(true);
  };

  const handleStatusChange = async (deliveryId, newStatus) => {
    try {
      await api.put(`/deliveries/${deliveryId}`, { status: newStatus });
      fetchDeliveries();
    } catch (err) {
      alert(err.message || 'Failed to update delivery status');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await api.put(`/deliveries/${editingId}`, formData);
      } else {
        await api.post('/deliveries', formData);
      }
      setIsModalOpen(false);
      fetchDeliveries();
    } catch (err) {
      alert(err.message || 'Operation failed');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete delivery order?')) {
      try {
        await api.delete(`/deliveries/${id}`);
        fetchDeliveries();
      } catch (err) {
        alert(err.message || 'Delete failed');
      }
    }
  };

  const columns = [
    {
      header: 'Tracking Code',
      accessor: 'tracking_number',
      render: (row) => (
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Package className="w-4 h-4" />
          </div>
          <div>
            <div className="font-bold text-indigo-400 font-mono">{row.tracking_number}</div>
            <div className="text-xs text-slate-400">{row.weight_kg} kg | {row.volume_m3} m³</div>
          </div>
        </div>
      )
    },
    {
      header: 'Delivery Address',
      accessor: 'delivery_address',
      render: (row) => (
        <div className="text-xs max-w-xs truncate flex items-center text-slate-300">
          <MapPin className="w-3.5 h-3.5 mr-1 text-rose-400 flex-shrink-0" />
          <span className="truncate">{row.delivery_address}</span>
        </div>
      )
    },
    {
      header: 'Priority & Status',
      accessor: 'status',
      render: (row) => (
        <div className="space-y-1">
          <div><StatusBadge status={row.status} /></div>
          <div><StatusBadge status={row.priority} /></div>
        </div>
      )
    },
    {
      header: 'Created At',
      accessor: 'created_at',
      render: (row) => (
        <span className="text-xs text-slate-400">
          {new Date(row.created_at).toLocaleDateString()}
        </span>
      )
    },
    {
      header: 'Admin Actions',
      accessor: 'id',
      render: (row) => (
        <div className="flex items-center space-x-2">
          {row.status === 'PENDING' && (
            <button
              onClick={() => handleStatusChange(row.id, 'IN_TRANSIT')}
              title="Start Delivery"
              className="px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20 transition-colors text-xs font-semibold flex items-center space-x-1"
            >
              <Play className="w-3 h-3 fill-emerald-400" />
              <span>Start</span>
            </button>
          )}

          {row.status === 'IN_TRANSIT' && (
            <button
              onClick={() => handleStatusChange(row.id, 'DELIVERED')}
              title="Complete Delivery"
              className="px-2.5 py-1 rounded-lg bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/20 transition-colors text-xs font-semibold flex items-center space-x-1"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Complete</span>
            </button>
          )}

          {row.status === 'DELIVERED' && (
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 flex items-center space-x-1">
              <CheckCircle2 className="w-3 h-3" />
              <span>Done</span>
            </span>
          )}

          <button
            onClick={() => handleDelete(row.id)}
            title="Delete Order"
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
        title="Delivery Order Management"
        subtitle="Track package shipments, start/complete deliveries, set priorities, and schedule dispatch"
      />

      <div className="p-8 max-w-7xl mx-auto space-y-6">
        <DataTable
          columns={columns}
          data={deliveries}
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
              <span>Create Delivery Order</span>
            </button>
          }
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create New Package Delivery Order"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Customer Account *</label>
            <select
              required
              value={formData.customer_id}
              onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
              className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="" disabled>Select Customer</option>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.company_name || c.email})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Pickup Address *</label>
            <input
              type="text"
              required
              value={formData.pickup_address}
              onChange={(e) => setFormData({ ...formData, pickup_address: e.target.value })}
              className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Delivery Destination Address *</label>
            <textarea
              required
              rows={2}
              value={formData.delivery_address}
              onChange={(e) => setFormData({ ...formData, delivery_address: e.target.value })}
              placeholder="250 Michigan Ave, Chicago, IL"
              className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Destination Latitude</label>
              <input
                type="number"
                step="any"
                required
                value={formData.delivery_lat}
                onChange={(e) => setFormData({ ...formData, delivery_lat: parseFloat(e.target.value) })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Destination Longitude</label>
              <input
                type="number"
                step="any"
                required
                value={formData.delivery_lng}
                onChange={(e) => setFormData({ ...formData, delivery_lng: parseFloat(e.target.value) })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Weight (kg) *</label>
              <input
                type="number"
                step="any"
                required
                value={formData.weight_kg}
                onChange={(e) => setFormData({ ...formData, weight_kg: parseFloat(e.target.value) })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Priority Tier</label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              >
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH">HIGH</option>
                <option value="URGENT">URGENT</option>
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
              Create Delivery Order
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
