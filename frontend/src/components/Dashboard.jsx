import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { StatsCard } from './ui/stats-card';
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
  Moon,
  Zap,
  Shield,
  Brain
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { useTheme } from '../contexts/ThemeContext';
import oauthEmailService from '../services/oauthEmailService';
import EmailAuthModal from './EmailAuthModal';

const Dashboard = ({ 
  onCreateNew, 
  onOpenProject, 
  onManageCrew, 
  onManageProjects, 
  onViewReports, 
  onLogout, 
  onAdminGc,
  onFinancialManagement,
  onProjectIntelligence 
}) => {
  const [projects, setProjects] = useState([]);
  const [actualProjects, setActualProjects] = useState([]);
  const [projectAnalytics, setProjectAnalytics] = useState([]);
  const [showEmailAuthModal, setShowEmailAuthModal] = useState(false);
  const { isDarkMode, toggleTheme, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();

  // Animation state
  const [visibleCards, setVisibleCards] = useState(new Set());

  useEffect(() => {
    loadData();
    // Animate cards on load
    const timer = setTimeout(() => {
      setVisibleCards(new Set([0, 1, 2, 3, 4, 5, 6, 7]));
    }, 100);
    return () => clearTimeout(timer);
  }, []);

  const loadData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const apiUrl = backendUrl ? `${backendUrl}/api` : '/api';
      
      if (apiUrl) {
        // Load projects from backend
        const projectsResponse = await fetch(`${apiUrl}/projects`);
        if (projectsResponse.ok) {
          const projectsData = await projectsResponse.json();
          setActualProjects(projectsData);
          
          // Calculate analytics for each project
          const analytics = await Promise.all(projectsData.map(async (project) => {
            try {
              const tmResponse = await fetch(`${apiUrl}/tm-tags`);
              const allTmTags = tmResponse.ok ? await tmResponse.json() : [];
              const tmTags = allTmTags.filter(tag => tag.projectId === project.id || tag.project_id === project.id);
              
              const totalHours = tmTags.reduce((sum, tag) => {
                // Handle both legacy and unified schema
                if (tag.labor_entries) {
                  // Legacy schema
                  return sum + tag.labor_entries.reduce((laborSum, entry) => 
                    laborSum + (entry.total_hours || entry.hours || 0), 0);
                } else if (tag.crewLogs) {
                  // Unified schema
                  return sum + tag.crewLogs.reduce((crewSum, crew) => 
                    crewSum + (crew.totalHours || crew.hoursWorked || 0), 0);
                }
                return sum;
              }, 0);
              
              const totalCost = tmTags.reduce((sum, tag) => 
                sum + (tag.total_cost || tag.totalBill || tag.totalLaborBill || 0), 0);
              
              return {
                projectId: project.id,
                projectName: project.name,
                totalHours: totalHours,
                totalCost: totalCost,
                tagCount: tmTags.length
              };
            } catch (error) {
              console.error(`Error calculating analytics for project ${project.id}:`, error);
              return {
                projectId: project.id,
                projectName: project.name,
                totalHours: 0,
                totalCost: 0,
                tagCount: 0
              };
            }
          }));
          
          setProjectAnalytics(analytics);
        } else {
          console.warn('Failed to load projects from backend');
          loadLocalStorageData();
        }
      } else {
        loadLocalStorageData();
      }
    } catch (error) {
      console.warn('Backend connection failed:', error);
      loadLocalStorageData();
    }
  };

  const loadLocalStorageData = () => {
    try {
      const savedProjects = localStorage.getItem('projects');
      if (savedProjects) {
        const projectsData = JSON.parse(savedProjects);
        setActualProjects(projectsData);
      }
    } catch (error) {
      console.error('Error loading localStorage data:', error);
      loadLocalStorageData();
    }
  };

  const handleCreateNewTag = () => {
    onCreateNew();
  };

  const handleLogout = () => {
    onLogout();
  };

  // Animated Card component
  const AnimatedCard = ({ children, index, delay = 0, className = "", ...props }) => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, delay);
      return () => clearTimeout(timer);
    }, [delay]);

    return (
      <div
        className={`transform transition-all duration-700 ease-out ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'
        } ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  };

  return (
    <div className={`min-h-screen ${themeClasses.background}`}>
      {/* Header */}
      <div className={themeClasses.header}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center space-x-4">
              <img 
                src="https://customer-assets.emergentagent.com/job_4a677f03-9858-4c3f-97bb-9e96952a200d/artifacts/ljd1o3d7_TITLEBLOCKRHINOFIRE.png" 
                alt="Rhino Fire Protection" 
                className="h-10 w-auto"
              />
              <div>
                <h1 className={`text-xl sm:text-2xl font-bold ${themeClasses.text.primary}`}>
                  Rhino Dashboard
                </h1>
                <p className={`text-sm ${themeClasses.text.secondary}`}>
                  Welcome
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 w-full sm:w-auto">
              {/* Theme Toggle */}
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleTheme}
                className="flex-shrink-0"
              >
                {isDarkMode ? <Sun className="w-5 h-5" style={{ color: '#FEF08A' }} /> : <Moon className="w-5 h-5" style={{ color: '#1E293B' }} />}
              </Button>
              
              {/* Logout Button */}
              <Button
                variant="ghost"
                size="sm"  
                onClick={handleLogout}
                className="flex-shrink-0"
              >
                <LogOut className="w-4 h-4 mr-2" />
                <span className="hidden sm:inline">Logout</span>
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Stats Cards with Animation */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <AnimatedCard index={0} delay={100}>
            <StatsCard
              title="Active Projects"
              value={actualProjects.filter(p => p.status === 'active').length}
              subtitle="Current workload"
              icon={Building}
              iconColor={themeClasses.colors.blue}
              onClick={onManageProjects}
              className="cursor-pointer hover:scale-105 transition-transform duration-200"
            />
          </AnimatedCard>

          <AnimatedCard index={1} delay={200}>
            <StatsCard
              title="Total Hours"
              value={projectAnalytics.reduce((sum, p) => sum + p.totalHours, 0).toFixed(1)}
              subtitle="Logged time"
              icon={Clock}
              iconColor={themeClasses.colors.green}
              onClick={onManageProjects}
              className="cursor-pointer hover:scale-105 transition-transform duration-200"
            />
          </AnimatedCard>

          <AnimatedCard index={2} delay={300}>
            <StatsCard
              title="Total Revenue"
              value={`$${projectAnalytics.reduce((sum, p) => sum + p.totalCost, 0).toLocaleString()}`}
              subtitle="Generated"
              icon={DollarSign}
              iconColor={themeClasses.colors.purple}
              onClick={onManageProjects}
              className="cursor-pointer hover:scale-105 transition-transform duration-200"
            />
          </AnimatedCard>

          <AnimatedCard index={3} delay={400}>
            <StatsCard
              title="T&M Tags"
              value={projectAnalytics.reduce((sum, p) => sum + p.tagCount, 0)}
              subtitle="Completed"
              icon={FileText}
              iconColor={themeClasses.colors.amber}
              onClick={onViewReports}
              className="cursor-pointer hover:scale-105 transition-transform duration-200"
            />
          </AnimatedCard>
        </div>

        {/* Quick Actions with Animation */}
        <div className="mb-6 sm:mb-8">
          <h2 className={`text-lg sm:text-xl font-semibold mb-4 sm:mb-6 ${themeClasses.text.primary}`}>Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
            <AnimatedCard index={4} delay={500}>
              <div className={`${themeClasses.card} rounded-lg p-4 sm:p-6 text-center cursor-pointer transform hover:scale-105 transition-all duration-200`}
                   onClick={handleCreateNewTag}>
                <div className={`w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 sm:mb-4 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.green}60`, color: themeClasses.colors.green }}>
                  <Plus className="w-5 h-5 sm:w-6 sm:h-6" style={{ filter: 'saturate(2)' }} />
                </div>
                <h3 className={`text-sm sm:text-base font-semibold ${themeClasses.text.primary} mb-1 sm:mb-2`}>Create New T&M Tag</h3>
                <p className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Start a new time & material tag</p>
              </div>
            </AnimatedCard>

            <AnimatedCard index={5} delay={600}>
              <div className={`${themeClasses.card} rounded-lg p-4 sm:p-6 text-center cursor-pointer transform hover:scale-105 transition-all duration-200`}
                   onClick={onViewReports}>
                <div className={`w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 sm:mb-4 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.blue}60`, color: themeClasses.colors.blue }}>
                  <FileText className="w-5 h-5 sm:w-6 sm:h-6" style={{ filter: 'saturate(2)' }} />
                </div>
                <h3 className={`text-sm sm:text-base font-semibold ${themeClasses.text.primary} mb-1 sm:mb-2`}>View Reports</h3>
                <p className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>View T&M tag history and reports</p>
              </div>
            </AnimatedCard>
            
            <AnimatedCard index={6} delay={700}>
              <div className={`${themeClasses.card} rounded-lg p-4 sm:p-6 text-center cursor-pointer transform hover:scale-105 transition-all duration-200`}
                   onClick={onManageCrew}>
                <div className={`w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 sm:mb-4 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.purple}60`, color: themeClasses.colors.purple }}>
                  <Users className="w-5 h-5 sm:w-6 sm:h-6" style={{ filter: 'saturate(2)' }} />
                </div>
                <h3 className={`text-sm sm:text-base font-semibold ${themeClasses.text.primary} mb-1 sm:mb-2`}>Manage Crew</h3>
                <p className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Add and manage crew member profiles</p>
              </div>
            </AnimatedCard>

            <AnimatedCard index={7} delay={800}>
              <div className={`${themeClasses.card} rounded-lg p-4 sm:p-6 text-center cursor-pointer transform hover:scale-105 transition-all duration-200`}
                   onClick={onManageProjects}>
                <div className={`w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 sm:mb-4 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.indigo}60`, color: themeClasses.colors.indigo }}>
                  <Building className="w-5 h-5 sm:w-6 sm:h-6" style={{ filter: 'saturate(2)' }} />
                </div>
                <h3 className={`text-sm sm:text-base font-semibold ${themeClasses.text.primary} mb-1 sm:mb-2`}>Manage Projects</h3>
                <p className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Create and track project profitability</p>
              </div>
            </AnimatedCard>

            <AnimatedCard index={8} delay={900}>
              <div className={`${themeClasses.card} rounded-lg p-4 sm:p-6 text-center cursor-pointer transform hover:scale-105 transition-all duration-200`}
                   onClick={() => console.log('AI Insights coming soon')}>
                <div className={`w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 sm:mb-4 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.amber}60`, color: themeClasses.colors.amber }}>
                  <Zap className="w-5 h-5 sm:w-6 sm:h-6" style={{ filter: 'saturate(2)' }} />
                </div>
                <h3 className={`text-sm sm:text-base font-semibold ${themeClasses.text.primary} mb-1 sm:mb-2`}>AI Insights</h3>
                <p className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Smart project analytics (Coming Soon)</p>
              </div>
            </AnimatedCard>

            <AnimatedCard index={9} delay={1000}>
              <div className={`${themeClasses.card} rounded-lg p-4 sm:p-6 text-center cursor-pointer transform hover:scale-105 transition-all duration-200`}
                   onClick={onAdminGc}>
                <div className={`w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 sm:mb-4 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.cyan}60`, color: themeClasses.colors.cyan }}>
                  <Shield className="w-5 h-5 sm:w-6 sm:h-6" style={{ filter: 'saturate(2)' }} />
                </div>
                <h3 className={`text-sm sm:text-base font-semibold ${themeClasses.text.primary} mb-1 sm:mb-2`}>GC Management</h3>
                <p className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Access keys & logs</p>
              </div>
            </AnimatedCard>

            <AnimatedCard index={10} delay={1100}>
              <div className={`${themeClasses.card} rounded-lg p-4 sm:p-6 text-center cursor-pointer transform hover:scale-105 transition-all duration-200`}
                   onClick={onFinancialManagement}>
                <div className={`w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 sm:mb-4 rounded-lg flex items-center justify-center`}
                     style={{ backgroundColor: `${themeClasses.colors.green}60`, color: themeClasses.colors.green }}>
                  <DollarSign className="w-5 h-5 sm:w-6 sm:h-6" style={{ filter: 'saturate(2)' }} />
                </div>
                <h3 className={`text-sm sm:text-base font-semibold ${themeClasses.text.primary} mb-1 sm:mb-2`}>Financial Management</h3>
                <p className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Invoices, payables & cashflow</p>
              </div>
            </AnimatedCard>

            <AnimatedCard index={11} delay={1200}>
              {(() => {
                const currentUser = oauthEmailService.getCurrentUser();
                return (
                  <div className={`${themeClasses.card} rounded-lg p-4 sm:p-6 text-center cursor-pointer transform hover:scale-105 transition-all duration-200`}
                       onClick={() => setShowEmailAuthModal(true)}>
                    {currentUser ? (
                      <>
                        <div className={`w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 sm:mb-4 rounded-lg flex items-center justify-center`}
                             style={{ backgroundColor: `${themeClasses.colors.green}60`, color: themeClasses.colors.green }}>
                          <CheckCircle className="w-5 h-5 sm:w-6 sm:h-6" style={{ filter: 'saturate(2)' }} />
                        </div>
                        <h3 className={`text-sm sm:text-base font-semibold ${themeClasses.text.primary} mb-1 sm:mb-2`}>Email Connected</h3>
                        <p className={`text-xs sm:text-sm ${themeClasses.text.secondary} capitalize break-words`}>
                          {currentUser.provider} ({currentUser.email.split('@')[0]})
                        </p>
                      </>
                    ) : (
                      <>
                        <div className={`w-10 h-10 sm:w-12 sm:h-12 mx-auto mb-3 sm:mb-4 rounded-lg flex items-center justify-center`}
                             style={{ backgroundColor: `${themeClasses.colors.amber}60`, color: themeClasses.colors.amber }}>
                          <Mail className="w-5 h-5 sm:w-6 sm:h-6" style={{ filter: 'saturate(2)' }} />
                        </div>
                        <h3 className={`text-sm sm:text-base font-semibold ${themeClasses.text.primary} mb-1 sm:mb-2`}>Connect Email</h3>
                        <p className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Setup Gmail or Outlook for sending</p>
                      </>
                    )}
                  </div>
                );
              })()}
            </AnimatedCard>
          </div>
        </div>
      </div>

      {/* Email Auth Modal */}
      {showEmailAuthModal && (
        <EmailAuthModal 
          onClose={() => setShowEmailAuthModal(false)}
          onSuccess={() => {
            setShowEmailAuthModal(false);
            toast({
              title: "Email Connected",
              description: "Email service has been successfully connected.",
            });
          }}
        />
      )}
    </div>
  );
};

export default Dashboard;