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
        ...newProject,
        contract_amount: parseFloat(newProject.contract_amount) || 0,
        labor_rate: parseFloat(newProject.labor_rate) || 95,
        start_date: newProject.start_date.toISOString(),
        estimated_completion: newProject.estimated_completion ? newProject.estimated_completion.toISOString() : null,
        // Include forecasted schedule fields
        estimated_hours: parseFloat(newProject.estimated_hours) || 0,
        estimated_labor_cost: parseFloat(newProject.estimated_labor_cost) || 0,
        estimated_material_cost: parseFloat(newProject.estimated_material_cost) || 0,
        estimated_profit: parseFloat(newProject.estimated_profit) || 0,
        // Include plan submittal fields
        plan_submittal_status: newProject.plan_submittal_status || (newProject.project_type === 'tm_only' ? 'approved' : 'in_design'),
        plan_submittal_date: newProject.plan_submittal_date ? newProject.plan_submittal_date.toISOString() : null,
        plan_submittal_notes: newProject.plan_submittal_notes || ''
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
        labor_rate: parseFloat(editProject.labor_rate) || 95,
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
      gc_email: project.gc_email || '',
      project_type: project.project_type || 'full_project',
      contract_amount: (project.contract_amount || 0).toString(),
      labor_rate: (project.labor_rate || 95).toString(),
      project_manager: project.project_manager,
      start_date: project.start_date,
      estimated_completion: project.estimated_completion,
      address: project.address || ''
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
                        <span className={`text-sm ${themeClasses.text.secondary}`}>Type:</span>
                        <Badge variant={project.project_type === 'tm_only' ? 'warning' : 'primary'}>
                          {project.project_type === 'tm_only' ? 'T&M Only' : 'Full Project'}
                        </Badge>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>
                          {project.project_type === 'tm_only' ? 'Estimate:' : 'Contract Value:'}
                        </span>
                        <span className={`font-bold text-lg ${themeClasses.text.primary}`}>
                          {project.project_type === 'tm_only' && !project.contract_amount 
                            ? 'T&M Based' 
                            : `$${project.contract_amount?.toLocaleString() || '0'}`
                          }
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

            {/* Project Type */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Project Type*</Label>
              <Select value={newProject.project_type} onValueChange={(value) => handleInputChange('project_type', value)}>
                <SelectTrigger className={themeClasses.input}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  <SelectItem value="full_project">Full Project (Fixed Contract)</SelectItem>
                  <SelectItem value="tm_only">Time & Material Only</SelectItem>
                </SelectContent>
              </Select>
              <p className={`text-xs ${themeClasses.text.secondary}`}>
                {newProject.project_type === 'full_project' 
                  ? 'Fixed contract with defined scope and budget'
                  : 'Open-ended T&M work - profit calculated from labor and material markup'
                }
              </p>
            </div>

            {/* Contract Amount and Labor Rate */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>
                  Contract Amount ($){newProject.project_type === 'full_project' ? '*' : ''}
                </Label>
                <Input
                  type="number"
                  value={newProject.contract_amount}
                  onChange={(e) => handleInputChange('contract_amount', e.target.value)}
                  className={themeClasses.input}
                  placeholder={newProject.project_type === 'full_project' ? '150000' : 'Optional - for reference only'}
                  disabled={newProject.project_type === 'tm_only'}
                />
                {newProject.project_type === 'tm_only' && (
                  <p className={`text-xs ${themeClasses.text.secondary}`}>
                    Not required for T&M projects - profit calculated from hourly rates
                  </p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Labor Rate ($/hr)*</Label>
                <Input
                  type="number"
                  value={newProject.labor_rate}
                  onChange={(e) => handleInputChange('labor_rate', e.target.value)}
                  className={themeClasses.input}
                  placeholder="95"
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

            {/* Address and GC Email */}
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
                <Label className={themeClasses.text.primary}>GC Email</Label>
                <Input
                  type="email"
                  value={newProject.gc_email}
                  onChange={(e) => handleInputChange('gc_email', e.target.value)}
                  className={themeClasses.input}
                  placeholder="gc@company.com"
                />
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

            {/* Forecasted Schedule (for better profit planning) */}
            <div className="space-y-4">
              <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-white/10' : 'bg-blue-50'} border`}>
                <h4 className={`font-medium text-sm mb-2 ${themeClasses.text.primary}`}>
                  📊 Forecasted Schedule & Budget (Optional)
                </h4>
                <p className={`text-xs ${themeClasses.text.secondary} mb-3`}>
                  Set expectations for better profit tracking and variance analysis
                </p>
                
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className={`text-xs ${themeClasses.text.primary}`}>Est. Total Hours</Label>
                    <Input
                      type="number"
                      value={newProject.estimated_hours}
                      onChange={(e) => handleInputChange('estimated_hours', e.target.value)}
                      className={`${themeClasses.input} h-8 text-sm`}
                      placeholder="120"
                    />
                  </div>
                  
                  <div className="space-y-1">
                    <Label className={`text-xs ${themeClasses.text.primary}`}>Est. Labor Revenue</Label>
                    <Input
                      type="number"
                      value={newProject.estimated_labor_cost}
                      onChange={(e) => handleInputChange('estimated_labor_cost', e.target.value)}
                      className={`${themeClasses.input} h-8 text-sm`}
                      placeholder="11400"
                    />
                  </div>
                  
                  <div className="space-y-1">
                    <Label className={`text-xs ${themeClasses.text.primary}`}>Est. Material Cost</Label>
                    <Input
                      type="number"
                      value={newProject.estimated_material_cost}
                      onChange={(e) => handleInputChange('estimated_material_cost', e.target.value)}
                      className={`${themeClasses.input} h-8 text-sm`}
                      placeholder="5000"
                    />
                  </div>
                  
                  <div className="space-y-1">
                    <Label className={`text-xs ${themeClasses.text.primary}`}>Est. Total Profit</Label>
                    <Input
                      type="number"
                      value={newProject.estimated_profit}
                      onChange={(e) => handleInputChange('estimated_profit', e.target.value)}
                      className={`${themeClasses.input} h-8 text-sm`}
                      placeholder="8000"
                    />
                  </div>
                </div>
                
                {/* Auto-calculate button */}
                {newProject.estimated_hours && newProject.labor_rate && (
                  <div className="mt-2 text-xs text-gray-500">
                    Auto-calc: {newProject.estimated_hours} hrs × ${newProject.labor_rate}/hr = ${(parseFloat(newProject.estimated_hours || 0) * parseFloat(newProject.labor_rate || 0)).toLocaleString()} labor revenue
                  </div>
                )}
              </div>
            </div>

            {/* Plan Submittal Section */}
            <div className={`p-4 rounded-lg border ${
              isDarkMode 
                ? 'bg-purple-900/20 border-purple-500/30' 
                : 'bg-purple-50 border-purple-200'
            }`}>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">📋</span>
                <h4 className={`font-semibold ${themeClasses.text.primary}`}>
                  Plan Submittal Tracking
                </h4>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className={themeClasses.text.primary}>Submittal Status</Label>
                  <Select 
                    value={newProject.plan_submittal_status || (newProject.project_type === 'tm_only' ? 'approved' : 'in_design')} 
                    onValueChange={(value) => handleInputChange('plan_submittal_status', value)}
                  >
                    <SelectTrigger className={themeClasses.input}>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className={themeClasses.modal}>
                      <SelectItem value="in_design">In Design</SelectItem>
                      <SelectItem value="submitted">Submitted</SelectItem>
                      <SelectItem value="corrections">Corrections Required</SelectItem>
                      <SelectItem value="approved">Approved</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label className={themeClasses.text.primary}>Submittal Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "justify-start text-left font-normal",
                          themeClasses.input,
                          !newProject.plan_submittal_date && "text-muted-foreground"
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {newProject.plan_submittal_date && !isNaN(new Date(newProject.plan_submittal_date)) 
                          ? format(new Date(newProject.plan_submittal_date), "MM/dd/yyyy") 
                          : "Select date"
                        }
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className={`w-auto p-0 ${themeClasses.modal}`}>
                      <Calendar
                        mode="single"
                        selected={newProject.plan_submittal_date ? new Date(newProject.plan_submittal_date) : null}
                        onSelect={(date) => handleInputChange('plan_submittal_date', date)}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>
              
              <div className="mt-3">
                <Label className={themeClasses.text.primary}>Submittal Notes</Label>
                <textarea
                  value={newProject.plan_submittal_notes || ''}
                  onChange={(e) => handleInputChange('plan_submittal_notes', e.target.value)}
                  className={`w-full mt-1 p-2 rounded border resize-none h-20 ${themeClasses.input}`}
                  placeholder={newProject.project_type === 'tm_only' ? 'T&M projects are auto-approved but notes can be added here...' : 'Add notes about plan submittal status...'}
                />
              </div>
              
              {newProject.project_type === 'tm_only' && (
                <div className={`mt-2 p-2 rounded text-xs ${
                  isDarkMode 
                    ? 'bg-green-900/20 text-green-300 border border-green-500/30' 
                    : 'bg-green-50 text-green-700 border border-green-200'
                }`}>
                  ℹ️ T&M projects are automatically set to "Approved" but can be edited if needed.
                </div>
              )}
            </div>
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
              disabled={!newProject.name || !newProject.client_company || (newProject.project_type === 'full_project' && !newProject.contract_amount)}
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

            {/* Project Type */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Project Type*</Label>
              <Select value={editProject.project_type || 'full_project'} onValueChange={(value) => handleEditInputChange('project_type', value)}>
                <SelectTrigger className={themeClasses.input}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  <SelectItem value="full_project">Full Project (Fixed Contract)</SelectItem>
                  <SelectItem value="tm_only">Time & Material Only</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Contract Amount and Labor Rate */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>
                  Contract Amount ($){(editProject.project_type || 'full_project') === 'full_project' ? '*' : ''}
                </Label>
                <Input
                  type="number"
                  value={editProject.contract_amount || ''}
                  onChange={(e) => handleEditInputChange('contract_amount', e.target.value)}
                  className={themeClasses.input}
                  disabled={(editProject.project_type || 'full_project') === 'tm_only'}
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Labor Rate ($/hr)*</Label>
                <Input
                  type="number"
                  value={editProject.labor_rate || '95'}
                  onChange={(e) => handleEditInputChange('labor_rate', e.target.value)}
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

            {/* Address and GC Email */}
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
                <Label className={themeClasses.text.primary}>GC Email</Label>
                <Input
                  type="email"
                  value={editProject.gc_email || ''}
                  onChange={(e) => handleEditInputChange('gc_email', e.target.value)}
                  className={themeClasses.input}
                />
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