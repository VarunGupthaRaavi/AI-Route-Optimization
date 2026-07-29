import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { DataTable } from '../components/DataTable';
import { StatusBadge } from '../components/StatusBadge';
import { Modal } from '../components/Modal';
import { api } from '../services/api';
import { Zap, Route as RouteIcon, UserCheck, Truck, MapPin, CheckCircle2, Loader2 } from 'lucide-react';

export const RoutesPage = () => {
  const [routes, setRoutes] = useState([]);
  const [pendingDeliveries, setPendingDeliveries] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [isOptimizeModalOpen, setIsOptimizeModalOpen] = useState(false);
  const [isAllocateModalOpen, setIsAllocateModalOpen] = useState(false);
  const [selectedRouteId, setSelectedRouteId] = useState(null);

  const [selectedDeliveryIds, setSelectedDeliveryIds] = useState([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState('');
  const [selectedDriverId, setSelectedDriverId] = useState('');
  const [optimizing, setOptimizing] = useState(false);

  const fetchRoutes = async () => {
    setLoading(true);
    try {
      const res = await api.get('/routes');
      setRoutes(res.data.items || []);
    } catch (err) {
      console.error('Error fetching routes', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingData = async () => {
    try {
      const [delRes, drivRes, vehRes] = await Promise.all([
        api.get('/deliveries?status=PENDING'),
        api.get('/drivers?status=IDLE'),
        api.get('/vehicles?status=AVAILABLE')
      ]);
      setPendingDeliveries(delRes.data.items || []);
      setDrivers(drivRes.data.items || []);
      setVehicles(vehRes.data.items || []);

      if (delRes.data.items?.length > 0) {
        setSelectedDeliveryIds(delRes.data.items.map(d => d.id));
      }
      if (drivRes.data.items?.length > 0) {
        setSelectedDriverId(drivRes.data.items[0].id);
      }
      if (vehRes.data.items?.length > 0) {
        setSelectedVehicleId(vehRes.data.items[0].id);
      }
    } catch (err) {
      console.error('Error fetching pending data', err);
    }
  };

  useEffect(() => {
    fetchRoutes();
    fetchPendingData();
  }, []);

  const handleRunOptimization = async (e) => {
    e.preventDefault();
    if (selectedDeliveryIds.length === 0) {
      alert('Please select at least one pending delivery order to optimize.');
      return;
    }
    setOptimizing(true);
    try {
      await api.post('/routes/optimize', {
        delivery_ids: selectedDeliveryIds,
        vehicle_id: selectedVehicleId || null
      });
      setIsOptimizeModalOpen(false);
      fetchRoutes();
      fetchPendingData();
    } catch (err) {
      alert(err.message || 'Route optimization failed');
    } finally {
      setOptimizing(false);
    }
  };

  const handleAllocateDriver = async (e) => {
    e.preventDefault();
    if (!selectedDriverId || !selectedRouteId) return;
    try {
      await api.post(`/routes/${selectedRouteId}/allocate-driver`, {
        driver_id: selectedDriverId,
        vehicle_id: selectedVehicleId || null
      });
      setIsAllocateModalOpen(false);
      fetchRoutes();
      fetchPendingData();
    } catch (err) {
      alert(err.message || 'Driver allocation failed');
    }
  };

  const handleOpenAllocate = (routeId) => {
    setSelectedRouteId(routeId);
    setIsAllocateModalOpen(true);
  };

  const toggleDeliverySelect = (id) => {
    if (selectedDeliveryIds.includes(id)) {
      setSelectedDeliveryIds(selectedDeliveryIds.filter(item => item !== id));
    } else {
      setSelectedDeliveryIds([...selectedDeliveryIds, id]);
    }
  };

  const columns = [
    {
      header: 'Route Code',
      accessor: 'route_code',
      render: (row) => (
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <RouteIcon className="w-4 h-4" />
          </div>
          <div>
            <div className="font-bold text-slate-100 font-mono">{row.route_code}</div>
            <div className="text-xs text-slate-400">{row.total_deliveries} delivery stops</div>
          </div>
        </div>
      )
    },
    {
      header: 'Distance & Duration',
      accessor: 'total_distance_km',
      render: (row) => (
        <div className="text-xs space-y-0.5">
          <div className="text-slate-200 font-semibold">{row.total_distance_km} km total</div>
          <div className="text-slate-400">~{row.estimated_duration_minutes} mins duration</div>
        </div>
      )
    },
    {
      header: 'Route State',
      accessor: 'status',
      render: (row) => <StatusBadge status={row.status} />
    },
    {
      header: 'Allocation & Dispatch',
      accessor: 'id',
      render: (row) => (
        <div>
          {row.status === 'OPTIMIZED' || row.status === 'DRAFT' ? (
            <button
              onClick={() => handleOpenAllocate(row.id)}
              className="px-3 py-1.5 rounded-lg bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 text-xs font-semibold hover:bg-indigo-600/50 transition-colors flex items-center space-x-1.5"
            >
              <UserCheck className="w-3.5 h-3.5" />
              <span>Allocate Driver</span>
            </button>
          ) : (
            <span className="text-xs text-emerald-400 font-medium flex items-center">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
              Driver Dispatched
            </span>
          )}
        </div>
      )
    }
  ];

  return (
    <div className="flex-1 pb-12">
      <Header
        title="AI Logistics Route Optimization"
        subtitle="Generate TSP multi-stop optimized route plans, assign fleet drivers, and monitor dispatch"
      />

      <div className="p-8 max-w-7xl mx-auto space-y-6">
        <DataTable
          columns={columns}
          data={routes}
          loading={loading}
          searchQuery=""
          onSearchChange={() => {}}
          page={1}
          totalPages={1}
          totalItems={routes.length}
          onPageChange={() => {}}
          actionButton={
            <button
              onClick={() => setIsOptimizeModalOpen(true)}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white font-bold text-xs flex items-center space-x-2 shadow-xl shadow-indigo-600/30 hover:opacity-90 transition-opacity"
            >
              <Zap className="w-4 h-4 text-amber-300" />
              <span>Run AI Route Optimizer</span>
            </button>
          }
        />
      </div>

      {/* AI Optimization Trigger Modal */}
      <Modal
        isOpen={isOptimizeModalOpen}
        onClose={() => setIsOptimizeModalOpen(false)}
        title="Run AI Logistics Route Optimization (TSP)"
      >
        <form onSubmit={handleRunOptimization} className="space-y-4">
          <p className="text-xs text-slate-400">
            Select pending package orders to generate an optimal multi-stop route minimizing total travel distance.
          </p>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-2">Pending Orders ({pendingDeliveries.length} Available)</label>
            <div className="max-h-48 overflow-y-auto space-y-2 pr-1">
              {pendingDeliveries.length === 0 ? (
                <p className="text-xs text-slate-500 py-4 text-center">No pending orders available for optimization.</p>
              ) : (
                pendingDeliveries.map((del) => (
                  <label key={del.id} className="flex items-center justify-between p-3 rounded-xl bg-slate-900/60 border border-slate-800 cursor-pointer hover:border-indigo-500/40">
                    <div className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={selectedDeliveryIds.includes(del.id)}
                        onChange={() => toggleDeliverySelect(del.id)}
                        className="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-indigo-500"
                      />
                      <div>
                        <div className="text-xs font-mono font-bold text-indigo-400">{del.tracking_number}</div>
                        <div className="text-[11px] text-slate-300 truncate max-w-xs">{del.delivery_address}</div>
                      </div>
                    </div>
                    <StatusBadge status={del.priority} />
                  </label>
                ))
              )}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Target Vehicle (Optional Capacity Constraint)</label>
            <select
              value={selectedVehicleId}
              onChange={(e) => setSelectedVehicleId(e.target.value)}
              className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="">Auto Select Available Fleet Vehicle</option>
              {vehicles.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.vehicle_model} ({v.license_plate}) - {v.capacity_kg} kg cap
                </option>
              ))}
            </select>
          </div>

          <div className="pt-4 border-t border-slate-800 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setIsOptimizeModalOpen(false)}
              className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-medium hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={optimizing || selectedDeliveryIds.length === 0}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 flex items-center space-x-2 disabled:opacity-50"
            >
              {optimizing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Computing Nearest-Neighbor TSP...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 text-amber-300" />
                  <span>Generate Optimized Route</span>
                </>
              )}
            </button>
          </div>
        </form>
      </Modal>

      {/* Driver Allocation Modal */}
      <Modal
        isOpen={isAllocateModalOpen}
        onClose={() => setIsAllocateModalOpen(false)}
        title="Allocate Driver & Dispatch Route"
      >
        <form onSubmit={handleAllocateDriver} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Select Available Fleet Driver *</label>
            <select
              required
              value={selectedDriverId}
              onChange={(e) => setSelectedDriverId(e.target.value)}
              className="w-full bg-slate-900/60 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            >
              <option value="" disabled>Select Idle Driver</option>
              {drivers.map((d) => (
                <option key={d.id} value={d.id}>
                  Commercial License: {d.license_number} (Rating: {d.rating})
                </option>
              ))}
            </select>
          </div>

          <div className="pt-4 border-t border-slate-800 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setIsAllocateModalOpen(false)}
              className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-medium hover:bg-slate-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30"
            >
              Confirm Driver Allocation & Dispatch
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
