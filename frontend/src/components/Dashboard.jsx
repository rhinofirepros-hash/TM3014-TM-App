import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Plus, FileText, Calendar, DollarSign, Users, LogOut, Mail, CheckCircle } from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import oauthEmailService from '../services/oauthEmailService';
import EmailAuthModal from './EmailAuthModal';

const Dashboard = ({ onCreateNew, onOpenProject, onManageWorkers, onViewReports, onLogout }) => {
  const [projects, setProjects] = useState([]);
  const [recentTags, setRecentTags] = useState([]);
  const [showEmailAuthModal, setShowEmailAuthModal] = useState(false);
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
        const response = await fetch(`${backendUrl}/api/tm-tags?limit=5`);
        if (response.ok) {
          const tmTags = await response.json();
          const recentTags = tmTags.map(tag => ({
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="w-20 h-16 flex items-center justify-center overflow-hidden">
                <img 
                  src="https://customer-assets.emergentagent.com/job_b98f6205-b977-4a20-97e0-9a9b9eeea432/artifacts/yzknuiqy_TITLEBLOCKRHINOFIRE1.png" 
                  alt="Rhino Fire Protection" 
                  className="w-20 h-16 object-contain"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'block';
                  }}
                />
                <span className="text-red-500 font-bold text-xl hidden">RF</span>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Rhino Fire Protection</h1>
                <p className="text-sm text-gray-500">T&M Daily Tag Dashboard</p>
              </div>
            </div>
            <Button 
              variant="outline" 
              onClick={handleLogout}
              className="flex items-center gap-2"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={handleCreateNewTag}>
              <CardContent className="p-6 text-center">
                <Plus className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <h3 className="font-medium text-gray-900">Create New T&M Tag</h3>
                <p className="text-sm text-gray-500 mt-1">Start a new time & material tag</p>
              </CardContent>
            </Card>
            
            <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={onViewReports}>
              <CardContent className="p-6 text-center">
                <FileText className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <h3 className="font-medium text-gray-900">View Reports</h3>
                <p className="text-sm text-gray-500 mt-1">View T&M tag history and reports</p>
              </CardContent>
            </Card>
            
            <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={onManageWorkers}>
              <CardContent className="p-6 text-center">
                <Users className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <h3 className="font-medium text-gray-900">Manage Workers</h3>
                <p className="text-sm text-gray-500 mt-1">Add and manage worker profiles</p>
              </CardContent>
            </Card>

            {(() => {
              const currentUser = oauthEmailService.getCurrentUser();
              return (
                <Card 
                  className="cursor-pointer hover:shadow-md transition-shadow" 
                  onClick={() => setShowEmailAuthModal(true)}
                >
                  <CardContent className="p-6 text-center">
                    {currentUser ? (
                      <>
                        <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
                        <h3 className="font-medium text-gray-900">Email Connected</h3>
                        <p className="text-sm text-gray-500 mt-1 capitalize">{currentUser.provider} ({currentUser.email.split('@')[0]})</p>
                      </>
                    ) : (
                      <>
                        <Mail className="w-8 h-8 text-orange-600 mx-auto mb-2" />
                        <h3 className="font-medium text-gray-900">Connect Email</h3>
                        <p className="text-sm text-gray-500 mt-1">Setup Gmail or Outlook for sending</p>
                      </>
                    )}
                  </CardContent>
                </Card>
              );
            })()}
          </div>
        </div>

        {/* Projects Overview */}
        <div className="mb-8">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Active Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((project) => (
              <Card key={project.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-base">{project.name}</CardTitle>
                    <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
                      {project.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      <span>Created: {project.created}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      <span>T&M Tags: {project.tagCount || 0}</span>
                    </div>
                  </div>
                  <Button 
                    size="sm" 
                    className="w-full mt-4"
                    onClick={() => onOpenProject(project)}
                  >
                    Create T&M Tag
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
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
  );
};

export default Dashboard;