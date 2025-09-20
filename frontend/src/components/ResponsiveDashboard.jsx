import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
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
  Moon,
  Zap,
  Shield,
  Menu,
  X
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { useTheme } from '../contexts/ThemeContext';
import oauthEmailService from '../services/oauthEmailService';
import EmailAuthModal from './EmailAuthModal';

const ResponsiveDashboard = ({ onCreateNew, onOpenProject, onManageCrew, onViewReports, onManageProjects, onLogout, onAdminGc, onFinancialManagement }) => {
  const [projects, setProjects] = useState([]);
  const [actualProjects, setActualProjects] = useState([]);
  const [recentTags, setRecentTags] = useState([]);
  const [projectAnalytics, setProjectAnalytics] = useState([]);
  const [showEmailAuthModal, setShowEmailAuthModal] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { isDarkMode, toggleTheme, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();

  useEffect(() => {
    fetchProjects();
    fetchRecentTags();
  }, []);

  const fetchProjects = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/projects`);
      if (response.ok) {
        const data = await response.json();
        setActualProjects(data);
        
        // Calculate analytics for each project
        const analytics = await Promise.all(data.map(async (project) => {
          const tagsResponse = await fetch(`${backendUrl}/api/tm-tags?projectId=${project.id}`);
          const tags = tagsResponse.ok ? await tagsResponse.json() : [];
          
          const totalHours = tags.reduce((sum, tag) => {
            return sum + tag.entries.reduce((entrySum, entry) => {
              return entry.category === 'Labor' ? entrySum + (entry.hours || 0) : entrySum;
            }, 0);
          }, 0);

          const totalCost = tags.reduce((sum, tag) => {
            return sum + tag.entries.reduce((entrySum, entry) => {
              return entrySum + (entry.total || 0);
            }, 0);
          }, 0);

          return {
            id: project.id,
            name: project.name,
            status: project.status,
            totalHours,
            totalCost,
            tagCount: tags.length,
            contractAmount: project.contract_amount || 0
          };
        }));

        setProjectAnalytics(analytics);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchRecentTags = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/tm-tags`);
      if (response.ok) {
        const data = await response.json();
        setRecentTags(data.slice(0, 5));
      }
    } catch (error) {
      console.error('Error fetching recent tags:', error);
    }
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

  const StatCard = ({ title, value, icon: Icon, onClick, delay = 0 }) => (
    <Card 
      className={`${themeClasses.card} cursor-pointer ${themeClasses.cardHover} transform transition-all duration-300`}
      onClick={onClick}
      style={{ animationDelay: `${delay}ms` }}
    >
      <CardContent className="p-4 md:p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
              {title}
            </p>
            <p className={`text-2xl md:text-3xl font-bold ${themeClasses.text.primary}`}>
              {value}
            </p>
          </div>
          <Icon className={`w-6 h-6 md:w-8 md:h-8 ${
            title.includes('Hours') ? 'text-blue-600' :
            title.includes('Revenue') ? 'text-green-600' :
            'text-orange-600'
          }`} />
        </div>
      </CardContent>
    </Card>
  );

  const ActionCard = ({ title, description, icon: Icon, onClick, delay = 0 }) => (
    <Card 
      className={`${themeClasses.card} cursor-pointer ${themeClasses.cardHover} transform transition-all duration-300`}
      onClick={onClick}
      style={{ animationDelay: `${delay}ms` }}
    >
      <CardContent className="p-4 md:p-6 text-center">
        <Icon className={`w-6 h-6 md:w-8 md:h-8 mx-auto mb-3 transition-colors duration-300 text-blue-600`} />
        <h3 className={`font-semibold text-sm md:text-base ${themeClasses.text.primary}`}>{title}</h3>
        <p className={`text-xs md:text-sm mt-1 ${themeClasses.text.secondary}`}>{description}</p>
      </CardContent>
    </Card>
  );

  return (
    <div className={`min-h-screen ${themeClasses.background}`}>
      {/* Mobile Header */}
      <div className={`${themeClasses.header} lg:hidden`}>
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-3">
            <img 
              src="https://customer-assets.emergentagent.com/job_4a677f03-9858-4c3f-97bb-9e96952a200d/artifacts/ljd1o3d7_TITLEBLOCKRHINOFIRE.png" 
              alt="Rhino Fire Protection" 
              className="h-8 w-auto"
            />
            <div>
              <h1 className={`text-lg font-bold ${themeClasses.text.primary}`}>
                Rhino Dashboard
              </h1>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className={themeClasses.button.ghost}
            >
              {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className={themeClasses.button.ghost}
            >
              {isMobileMenuOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
            </Button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className={`${themeClasses.card} m-4 p-4 rounded-lg`}>
            <div className="space-y-2">
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => {
                  onCreateNew();
                  setIsMobileMenuOpen(false);
                }}
              >
                <Plus className="w-4 h-4 mr-2" />
                Create T&M Tag
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => {
                  onManageProjects();
                  setIsMobileMenuOpen(false);
                }}
              >
                <Building className="w-4 h-4 mr-2" />
                Manage Projects
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => {
                  onManageCrew();
                  setIsMobileMenuOpen(false);
                }}
              >
                <Users className="w-4 h-4 mr-2" />
                Manage Crew
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => {
                  onViewReports();
                  setIsMobileMenuOpen(false);
                }}
              >
                <BarChart3 className="w-4 h-4 mr-2" />
                View Reports
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => {
                  onAdminGc();
                  setIsMobileMenuOpen(false);
                }}
              >
                <Shield className="w-4 h-4 mr-2" />
                GC Management
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start"
                onClick={() => {
                  onFinancialManagement();
                  setIsMobileMenuOpen(false);
                }}
              >
                <DollarSign className="w-4 h-4 mr-2" />
                Financial Management
              </Button>
              <hr className={`border-t ${isDarkMode ? 'border-slate-700' : 'border-gray-200'}`} />
              <Button
                variant="ghost"
                className="w-full justify-start text-red-600"
                onClick={() => {
                  handleLogout();
                  setIsMobileMenuOpen(false);
                }}
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Desktop Header */}
      <div className={`${themeClasses.header} hidden lg:block`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-4">
              <img 
                src="https://customer-assets.emergentagent.com/job_4a677f03-9858-4c3f-97bb-9e96952a200d/artifacts/ljd1o3d7_TITLEBLOCKRHINOFIRE.png" 
                alt="Rhino Fire Protection" 
                className="h-10 w-auto"
              />
              <div>
                <h1 className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                  Rhino Dashboard
                </h1>
                <p className={`text-sm ${themeClasses.text.secondary}`}>
                  Time & Material Management System
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button
                onClick={onCreateNew}
                className={themeClasses.button.primary}
              >
                <Plus className="w-4 h-4 mr-2" />
                Create T&M Tag
              </Button>
              
              <Button
                variant="outline"
                onClick={toggleTheme}
                className={themeClasses.button.secondary}
              >
                {isDarkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              </Button>
              
              <Button
                variant="outline"
                onClick={handleLogout}
                className="text-red-600 border-red-600 hover:bg-red-50"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6 mb-8">
          <StatCard
            title="Total Hours"
            value={projectAnalytics.reduce((sum, p) => sum + p.totalHours, 0).toFixed(1)}
            icon={Clock}
            onClick={onManageProjects}
            delay={0}
          />
          <StatCard
            title="Total Revenue"
            value={`$${projectAnalytics.reduce((sum, p) => sum + p.totalCost, 0).toLocaleString()}`}
            icon={DollarSign}
            onClick={onManageProjects}
            delay={100}
          />
          <StatCard
            title="T&M Tags"
            value={projectAnalytics.reduce((sum, p) => sum + p.tagCount, 0)}
            icon={FileText}
            onClick={onViewReports}
            delay={200}
          />
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className={`text-lg lg:text-xl font-semibold mb-4 ${themeClasses.text.primary}`}>
            Quick Actions
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-3 lg:gap-4">
            <ActionCard
              title="Manage Crew"
              description="Add and manage crew member profiles"
              icon={Users}
              onClick={onManageCrew}
              delay={300}
            />
            <ActionCard
              title="Manage Projects"
              description="Create and track project profitability"
              icon={Building}
              onClick={onManageProjects}
              delay={400}
            />
            <ActionCard
              title="View Reports"
              description="Analyze project performance"
              icon={BarChart3}
              onClick={onViewReports}
              delay={500}
            />
            <ActionCard
              title="GC Management"
              description="Access keys & logs"
              icon={Shield}
              onClick={onAdminGc}
              delay={600}
            />
            <ActionCard
              title="Financial Management"
              description="Invoices, payables & cashflow"
              icon={DollarSign}
              onClick={onFinancialManagement}
              delay={700}
            />
            <ActionCard
              title="Connect Email"
              description="Setup Gmail or Outlook for sending"
              icon={Mail}
              onClick={() => setShowEmailAuthModal(true)}
              delay={800}
            />
          </div>
        </div>

        {/* Projects Overview */}
        <div className="mb-8">
          <h2 className={`text-lg lg:text-xl font-semibold mb-4 ${themeClasses.text.primary}`}>
            Active Projects
          </h2>
          {projectAnalytics.length === 0 ? (
            <Card className={themeClasses.card}>
              <CardContent className="p-8 text-center">
                <FileText className={`w-12 h-12 mx-auto mb-4 ${themeClasses.text.muted}`} />
                <p className={themeClasses.text.secondary}>No project data available</p>
                <p className={`text-sm mt-1 ${themeClasses.text.muted}`}>Create your first T&M tag to see project analytics</p>
                <Button className="mt-4" onClick={onCreateNew}>
                  Create T&M Tag
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 lg:gap-6">
              {projectAnalytics.map((project, index) => (
                <Card 
                  key={project.id} 
                  className={`${themeClasses.card} ${themeClasses.cardHover} cursor-pointer`}
                  onClick={() => onOpenProject(project)}
                  style={{ animationDelay: `${900 + index * 100}ms` }}
                >
                  <CardContent className="p-4 lg:p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className={`font-semibold text-base lg:text-lg ${themeClasses.text.primary}`}>
                          {project.name}
                        </h3>
                        <Badge variant={project.status === 'active' ? 'default' : 'secondary'} className="mt-1">
                          {project.status}
                        </Badge>
                      </div>
                      <ArrowRight className={`w-4 h-4 ${themeClasses.text.muted}`} />
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>Total Hours:</span>
                        <span className={`text-sm font-medium ${themeClasses.text.primary}`}>{project.totalHours.toFixed(1)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>Total Cost:</span>
                        <span className={`text-sm font-medium ${themeClasses.text.primary}`}>${project.totalCost.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className={`text-sm ${themeClasses.text.secondary}`}>T&M Tags:</span>
                        <span className={`text-sm font-medium ${themeClasses.text.primary}`}>{project.tagCount}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Email Auth Modal */}
      {showEmailAuthModal && (
        <EmailAuthModal onClose={() => setShowEmailAuthModal(false)} />
      )}
    </div>
  );
};

export default ResponsiveDashboard;