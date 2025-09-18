import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Calendar } from './ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Badge } from './ui/badge';
import { format } from 'date-fns';
import { 
  ArrowLeft, 
  Plus, 
  Users, 
  Calendar as CalendarIcon,
  DollarSign,
  TrendingUp,
  Edit,
  Trash2,
  Phone,
  Mail,
  AlertTriangle,
  Search,
  Filter
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';

const EmployeeManagement = ({ onBack }) => {
  const [employees, setEmployees] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [positionFilter, setPositionFilter] = useState('');
  const [newEmployee, setNewEmployee] = useState({
    name: '',
    hourly_rate: '',
    position: '',
    hire_date: new Date(),
    phone: '',
    email: '',
    emergency_contact: ''
  });
  const [editEmployee, setEditEmployee] = useState({});
  
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();

  const positions = [
    'Apprentice Electrician',
    'Journeyman Electrician', 
    'Senior Electrician',
    'Master Electrician',
    'Foreman',
    'Project Manager',
    'Helper',
    'Welder',
    'Pipe Fitter'
  ];

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (backendUrl) {
        const response = await fetch(`${backendUrl}/api/employees`);
        if (response.ok) {
          const employeesData = await response.json();
          setEmployees(employeesData);
        }
      }
    } catch (error) {
      console.warn('Failed to load employees:', error);
    }
  };

  const handleCreateEmployee = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl) {
        toast({
          title: "Backend Error",
          description: "Backend URL not configured",
          variant: "destructive"
        });
        return;
      }

      const employeeData = {
        name: newEmployee.name,
        base_pay: parseFloat(newEmployee.base_pay) || 0,
        burden_cost: parseFloat(newEmployee.burden_cost) || 0,
        position: newEmployee.position,
        hire_date: newEmployee.hire_date.toISOString(),
        phone: newEmployee.phone,
        email: newEmployee.email,
        emergency_contact: newEmployee.emergency_contact
      };

      const response = await fetch(`${backendUrl}/api/employees`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(employeeData)
      });

      if (response.ok) {
        const createdEmployee = await response.json();
        setEmployees(prev => [createdEmployee, ...prev]);
        setShowCreateModal(false);
        resetNewEmployee();
        
        toast({
          title: "Employee Added",
          description: `${createdEmployee.name} has been added to the system.`,
        });
      } else {
        throw new Error('Failed to create employee');
      }
    } catch (error) {
      toast({
        title: "Creation Failed",
        description: "Failed to add employee. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleUpdateEmployee = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl || !selectedEmployee) return;

      const updateData = {
        name: editEmployee.name,
        base_pay: parseFloat(editEmployee.base_pay) || 0,
        burden_cost: parseFloat(editEmployee.burden_cost) || 0,
        position: editEmployee.position,
        hire_date: editEmployee.hire_date,
        phone: editEmployee.phone,
        email: editEmployee.email,
        emergency_contact: editEmployee.emergency_contact
      };

      const response = await fetch(`${backendUrl}/api/employees/${selectedEmployee.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
      });

      if (response.ok) {
        const updatedEmployee = await response.json();
        setEmployees(prev => prev.map(emp => 
          emp.id === selectedEmployee.id ? updatedEmployee : emp
        ));
        setShowEditModal(false);
        setSelectedEmployee(null);
        
        toast({
          title: "Employee Updated",
          description: `${updatedEmployee.name} has been updated successfully.`,
        });
      } else {
        throw new Error('Failed to update employee');
      }
    } catch (error) {
      toast({
        title: "Update Failed",
        description: "Failed to update employee. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleDeleteEmployee = async (employeeId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl) return;

      const response = await fetch(`${backendUrl}/api/employees/${employeeId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setEmployees(prev => prev.filter(emp => emp.id !== employeeId));
        toast({
          title: "Employee Deleted",
          description: "Employee has been deleted successfully.",
        });
      }
    } catch (error) {
      toast({
        title: "Deletion Failed",
        description: "Failed to delete employee.",
        variant: "destructive"
      });
    }
  };

  const resetNewEmployee = () => {
    setNewEmployee({
      name: '',
      base_pay: '',
      burden_cost: '',
      position: '',
      hire_date: new Date(),
      phone: '',
      email: '',
      emergency_contact: ''
    });
  };

  const handleInputChange = (field, value) => {
    setNewEmployee(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleEditInputChange = (field, value) => {
    setEditEmployee(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const openEditModal = (employee) => {
    setSelectedEmployee(employee);
    setEditEmployee({
      name: employee.name,
      base_pay: employee.base_pay.toString(),
      burden_cost: employee.burden_cost.toString(),
      position: employee.position,
      hire_date: employee.hire_date,
      phone: employee.phone || '',
      email: employee.email || '',
      emergency_contact: employee.emergency_contact || ''
    });
    setShowEditModal(true);
  };

  const getStatusColor = (status) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      inactive: 'bg-yellow-100 text-yellow-800',
      terminated: 'bg-red-100 text-red-800'
    };
    return colors[status] || colors.active;
  };

  const getTotalCostPerHour = (employee) => {
    return (employee.base_pay || 0) + (employee.burden_cost || 0);
  };

  const getUniquePositions = () => {
    return [...new Set(employees.map(emp => emp.position).filter(Boolean))];
  };

  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = !searchTerm || 
      employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      employee.position.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === '' || statusFilter === 'all' || employee.status === statusFilter;
    const matchesPosition = positionFilter === '' || positionFilter === 'all' || employee.position === positionFilter;
    
    return matchesSearch && matchesStatus && matchesPosition;
  });

  const totalEmployees = filteredEmployees.length;
  const averageBasePay = filteredEmployees.length > 0 
    ? filteredEmployees.reduce((sum, emp) => sum + (emp.base_pay || 0), 0) / filteredEmployees.length
    : 0;
  const totalPayrollCost = filteredEmployees.reduce((sum, emp) => sum + getTotalCostPerHour(emp), 0);

  return (
    <>
      <div className={`min-h-screen transition-all duration-300 ${themeClasses.background}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-4">
              <Button 
                variant="outline" 
                onClick={onBack}
                className={`flex items-center gap-2 ${themeClasses.button.secondary}`}
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                  Employee Management
                </h1>
                <p className={themeClasses.text.secondary}>
                  Manage employee information and cost calculations
                </p>
              </div>
            </div>
            
            <Button 
              onClick={() => setShowCreateModal(true)}
              className={themeClasses.button.primary}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Employee
            </Button>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Total Employees
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {totalEmployees}
                    </p>
                  </div>
                  <Users className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Avg Base Pay
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      ${averageBasePay.toFixed(2)}
                    </p>
                  </div>
                  <DollarSign className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Total Hourly Cost
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      ${totalPayrollCost.toFixed(2)}
                    </p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Active Employees
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {employees.filter(emp => emp.status === 'active').length}
                    </p>
                  </div>
                  <Users className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Search and Filters */}
          <div className="mb-6">
            <div className="flex gap-4 items-center flex-wrap">
              <div className="relative flex-1 max-w-md">
                <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 ${themeClasses.text.secondary}`} />
                <Input
                  placeholder="Search employees..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className={`pl-10 ${themeClasses.input}`}
                />
              </div>
              
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className={`w-40 ${themeClasses.input}`}>
                  <SelectValue placeholder="All Status" />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                  <SelectItem value="terminated">Terminated</SelectItem>
                </SelectContent>
              </Select>

              <Select value={positionFilter} onValueChange={setPositionFilter}>
                <SelectTrigger className={`w-48 ${themeClasses.input}`}>
                  <SelectValue placeholder="All Positions" />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  <SelectItem value="all">All Positions</SelectItem>
                  {getUniquePositions().map((position) => (
                    <SelectItem key={position} value={position}>
                      {position}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {(searchTerm || (statusFilter && statusFilter !== 'all') || (positionFilter && positionFilter !== 'all')) && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    setSearchTerm('');
                    setStatusFilter('');
                    setPositionFilter('');
                  }}
                  className={themeClasses.button.secondary}
                >
                  Clear Filters
                </Button>
              )}
            </div>
          </div>

          {/* Employees Table */}
          {filteredEmployees.length === 0 ? (
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-12 text-center">
                <Users className={`w-16 h-16 mx-auto mb-4 ${themeClasses.text.muted}`} />
                <h3 className={`text-lg font-medium mb-2 ${themeClasses.text.primary}`}>
                  {employees.length === 0 ? 'No Employees Yet' : 'No Employees Match Filters'}
                </h3>
                <p className={`mb-6 ${themeClasses.text.secondary}`}>
                  {employees.length === 0 
                    ? 'Add your first employee to start tracking costs and assignments.'
                    : 'Try adjusting your search or filter criteria.'
                  }
                </p>
                <Button 
                  onClick={() => setShowCreateModal(true)}
                  className={themeClasses.button.primary}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add First Employee
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardHeader>
                <CardTitle className={themeClasses.text.primary}>
                  Employees ({filteredEmployees.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                        <TableHead className={themeClasses.text.primary}>Name</TableHead>
                        <TableHead className={themeClasses.text.primary}>Position</TableHead>
                        <TableHead className={themeClasses.text.primary}>Base Pay</TableHead>
                        <TableHead className={themeClasses.text.primary}>Burden Cost</TableHead>
                        <TableHead className={themeClasses.text.primary}>Total/Hour</TableHead>
                        <TableHead className={themeClasses.text.primary}>Hire Date</TableHead>
                        <TableHead className={themeClasses.text.primary}>Status</TableHead>
                        <TableHead className={themeClasses.text.primary}>Contact</TableHead>
                        <TableHead className={themeClasses.text.primary}>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredEmployees.map((employee) => (
                        <TableRow key={employee.id} className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                          <TableCell className={`font-medium ${themeClasses.text.primary}`}>
                            {employee.name}
                          </TableCell>
                          <TableCell className={themeClasses.text.primary}>
                            {employee.position}
                          </TableCell>
                          <TableCell className={themeClasses.text.primary}>
                            ${employee.base_pay.toFixed(2)}
                          </TableCell>
                          <TableCell className={themeClasses.text.primary}>
                            ${employee.burden_cost.toFixed(2)}
                          </TableCell>
                          <TableCell className={`font-semibold ${themeClasses.text.primary}`}>
                            ${getTotalCostPerHour(employee).toFixed(2)}
                          </TableCell>
                          <TableCell className={themeClasses.text.primary}>
                            {format(new Date(employee.hire_date), 'MM/dd/yyyy')}
                          </TableCell>
                          <TableCell>
                            <Badge className={getStatusColor(employee.status)}>
                              {employee.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              {employee.phone && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => window.open(`tel:${employee.phone}`)}
                                  className="p-1"
                                >
                                  <Phone className="w-4 h-4" />
                                </Button>
                              )}
                              {employee.email && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => window.open(`mailto:${employee.email}`)}
                                  className="p-1"
                                >
                                  <Mail className="w-4 h-4" />
                                </Button>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => openEditModal(employee)}
                                className={themeClasses.button.secondary}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDeleteEmployee(employee.id)}
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
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Create Employee Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className={`sm:max-w-[600px] ${themeClasses.modal}`}>
          <DialogHeader>
            <DialogTitle className={themeClasses.text.primary}>Add New Employee</DialogTitle>
          </DialogHeader>
          
          <div className="grid gap-4 py-4 max-h-96 overflow-y-auto">
            {/* Name and Position */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Full Name*</Label>
                <Input
                  value={newEmployee.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className={themeClasses.input}
                  placeholder="John Smith"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Position*</Label>
                <Select value={newEmployee.position} onValueChange={(value) => handleInputChange('position', value)}>
                  <SelectTrigger className={themeClasses.input}>
                    <SelectValue placeholder="Select position" />
                  </SelectTrigger>
                  <SelectContent className={themeClasses.modal}>
                    {positions.map((position) => (
                      <SelectItem key={position} value={position}>
                        {position}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Pay Information */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Base Pay ($/hour)*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newEmployee.base_pay}
                  onChange={(e) => handleInputChange('base_pay', e.target.value)}
                  className={themeClasses.input}
                  placeholder="28.50"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Burden Cost ($/hour)*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newEmployee.burden_cost}
                  onChange={(e) => handleInputChange('burden_cost', e.target.value)}
                  className={themeClasses.input}
                  placeholder="12.75"
                />
                <p className={`text-xs ${themeClasses.text.secondary}`}>
                  Benefits, taxes, insurance, etc.
                </p>
              </div>
            </div>

            {/* Hire Date */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Hire Date*</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      `w-full justify-start text-left font-normal ${themeClasses.button.secondary}`,
                      !newEmployee.hire_date && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {newEmployee.hire_date ? format(newEmployee.hire_date, "MM/dd/yyyy") : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className={`w-auto p-0 ${themeClasses.modal}`} align="start">
                  <Calendar
                    mode="single"
                    selected={newEmployee.hire_date}
                    onSelect={(date) => handleInputChange('hire_date', date)}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            {/* Contact Information */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Phone</Label>
                <Input
                  type="tel"
                  value={newEmployee.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className={themeClasses.input}
                  placeholder="(555) 123-4567"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Email</Label>
                <Input
                  type="email"
                  value={newEmployee.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className={themeClasses.input}
                  placeholder="john@example.com"
                />
              </div>
            </div>

            {/* Emergency Contact */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Emergency Contact</Label>
              <Input
                value={newEmployee.emergency_contact}
                onChange={(e) => handleInputChange('emergency_contact', e.target.value)}
                className={themeClasses.input}
                placeholder="Jane Smith - (555) 987-6543"
              />
            </div>

            {/* Cost Summary */}
            {newEmployee.base_pay && newEmployee.burden_cost && (
              <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-white/10' : 'bg-blue-50'} border`}>
                <div className="flex justify-between items-center">
                  <span className={`text-sm ${themeClasses.text.secondary}`}>Total Cost per Hour:</span>
                  <span className={`font-bold text-lg ${themeClasses.text.primary}`}>
                    ${(parseFloat(newEmployee.base_pay || 0) + parseFloat(newEmployee.burden_cost || 0)).toFixed(2)}
                  </span>
                </div>
              </div>
            )}
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setShowCreateModal(false);
                resetNewEmployee();
              }}
              className={themeClasses.button.secondary}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleCreateEmployee}
              disabled={!newEmployee.name || !newEmployee.position || !newEmployee.base_pay || !newEmployee.burden_cost}
              className={themeClasses.button.primary}
            >
              Add Employee
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Employee Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className={`sm:max-w-[600px] ${themeClasses.modal}`}>
          <DialogHeader>
            <DialogTitle className={themeClasses.text.primary}>
              Edit Employee - {selectedEmployee?.name}
            </DialogTitle>
          </DialogHeader>
          
          <div className="grid gap-4 py-4 max-h-96 overflow-y-auto">
            {/* Name and Position */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Full Name*</Label>
                <Input
                  value={editEmployee.name || ''}
                  onChange={(e) => handleEditInputChange('name', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Position*</Label>
                <Select value={editEmployee.position || ''} onValueChange={(value) => handleEditInputChange('position', value)}>
                  <SelectTrigger className={themeClasses.input}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className={themeClasses.modal}>
                    {positions.map((position) => (
                      <SelectItem key={position} value={position}>
                        {position}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Pay Information */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Base Pay ($/hour)*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={editEmployee.base_pay || ''}
                  onChange={(e) => handleEditInputChange('base_pay', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Burden Cost ($/hour)*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={editEmployee.burden_cost || ''}
                  onChange={(e) => handleEditInputChange('burden_cost', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
            </div>

            {/* Contact Information */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Phone</Label>
                <Input
                  type="tel"
                  value={editEmployee.phone || ''}
                  onChange={(e) => handleEditInputChange('phone', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Email</Label>
                <Input
                  type="email"
                  value={editEmployee.email || ''}
                  onChange={(e) => handleEditInputChange('email', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Emergency Contact</Label>
              <Input
                value={editEmployee.emergency_contact || ''}
                onChange={(e) => handleEditInputChange('emergency_contact', e.target.value)}
                className={themeClasses.input}
              />
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setShowEditModal(false);
                setSelectedEmployee(null);
              }}
              className={themeClasses.button.secondary}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleUpdateEmployee}
              className={themeClasses.button.primary}
            >
              Update Employee
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default EmployeeManagement;