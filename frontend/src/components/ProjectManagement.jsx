import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Calendar } from './ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { format } from 'date-fns';
import { 
  ArrowLeft, 
  Plus, 
  Building, 
  DollarSign, 
  Calendar as CalendarIcon,
  Users, 
  FileText,
  Edit,
  Trash2,
  Eye,
  TrendingUp,
  Clock,
  Wrench
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';
import ProjectOverview from './ProjectOverview';
import InspectionManagement from './InspectionManagement';

const ProjectManagement = ({ onBack, onViewReports }) => {
  const [projects, setProjects] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [showProjectOverview, setShowProjectOverview] = useState(false);
  const [showInspectionManagement, setShowInspectionManagement] = useState(false);
  const [editProject, setEditProject] = useState({});
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    client_company: '',
    project_manager: 'Jesus Garcia',
    address: '',
    billing_type: 'TM',  // TM, SOV, Fixed, Bid
    tm_bill_rate: '95.00',  // GC billing rate for T&M projects
    contract_amount: '',
    start_date: new Date(),
    estimated_completion: null,
    status: 'active'
  });
  
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();

  const projectManagers = [
    'Jesus Garcia',
    'Mike Rodriguez', 
    'Sarah Johnson',
    'David Chen'
  ];

  const statusColors = {
    active: 'bg-green-100 text-green-800',
    planning: 'bg-blue-100 text-blue-800',
    on_hold: 'bg-yellow-100 text-yellow-800',
    completed: 'bg-gray-100 text-gray-800'
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (backendUrl) {
        const response = await fetch(`${backendUrl}/api/projects`);
        if (response.ok) {
          const projectsData = await response.json();
          setProjects(projectsData);
        }
      }
    } catch (error) {
      console.warn('Failed to load projects:', error);
    }
  };

  const handleCreateProject = async () => {
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

      const projectData = {
        name: newProject.name,
        description: newProject.description,
        client_company: newProject.client_company,
        project_manager: newProject.project_manager,
        address: newProject.address,
        billing_type: newProject.billing_type,
        tm_bill_rate: newProject.billing_type === 'TM' ? parseFloat(newProject.tm_bill_rate) || 95.00 : null,
        contract_amount: parseFloat(newProject.contract_amount) || null,
        start_date: newProject.start_date.toISOString().split('T')[0], // Date only
        estimated_completion: newProject.estimated_completion ? newProject.estimated_completion.toISOString().split('T')[0] : null,
        status: newProject.status
      };

      const response = await fetch(`${backendUrl}/api/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(projectData)
      });

      if (response.ok) {
        const createdProject = await response.json();
        setProjects(prev => [createdProject, ...prev]);
        setShowCreateModal(false);
        resetNewProject();
        
        toast({
          title: "Project Created",
          description: `${createdProject.name} has been created successfully.`,
        });
      } else {
        throw new Error('Failed to create project');
      }
    } catch (error) {
      toast({
        title: "Creation Failed",
        description: "Failed to create project. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleDeleteProject = async (projectId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl) return;

      const response = await fetch(`${backendUrl}/api/projects/${projectId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setProjects(prev => prev.filter(project => project.id !== projectId));
        toast({
          title: "Project Deleted",
          description: "Project has been deleted successfully.",
        });
      }
    } catch (error) {
      toast({
        title: "Deletion Failed",
        description: "Failed to delete project.",
        variant: "destructive"
      });
    }
  };

  const handleEditProject = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl || !selectedProject) return;

      const projectData = {
        ...editProject,
        contract_amount: parseFloat(editProject.contract_amount) || 0,
        tm_bill_rate: parseFloat(editProject.tm_bill_rate) || 95.00,
        start_date: editProject.start_date,
        estimated_completion: editProject.estimated_completion
      };

      const response = await fetch(`${backendUrl}/api/projects/${selectedProject.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(projectData)
      });

      if (response.ok) {
        const updatedProject = await response.json();
        setProjects(prev => prev.map(p => p.id === selectedProject.id ? updatedProject : p));
        setShowEditModal(false);
        setSelectedProject(null);
        
        toast({
          title: "Project Updated",
          description: `${updatedProject.name} has been updated successfully.`,
        });
      } else {
        throw new Error('Failed to update project');
      }
    } catch (error) {
      toast({
        title: "Update Failed",
        description: "Failed to update project. Please try again.",
        variant: "destructive"
      });
    }
  };

  const openEditModal = (project) => {
    setSelectedProject(project);
    setEditProject({
      name: project.name,
      description: project.description || '',
      client_company: project.client_company,
      project_manager: project.project_manager,
      address: project.address || '',
      billing_type: project.billing_type || 'TM',
      tm_bill_rate: (project.tm_bill_rate || 95.00).toString(),
      contract_amount: (project.contract_amount || 0).toString(),
      start_date: project.start_date,
      estimated_completion: project.estimated_completion,
      status: project.status || 'active'
    });
    setShowEditModal(true);
  };

  const resetNewProject = () => {
    setNewProject({
      name: '',
      description: '',
      client_company: '',
      project_manager: 'Jesus Garcia',
      address: '',
      billing_type: 'TM',  // TM, SOV, Fixed, Bid
      tm_bill_rate: '95.00',  // GC billing rate for T&M projects
      contract_amount: '',
      start_date: new Date(),
      estimated_completion: null,
      status: 'active'
    });
  };

  const handleInputChange = (field, value) => {
    setNewProject(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleEditInputChange = (field, value) => {
    setEditProject(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const openProjectOverview = (project) => {
    setSelectedProject(project);
    setShowProjectOverview(true);
  };

  const openInspectionManagement = (project) => {
    setSelectedProject(project);
    setShowInspectionManagement(true);
  };

  // If showing project overview, render that component
  if (showProjectOverview && selectedProject) {
    return (
      <ProjectOverview 
        project={selectedProject}
        onBack={() => {
          setShowProjectOverview(false);
          setSelectedProject(null);
        }}
        onViewTMTags={() => {
          // Navigate back to parent and then to reports
          if (onViewReports) {
            onViewReports();
          } else {
            toast({
              title: "Navigation",
              description: "Go to Reports to view T&M tags for this project",
            });
          }
        }}
      />
    );
  }

  // If showing inspection management, render that component
  if (showInspectionManagement && selectedProject) {
    return (
      <InspectionManagement 
        project={selectedProject}
        onProjectUpdate={(updatedProject) => {
          setProjects(projects.map(p => p.id === updatedProject.id ? updatedProject : p));
          setSelectedProject(updatedProject);
        }}
        onBack={() => {
          setShowInspectionManagement(false);
          setSelectedProject(null);
        }}
      />
    );
  }

  const totalProjects = projects.length;
  const totalValue = projects.reduce((sum, project) => sum + (project.contract_amount || 0), 0);
  const activeProjects = projects.filter(p => p.status === 'active').length;
  const avgProjectValue = totalProjects > 0 ? totalValue / totalProjects : 0;

  return (
    <>
      <div className={`min-h-screen transition-all duration-300 ${themeClasses.background}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
          {/* Mobile-First Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 sm:mb-8">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full sm:w-auto">
              <Button 
                variant="outline" 
                onClick={onBack}
                className={`${themeClasses.button.secondary} w-full sm:w-auto`}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              <div className="w-full sm:w-auto">
                <h1 className={`text-2xl sm:text-3xl font-bold ${themeClasses.text.primary}`}>
                  Project Management
                </h1>
                <p className={`${themeClasses.text.secondary} text-sm sm:text-base`}>
                  Manage and track your projects
                </p>
              </div>
            </div>
            
            <Button 
              onClick={() => setShowCreateModal(true)}
              className={`${themeClasses.button.primary} w-full sm:w-auto`}
            >
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Button>
          </div>

          {/* Vision UI Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className={`${themeClasses.statsCard} rounded-lg p-6 transform hover:scale-105 transition-all duration-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Total Projects</p>
                  <p className={`text-3xl font-bold ${themeClasses.text.primary} mt-2`}>{totalProjects}</p>
                  <p className={`text-xs ${themeClasses.text.muted} mt-1`}>Active management</p>
                </div>
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.blue}20`, color: themeClasses.colors.blue }}>
                  <Building className="w-6 h-6" />
                </div>
              </div>
            </div>

            <div className={`${themeClasses.statsCard} rounded-lg p-6 transform hover:scale-105 transition-all duration-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Active Projects</p>
                  <p className={`text-3xl font-bold ${themeClasses.text.primary} mt-2`}>{activeProjects}</p>
                  <p className={`text-xs ${themeClasses.text.muted} mt-1`}>In progress</p>
                </div>
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.green}20`, color: themeClasses.colors.green }}>
                  <TrendingUp className="w-6 h-6" />
                </div>
              </div>
            </div>

            <div className={`${themeClasses.statsCard} rounded-lg p-6 transform hover:scale-105 transition-all duration-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Total Value</p>
                  <p className={`text-3xl font-bold ${themeClasses.text.primary} mt-2`}>${totalValue.toLocaleString()}</p>
                  <p className={`text-xs ${themeClasses.text.muted} mt-1`}>Portfolio value</p>
                </div>
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.purple}20`, color: themeClasses.colors.purple }}>
                  <DollarSign className="w-6 h-6" />
                </div>
              </div>
            </div>

            <div className={`${themeClasses.statsCard} rounded-lg p-6 transform hover:scale-105 transition-all duration-200`}>
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Avg Project</p>
                  <p className={`text-3xl font-bold ${themeClasses.text.primary} mt-2`}>${avgProjectValue.toLocaleString()}</p>
                  <p className={`text-xs ${themeClasses.text.muted} mt-1`}>Average value</p>
                </div>
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.amber}20`, color: themeClasses.colors.amber }}>
                  <FileText className="w-6 h-6" />
                </div>
              </div>
            </div>
          </div>

          {/* Vision UI Project Cards */}
          {projects.length === 0 ? (
            <div className={`${themeClasses.card} rounded-lg p-12 text-center`}>
              <div className={`w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center`}
                   style={{ backgroundColor: `${themeClasses.colors.blue}10` }}>
                <Building className={`w-10 h-10`} style={{ color: themeClasses.colors.blue }} />
              </div>
              <h3 className={`text-xl font-semibold mb-3 ${themeClasses.text.primary}`}>No Projects Yet</h3>
              <p className={`mb-8 ${themeClasses.text.secondary}`}>Create your first project to get started with project management.</p>
              <Button 
                onClick={() => setShowCreateModal(true)}
                className="px-8"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create First Project
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {projects.map((project) => (
                <div key={project.id} className={`${themeClasses.card} rounded-lg transform hover:scale-105 transition-all duration-200 cursor-pointer`}>
                  <div className="p-6">
                    {/* Header Section */}
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex-1">
                        <h3 className={`text-xl font-bold ${themeClasses.text.primary} mb-2 line-clamp-2`}>
                          {project.name}
                        </h3>
                        <p className={`text-sm ${themeClasses.text.secondary} flex items-center`}>
                          <Building className="w-4 h-4 mr-2" />
                          {project.client_company}
                        </p>
                      </div>
                      <div className="text-right">
                        <Badge variant={project.status === 'active' ? 'success' : project.status === 'planning' ? 'primary' : 'secondary'}>
                          {project.status || 'Active'}
                        </Badge>
                        {project.gc_pin && (
                          <div className={`text-xs ${themeClasses.text.muted} font-mono mt-2 px-2 py-1 rounded`}
                               style={{ backgroundColor: `${themeClasses.colors.blue}10` }}>
                            PIN: {project.gc_pin}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Project Details */}
                    <div className="space-y-4 mb-6">
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>Billing Type:</span>
                        <Badge variant={project.billing_type === 'TM' ? 'warning' : 'primary'}>
                          {project.billing_type || 'TM'}
                        </Badge>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>Contract Value:</span>
                        <span className={`font-bold text-lg ${themeClasses.text.primary}`}>
                          {project.contract_amount 
                            ? `$${project.contract_amount?.toLocaleString()}` 
                            : 'Not Set'
                          }
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>T&M Rate:</span>
                        <span className={`font-bold text-lg ${themeClasses.text.primary}`}>
                          ${project.tm_bill_rate || '95.00'}/hr
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>Manager:</span>
                        <span className={`text-sm font-medium ${themeClasses.text.primary}`}>{project.project_manager}</span>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>Start Date:</span>
                        <span className={`text-sm font-medium ${themeClasses.text.primary}`}>
                          {project.start_date && !isNaN(new Date(project.start_date)) 
                            ? format(new Date(project.start_date), 'MM/dd/yyyy')
                            : 'Not set'
                          }
                        </span>
                      </div>
                      
                      {project.description && (
                        <div className="p-3 rounded-lg" style={{ backgroundColor: `${themeClasses.colors.blue}05` }}>
                          <p className={`text-sm ${themeClasses.text.secondary} line-clamp-2`}>
                            {project.description}
                          </p>
                        </div>
                      )}
                    </div>
                    
                    {/* Action Buttons */}
                    <div className={`flex gap-2 pt-4 border-t`} style={{ borderColor: `${themeClasses.colors.blue}20` }}>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => openProjectOverview(project)}
                        className="flex-1 text-xs"
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        View
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => openInspectionManagement(project)}
                        className="text-xs"
                        title="Manage Inspections"
                      >
                        <Wrench className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => openEditModal(project)}
                        className="text-xs"
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDeleteProject(project.id)}
                        className="text-xs"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Create Project Modal - Vision UI Styled */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className={`sm:max-w-[700px] ${themeClasses.modal} rounded-xl`}>
          <DialogHeader className="pb-4">
            <DialogTitle className={`text-2xl font-bold ${themeClasses.text.primary} flex items-center`}>
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center mr-3 ${
                isDarkMode ? 'bg-purple-500/20 text-purple-400' : 'bg-purple-500/10 text-purple-600'
              }`}>
                <Plus className="w-5 h-5" />
              </div>
              Create New Project
            </DialogTitle>
          </DialogHeader>
          
          <div className="grid gap-4 py-4 max-h-96 overflow-y-auto">
            {/* Project Name and Client */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Project Name*</Label>
                <Input
                  value={newProject.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className={themeClasses.input}
                  placeholder="Downtown Office Complex"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Client Company*</Label>
                <Input
                  value={newProject.client_company}
                  onChange={(e) => handleInputChange('client_company', e.target.value)}
                  className={themeClasses.input}
                  placeholder="ABC Construction"
                />
              </div>
            </div>

            {/* Billing Type */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Billing Type*</Label>
              <Select value={newProject.billing_type} onValueChange={(value) => handleInputChange('billing_type', value)}>
                <SelectTrigger className={themeClasses.input}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  <SelectItem value="TM">Time & Material</SelectItem>
                  <SelectItem value="SOV">Schedule of Values</SelectItem>
                  <SelectItem value="Fixed">Fixed Price</SelectItem>
                  <SelectItem value="Bid">Bid Project</SelectItem>
                </SelectContent>
              </Select>
              <p className={`text-xs ${themeClasses.text.secondary}`}>
                Select the billing method for this project
              </p>
            </div>

            {/* Contract Amount and T&M Bill Rate */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Contract Amount ($)</Label>
                <Input
                  type="number"
                  value={newProject.contract_amount}
                  onChange={(e) => handleInputChange('contract_amount', e.target.value)}
                  className={themeClasses.input}
                  placeholder="150000"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>T&M Bill Rate ($/hr)*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newProject.tm_bill_rate}
                  onChange={(e) => handleInputChange('tm_bill_rate', e.target.value)}
                  className={themeClasses.input}
                  placeholder="95.00"
                />
              </div>
            </div>

            {/* Project Manager */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Project Manager*</Label>
              <Select value={newProject.project_manager} onValueChange={(value) => handleInputChange('project_manager', value)}>
                <SelectTrigger className={themeClasses.input}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  {projectManagers.map((manager) => (
                    <SelectItem key={manager} value={manager}>
                      {manager}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Description</Label>
              <Textarea
                value={newProject.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                className={themeClasses.input}
                placeholder="Fire protection system installation..."
                rows={3}
              />
            </div>

            {/* Address and Status */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Project Address</Label>
                <Input
                  value={newProject.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  className={themeClasses.input}
                  placeholder="123 Main St, City, State"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Status*</Label>
                <Select value={newProject.status} onValueChange={(value) => handleInputChange('status', value)}>
                  <SelectTrigger className={themeClasses.input}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className={themeClasses.modal}>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="planning">Planning</SelectItem>
                    <SelectItem value="on_hold">On Hold</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Start Date*</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        `w-full justify-start text-left font-normal ${themeClasses.button.secondary}`,
                        !newProject.start_date && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {newProject.start_date && !isNaN(new Date(newProject.start_date)) 
                        ? format(new Date(newProject.start_date), "MM/dd/yyyy") 
                        : "Pick a date"
                      }
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className={`w-auto p-0 ${themeClasses.modal}`} align="start">
                    <Calendar
                      mode="single"
                      selected={newProject.start_date}
                      onSelect={(date) => handleInputChange('start_date', date)}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Est. Completion</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        `w-full justify-start text-left font-normal ${themeClasses.button.secondary}`,
                        !newProject.estimated_completion && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {newProject.estimated_completion && !isNaN(new Date(newProject.estimated_completion)) 
                        ? format(new Date(newProject.estimated_completion), "MM/dd/yyyy") 
                        : "Pick a date"
                      }
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className={`w-auto p-0 ${themeClasses.modal}`} align="start">
                    <Calendar
                      mode="single"
                      selected={newProject.estimated_completion}
                      onSelect={(date) => handleInputChange('estimated_completion', date)}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
            </div>

            {/* Additional project fields can be added here in the future */}
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setShowCreateModal(false);
                resetNewProject();
              }}
              className={themeClasses.button.secondary}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleCreateProject}
              disabled={!newProject.name || !newProject.client_company}
              className={themeClasses.button.primary}
            >
              Create Project
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Project Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className={`sm:max-w-[600px] ${themeClasses.modal}`}>
          <DialogHeader>
            <DialogTitle className={themeClasses.text.primary}>
              Edit Project - {selectedProject?.name}
            </DialogTitle>
          </DialogHeader>
          
          <div className="grid gap-4 py-4 max-h-96 overflow-y-auto">
            {/* Project Name and Client */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Project Name*</Label>
                <Input
                  value={editProject.name || ''}
                  onChange={(e) => handleEditInputChange('name', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Client Company*</Label>
                <Input
                  value={editProject.client_company || ''}
                  onChange={(e) => handleEditInputChange('client_company', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
            </div>

            {/* Billing Type */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Billing Type*</Label>
              <Select value={editProject.billing_type || 'TM'} onValueChange={(value) => handleEditInputChange('billing_type', value)}>
                <SelectTrigger className={themeClasses.input}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  <SelectItem value="TM">Time & Material</SelectItem>
                  <SelectItem value="SOV">Schedule of Values</SelectItem>
                  <SelectItem value="Fixed">Fixed Price</SelectItem>
                  <SelectItem value="Bid">Bid Project</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Contract Amount and T&M Bill Rate */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Contract Amount ($)</Label>
                <Input
                  type="number"
                  value={editProject.contract_amount || ''}
                  onChange={(e) => handleEditInputChange('contract_amount', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>T&M Bill Rate ($/hr)*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={editProject.tm_bill_rate || '95.00'}
                  onChange={(e) => handleEditInputChange('tm_bill_rate', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
            </div>

            {/* Project Manager */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Project Manager*</Label>
              <Select value={editProject.project_manager || ''} onValueChange={(value) => handleEditInputChange('project_manager', value)}>
                <SelectTrigger className={themeClasses.input}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  {projectManagers.map((manager) => (
                    <SelectItem key={manager} value={manager}>
                      {manager}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Description</Label>
              <Textarea
                value={editProject.description || ''}
                onChange={(e) => handleEditInputChange('description', e.target.value)}
                className={themeClasses.input}
                rows={3}
              />
            </div>

            {/* Address and Status */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Project Address</Label>
                <Input
                  value={editProject.address || ''}
                  onChange={(e) => handleEditInputChange('address', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Status*</Label>
                <Select value={editProject.status || 'active'} onValueChange={(value) => handleEditInputChange('status', value)}>
                  <SelectTrigger className={themeClasses.input}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className={themeClasses.modal}>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="planning">Planning</SelectItem>
                    <SelectItem value="on_hold">On Hold</SelectItem>
                    <SelectItem value="completed">Completed</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setShowEditModal(false);
                setSelectedProject(null);
              }}
              className={themeClasses.button.secondary}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleEditProject}
              className={themeClasses.button.primary}
            >
              Update Project
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ProjectManagement;