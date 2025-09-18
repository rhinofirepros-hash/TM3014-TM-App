import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
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
  Clock,
  DollarSign,
  Edit,
  Trash2,
  CloudRain,
  Sun,
  Cloud,
  Filter,
  RefreshCw,
  Zap
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';

const CrewLogging = ({ project, onBack, onDataUpdate }) => {
  const [crewLogs, setCrewLogs] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedLog, setSelectedLog] = useState(null);
  const [editingLog, setEditingLog] = useState(null);
  const [filterDate, setFilterDate] = useState('');
  const [newLog, setNewLog] = useState({
    date: new Date(),
    crew_members: [],
    work_description: '',
    weather_conditions: 'clear'
  });
  
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();

  const weatherOptions = [
    { value: 'clear', label: 'Clear', icon: Sun },
    { value: 'cloudy', label: 'Cloudy', icon: Cloud },
    { value: 'rainy', label: 'Rainy', icon: CloudRain },
    { value: 'stormy', label: 'Stormy', icon: CloudRain }
  ];

  useEffect(() => {
    if (project?.id) {
      loadCrewLogs();
      loadEmployees();
    }
  }, [project]);

  const loadCrewLogs = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (backendUrl && project?.id) {
        const response = await fetch(`${backendUrl}/api/crew-logs?project_id=${project.id}`);
        if (response.ok) {
          const logs = await response.json();
          setCrewLogs(logs);
        }
      }
    } catch (error) {
      console.warn('Failed to load crew logs:', error);
    }
  };

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

  const handleCreateLog = async () => {
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

      const logData = {
        project_id: project.id,
        date: newLog.date.toISOString(),
        crew_members: newLog.crew_members.map(member => ({
          ...member,
          st_hours: parseFloat(member.st_hours) || 0,
          ot_hours: parseFloat(member.ot_hours) || 0,
          dt_hours: parseFloat(member.dt_hours) || 0,
          pot_hours: parseFloat(member.pot_hours) || 0,
          total_hours: parseFloat(member.total_hours) || 0
        })),
        work_description: newLog.work_description,
        weather_conditions: newLog.weather_conditions,
        expenses: {}
      };

      const response = await fetch(`${backendUrl}/api/crew-logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logData)
      });

      if (response.ok) {
        const result = await response.json();
        await loadCrewLogs(); // Reload logs
        resetNewLog();
        setShowCreateModal(false);
        
        // Notify parent component to refresh analytics
        if (onDataUpdate) {
          onDataUpdate();
        }
        
        toast({
          title: "Crew Log Created",
          description: "Crew log saved and automatically synced with T&M data.",
        });
      } else {
        throw new Error('Failed to create crew log');
      }
    } catch (error) {
      toast({
        title: "Creation Failed",
        description: "Failed to create crew log. Please try again.",
        variant: "destructive"
      });
    }
  };

  // Auto-populate from existing T&M or crew data
  const handleEditLog = (log) => {
    setEditingLog({
      id: log.id,
      date: new Date(log.date),
      crew_members: log.crew_members || [],
      work_description: log.work_description || '',
      weather_conditions: log.weather_conditions || 'clear'
    });
    setShowEditModal(true);
  };

  const handleUpdateLog = async () => {
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

      const logData = {
        date: editingLog.date.toISOString(),
        crew_members: editingLog.crew_members.map(member => ({
          ...member,
          st_hours: parseFloat(member.st_hours) || 0,
          ot_hours: parseFloat(member.ot_hours) || 0,
          dt_hours: parseFloat(member.dt_hours) || 0,
          pot_hours: parseFloat(member.pot_hours) || 0,
          total_hours: parseFloat(member.total_hours) || 0
        })),
        work_description: editingLog.work_description,
        weather_conditions: editingLog.weather_conditions
      };

      const response = await fetch(`${backendUrl}/api/crew-logs/${editingLog.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logData)
      });

      if (response.ok) {
        await loadCrewLogs(); // Reload logs
        setShowEditModal(false);
        setEditingLog(null);
        
        // Notify parent component to refresh analytics
        if (onDataUpdate) {
          onDataUpdate();
        }
        
        toast({
          title: "Crew Log Updated",
          description: "Changes have been saved successfully.",
        });
      } else {
        throw new Error('Failed to update crew log');
      }
    } catch (error) {
      toast({
        title: "Update Failed",
        description: "Failed to update crew log. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleDeleteLog = async (logId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl) return;

      const response = await fetch(`${backendUrl}/api/crew-logs/${logId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await loadCrewLogs(); // Reload logs
        
        // Notify parent component to refresh analytics
        if (onDataUpdate) {
          onDataUpdate();
        }
        
        toast({
          title: "Crew Log Deleted",
          description: "Crew log has been deleted successfully.",
        });
      } else {
        throw new Error('Failed to delete crew log');
      }
    } catch (error) {
      toast({
        title: "Delete Failed",
        description: "Failed to delete crew log. Please try again.",
        variant: "destructive"
      });
    }
  };

  // Auto-populate from existing T&M or crew data
  const handleAutoPopulate = async (selectedDate) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl || !project?.id) return;

      const dateString = selectedDate.toISOString().split('T')[0];
      const response = await fetch(`${backendUrl}/api/daily-crew-data?project_id=${project.id}&date=${dateString}`);
      
      if (response.ok) {
        const data = await response.json();
        
        if (data.source && data.crew_members && data.crew_members.length > 0) {
          setNewLog(prev => ({
            ...prev,
            date: selectedDate,
            crew_members: data.crew_members,
            work_description: data.work_description || prev.work_description
          }));
          
          toast({
            title: "Data Auto-Populated",
            description: `Loaded crew data from existing ${data.source === 'tm_tag' ? 'T&M tag' : 'crew log'}.`,
          });
        } else {
          setNewLog(prev => ({
            ...prev,
            date: selectedDate
          }));
        }
      }
    } catch (error) {
      console.warn('Failed to auto-populate crew data:', error);
      setNewLog(prev => ({
        ...prev,
        date: selectedDate
      }));
    }
  };

  const resetNewLog = () => {
    setNewLog({
      date: new Date(),
      crew_members: [],
      work_description: '',
      weather_conditions: 'clear'
    });
  };

  const addCrewMember = () => {
    const newMember = {
      id: Date.now(),
      name: '',
      st_hours: 0,
      ot_hours: 0,
      dt_hours: 0,
      pot_hours: 0,
      total_hours: 0
    };
    setNewLog(prev => ({
      ...prev,
      crew_members: [...prev.crew_members, newMember]
    }));
  };

  const updateCrewMember = (index, field, value) => {
    setNewLog(prev => {
      const updatedMembers = [...prev.crew_members];
      updatedMembers[index] = {
        ...updatedMembers[index],
        [field]: value
      };

      // Auto-calculate total hours
      if (field.includes('hours')) {
        const member = updatedMembers[index];
        member.total_hours = 
          (parseFloat(member.st_hours) || 0) +
          (parseFloat(member.ot_hours) || 0) +
          (parseFloat(member.dt_hours) || 0) +
          (parseFloat(member.pot_hours) || 0);
      }

      return {
        ...prev,
        crew_members: updatedMembers
      };
    });
  };

  const removeCrewMember = (index) => {
    setNewLog(prev => ({
      ...prev,
      crew_members: prev.crew_members.filter((_, i) => i !== index)
    }));
  };

  const totalHours = crewLogs.reduce((sum, log) => {
    return sum + log.crew_members?.reduce((memberSum, member) => 
      memberSum + (member.total_hours || 0), 0) || 0;
  }, 0);

  const totalDays = new Set(crewLogs.map(log => 
    new Date(log.date).toISOString().split('T')[0]
  )).size;

  const filteredLogs = crewLogs.filter(log => {
    if (!filterDate) return true;
    return log.date.includes(filterDate);
  });

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
                className={themeClasses.button.secondary}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Project
              </Button>
              <div>
                <h1 className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                  Crew Logging - {project?.name}
                </h1>
                <p className={themeClasses.text.secondary}>
                  Log crew activities and sync with T&M data
                </p>
              </div>
            </div>
            
            <Button 
              onClick={() => setShowCreateModal(true)}
              className={themeClasses.button.primary}
            >
              <Plus className="w-4 h-4 mr-2" />
              Log Crew Activity
            </Button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className={`${themeClasses.card} shadow-lg`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Total Logs</p>
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>{crewLogs.length}</p>
                  </div>
                  <Users className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-lg`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Total Hours</p>
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>{totalHours.toFixed(1)}</p>
                  </div>
                  <Clock className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-lg`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Work Days</p>
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>{totalDays}</p>
                  </div>
                  <CalendarIcon className="w-8 h-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-lg`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Labor Cost</p>
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>${(totalHours * 95).toLocaleString()}</p>
                  </div>
                  <DollarSign className="w-8 h-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Crew Logs Table */}
          <Card className={`${themeClasses.card} shadow-lg`}>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className={themeClasses.text.primary}>
                  Crew Activity Logs ({filteredLogs.length})
                </CardTitle>
                <div className="flex items-center gap-4">
                  <Input
                    placeholder="Filter by date (YYYY-MM-DD)"
                    value={filterDate}
                    onChange={(e) => setFilterDate(e.target.value)}
                    className={`w-48 ${themeClasses.input}`}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setFilterDate('')}
                    className={themeClasses.button.secondary}
                  >
                    Clear
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredLogs.length === 0 ? (
                <div className="text-center py-12">
                  <Users className={`w-16 h-16 mx-auto mb-4 ${themeClasses.text.muted}`} />
                  <h3 className={`text-lg font-medium mb-2 ${themeClasses.text.primary}`}>
                    No Crew Logs Yet
                  </h3>
                  <p className={`mb-6 ${themeClasses.text.secondary}`}>
                    Start logging crew activities to track project progress.
                  </p>
                  <Button 
                    onClick={() => setShowCreateModal(true)}
                    className={themeClasses.button.primary}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Create First Log
                  </Button>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                        <TableHead className={themeClasses.text.primary}>Date</TableHead>
                        <TableHead className={themeClasses.text.primary}>Crew Members</TableHead>
                        <TableHead className={themeClasses.text.primary}>Total Hours</TableHead>
                        <TableHead className={themeClasses.text.primary}>Work Description</TableHead>
                        <TableHead className={themeClasses.text.primary}>Weather</TableHead>
                        <TableHead className={themeClasses.text.primary}>Sync Status</TableHead>
                        <TableHead className={themeClasses.text.primary}>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredLogs.map((log) => {
                        const logTotalHours = log.crew_members?.reduce((sum, member) => 
                          sum + (member.total_hours || 0), 0) || 0;
                        
                        return (
                          <TableRow key={log.id} className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                            <TableCell className={themeClasses.text.primary}>
                              {format(new Date(log.date), 'MM/dd/yyyy')}
                            </TableCell>
                            <TableCell className={themeClasses.text.primary}>
                              {log.crew_members?.length || 0} members
                            </TableCell>
                            <TableCell className={themeClasses.text.primary}>
                              {logTotalHours.toFixed(1)}h
                            </TableCell>
                            <TableCell className={`max-w-xs truncate ${themeClasses.text.secondary}`}>
                              {log.work_description || 'No description'}
                            </TableCell>
                            <TableCell>
                              <Badge className="bg-blue-100 text-blue-800">
                                {weatherOptions.find(w => w.value === log.weather_conditions)?.label || 'Clear'}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              {log.synced_to_tm ? (
                                <Badge className="bg-green-100 text-green-800">
                                  <Zap className="w-3 h-3 mr-1" />
                                  Synced
                                </Badge>
                              ) : (
                                <Badge className="bg-yellow-100 text-yellow-800">
                                  Pending
                                </Badge>
                              )}
                            </TableCell>
                            <TableCell>
                              <div className="flex gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleEditLog(log)}
                                  className={themeClasses.button.secondary}
                                >
                                  <Edit className="w-4 h-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleDeleteLog(log.id)}
                                  className="text-red-600 hover:bg-red-50"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Create Crew Log Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className={`max-w-4xl max-h-[90vh] overflow-y-auto ${themeClasses.modal}`}>
          <DialogHeader>
            <DialogTitle className={themeClasses.text.primary}>
              Log Crew Activity
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* Date Selection with Auto-Populate */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Date *</Label>
              <div className="flex gap-2">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        `w-full justify-start text-left font-normal ${themeClasses.button.secondary}`,
                        !newLog.date && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {newLog.date ? format(newLog.date, "MM/dd/yyyy") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className={`w-auto p-0 ${themeClasses.modal}`} align="start">
                    <Calendar
                      mode="single"
                      selected={newLog.date}
                      onSelect={(date) => handleAutoPopulate(date)}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => handleAutoPopulate(newLog.date)}
                  className={themeClasses.button.secondary}
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Auto-Fill
                </Button>
              </div>
              <p className={`text-xs ${themeClasses.text.secondary}`}>
                Auto-fill will load existing crew data from T&M tags or previous logs for this date
              </p>
            </div>

            {/* Work Description */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Work Description</Label>
              <Textarea
                value={newLog.work_description}
                onChange={(e) => setNewLog(prev => ({ ...prev, work_description: e.target.value }))}
                className={themeClasses.input}
                placeholder="Describe the work performed..."
                rows={3}
              />
            </div>

            {/* Weather Conditions */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Weather Conditions</Label>
              <Select value={newLog.weather_conditions} onValueChange={(value) => setNewLog(prev => ({ ...prev, weather_conditions: value }))}>
                <SelectTrigger className={themeClasses.input}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  {weatherOptions.map((weather) => (
                    <SelectItem key={weather.value} value={weather.value}>
                      <div className="flex items-center gap-2">
                        <weather.icon className="w-4 h-4" />
                        {weather.label}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Crew Members */}
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <Label className={themeClasses.text.primary}>Crew Members</Label>
                <Button
                  type="button"
                  onClick={addCrewMember}
                  size="sm"
                  className={themeClasses.button.primary}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Member
                </Button>
              </div>

              {newLog.crew_members.map((member, index) => (
                <Card key={member.id} className={themeClasses.card}>
                  <CardContent className="p-4">
                    <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                      <div className="md:col-span-2">
                        <Label className={`text-sm ${themeClasses.text.primary}`}>Name</Label>
                        <Select 
                          value={member.name} 
                          onValueChange={(value) => updateCrewMember(index, 'name', value)}
                        >
                          <SelectTrigger className={themeClasses.input}>
                            <SelectValue placeholder="Select employee" />
                          </SelectTrigger>
                          <SelectContent className={themeClasses.modal}>
                            {employees.map((employee) => (
                              <SelectItem key={employee.id} value={employee.name}>
                                {employee.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div>
                        <Label className={`text-sm ${themeClasses.text.primary}`}>ST Hours</Label>
                        <Input
                          type="number"
                          step="0.5"
                          value={member.st_hours || ''}
                          onChange={(e) => updateCrewMember(index, 'st_hours', e.target.value)}
                          className={themeClasses.input}
                        />
                      </div>
                      
                      <div>
                        <Label className={`text-sm ${themeClasses.text.primary}`}>OT Hours</Label>
                        <Input
                          type="number"
                          step="0.5"
                          value={member.ot_hours || ''}
                          onChange={(e) => updateCrewMember(index, 'ot_hours', e.target.value)}
                          className={themeClasses.input}
                        />
                      </div>
                      
                      <div>
                        <Label className={`text-sm ${themeClasses.text.primary}`}>DT Hours</Label>
                        <Input
                          type="number"
                          step="0.5"
                          value={member.dt_hours || ''}
                          onChange={(e) => updateCrewMember(index, 'dt_hours', e.target.value)}
                          className={themeClasses.input}
                        />
                      </div>
                      
                      <div className="flex items-end">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={() => removeCrewMember(index)}
                          className="text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    
                    <div className="mt-2 text-sm text-right">
                      <span className={themeClasses.text.secondary}>
                        Total Hours: <span className="font-semibold">{member.total_hours || 0}</span>
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {newLog.crew_members.length === 0 && (
                <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
                  <Users className={`w-12 h-12 mx-auto mb-2 ${themeClasses.text.muted}`} />
                  <p className={themeClasses.text.secondary}>
                    No crew members added yet. Click "Add Member" to start.
                  </p>
                </div>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setShowCreateModal(false);
                resetNewLog();
              }}
              className={themeClasses.button.secondary}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleCreateLog}
              disabled={newLog.crew_members.length === 0}
              className={themeClasses.button.primary}
            >
              Create Log & Sync with T&M
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Crew Log Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className={`max-w-4xl max-h-[90vh] overflow-y-auto ${themeClasses.modal}`}>
          <DialogHeader>
            <DialogTitle className={themeClasses.text.primary}>
              Edit Crew Activity Log
            </DialogTitle>
          </DialogHeader>
          
          {editingLog && (
            <div className="space-y-6">
              {/* Date Selection */}
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Date *</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        `w-full justify-start text-left font-normal ${themeClasses.button.secondary}`,
                        !editingLog.date && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {editingLog.date ? format(editingLog.date, "MM/dd/yyyy") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className={`w-auto p-0 ${themeClasses.modal}`} align="start">
                    <Calendar
                      mode="single"
                      selected={editingLog.date}
                      onSelect={(date) => setEditingLog(prev => ({ ...prev, date }))}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>

              {/* Work Description */}
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Work Description</Label>
                <Textarea
                  value={editingLog.work_description}
                  onChange={(e) => setEditingLog(prev => ({ ...prev, work_description: e.target.value }))}
                  className={themeClasses.input}
                  placeholder="Describe the work performed..."
                  rows={3}
                />
              </div>

              {/* Weather Conditions */}
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Weather Conditions</Label>
                <Select value={editingLog.weather_conditions} onValueChange={(value) => setEditingLog(prev => ({ ...prev, weather_conditions: value }))}>
                  <SelectTrigger className={themeClasses.input}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className={themeClasses.modal}>
                    {weatherOptions.map((weather) => (
                      <SelectItem key={weather.value} value={weather.value}>
                        <div className="flex items-center gap-2">
                          <weather.icon className="w-4 h-4" />
                          {weather.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Crew Members */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Label className={themeClasses.text.primary}>Crew Members</Label>
                  <Button
                    type="button"
                    onClick={() => setEditingLog(prev => ({
                      ...prev,
                      crew_members: [...prev.crew_members, {
                        id: Date.now(),
                        name: '',
                        st_hours: 0,
                        ot_hours: 0,
                        dt_hours: 0,
                        pot_hours: 0,
                        total_hours: 0
                      }]
                    }))}
                    size="sm"
                    className={themeClasses.button.primary}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Member
                  </Button>
                </div>

                {editingLog.crew_members.map((member, index) => (
                  <Card key={member.id || index} className={themeClasses.card}>
                    <CardContent className="p-4">
                      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                        <div className="md:col-span-2">
                          <Label className={`text-sm ${themeClasses.text.primary}`}>Name</Label>
                          <Select 
                            value={member.name} 
                            onValueChange={(value) => {
                              const updatedMembers = [...editingLog.crew_members];
                              updatedMembers[index] = { ...updatedMembers[index], name: value };
                              setEditingLog(prev => ({ ...prev, crew_members: updatedMembers }));
                            }}
                          >
                            <SelectTrigger className={themeClasses.input}>
                              <SelectValue placeholder="Select employee" />
                            </SelectTrigger>
                            <SelectContent className={themeClasses.modal}>
                              {employees.map((employee) => (
                                <SelectItem key={employee.id} value={employee.name}>
                                  {employee.name}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        
                        <div>
                          <Label className={`text-sm ${themeClasses.text.primary}`}>ST Hours</Label>
                          <Input
                            type="number"
                            step="0.5"
                            value={member.st_hours || ''}
                            onChange={(e) => {
                              const updatedMembers = [...editingLog.crew_members];
                              updatedMembers[index] = { 
                                ...updatedMembers[index], 
                                st_hours: e.target.value,
                                total_hours: 
                                  (parseFloat(e.target.value) || 0) +
                                  (parseFloat(updatedMembers[index].ot_hours) || 0) +
                                  (parseFloat(updatedMembers[index].dt_hours) || 0) +
                                  (parseFloat(updatedMembers[index].pot_hours) || 0)
                              };
                              setEditingLog(prev => ({ ...prev, crew_members: updatedMembers }));
                            }}
                            className={themeClasses.input}
                          />
                        </div>
                        
                        <div>
                          <Label className={`text-sm ${themeClasses.text.primary}`}>OT Hours</Label>
                          <Input
                            type="number"
                            step="0.5"
                            value={member.ot_hours || ''}
                            onChange={(e) => {
                              const updatedMembers = [...editingLog.crew_members];
                              updatedMembers[index] = { 
                                ...updatedMembers[index], 
                                ot_hours: e.target.value,
                                total_hours: 
                                  (parseFloat(updatedMembers[index].st_hours) || 0) +
                                  (parseFloat(e.target.value) || 0) +
                                  (parseFloat(updatedMembers[index].dt_hours) || 0) +
                                  (parseFloat(updatedMembers[index].pot_hours) || 0)
                              };
                              setEditingLog(prev => ({ ...prev, crew_members: updatedMembers }));
                            }}
                            className={themeClasses.input}
                          />
                        </div>
                        
                        <div>
                          <Label className={`text-sm ${themeClasses.text.primary}`}>DT Hours</Label>
                          <Input
                            type="number"
                            step="0.5"
                            value={member.dt_hours || ''}
                            onChange={(e) => {
                              const updatedMembers = [...editingLog.crew_members];
                              updatedMembers[index] = { 
                                ...updatedMembers[index], 
                                dt_hours: e.target.value,
                                total_hours: 
                                  (parseFloat(updatedMembers[index].st_hours) || 0) +
                                  (parseFloat(updatedMembers[index].ot_hours) || 0) +
                                  (parseFloat(e.target.value) || 0) +
                                  (parseFloat(updatedMembers[index].pot_hours) || 0)
                              };
                              setEditingLog(prev => ({ ...prev, crew_members: updatedMembers }));
                            }}
                            className={themeClasses.input}
                          />
                        </div>
                        
                        <div className="flex items-end">
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              const updatedMembers = editingLog.crew_members.filter((_, i) => i !== index);
                              setEditingLog(prev => ({ ...prev, crew_members: updatedMembers }));
                            }}
                            className="text-red-600 hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      
                      <div className="mt-2 text-sm text-right">
                        <span className={themeClasses.text.secondary}>
                          Total Hours: <span className="font-semibold">{member.total_hours || 0}</span>
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {editingLog.crew_members.length === 0 && (
                  <div className="text-center py-8 border-2 border-dashed border-gray-300 rounded-lg">
                    <Users className={`w-12 h-12 mx-auto mb-2 ${themeClasses.text.muted}`} />
                    <p className={themeClasses.text.secondary}>
                      No crew members added yet. Click "Add Member" to start.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setShowEditModal(false);
                setEditingLog(null);
              }}
              className={themeClasses.button.secondary}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleUpdateLog}
              disabled={!editingLog || editingLog.crew_members.length === 0}
              className={themeClasses.button.primary}
            >
              Update Log & Sync with T&M
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default CrewLogging;