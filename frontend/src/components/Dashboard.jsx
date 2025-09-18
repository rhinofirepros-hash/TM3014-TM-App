import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { 
  Plus, 
  FileText, 
  Calendar, 
  DollarSign, 
  Users, 
  LogOut, 
  Mail, 
  CheckCircle,
  BarChart3,
  TrendingUp,
  Clock,
  Building,
  ArrowRight,
  Sun,
  Moon
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import oauthEmailService from '../services/oauthEmailService';
import EmailAuthModal from './EmailAuthModal';

const Dashboard = ({ onCreateNew, onOpenProject, onManageWorkers, onViewReports, onLogout }) => {
  const [projects, setProjects] = useState([]);
  const [recentTags, setRecentTags] = useState([]);
  const [projectAnalytics, setProjectAnalytics] = useState([]);
  const [showEmailAuthModal, setShowEmailAuthModal] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    // Clear any old mock data from localStorage
    localStorage.removeItem('tm_tags_history');
    localStorage.removeItem('recent_tm_tags');
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      if (backendUrl) {
        // Try to load recent T&M tags from backend
        const response = await fetch(`${backendUrl}/api/tm-tags?limit=50`); // Get more tags for analytics
        if (response.ok) {
          const tmTags = await response.json();
          
          // Process recent tags
          const recentTags = tmTags.slice(0, 5).map(tag => ({
            id: tag.id,
            project: tag.project_name,
            title: tag.tm_tag_title,
            date: new Date(tag.date_of_work).toLocaleDateString(),
            foreman: tag.foreman_name || 'Jesus Garcia',
            status: tag.status || 'completed',
            totalHours: tag.labor_entries?.reduce((sum, entry) => sum + (entry.total_hours || 0), 0) || 0,
            laborCost: tag.labor_entries?.reduce((sum, entry) => sum + (entry.total_hours || 0) * 95, 0) || 0,
            materialCost: tag.material_entries?.reduce((sum, entry) => sum + (entry.total || 0), 0) || 0
          }));
          setRecentTags(recentTags);
          
          // Generate project analytics
          generateProjectAnalytics(tmTags);
        } else {
          console.warn('Failed to load T&M tags from backend, using localStorage fallback');
          loadLocalStorageData();
        }
      } else {
        loadLocalStorageData();
      }
    } catch (error) {
      console.warn('Backend connection failed, using localStorage fallback:', error);
      loadLocalStorageData();
    }
  };

  const generateProjectAnalytics = (tmTags) => {
    // Group T&M tags by project name
    const projectGroups = tmTags.reduce((groups, tag) => {
      const projectName = tag.project_name;
      if (!groups[projectName]) {
        groups[projectName] = [];
      }
      groups[projectName].push(tag);
      return groups;
    }, {});

    // Calculate analytics for each project
    const analytics = Object.entries(projectGroups).map(([projectName, tags]) => {
      const totalHours = tags.reduce((sum, tag) => {
        return sum + (tag.labor_entries?.reduce((entrySum, entry) => entrySum + (entry.total_hours || 0), 0) || 0);
      }, 0);
      
      const totalLaborCost = tags.reduce((sum, tag) => {
        return sum + (tag.labor_entries?.reduce((entrySum, entry) => entrySum + (entry.total_hours || 0) * 95, 0) || 0);
      }, 0);
      
      const totalMaterialCost = tags.reduce((sum, tag) => {
        return sum + (tag.material_entries?.reduce((entrySum, entry) => entrySum + (entry.total || 0), 0) || 0);
      }, 0);

      const totalCost = totalLaborCost + totalMaterialCost;
      
      // Get latest date
      const latestDate = tags.reduce((latest, tag) => {
        const tagDate = new Date(tag.date_of_work);
        return tagDate > latest ? tagDate : latest;
      }, new Date(0));

      return {
        id: projectName.toLowerCase().replace(/\s+/g, '-'),
        name: projectName,
        tagCount: tags.length,
        totalHours,
        totalCost,
        laborCost: totalLaborCost,
        materialCost: totalMaterialCost,
        status: 'active',
        lastActivity: latestDate.toLocaleDateString(),
        progress: Math.min(100, (tags.length * 10)), // Simple progress calculation
        tags: tags.slice(0, 3) // Keep first 3 tags for quick reference
      };
    });

    // Sort by most recent activity
    analytics.sort((a, b) => new Date(b.lastActivity) - new Date(a.lastActivity));
    
    setProjectAnalytics(analytics);
    setProjects(analytics); // Update projects with analytics data
  };

  const loadLocalStorageData = () => {
    // Load saved projects and recent T&M tags from localStorage (fallback)
    const savedProjects = localStorage.getItem('saved_projects');
    const savedTags = localStorage.getItem('tm_tags_history');
    
    if (savedProjects) {
      setProjects(JSON.parse(savedProjects));
    } else {
      // No default projects - start clean
      setProjects([]);
    }
    
    if (savedTags) {
      const tags = JSON.parse(savedTags);
      setRecentTags(tags.slice(0, 5)); // Show only recent 5 tags
    }
  };

  const handleCreateNewTag = () => {
    onCreateNew();
  };

  const handleLogout = () => {
    localStorage.removeItem('tm_app_authenticated');
    localStorage.removeItem('tm_app_login_time');
    onLogout();
    toast({
      title: "Logged Out",
      description: "You have been logged out successfully.",
    });
  };

  return (
    <>
    <div className={`min-h-screen transition-all duration-300 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900' 
        : 'bg-gradient-to-br from-blue-50 via-purple-50 to-indigo-100'
    }`}>
      {/* Header with Theme Toggle */}
      <div className="backdrop-blur-sm bg-white/10 border-b border-white/20 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <img 
                src="https://customer-assets.emergentagent.com/job_4a677f03-9858-4c3f-97bb-9e96952a200d/artifacts/ljd1o3d7_TITLEBLOCKRHINOFIRE.png" 
                alt="Rhino Fire Protection" 
                className="h-10 w-auto"
              />
              <div>
                <h1 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                  T&M Dashboard
                </h1>
                <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  Welcome back, Jesus Garcia
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Theme Toggle */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsDarkMode(!isDarkMode)}
                className={`${isDarkMode ? 'text-white hover:bg-white/20' : 'text-gray-700 hover:bg-black/10'}`}
              >
                {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </Button>
              
              {/* Logout Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className={`${isDarkMode ? 'text-white hover:bg-white/20' : 'text-gray-700 hover:bg-black/10'}`}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Projects */}
          <Card className={`backdrop-blur-md border-0 shadow-xl ${
            isDarkMode 
              ? 'bg-white/10 text-white' 
              : 'bg-white/70 text-gray-900'
          }`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Active Projects
                  </p>
                  <p className="text-3xl font-bold">{projectAnalytics.length}</p>
                </div>
                <Building className={`w-8 h-8 ${isDarkMode ? 'text-purple-400' : 'text-purple-600'}`} />
              </div>
            </CardContent>
          </Card>

          {/* Total Hours */}
          <Card className={`backdrop-blur-md border-0 shadow-xl ${
            isDarkMode 
              ? 'bg-white/10 text-white' 
              : 'bg-white/70 text-gray-900'
          }`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Total Hours
                  </p>
                  <p className="text-3xl font-bold">
                    {projectAnalytics.reduce((sum, p) => sum + p.totalHours, 0).toFixed(1)}
                  </p>
                </div>
                <Clock className={`w-8 h-8 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
              </div>
            </CardContent>
          </Card>

          {/* Total Revenue */}
          <Card className={`backdrop-blur-md border-0 shadow-xl ${
            isDarkMode 
              ? 'bg-white/10 text-white' 
              : 'bg-white/70 text-gray-900'
          }`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Total Revenue
                  </p>
                  <p className="text-3xl font-bold">
                    ${projectAnalytics.reduce((sum, p) => sum + p.totalCost, 0).toLocaleString()}
                  </p>
                </div>
                <DollarSign className={`w-8 h-8 ${isDarkMode ? 'text-green-400' : 'text-green-600'}`} />
              </div>
            </CardContent>
          </Card>

          {/* T&M Tags */}
          <Card className={`backdrop-blur-md border-0 shadow-xl ${
            isDarkMode 
              ? 'bg-white/10 text-white' 
              : 'bg-white/70 text-gray-900'
          }`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    T&M Tags
                  </p>
                  <p className="text-3xl font-bold">
                    {projectAnalytics.reduce((sum, p) => sum + p.tagCount, 0)}
                  </p>
                </div>
                <FileText className={`w-8 h-8 ${isDarkMode ? 'text-orange-400' : 'text-orange-600'}`} />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className={`text-lg font-medium mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className={`cursor-pointer hover:shadow-md transition-shadow backdrop-blur-md border-0 shadow-xl ${
              isDarkMode 
                ? 'bg-white/10 text-white hover:bg-white/20' 
                : 'bg-white/70 text-gray-900 hover:bg-white/90'
            }`} onClick={handleCreateNewTag}>
              <CardContent className="p-6 text-center">
                <Plus className={`w-8 h-8 mx-auto mb-2 ${isDarkMode ? 'text-green-400' : 'text-green-600'}`} />
                <h3 className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Create New T&M Tag</h3>
                <p className={`text-sm mt-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>Start a new time & material tag</p>
              </CardContent>
            </Card>
            
            <Card className={`cursor-pointer hover:shadow-md transition-shadow backdrop-blur-md border-0 shadow-xl ${
              isDarkMode 
                ? 'bg-white/10 text-white hover:bg-white/20' 
                : 'bg-white/70 text-gray-900 hover:bg-white/90'
            }`} onClick={onViewReports}>
              <CardContent className="p-6 text-center">
                <FileText className={`w-8 h-8 mx-auto mb-2 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
                <h3 className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>View Reports</h3>
                <p className={`text-sm mt-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>View T&M tag history and reports</p>
              </CardContent>
            </Card>
            
            <Card className={`cursor-pointer hover:shadow-md transition-shadow backdrop-blur-md border-0 shadow-xl ${
              isDarkMode 
                ? 'bg-white/10 text-white hover:bg-white/20' 
                : 'bg-white/70 text-gray-900 hover:bg-white/90'
            }`} onClick={onManageWorkers}>
              <CardContent className="p-6 text-center">
                <Users className={`w-8 h-8 mx-auto mb-2 ${isDarkMode ? 'text-purple-400' : 'text-purple-600'}`} />
                <h3 className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Manage Workers</h3>
                <p className={`text-sm mt-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>Add and manage worker profiles</p>
              </CardContent>
            </Card>

            {(() => {
              const currentUser = oauthEmailService.getCurrentUser();
              return (
                <Card 
                  className={`cursor-pointer hover:shadow-md transition-shadow backdrop-blur-md border-0 shadow-xl ${
                    isDarkMode 
                      ? 'bg-white/10 text-white hover:bg-white/20' 
                      : 'bg-white/70 text-gray-900 hover:bg-white/90'
                  }`}
                  onClick={() => setShowEmailAuthModal(true)}
                >
                  <CardContent className="p-6 text-center">
                    {currentUser ? (
                      <>
                        <CheckCircle className={`w-8 h-8 mx-auto mb-2 ${isDarkMode ? 'text-green-400' : 'text-green-600'}`} />
                        <h3 className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Email Connected</h3>
                        <p className={`text-sm mt-1 capitalize ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>{currentUser.provider} ({currentUser.email.split('@')[0]})</p>
                      </>
                    ) : (
                      <>
                        <Mail className={`w-8 h-8 mx-auto mb-2 ${isDarkMode ? 'text-orange-400' : 'text-orange-600'}`} />
                        <h3 className={`font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Connect Email</h3>
                        <p className={`text-sm mt-1 ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>Setup Gmail or Outlook for sending</p>
                      </>
                    )}
                  </CardContent>
                </Card>
              );
            })()}
          </div>
        </div>

        {/* Projects Overview with Analytics */}
        <div className="mb-8">
          <h2 className={`text-lg font-medium mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>Active Projects</h2>
          {projectAnalytics.length === 0 ? (
            <Card className={`backdrop-blur-md border-0 shadow-xl ${
              isDarkMode 
                ? 'bg-white/10 text-white' 
                : 'bg-white/70 text-gray-900'
            }`}>
              <CardContent className="p-8 text-center">
                <FileText className={`w-12 h-12 mx-auto mb-4 ${isDarkMode ? 'text-gray-400' : 'text-gray-300'}`} />
                <p className={isDarkMode ? 'text-gray-300' : 'text-gray-500'}>No project data available</p>
                <p className={`text-sm mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>Create your first T&M tag to see project analytics</p>
                <Button className="mt-4" onClick={handleCreateNewTag}>
                  Create First T&M Tag
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projectAnalytics.map((project) => (
                <Card key={project.id} className={`hover:shadow-lg transition-shadow backdrop-blur-md border-0 shadow-xl ${
                  isDarkMode 
                    ? 'bg-white/10 text-white' 
                    : 'bg-white/70 text-gray-900'
                }`}>
                  <CardHeader className="pb-3">
                    <div className="flex justify-between items-start">
                      <CardTitle className={`text-base font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{project.name}</CardTitle>
                      <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
                        {project.status}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    {/* Project Statistics */}
                    <div className="space-y-3 mb-4">
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>T&M Tags:</span>
                        <span className={`font-semibold ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`}>{project.tagCount}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Total Hours:</span>
                        <span className={`font-semibold ${isDarkMode ? 'text-green-400' : 'text-green-600'}`}>{project.totalHours.toFixed(1)}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Total Cost:</span>
                        <span className={`font-semibold ${isDarkMode ? 'text-purple-400' : 'text-purple-600'}`}>${project.totalCost.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Last Activity:</span>
                        <span className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>{project.lastActivity}</span>
                      </div>
                    </div>

                    {/* Mini Cost Breakdown Chart */}
                    <div className="mb-4">
                      <div className={`text-xs mb-2 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Cost Breakdown</div>
                      <div className={`flex h-2 rounded-full overflow-hidden ${isDarkMode ? 'bg-gray-700' : 'bg-gray-200'}`}>
                        <div 
                          className={isDarkMode ? 'bg-green-400' : 'bg-green-500'}
                          style={{ 
                            width: `${project.totalCost > 0 ? (project.laborCost / project.totalCost) * 100 : 0}%` 
                          }}
                          title={`Labor: $${project.laborCost.toLocaleString()}`}
                        ></div>
                        <div 
                          className={isDarkMode ? 'bg-blue-400' : 'bg-blue-500'}
                          style={{ 
                            width: `${project.totalCost > 0 ? (project.materialCost / project.totalCost) * 100 : 0}%` 
                          }}
                          title={`Materials: $${project.materialCost.toLocaleString()}`}
                        ></div>
                      </div>
                      <div className={`flex justify-between text-xs mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        <span>Labor: ${project.laborCost.toLocaleString()}</span>
                        <span>Materials: ${project.materialCost.toLocaleString()}</span>
                      </div>
                    </div>

                    {/* Recent Tags Preview */}
                    {project.tags && project.tags.length > 0 && (
                      <div className="mb-4">
                        <div className="text-xs text-gray-600 mb-2">Recent Tags</div>
                        <div className="space-y-1">
                          {project.tags.slice(0, 2).map((tag, index) => (
                            <div key={index} className="text-xs bg-gray-50 p-2 rounded">
                              <div className="font-medium truncate">{tag.tm_tag_title}</div>
                              <div className="text-gray-500">
                                {new Date(tag.date_of_work).toLocaleDateString()}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <Button 
                      size="sm" 
                      className="w-full"
                      onClick={() => onOpenProject(project)}
                    >
                      Create T&M Tag
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div>
          <h2 className="text-lg font-medium text-gray-900 mb-4">Recent T&M Tags</h2>
          {recentTags.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>No T&M tags created yet</p>
                <p className="text-sm mt-1">Create your first T&M tag to get started</p>
                <Button className="mt-4" onClick={handleCreateNewTag}>
                  Create First T&M Tag
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {recentTags.map((tag, index) => (
                <Card key={index}>
                  <CardContent className="p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="font-medium text-gray-900">{tag.title}</h3>
                        <p className="text-sm text-gray-500">{tag.project} • {tag.date}</p>
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <Users className="w-4 h-4" />
                          {tag.workers} workers
                        </span>
                        <span className="flex items-center gap-1">
                          <DollarSign className="w-4 h-4" />
                          ${tag.total}
                        </span>
                        <Badge variant="outline">
                          {tag.status}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>

    {/* Email Authentication Modal */}
    <EmailAuthModal
      open={showEmailAuthModal}
      onClose={() => setShowEmailAuthModal(false)}
      onAuthSuccess={() => {
        setShowEmailAuthModal(false);
        toast({
          title: "Email Connected",
          description: "You can now send T&M tags directly from your email account",
        });
      }}
    />
    </>
  );
};

export default Dashboard;