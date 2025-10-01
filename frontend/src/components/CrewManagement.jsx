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
  Search,
  Filter
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';

const CrewManagement = ({ onBack }) => {
  const [crewMembers, setCrewMembers] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedCrewMember, setSelectedCrewMember] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [positionFilter, setPositionFilter] = useState('');
  const [newCrewMember, setNewCrewMember] = useState({
    name: '',
    cost_rate: '',  // Changed from hourly_rate to cost_rate
    position: '',
    hire_date: new Date(),
    phone: '',
    email: '',
    active: true
  });
  const [editCrewMember, setEditCrewMember] = useState({});
  
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();

  const positions = [
    'Helper',
    'Fitter',
    'Journeyman',
    'Foreman',
    'Superintendent',
    'Project Manager'
  ];

  useEffect(() => {
    loadCrewMembers();
  }, []);

  const loadCrewMembers = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (backendUrl) {
        const installersResponse = await fetch(`${backendUrl}/api/installers`);
        if (installersResponse.ok) {
          const installersData = await installersResponse.json();
          setCrewMembers(installersData);
        } else {
          console.warn('Failed to fetch installers from API');
        }
      }
    } catch (error) {
      console.warn('Failed to load crew members:', error);
    }
  };

  const handleCreateCrewMember = async () => {
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

      const installerData = {
        name: newCrewMember.name,
        cost_rate: parseFloat(newCrewMember.cost_rate) || 0,
        position: newCrewMember.position || 'Installer',
        hire_date: newCrewMember.hire_date.toISOString().split('T')[0], // Date only
        phone: newCrewMember.phone,
        email: newCrewMember.email,
        active: newCrewMember.active !== false
      };

      // Create using new installers endpoint
      const response = await fetch(`${backendUrl}/api/installers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(installerData)
      });

      if (response.ok) {
        const createdMember = await response.json();
        setCrewMembers(prev => [createdMember, ...prev]);
        setShowCreateModal(false);
        resetNewCrewMember();
        
        toast({
          title: "Installer Added",
          description: `${createdMember.name} has been added to the crew.`,
        });
        
        loadCrewMembers(); // Refresh the list
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create installer');
      }
    } catch (error) {
      toast({
        title: "Creation Failed",
        description: "Failed to add crew member. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleUpdateCrewMember = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl || !selectedCrewMember) return;

      const updateData = {
        name: editCrewMember.name,
        cost_rate: parseFloat(editCrewMember.cost_rate) || 0,
        gc_billing_rate: parseFloat(editCrewMember.gc_billing_rate) || 95.0,
        position: editCrewMember.position,
        hire_date: editCrewMember.hire_date,
        phone: editCrewMember.phone,
        email: editCrewMember.email,
        emergency_contact: editCrewMember.emergency_contact
      };

      const response = await fetch(`${backendUrl}/api/employees/${selectedCrewMember.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
      });

      if (response.ok) {
        const updatedMember = await response.json();
        setCrewMembers(prev => prev.map(member => 
          member.id === selectedCrewMember.id ? updatedMember : member
        ));
        setShowEditModal(false);
        setSelectedCrewMember(null);
        
        toast({
          title: "Crew Member Updated",
          description: `${updatedMember.name} has been updated successfully.`,
        });
      } else {
        throw new Error('Failed to update crew member');
      }
    } catch (error) {
      toast({
        title: "Update Failed",
        description: "Failed to update crew member. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleDeleteCrewMember = async (memberId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl) return;

      const response = await fetch(`${backendUrl}/api/employees/${memberId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setCrewMembers(prev => prev.filter(member => member.id !== memberId));
        toast({
          title: "Crew Member Removed",
          description: "Crew member has been removed successfully.",
        });
      }
    } catch (error) {
      toast({
        title: "Deletion Failed",
        description: "Failed to remove crew member.",
        variant: "destructive"
      });
    }
  };

  const resetNewCrewMember = () => {
    setNewCrewMember({
      name: '',
      cost_rate: '',
      position: '',
      hire_date: new Date(),
      phone: '',
      email: '',
      active: true
    });
  };

  const handleInputChange = (field, value) => {
    setNewCrewMember(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleEditInputChange = (field, value) => {
    setEditCrewMember(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const openEditModal = (member) => {
    setSelectedCrewMember(member);
    setEditCrewMember({
      name: member.name,
      hourly_rate: (member.hourly_rate || 0).toString(),
      gc_billing_rate: (member.gc_billing_rate || 95.0).toString(),
      position: member.position,
      hire_date: member.hire_date,
      phone: member.phone || '',
      email: member.email || '',
      emergency_contact: member.emergency_contact || ''
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

  const getTotalCostPerHour = (member) => {
    // New Rhino Platform schema uses cost_rate
    return member.cost_rate || 0;
  };

  const getUniquePositions = () => {
    return [...new Set(crewMembers.map(member => member.position).filter(Boolean))];
  };

  const filteredCrewMembers = crewMembers.filter(member => {
    const matchesSearch = !searchTerm || 
      member.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      member.position.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === '' || statusFilter === 'all' || member.status === statusFilter;
    const matchesPosition = positionFilter === '' || positionFilter === 'all' || member.position === positionFilter;
    
    return matchesSearch && matchesStatus && matchesPosition;
  });

  const totalCrewMembers = filteredCrewMembers.length;
  const averageHourlyRate = filteredCrewMembers.length > 0 
    ? filteredCrewMembers.reduce((sum, member) => sum + (member.cost_rate || 0), 0) / filteredCrewMembers.length
    : 0;
  const totalPayrollCost = filteredCrewMembers.reduce((sum, member) => sum + getTotalCostPerHour(member), 0);

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
                  Crew Management
                </h1>
                <p className={themeClasses.text.secondary}>
                  Manage crew member information and cost calculations
                </p>
              </div>
            </div>
            
            <Button 
              onClick={() => setShowCreateModal(true)}
              className={themeClasses.button.primary}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Crew Member
            </Button>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Total Crew Members
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {totalCrewMembers}
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
                      Avg Hourly Rate
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      ${(averageHourlyRate || 0).toFixed(2)}
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
                      ${(totalPayrollCost || 0).toFixed(2)}
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
                      Active Crew
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {crewMembers.filter(member => member.status === 'active').length}
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
                  placeholder="Search crew members..."
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

          {/* Crew Members Table */}
          {filteredCrewMembers.length === 0 ? (
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-12 text-center">
                <Users className={`w-16 h-16 mx-auto mb-4 ${themeClasses.text.muted}`} />
                <h3 className={`text-lg font-medium mb-2 ${themeClasses.text.primary}`}>
                  {crewMembers.length === 0 ? 'No Crew Members Yet' : 'No Crew Members Match Filters'}
                </h3>
                <p className={`mb-6 ${themeClasses.text.secondary}`}>
                  {crewMembers.length === 0 
                    ? 'Add your first crew member to start tracking costs and assignments.'
                    : 'Try adjusting your search or filter criteria.'
                  }
                </p>
                <Button 
                  onClick={() => setShowCreateModal(true)}
                  className={themeClasses.button.primary}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add First Crew Member
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardHeader>
                <CardTitle className={themeClasses.text.primary}>
                  Crew Members ({filteredCrewMembers.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                        <TableHead className={themeClasses.text.primary}>Name</TableHead>
                        <TableHead className={themeClasses.text.primary}>Position</TableHead>
                        <TableHead className={themeClasses.text.primary}>Cost Rate</TableHead>
                        <TableHead className={themeClasses.text.primary}>Hire Date</TableHead>
                        <TableHead className={themeClasses.text.primary}>Status</TableHead>
                        <TableHead className={themeClasses.text.primary}>Contact</TableHead>
                        <TableHead className={themeClasses.text.primary}>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredCrewMembers.map((member) => (
                        <TableRow key={member.id} className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                          <TableCell className={`font-medium ${themeClasses.text.primary}`}>
                            {member.name}
                          </TableCell>
                          <TableCell className={themeClasses.text.primary}>
                            {member.position}
                          </TableCell>
                          <TableCell className={themeClasses.text.primary}>
                            ${(member.cost_rate || 0).toFixed(2)}
                          </TableCell>
                          <TableCell className={themeClasses.text.primary}>
                            {format(new Date(member.hire_date), 'MM/dd/yyyy')}
                          </TableCell>
                          <TableCell>
                            <Badge className={getStatusColor(member.status)}>
                              {member.status}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              {member.phone && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => window.open(`tel:${member.phone}`)}
                                  className="p-1"
                                >
                                  <Phone className="w-4 h-4" />
                                </Button>
                              )}
                              {member.email && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => window.open(`mailto:${member.email}`)}
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
                                onClick={() => openEditModal(member)}
                                className={themeClasses.button.secondary}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDeleteCrewMember(member.id)}
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

      {/* Create Crew Member Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className={`sm:max-w-[600px] ${themeClasses.modal}`}>
          <DialogHeader>
            <DialogTitle className={themeClasses.text.primary}>Add New Crew Member</DialogTitle>
          </DialogHeader>
          
          <div className="grid gap-4 py-4 max-h-96 overflow-y-auto">
            {/* Name and Position */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Full Name*</Label>
                <Input
                  value={newCrewMember.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className={themeClasses.input}
                  placeholder="John Smith"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Position*</Label>
                <Select value={newCrewMember.position} onValueChange={(value) => handleInputChange('position', value)}>
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
            <div className="space-y-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Labor Cost Rate ($/hour)*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newCrewMember.cost_rate}
                  onChange={(e) => handleInputChange('cost_rate', e.target.value)}
                  className={themeClasses.input}
                  placeholder="65.00"
                />
                <p className={`text-xs ${themeClasses.text.secondary}`}>
                  Internal cost including benefits, taxes, insurance (GC rates are set per project)
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
                      !newCrewMember.hire_date && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {newCrewMember.hire_date ? format(newCrewMember.hire_date, "MM/dd/yyyy") : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className={`w-auto p-0 ${themeClasses.modal}`} align="start">
                  <Calendar
                    mode="single"
                    selected={newCrewMember.hire_date}
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
                  value={newCrewMember.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className={themeClasses.input}
                  placeholder="(555) 123-4567"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Email</Label>
                <Input
                  type="email"
                  value={newCrewMember.email}
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
                value={newCrewMember.emergency_contact}
                onChange={(e) => handleInputChange('emergency_contact', e.target.value)}
                className={themeClasses.input}
                placeholder="Jane Smith - (555) 987-6543"
              />
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setShowCreateModal(false);
                resetNewCrewMember();
              }}
              className={themeClasses.button.secondary}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleCreateCrewMember}
              disabled={!newCrewMember.name || !newCrewMember.position || !newCrewMember.cost_rate}
              className={themeClasses.button.primary}
            >
              Add Installer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Crew Member Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className={`sm:max-w-[600px] ${themeClasses.modal}`}>
          <DialogHeader>
            <DialogTitle className={themeClasses.text.primary}>
              Edit Crew Member - {selectedCrewMember?.name}
            </DialogTitle>
          </DialogHeader>
          
          <div className="grid gap-4 py-4 max-h-96 overflow-y-auto">
            {/* Name and Position */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Full Name*</Label>
                <Input
                  value={editCrewMember.name || ''}
                  onChange={(e) => handleEditInputChange('name', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Position*</Label>
                <Select value={editCrewMember.position || ''} onValueChange={(value) => handleEditInputChange('position', value)}>
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
                <Label className={themeClasses.text.primary}>Hourly Rate ($/hour)*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={editCrewMember.hourly_rate || ''}
                  onChange={(e) => handleEditInputChange('hourly_rate', e.target.value)}
                  className={themeClasses.input}
                />
                <p className={`text-xs ${themeClasses.text.secondary}`}>
                  True cost including benefits, taxes, insurance
                </p>
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>GC Billing Rate ($/hour)*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={editCrewMember.gc_billing_rate || ''}
                  onChange={(e) => handleEditInputChange('gc_billing_rate', e.target.value)}
                  className={themeClasses.input}
                />
                <p className={`text-xs ${themeClasses.text.secondary}`}>
                  Rate billed to General Contractor
                </p>
              </div>
            </div>

            {/* Contact Information */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Phone</Label>
                <Input
                  type="tel"
                  value={editCrewMember.phone || ''}
                  onChange={(e) => handleEditInputChange('phone', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Email</Label>
                <Input
                  type="email"
                  value={editCrewMember.email || ''}
                  onChange={(e) => handleEditInputChange('email', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Emergency Contact</Label>
              <Input
                value={editCrewMember.emergency_contact || ''}
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
                setSelectedCrewMember(null);
              }}
              className={themeClasses.button.secondary}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleUpdateCrewMember}
              className={themeClasses.button.primary}
            >
              Update Crew Member
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default CrewManagement;