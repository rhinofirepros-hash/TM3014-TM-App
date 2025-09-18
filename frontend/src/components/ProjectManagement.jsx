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
  Clock
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';
import ProjectOverview from './ProjectOverview';

const ProjectManagement = ({ onBack, onViewReports }) => {
  const [projects, setProjects] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [showProjectOverview, setShowProjectOverview] = useState(false);
  const [editProject, setEditProject] = useState({});
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    client_company: '',
    gc_email: '',
    project_type: 'full_project',
    contract_amount: '',
    labor_rate: '95',  // Default to $95/hr but customizable
    project_manager: 'Jesus Garcia',
    start_date: new Date(),
    estimated_completion: null,
    address: ''
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
        estimated_completion: newProject.estimated_completion ? newProject.estimated_completion.toISOString() : null
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
      contract_amount: project.contract_amount.toString(),
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
      gc_email: '',
      contract_amount: '',
      labor_rate: '95',  // Reset to default
      project_manager: 'Jesus Garcia',
      start_date: new Date(),
      estimated_completion: null,
      address: ''
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

  const totalProjects = projects.length;
  const totalValue = projects.reduce((sum, project) => sum + (project.contract_amount || 0), 0);
  const activeProjects = projects.filter(p => p.status === 'active').length;
  const avgProjectValue = totalProjects > 0 ? totalValue / totalProjects : 0;

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
                Back to Dashboard
              </Button>
              <div>
                <h1 className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                  Project Management
                </h1>
                <p className={themeClasses.text.secondary}>
                  Manage and track your projects
                </p>
              </div>
            </div>
            
            <Button 
              onClick={() => setShowCreateModal(true)}
              className={themeClasses.button.primary}
            >
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className={`${themeClasses.card} shadow-lg`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Total Projects</p>
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>{totalProjects}</p>
                  </div>
                  <Building className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-lg`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Active Projects</p>
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>{activeProjects}</p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-lg`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Total Value</p>
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>${totalValue.toLocaleString()}</p>
                  </div>
                  <DollarSign className="w-8 h-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-lg`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Avg Project</p>
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>${avgProjectValue.toLocaleString()}</p>
                  </div>
                  <FileText className="w-8 h-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Projects Grid */}
          {projects.length === 0 ? (
            <Card className={`${themeClasses.card} shadow-lg`}>
              <CardContent className="p-12 text-center">
                <Building className={`w-16 h-16 mx-auto mb-4 ${themeClasses.text.muted}`} />
                <h3 className={`text-lg font-medium mb-2 ${themeClasses.text.primary}`}>No Projects Yet</h3>
                <p className={`mb-6 ${themeClasses.text.secondary}`}>Create your first project to get started.</p>
                <Button 
                  onClick={() => setShowCreateModal(true)}
                  className={themeClasses.button.primary}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create First Project
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <Card key={project.id} className={`${themeClasses.card} shadow-lg hover:shadow-xl transition-shadow cursor-pointer`}>
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <CardTitle className={`text-lg ${themeClasses.text.primary} mb-1`}>
                          {project.name}
                        </CardTitle>
                        <p className={`text-sm ${themeClasses.text.secondary}`}>
                          {project.client_company}
                        </p>
                      </div>
                      <Badge className={statusColors[project.status || 'active']}>
                        {project.status || 'Active'}
                      </Badge>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="pt-0">
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className={themeClasses.text.secondary}>Contract Value:</span>
                        <span className={`font-semibold ${themeClasses.text.primary}`}>
                          ${project.contract_amount?.toLocaleString() || '0'}
                        </span>
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span className={themeClasses.text.secondary}>Manager:</span>
                        <span className={themeClasses.text.primary}>{project.project_manager}</span>
                      </div>
                      
                      <div className="flex justify-between text-sm">
                        <span className={themeClasses.text.secondary}>Start Date:</span>
                        <span className={themeClasses.text.primary}>
                          {format(new Date(project.start_date), 'MM/dd/yyyy')}
                        </span>
                      </div>
                      
                      {project.description && (
                        <p className={`text-sm ${themeClasses.text.secondary} line-clamp-2`}>
                          {project.description}
                        </p>
                      )}
                    </div>
                    
                    <div className={`flex gap-2 mt-4 pt-4 border-t ${isDarkMode ? 'border-white/10' : 'border-gray-100'}`}>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openProjectOverview(project)}
                        className={`flex-1 ${themeClasses.button.secondary}`}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        View
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openEditModal(project)}
                        className={themeClasses.button.secondary}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteProject(project.id)}
                        className="text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Create Project Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className={`sm:max-w-[600px] ${themeClasses.modal}`}>
          <DialogHeader>
            <DialogTitle className={themeClasses.text.primary}>Create New Project</DialogTitle>
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
                      {newProject.start_date ? format(newProject.start_date, "MM/dd/yyyy") : "Pick a date"}
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
                      {newProject.estimated_completion ? format(newProject.estimated_completion, "MM/dd/yyyy") : "Pick a date"}
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
              disabled={!newProject.name || !newProject.client_company || !newProject.contract_amount}
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

            {/* Contract Amount and Manager */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Contract Amount ($)*</Label>
                <Input
                  type="number"
                  value={editProject.contract_amount || ''}
                  onChange={(e) => handleEditInputChange('contract_amount', e.target.value)}
                  className={themeClasses.input}
                />
              </div>
              
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