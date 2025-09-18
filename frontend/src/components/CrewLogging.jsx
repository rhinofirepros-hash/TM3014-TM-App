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
  Filter
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';

const CrewLogging = ({ project, onBack }) => {
  const [crewLogs, setCrewLogs] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedLog, setSelectedLog] = useState(null);
  const [filterDate, setFilterDate] = useState('');
  const [newLog, setNewLog] = useState({
    date: new Date(),
    crew_members: [],
    work_description: '',
    hours_worked: '',
    per_diem: '',
    hotel_cost: '',
    gas_expense: '',
    other_expenses: '',
    expense_notes: '',
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
    loadCrewLogs();
    loadEmployees();
  }, [project]);

  const loadCrewLogs = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (backendUrl && project) {
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
        expenses: {
          per_diem: parseFloat(newLog.per_diem) || 0,
          hotel_cost: parseFloat(newLog.hotel_cost) || 0,
          gas_expense: parseFloat(newLog.gas_expense) || 0,
          other_expenses: parseFloat(newLog.other_expenses) || 0,
          expense_notes: newLog.expense_notes
        }
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
        toast({
          title: "Backend Error",
          description: "Backend URL not configured",
          variant: "destructive"
        });
        return;
      }

      const logData = {
        project_id: project.id,
        project_name: project.name,
        date: newLog.date.toISOString(),
        crew_members: newLog.crew_members,
        work_description: newLog.work_description,
        hours_worked: parseFloat(newLog.hours_worked) || 0,
        per_diem: parseFloat(newLog.per_diem) || 0,
        hotel_cost: parseFloat(newLog.hotel_cost) || 0,
        gas_expense: parseFloat(newLog.gas_expense) || 0,
        other_expenses: parseFloat(newLog.other_expenses) || 0,
        expense_notes: newLog.expense_notes,
        weather_conditions: newLog.weather_conditions
      };

      const response = await fetch(`${backendUrl}/api/crew-logs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(logData)
      });

      if (response.ok) {
        const createdLog = await response.json();
        setCrewLogs(prev => [createdLog, ...prev]);
        setShowCreateModal(false);
        resetNewLog();
        
        toast({
          title: "Crew Log Created",
          description: `Crew log for ${format(newLog.date, 'MM/dd/yyyy')} has been created.`,
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

  const handleDeleteLog = async (logId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl) return;

      const response = await fetch(`${backendUrl}/api/crew-logs/${logId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setCrewLogs(prev => prev.filter(log => log.id !== logId));
        toast({
          title: "Log Deleted",
          description: "Crew log has been deleted successfully.",
        });
      }
    } catch (error) {
      toast({
        title: "Deletion Failed",
        description: "Failed to delete crew log.",
        variant: "destructive"
      });
    }
  };

  const resetNewLog = () => {
    setNewLog({
      date: new Date(),
      crew_members: [],
      work_description: '',
      hours_worked: '',
      per_diem: '',
      hotel_cost: '',
      gas_expense: '',
      other_expenses: '',
      expense_notes: '',
      weather_conditions: 'clear'
    });
  };

  const handleInputChange = (field, value) => {
    setNewLog(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCrewMemberToggle = (employeeName) => {
    setNewLog(prev => ({
      ...prev,
      crew_members: prev.crew_members.includes(employeeName)
        ? prev.crew_members.filter(name => name !== employeeName)
        : [...prev.crew_members, employeeName]
    }));
  };

  const getTotalExpenses = (log) => {
    return (log.per_diem || 0) + (log.hotel_cost || 0) + (log.gas_expense || 0) + (log.other_expenses || 0);
  };

  const getWeatherIcon = (weather) => {
    const option = weatherOptions.find(opt => opt.value === weather);
    return option ? option.icon : Sun;
  };

  const filteredLogs = filterDate 
    ? crewLogs.filter(log => format(new Date(log.date), 'yyyy-MM-dd') === filterDate)
    : crewLogs;

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
                Back to Project
              </Button>
              <div>
                <h1 className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                  Crew Logging
                </h1>
                <p className={themeClasses.text.secondary}>
                  {project.name} - Daily crew activities and expenses
                </p>
              </div>
            </div>
            
            <Button 
              onClick={() => setShowCreateModal(true)}
              className={themeClasses.button.primary}
            >
              <Plus className="w-4 h-4 mr-2" />
              Log Daily Activity
            </Button>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Total Logs
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {crewLogs.length}
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
                      Total Hours
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {crewLogs.reduce((sum, log) => sum + (log.hours_worked || 0), 0).toFixed(1)}
                    </p>
                  </div>
                  <Clock className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Total Expenses
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      ${crewLogs.reduce((sum, log) => sum + getTotalExpenses(log), 0).toLocaleString()}
                    </p>
                  </div>
                  <DollarSign className="w-8 h-8 text-red-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Avg Daily Hours
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {crewLogs.length > 0 
                        ? (crewLogs.reduce((sum, log) => sum + (log.hours_worked || 0), 0) / crewLogs.length).toFixed(1)
                        : '0.0'
                      }
                    </p>
                  </div>
                  <Clock className="w-8 h-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <div className="mb-6">
            <div className="flex gap-4 items-center">
              <div className="flex items-center gap-2">
                <Filter className={`w-4 h-4 ${themeClasses.text.secondary}`} />
                <Label className={themeClasses.text.secondary}>Filter by Date:</Label>
              </div>
              <Input
                type="date"
                value={filterDate}
                onChange={(e) => setFilterDate(e.target.value)}
                className={`w-48 ${themeClasses.input}`}
              />
              {filterDate && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setFilterDate('')}
                  className={themeClasses.button.secondary}
                >
                  Clear Filter
                </Button>
              )}
            </div>
          </div>

          {/* Crew Logs Table */}
          {filteredLogs.length === 0 ? (
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-12 text-center">
                <Users className={`w-16 h-16 mx-auto mb-4 ${themeClasses.text.muted}`} />
                <h3 className={`text-lg font-medium mb-2 ${themeClasses.text.primary}`}>
                  {filterDate ? 'No Logs for Selected Date' : 'No Crew Logs Yet'}
                </h3>
                <p className={`mb-6 ${themeClasses.text.secondary}`}>
                  {filterDate 
                    ? 'Try selecting a different date or clear the filter.'
                    : 'Start logging daily crew activities and expenses.'
                  }
                </p>
                <Button 
                  onClick={() => setShowCreateModal(true)}
                  className={themeClasses.button.primary}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create First Log
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardHeader>
                <CardTitle className={themeClasses.text.primary}>
                  Crew Activity Logs ({filteredLogs.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                        <TableHead className={themeClasses.text.primary}>Date</TableHead>
                        <TableHead className={themeClasses.text.primary}>Crew Members</TableHead>
                        <TableHead className={themeClasses.text.primary}>Work Description</TableHead>
                        <TableHead className={themeClasses.text.primary}>Hours</TableHead>
                        <TableHead className={themeClasses.text.primary}>Weather</TableHead>
                        <TableHead className={themeClasses.text.primary}>Expenses</TableHead>
                        <TableHead className={themeClasses.text.primary}>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredLogs.map((log) => {
                        const WeatherIcon = getWeatherIcon(log.weather_conditions);
                        return (
                          <TableRow key={log.id} className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                            <TableCell className={themeClasses.text.primary}>
                              {format(new Date(log.date), 'MM/dd/yyyy')}
                            </TableCell>
                            <TableCell>
                              <div className="flex flex-wrap gap-1">
                                {log.crew_members.slice(0, 2).map((member, index) => (
                                  <Badge key={index} variant="outline" className="text-xs">
                                    {member}
                                  </Badge>
                                ))}
                                {log.crew_members.length > 2 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{log.crew_members.length - 2} more
                                  </Badge>
                                )}
                              </div>
                            </TableCell>
                            <TableCell className={`max-w-xs truncate ${themeClasses.text.primary}`}>
                              {log.work_description}
                            </TableCell>
                            <TableCell className={themeClasses.text.primary}>
                              {log.hours_worked} hrs
                            </TableCell>
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <WeatherIcon className={`w-4 h-4 ${themeClasses.text.secondary}`} />
                                <span className={`capitalize text-sm ${themeClasses.text.secondary}`}>
                                  {log.weather_conditions}
                                </span>
                              </div>
                            </TableCell>
                            <TableCell className={themeClasses.text.primary}>
                              ${getTotalExpenses(log).toLocaleString()}
                            </TableCell>
                            <TableCell>
                              <div className="flex gap-2">
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => setSelectedLog(log)}
                                  className={themeClasses.button.secondary}
                                >
                                  <Edit className="w-4 h-4" />
                                </Button>
                                <Button
                                  size="sm"
                                  variant="outline"
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
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Create/Edit Crew Log Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className={`sm:max-w-[700px] ${themeClasses.modal}`}>
          <DialogHeader>
            <DialogTitle className={themeClasses.text.primary}>Log Daily Crew Activity</DialogTitle>
          </DialogHeader>
          
          <div className="grid gap-4 py-4 max-h-96 overflow-y-auto">
            {/* Date and Weather */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Date*</Label>
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
                      onSelect={(date) => handleInputChange('date', date)}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Weather Conditions</Label>
                <Select value={newLog.weather_conditions} onValueChange={(value) => handleInputChange('weather_conditions', value)}>
                  <SelectTrigger className={themeClasses.input}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className={themeClasses.modal}>
                    {weatherOptions.map((option) => {
                      const IconComponent = option.icon;
                      return (
                        <SelectItem key={option.value} value={option.value}>
                          <div className="flex items-center gap-2">
                            <IconComponent className="w-4 h-4" />
                            {option.label}
                          </div>
                        </SelectItem>
                      );
                    })}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Crew Members Selection */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Crew Members*</Label>
              <div className="grid grid-cols-2 gap-2 max-h-32 overflow-y-auto border rounded p-2">
                {employees.map((employee) => (
                  <label key={employee.id} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={newLog.crew_members.includes(employee.name)}
                      onChange={() => handleCrewMemberToggle(employee.name)}
                      className="rounded"
                    />
                    <span className={`text-sm ${themeClasses.text.primary}`}>{employee.name}</span>
                  </label>
                ))}
              </div>
              {newLog.crew_members.length === 0 && (
                <p className={`text-xs ${themeClasses.text.secondary}`}>
                  Select at least one crew member
                </p>
              )}
            </div>

            {/* Work Description */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Work Description*</Label>
              <Textarea
                value={newLog.work_description}
                onChange={(e) => handleInputChange('work_description', e.target.value)}
                className={themeClasses.input}
                placeholder="Describe the work performed today..."
                rows={3}
              />
            </div>

            {/* Hours and Expenses */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Hours Worked*</Label>
                <Input
                  type="number"
                  step="0.5"
                  value={newLog.hours_worked}
                  onChange={(e) => handleInputChange('hours_worked', e.target.value)}
                  className={themeClasses.input}
                  placeholder="8.0"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Per Diem ($)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newLog.per_diem}
                  onChange={(e) => handleInputChange('per_diem', e.target.value)}
                  className={themeClasses.input}
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Hotel Cost ($)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newLog.hotel_cost}
                  onChange={(e) => handleInputChange('hotel_cost', e.target.value)}
                  className={themeClasses.input}
                  placeholder="0.00"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Gas Expense ($)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newLog.gas_expense}
                  onChange={(e) => handleInputChange('gas_expense', e.target.value)}
                  className={themeClasses.input}
                  placeholder="0.00"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Other Expenses ($)</Label>
              <Input
                type="number"
                step="0.01"
                value={newLog.other_expenses}
                onChange={(e) => handleInputChange('other_expenses', e.target.value)}
                className={themeClasses.input}
                placeholder="0.00"
              />
            </div>

            {/* Expense Notes */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Expense Notes</Label>
              <Textarea
                value={newLog.expense_notes}
                onChange={(e) => handleInputChange('expense_notes', e.target.value)}
                className={themeClasses.input}
                placeholder="Additional notes about expenses..."
                rows={2}
              />
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
              disabled={!newLog.work_description || !newLog.hours_worked || newLog.crew_members.length === 0}
              className={themeClasses.button.primary}
            >
              Create Log
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default CrewLogging;