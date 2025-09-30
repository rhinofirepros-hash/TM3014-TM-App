import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  ArrowLeft, 
  LogOut, 
  Calendar, 
  Clock,
  FileText,
  Users,
  Building,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  BarChart3,
  Sun,
  Moon,
  ClipboardCheck,
  Timer,
  Activity,
  MapPin
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const GcDashboard = ({ selectedProject, onBack, onLogout }) => {
  const [projectData, setProjectData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeLogs, setTimeLogs] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [progress, setProgress] = useState([]);
  const [error, setError] = useState(null);
  const { isDarkMode, toggleTheme, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();

  useEffect(() => {
    if (selectedProject) {
      fetchProjectData();
    }
  }, [selectedProject]);

  const fetchProjectData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      
      // Fetch project details
      const projectResponse = await fetch(`${backendUrl}/api/projects/${selectedProject}`);
      if (!projectResponse.ok) {
        throw new Error('Failed to fetch project data');
      }
      const project = await projectResponse.json();
      setProjectData(project);

      // Fetch time logs for this project (without financial data)
      const timeLogsResponse = await fetch(`${backendUrl}/api/timelogs?project_id=${selectedProject}`);
      if (timeLogsResponse.ok) {
        const logs = await timeLogsResponse.json();
        setTimeLogs(logs);
      }

      // Fetch tasks for this project
      const tasksResponse = await fetch(`${backendUrl}/api/tasks?project_id=${selectedProject}`);
      if (tasksResponse.ok) {
        const projectTasks = await tasksResponse.json();
        setTasks(projectTasks);
      }

      // Try to fetch project progress
      try {
        const progressResponse = await fetch(`${backendUrl}/api/intelligence/project/${selectedProject}`);
        if (progressResponse.ok) {
          const progressData = await progressResponse.json();
          setProgress(progressData);
        }
      } catch (progressError) {
        console.log('Progress data not available:', progressError);
      }
      
    } catch (error) {
      console.error('Error fetching project data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  // Calculate project metrics (non-financial)
  const calculateMetrics = () => {
    const totalHours = timeLogs.reduce((sum, log) => sum + (log.hours || 0), 0);
    const uniqueInstallers = [...new Set(timeLogs.map(log => log.installer_id))].length;
    const completedTasks = tasks.filter(task => task.status === 'completed').length;
    const totalTasks = tasks.length;
    const completionPercentage = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    
    // Group time logs by date for recent activity
    const recentActivity = timeLogs
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .slice(0, 5);

    return {
      totalHours,
      uniqueInstallers,
      completedTasks,
      totalTasks,
      completionPercentage,
      recentActivity
    };
  };

  const getInspectionStatus = (tasks) => {
    const inspectionTasks = tasks.filter(task => 
      task.type === 'inspection' || task.title.toLowerCase().includes('inspection')
    );
    
    if (inspectionTasks.length === 0) return { status: 'none', message: 'No inspections scheduled' };
    
    const completed = inspectionTasks.filter(t => t.status === 'completed');
    const inProgress = inspectionTasks.filter(t => t.status === 'in_progress');
    const pending = inspectionTasks.filter(t => t.status === 'open');
    
    if (completed.length > 0) {
      return { status: 'passed', message: `${completed.length} inspection(s) completed` };
    } else if (inProgress.length > 0) {
      return { status: 'scheduled', message: `${inProgress.length} inspection(s) in progress` };
    } else if (pending.length > 0) {
      return { status: 'pending', message: `${pending.length} inspection(s) pending` };
    }
    
    return { status: 'none', message: 'No active inspections' };
  };

  if (loading) {
    return (
      <div className={`min-h-screen p-4 ${themeClasses.background}`}>
        <div className="flex justify-center items-center h-64">
          <div className="text-white">Loading project data...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen p-4 ${themeClasses.background}`}>
        <div className="flex justify-center items-center h-64">
          <div className="text-red-400">Error: {error}</div>
        </div>
      </div>
    );
  }

  if (!projectData) {
    return (
      <div className={`min-h-screen p-4 ${themeClasses.background}`}>
        <div className="flex justify-center items-center h-64">
          <div className="text-white">No project data available</div>
        </div>
      </div>
    );
  }

  const metrics = calculateMetrics();
  const inspectionStatus = getInspectionStatus(tasks);

  return (
    <div className={`min-h-screen p-4 ${themeClasses.background}`}>
      {/* Header */}
      <div className={`${themeClasses.card} rounded-lg p-6 mb-6`}>
        <div className="flex justify-between items-center mb-4">
          <Button
            onClick={onBack}
            variant="ghost"
            className="flex items-center gap-2 text-slate-300 hover:text-white"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Button>
          
          <div className="flex items-center gap-4">
            <Button
              onClick={toggleTheme}
              variant="ghost"
              size="sm"
              className="text-slate-300 hover:text-white"
            >
              {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </Button>
            
            <Button
              onClick={onLogout}
              variant="ghost"
              className="flex items-center gap-2 text-slate-300 hover:text-white"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </div>
        </div>
        
        {/* Project Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-2">{projectData.name}</h1>
          <div className="flex justify-center items-center gap-4 text-slate-300">
            <div className="flex items-center gap-2">
              <Building className="w-4 h-4" />
              <span>{projectData.client_company || 'Client Name'}</span>
            </div>
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              <span>{projectData.address || 'Project Location'}</span>
            </div>
            <Badge variant={projectData.status === 'active' ? 'default' : 'secondary'}>
              {projectData.status || 'Active'}
            </Badge>
          </div>
        </div>
      </div>

      {/* Project Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <Card className={`${themeClasses.card} border-slate-700`}>
          <CardHeader className="pb-3">
            <CardTitle className="text-slate-300 text-sm flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Total Hours
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-400">{metrics.totalHours.toFixed(1)}</p>
            <p className="text-xs text-slate-500">logged to date</p>
          </CardContent>
        </Card>
        
        <Card className={`${themeClasses.card} border-slate-700`}>
          <CardHeader className="pb-3">
            <CardTitle className="text-slate-300 text-sm flex items-center gap-2">
              <Users className="w-4 h-4" />
              Active Crew
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-400">{metrics.uniqueInstallers}</p>
            <p className="text-xs text-slate-500">installers working</p>
          </CardContent>
        </Card>
        
        <Card className={`${themeClasses.card} border-slate-700`}>
          <CardHeader className="pb-3">
            <CardTitle className="text-slate-300 text-sm flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              Task Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-400">{metrics.completionPercentage}%</p>
            <p className="text-xs text-slate-500">{metrics.completedTasks}/{metrics.totalTasks} completed</p>
          </CardContent>
        </Card>
        
        <Card className={`${themeClasses.card} border-slate-700`}>
          <CardHeader className="pb-3">
            <CardTitle className="text-slate-300 text-sm flex items-center gap-2">
              <ClipboardCheck className="w-4 h-4" />
              Inspection Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2 mb-2">
              {inspectionStatus.status === 'passed' && <CheckCircle className="w-5 h-5 text-green-400" />}
              {inspectionStatus.status === 'scheduled' && <Timer className="w-5 h-5 text-yellow-400" />}
              {inspectionStatus.status === 'pending' && <AlertCircle className="w-5 h-5 text-orange-400" />}
              {inspectionStatus.status === 'none' && <Activity className="w-5 h-5 text-gray-400" />}
              <span className={`font-semibold ${
                inspectionStatus.status === 'passed' ? 'text-green-400' :
                inspectionStatus.status === 'scheduled' ? 'text-yellow-400' :
                inspectionStatus.status === 'pending' ? 'text-orange-400' : 'text-gray-400'
              }`}>
                {inspectionStatus.status === 'passed' ? 'Passed' :
                 inspectionStatus.status === 'scheduled' ? 'Scheduled' :
                 inspectionStatus.status === 'pending' ? 'Pending' : 'None'}
              </span>
            </div>
            <p className="text-xs text-slate-500">{inspectionStatus.message}</p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card className={`${themeClasses.card} border-slate-700`}>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Recent Work Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {metrics.recentActivity.length > 0 ? (
              <div className="space-y-4">
                {metrics.recentActivity.map((log, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-slate-800 rounded-lg">
                    <div>
                      <p className="text-white font-medium">{log.installer_name}</p>
                      <p className="text-slate-400 text-sm">{log.date}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-blue-400 font-semibold">{log.hours}h</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400">
                <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No recent work activity</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Task Progress */}
        <Card className={`${themeClasses.card} border-slate-700`}>
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Project Tasks
            </CardTitle>
          </CardHeader>
          <CardContent>
            {tasks.length > 0 ? (
              <div className="space-y-3">
                {tasks.slice(0, 6).map((task, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-slate-800 rounded-lg">
                    <div className="flex-1">
                      <p className="text-white font-medium">{task.title}</p>
                      <p className="text-slate-400 text-sm">{task.type}</p>
                    </div>
                    <Badge 
                      variant={task.status === 'completed' ? 'default' : 
                              task.status === 'in_progress' ? 'secondary' : 'outline'}
                      className={`${
                        task.status === 'completed' ? 'bg-green-600 text-white' :
                        task.status === 'in_progress' ? 'bg-yellow-600 text-white' :
                        'border-slate-600 text-slate-300'
                      }`}
                    >
                      {task.status}
                    </Badge>
                  </div>
                ))}
                {tasks.length > 6 && (
                  <p className="text-slate-400 text-sm text-center">
                    +{tasks.length - 6} more tasks
                  </p>
                )}
              </div>
            ) : (
              <div className="text-center py-8 text-slate-400">
                <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No tasks assigned yet</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Project Information */}
      <Card className={`${themeClasses.card} border-slate-700`}>
        <CardHeader>
          <CardTitle className="text-white">Project Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h4 className="text-slate-300 font-medium mb-2">Project Details</h4>
              <div className="space-y-2">
                <p className="text-slate-400 text-sm">
                  <span className="font-medium">Type:</span> {projectData.billing_type}
                </p>
                <p className="text-slate-400 text-sm">
                  <span className="font-medium">Manager:</span> {projectData.project_manager || 'Not assigned'}
                </p>
                <p className="text-slate-400 text-sm">
                  <span className="font-medium">Start Date:</span> {projectData.start_date || 'Not set'}
                </p>
              </div>
            </div>
            
            <div>
              <h4 className="text-slate-300 font-medium mb-2">Description</h4>
              <p className="text-slate-400 text-sm">
                {projectData.description || 'No description available'}
              </p>
            </div>
            
            <div>
              <h4 className="text-slate-300 font-medium mb-2">Progress Summary</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Completion</span>
                  <span className="text-white">{metrics.completionPercentage}%</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${metrics.completionPercentage}%` }}
                  ></div>
                </div>
                <p className="text-slate-400 text-xs">
                  Based on completed tasks and milestones
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default GcDashboard;