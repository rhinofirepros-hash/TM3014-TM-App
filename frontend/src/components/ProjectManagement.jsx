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

const ProjectManagement = ({ onBack }) => {
  const [projects, setProjects] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [showProjectOverview, setShowProjectOverview] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    client_company: '',
    gc_email: '',
    contract_amount: '',
    project_manager: 'Jesus Garcia',
    start_date: new Date(),
    estimated_completion: null,
    address: ''
  });
  
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();

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
          description: `"${createdProject.name}" has been successfully created.`,
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

  const resetNewProject = () => {
    setNewProject({
      name: '',
      description: '',
      client_company: '',
      gc_email: '',
      contract_amount: '',
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

  const handleViewProject = (project) => {
    setSelectedProject(project);
    setShowProjectOverview(true);
  };

  const getProjectStatusColor = (status) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      completed: 'bg-blue-100 text-blue-800',
      on_hold: 'bg-yellow-100 text-yellow-800',
      cancelled: 'bg-red-100 text-red-800'
    };
    return colors[status] || colors.active;
  };

  if (showProjectOverview && selectedProject) {
    return (
      <ProjectOverview
        project={selectedProject}
        onBack={() => {
          setShowProjectOverview(false);
          setSelectedProject(null);
        }}
        onAddCrewLog={() => {}} // TODO: Implement crew logging
        onAddMaterial={() => {}} // TODO: Implement material tracking
        onViewTMTags={() => {
          // Navigate back to reports filtered by this project
          onBack(); // Go back to project management first
        }}
      />
    );
  }

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
                  Project Management
                </h1>
                <p className={themeClasses.text.secondary}>
                  Manage projects, crews, and track profitability
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

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Total Projects
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {projects.length}
                    </p>
                  </div>
                  <Building className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Active Projects
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {projects.filter(p => p.status === 'active').length}
                    </p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Contract Value
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      ${projects.reduce((sum, p) => sum + (p.contract_amount || 0), 0).toLocaleString()}
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
                      Completed Projects
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {projects.filter(p => p.status === 'completed').length}
                    </p>
                  </div>
                  <FileText className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Projects Grid */}
          {projects.length === 0 ? (
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-12 text-center">
                <Building className={`w-16 h-16 mx-auto mb-4 ${themeClasses.text.muted}`} />
                <h3 className={`text-lg font-medium mb-2 ${themeClasses.text.primary}`}>
                  No Projects Yet
                </h3>
                <p className={`mb-6 ${themeClasses.text.secondary}`}>
                  Create your first project to start tracking crews, materials, and profitability.
                </p>
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
                <Card key={project.id} className={`${themeClasses.card} shadow-xl hover:shadow-2xl transition-all duration-300 cursor-pointer`}>
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <CardTitle className={`text-lg font-semibold ${themeClasses.text.primary}`}>
                        {project.name}
                      </CardTitle>
                      <Badge className={getProjectStatusColor(project.status)}>
                        {project.status}
                      </Badge>
                    </div>
                    <p className={`text-sm ${themeClasses.text.secondary}`}>
                      {project.client_company}
                    </p>
                  </CardHeader>
                  
                  <CardContent className="pt-0">
                    <div className="space-y-3 mb-4">
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>Contract:</span>
                        <span className={`font-semibold ${themeClasses.text.primary}`}>
                          ${(project.contract_amount || 0).toLocaleString()}
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>Manager:</span>
                        <span className={`text-sm ${themeClasses.text.primary}`}>
                          {project.project_manager}
                        </span>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>Started:</span>
                        <span className={`text-sm ${themeClasses.text.primary}`}>
                          {new Date(project.start_date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>

                    {project.description && (
                      <p className={`text-sm mb-4 ${themeClasses.text.secondary} line-clamp-2`}>
                        {project.description}
                      </p>
                    )}

                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        className={`flex-1 ${themeClasses.button.primary}`}
                        onClick={() => handleViewProject(project)}
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        View
                      </Button>
                      
                      <Button 
                        size="sm" 
                        variant="outline"
                        className={themeClasses.button.secondary}
                      >
                        <Edit className="w-4 h-4" />
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
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name" className={themeClasses.text.primary}>
                  Project Name*
                </Label>
                <Input
                  id="name"
                  value={newProject.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  className={themeClasses.input}
                  placeholder="Downtown Office Complex"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="client_company" className={themeClasses.text.primary}>
                  Client Company*
                </Label>
                <Input
                  id="client_company"
                  value={newProject.client_company}
                  onChange={(e) => handleInputChange('client_company', e.target.value)}
                  className={themeClasses.input}
                  placeholder="ABC Construction"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description" className={themeClasses.text.primary}>
                Description
              </Label>
              <Textarea
                id="description"
                value={newProject.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                className={themeClasses.input}
                placeholder="Brief project description..."
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="gc_email" className={themeClasses.text.primary}>
                  GC Email*
                </Label>
                <Input
                  id="gc_email"
                  type="email"
                  value={newProject.gc_email}
                  onChange={(e) => handleInputChange('gc_email', e.target.value)}
                  className={themeClasses.input}
                  placeholder="gc@abcconstruction.com"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="contract_amount" className={themeClasses.text.primary}>
                  Contract Amount
                </Label>
                <Input
                  id="contract_amount"
                  type="number"
                  value={newProject.contract_amount}
                  onChange={(e) => handleInputChange('contract_amount', e.target.value)}
                  className={themeClasses.input}
                  placeholder="150000"
                />
              </div>
            </div>

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
                <Label className={themeClasses.text.primary}>Estimated Completion</Label>
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

            <div className="space-y-2">
              <Label htmlFor="address" className={themeClasses.text.primary}>
                Project Address
              </Label>
              <Input
                id="address"
                value={newProject.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                className={themeClasses.input}
                placeholder="123 Main St, City, State"
              />
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
              disabled={!newProject.name || !newProject.client_company || !newProject.gc_email}
              className={themeClasses.button.primary}
            >
              Create Project
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ProjectManagement;