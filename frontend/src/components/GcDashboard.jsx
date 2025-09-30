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
  };
      setProjectData(data);
      // tmTagSummary is an object with summary stats, not an array of tags
      setTmTags([]); // Initialize as empty array since we don't have individual tags
      setCrewLogs([]);
    } catch (error) {
      console.error('Error fetching project data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${themeClasses.background}`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className={themeClasses.text.secondary}>Loading project data...</p>
        </div>
      </div>
    );
  }

  if (!projectData) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${themeClasses.background}`}>
        <Card className={themeClasses.card}>
          <CardContent className="text-center p-8">
            <AlertCircle className={`w-12 h-12 mx-auto mb-4`} style={{ color: themeClasses.colors.red }} />
            <h3 className={`text-lg font-semibold mb-2 ${themeClasses.text.primary}`}>Project Not Found</h3>
            <p className={`mb-4 ${themeClasses.text.secondary}`}>Unable to load project data.</p>
            <Button onClick={onBack}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Projects
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Use the summary data from the API response instead of calculating from individual tags
  const totalHours = projectData?.tmTagSummary?.totalHours || 0;
  const totalCost = 0; // Cost data not available in summary, would need separate calculation

  return (
    <div className={`min-h-screen ${themeClasses.background}`}>
      {/* Header */}
      <div className={themeClasses.header}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" onClick={onBack} className="shrink-0">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <div className="min-w-0">
                <h1 className={`text-xl sm:text-2xl font-bold ${themeClasses.text.primary} truncate`}>
                  {projectData.name}
                </h1>
                <p className={`text-sm ${themeClasses.text.secondary}`}>
                  {projectData.client_company}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button variant="ghost" size="sm" onClick={toggleTheme}>
                {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </Button>
              <Button variant="ghost" size="sm" onClick={onLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Project Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className={themeClasses.statsCard}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Total Hours</p>
                  <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>{totalHours.toFixed(1)}</p>
                </div>
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.blue}20`, color: themeClasses.colors.blue }}>
                  <Clock className="w-5 h-5" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className={themeClasses.statsCard}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Total Cost</p>
                  <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>${totalCost.toLocaleString()}</p>
                </div>
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.green}20`, color: themeClasses.colors.green }}>
                  <DollarSign className="w-5 h-5" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className={themeClasses.statsCard}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>T&M Tags</p>
                  <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>{tmTags.length}</p>
                </div>
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.purple}20`, color: themeClasses.colors.purple }}>
                  <FileText className="w-5 h-5" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className={`${themeClasses.statsCard} pointer-events-none`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Status</p>
                  <Badge variant={projectData.status === 'active' ? 'success' : 'secondary'}>
                    {projectData.status || 'Active'}
                  </Badge>
                </div>
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.amber}20`, color: themeClasses.colors.amber }}>
                  <CheckCircle className="w-5 h-5" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent T&M Tags */}
        <Card className={themeClasses.card}>
          <CardHeader>
            <CardTitle className={themeClasses.text.primary}>Recent T&M Tags</CardTitle>
          </CardHeader>
          <CardContent>
            {tmTags.length === 0 ? (
              <div className="text-center py-8">
                <FileText className={`w-12 h-12 mx-auto mb-4 ${themeClasses.text.muted}`} />
                <p className={`text-sm ${themeClasses.text.secondary}`}>No T&M tags found for this project.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {tmTags.slice(0, 5).map((tag, index) => (
                  <div key={index} className={`p-4 rounded-lg border`} 
                       style={{ borderColor: `${themeClasses.colors.blue}20`, backgroundColor: `${themeClasses.colors.blue}05` }}>
                    <div className="flex justify-between items-start">
                      <div>
                        <p className={`font-medium ${themeClasses.text.primary}`}>
                          Tag #{index + 1}
                        </p>
                        <p className={`text-sm ${themeClasses.text.secondary}`}>
                          {new Date(tag.date).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className={`font-semibold ${themeClasses.text.primary}`}>
                          ${(tag.total_cost || 0).toLocaleString()}
                        </p>
                        <p className={`text-sm ${themeClasses.text.secondary}`}>
                          {((tag.labor_entries || []).reduce((sum, entry) => sum + (entry.hours || 0), 0)).toFixed(1)}h
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default GcDashboard;