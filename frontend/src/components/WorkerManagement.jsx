import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Plus, Edit, Trash2, Users, ArrowLeft } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const WorkerManagement = ({ onBack }) => {
  const [workers, setWorkers] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingWorker, setEditingWorker] = useState(null);
  const [newWorker, setNewWorker] = useState({
    name: '',
    rate: 95,
    position: '',
    phone: '',
    email: ''
  });
  const { toast } = useToast();

  useEffect(() => {
    loadWorkers();
  }, []);

  const loadWorkers = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      if (backendUrl) {
        // Try to load workers from backend
        const response = await fetch(`${backendUrl}/api/workers`);
        if (response.ok) {
          const workersData = await response.json();
          const formattedWorkers = workersData.map(worker => ({
            id: worker.id,
            name: worker.name,
            rate: worker.rate || 95,
            position: worker.position || '',
            phone: worker.phone || '',
            email: worker.email || ''
          }));
          setWorkers(formattedWorkers);
          // Also update localStorage for fallback
          localStorage.setItem('saved_workers', JSON.stringify(formattedWorkers));
        } else {
          console.warn('Failed to load workers from backend, using localStorage fallback');
          loadLocalStorageData();
        }
      } else {
        loadLocalStorageData();
      }
    } catch (error) {
      console.warn('Backend connection failed, using localStorage fallback:', error);
      loadLocalStorageData();
    }
  };

  const loadLocalStorageData = () => {
    // Load workers from localStorage (fallback)
    const savedWorkers = localStorage.getItem('saved_workers');
    if (savedWorkers) {
      setWorkers(JSON.parse(savedWorkers));
    } else {
      // Default workers
      const defaultWorkers = [
        { id: 1, name: "Jesus Garcia", rate: 95, position: "Foreman", phone: "", email: "" },
        { id: 2, name: "Mike Rodriguez", rate: 95, position: "Technician", phone: "", email: "" },
        { id: 3, name: "Sarah Johnson", rate: 85, position: "Apprentice", phone: "", email: "" }
      ];
      setWorkers(defaultWorkers);
      localStorage.setItem('saved_workers', JSON.stringify(defaultWorkers));
    }
  };

  const saveWorkers = (updatedWorkers) => {
    setWorkers(updatedWorkers);
    localStorage.setItem('saved_workers', JSON.stringify(updatedWorkers));
  };

  const handleAddWorker = async () => {
    if (!newWorker.name.trim()) {
      toast({
        title: "Name Required",
        description: "Please enter a worker name.",
        variant: "destructive"
      });
      return;
    }

    const workerData = {
      name: newWorker.name.trim(),
      rate: parseFloat(newWorker.rate) || 95,
      position: newWorker.position.trim(),
      phone: newWorker.phone.trim(),
      email: newWorker.email.trim()
    };

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      let savedWorker = null;
      
      if (backendUrl) {
        // Try to save to backend
        const response = await fetch(`${backendUrl}/api/workers`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(workerData)
        });
        
        if (response.ok) {
          savedWorker = await response.json();
        } else {
          console.warn('Failed to save worker to backend, using localStorage fallback');
          savedWorker = { id: Date.now(), ...workerData };
        }
      } else {
        savedWorker = { id: Date.now(), ...workerData };
      }
      
      // Update local state and localStorage (fallback)
      const updatedWorkers = [...workers, savedWorker];
      setWorkers(updatedWorkers);
      localStorage.setItem('saved_workers', JSON.stringify(updatedWorkers));
      
      setNewWorker({ name: '', rate: 95, position: '', phone: '', email: '' });
      setShowAddModal(false);
      
      toast({
        title: "Worker Added",
        description: `${savedWorker.name} has been added to the worker database.`,
      });
    } catch (error) {
      console.error('Error adding worker:', error);
      toast({
        title: "Error",
        description: "Failed to add worker. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleEditWorker = (worker) => {
    setEditingWorker(worker);
    setNewWorker({
      name: worker.name,
      rate: worker.rate,
      position: worker.position || '',
      phone: worker.phone || '',
      email: worker.email || ''
    });
    setShowAddModal(true);
  };

  const handleUpdateWorker = () => {
    if (!newWorker.name.trim()) {
      toast({
        title: "Name Required",
        description: "Please enter a worker name.",
        variant: "destructive"
      });
      return;
    }

    const updatedWorkers = workers.map(worker => 
      worker.id === editingWorker.id 
        ? {
            ...worker,
            name: newWorker.name.trim(),
            rate: parseFloat(newWorker.rate) || 95,
            position: newWorker.position.trim(),
            phone: newWorker.phone.trim(),
            email: newWorker.email.trim()
          }
        : worker
    );

    saveWorkers(updatedWorkers);
    
    setNewWorker({ name: '', rate: 95, position: '', phone: '', email: '' });
    setEditingWorker(null);
    setShowAddModal(false);
    
    toast({
      title: "Worker Updated",
      description: "Worker information has been updated.",
    });
  };

  const handleDeleteWorker = (workerId) => {
    if (window.confirm('Are you sure you want to delete this worker?')) {
      const updatedWorkers = workers.filter(worker => worker.id !== workerId);
      saveWorkers(updatedWorkers);
      
      toast({
        title: "Worker Deleted",
        description: "Worker has been removed from the database.",
      });
    }
  };

  const resetModal = () => {
    setNewWorker({ name: '', rate: 95, position: '', phone: '', email: '' });
    setEditingWorker(null);
    setShowAddModal(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={onBack} className="flex items-center gap-2">
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </Button>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">Worker Management</h1>
                  <p className="text-sm text-gray-500">Manage your team database</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Workers</p>
                  <p className="text-2xl font-bold text-gray-900">{workers.length}</p>
                </div>
                <Users className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Average Rate</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${workers.length > 0 ? (workers.reduce((sum, w) => sum + w.rate, 0) / workers.length).toFixed(0) : '0'}
                  </p>
                </div>
                <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-sm">$</span>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Workers</p>
                  <p className="text-2xl font-bold text-gray-900">{workers.length}</p>
                </div>
                <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
                  <Users className="w-4 h-4 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Workers Table */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Worker Database</CardTitle>
              <Button 
                onClick={() => setShowAddModal(true)}
                className="bg-green-600 hover:bg-green-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Worker
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {workers.length === 0 ? (
              <div className="text-center py-12">
                <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No workers yet</h3>
                <p className="text-gray-500 mb-4">Add your first worker to get started</p>
                <Button onClick={() => setShowAddModal(true)}>
                  <Plus className="w-4 h-4 mr-2" />
                  Add First Worker
                </Button>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Position</TableHead>
                    <TableHead>Hourly Rate</TableHead>
                    <TableHead>Phone</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {workers.map((worker) => (
                    <TableRow key={worker.id}>
                      <TableCell className="font-medium">{worker.name}</TableCell>
                      <TableCell>{worker.position || '-'}</TableCell>
                      <TableCell>${worker.rate}/hr</TableCell>
                      <TableCell>{worker.phone || '-'}</TableCell>
                      <TableCell>{worker.email || '-'}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleEditWorker(worker)}
                          >
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeleteWorker(worker.id)}
                            className="text-red-600 hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Add/Edit Worker Modal */}
      <Dialog open={showAddModal} onOpenChange={resetModal}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingWorker ? 'Edit Worker' : 'Add New Worker'}
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name*</Label>
              <Input
                id="name"
                value={newWorker.name}
                onChange={(e) => setNewWorker({...newWorker, name: e.target.value})}
                placeholder="Enter worker name"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="position">Position</Label>
              <Input
                id="position"
                value={newWorker.position}
                onChange={(e) => setNewWorker({...newWorker, position: e.target.value})}
                placeholder="e.g., Foreman, Technician, Apprentice"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="rate">Hourly Rate*</Label>
              <Input
                id="rate"
                type="number"
                value={newWorker.rate}
                onChange={(e) => setNewWorker({...newWorker, rate: e.target.value})}
                placeholder="95"
                step="0.01"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                value={newWorker.phone}
                onChange={(e) => setNewWorker({...newWorker, phone: e.target.value})}
                placeholder="Enter phone number"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={newWorker.email}
                onChange={(e) => setNewWorker({...newWorker, email: e.target.value})}
                placeholder="Enter email address"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={resetModal}>
              Cancel
            </Button>
            <Button 
              onClick={editingWorker ? handleUpdateWorker : handleAddWorker}
              className="bg-green-600 hover:bg-green-700"
            >
              {editingWorker ? 'Update Worker' : 'Add Worker'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default WorkerManagement;