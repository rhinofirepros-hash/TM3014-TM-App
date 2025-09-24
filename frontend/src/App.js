import React, { useState, useEffect } from "react";
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import Dashboard from './components/Dashboard';
import TimeAndMaterialForm from './components/TimeAndMaterialForm';
import ProjectOverview from './components/ProjectOverview';
import ProjectManagement from './components/ProjectManagement';
import CrewLogging from './components/CrewLogging';
import MaterialTracking from './components/MaterialTracking';
import EmployeeManagement from './components/EmployeeManagement';
import CrewManagement from './components/CrewManagement';
import FinancialTabs from './components/FinancialTabs';
import Reports from './components/Reports';
import PinLogin from './components/PinLogin';
import GcDashboard from './components/GcDashboard';
import GcOnlyLogin from './components/GcOnlyLogin';
import GcPortal from './components/GcPortal';
import AdminGcManagement from './components/AdminGcManagement';
import InspectionManagement from './components/InspectionManagement';
import { Toaster } from './components/ui/toaster';

function AppContent() {
  const [currentView, setCurrentView] = useState('login');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isGcAuthenticated, setIsGcAuthenticated] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedTmTag, setSelectedTmTag] = useState(null);
  const [selectedGcProject, setSelectedGcProject] = useState(null);
  const { isDarkMode } = useTheme();

  // Check authentication status on app load
  useEffect(() => {
    const authStatus = localStorage.getItem('isAuthenticated');
    const gcAuthStatus = localStorage.getItem('isGcAuthenticated');
    const gcProjectId = localStorage.getItem('selectedGcProject');
    
    // Handle hash-based navigation
    const hash = window.location.hash.substring(1);
    
    if (hash === 'gc-login') {
      setCurrentView('gc-login');
    } else if (authStatus === 'true') {
      setIsAuthenticated(true);
      setCurrentView('dashboard');
    } else if (gcAuthStatus === 'true') {
      setIsGcAuthenticated(true);
      if (gcProjectId) {
        setSelectedGcProject(gcProjectId);
        setCurrentView('gc-dashboard');
      } else {
        setCurrentView('gc-portal');
      }
    }
  }, []);

  useEffect(() => {
    // Listen for hash changes
    const handleHashChange = () => {
      const hash = window.location.hash.substring(1);
      if (hash === 'gc-login') {
        setCurrentView('gc-login');
      }
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
    setCurrentView('dashboard');
  };

  const handleGcLogin = () => {
    setIsGcAuthenticated(true);
    localStorage.setItem('isGcAuthenticated', 'true');
    setCurrentView('gc-portal');
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setIsGcAuthenticated(false);
    setCurrentView('login');
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('isGcAuthenticated');
    localStorage.removeItem('selectedGcProject');
    setSelectedProject(null);
    setSelectedTmTag(null);
    setSelectedGcProject(null);
  };

  const navigateToView = (view, project = null, tmTag = null, gcProject = null) => {
    setCurrentView(view);
    if (project) setSelectedProject(project);
    if (tmTag) setSelectedTmTag(tmTag);
    if (gcProject) {
      setSelectedGcProject(gcProject);
      localStorage.setItem('selectedGcProject', gcProject);
    }
  };

  const handleViewFinancialManagement = () => {
    setCurrentView('financial');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'login':
        return <PinLogin onLogin={handleLogin} onGcLogin={handleGcLogin} />;
      case 'gc-login':
        return <GcOnlyLogin onLoginSuccess={handleGcLogin} onBack={() => setCurrentView('login')} />;
      case 'gc-portal':
        return <GcPortal 
          onSelectProject={(projectId) => navigateToView('gc-dashboard', null, null, projectId)}
          onLogout={handleLogout}
          onLogin={() => setCurrentView('gc-login')}
        />;
      case 'gc-dashboard':
        return <GcDashboard 
          selectedProject={selectedGcProject}
          onBack={() => navigateToView('gc-portal')}
          onLogout={handleLogout}
        />;
      case 'dashboard':
        return (
          <Dashboard
            onCreateNew={() => navigateToView('create')}
            onOpenProject={(project) => navigateToView('project-overview', project)}
            onManageCrew={() => navigateToView('crew-management')}
            onManageProjects={() => navigateToView('project-management')}
            onViewReports={() => navigateToView('reports')}
            onLogout={handleLogout}
            onAdminGc={() => navigateToView('admin-gc')}
            onFinancialManagement={handleViewFinancialManagement}
          />
        );
      case 'create':
        return (
          <TimeAndMaterialForm
            onBack={() => navigateToView('dashboard')}
            onSave={() => navigateToView('dashboard')}
            project={selectedProject}
          />
        );
      case 'project-overview':
        return (
          <ProjectOverview
            project={selectedProject}
            onBack={() => navigateToView('dashboard')}
            onCreateTag={(project) => navigateToView('create', project)}
            onEditTag={(tmTag) => navigateToView('edit-tag', null, tmTag)}
            onViewTMTags={() => navigateToView('reports')}
          />
        );
      case 'edit-tag':
        return (
          <TimeAndMaterialForm
            onBack={() => navigateToView('project-overview', selectedProject)}
            onSave={() => navigateToView('project-overview', selectedProject)}
            project={selectedProject}
            tmTag={selectedTmTag}
          />
        );
      case 'project-management':
        return (
          <ProjectManagement
            onBack={() => navigateToView('dashboard')}
            onOpenProject={(project) => navigateToView('project-overview', project)}
          />
        );
      case 'crew-logging':
        return (
          <CrewLogging
            onBack={() => navigateToView('dashboard')}
            project={selectedProject}
          />
        );
      case 'material-tracking':
        return (
          <MaterialTracking
            onBack={() => navigateToView('dashboard')}
            project={selectedProject}
          />
        );
      case 'employee-management':
        return (
          <EmployeeManagement
            onBack={() => navigateToView('dashboard')}
          />
        );
      case 'crew-management':
        return (
          <CrewManagement
            onBack={() => navigateToView('dashboard')}
          />
        );
      case 'financial':
        return (
          <FinancialTabs
            onBack={() => navigateToView('dashboard')}
          />
        );
      case 'reports':
        return (
          <Reports
            onBack={() => navigateToView('dashboard')}
          />
        );
      case 'admin-gc':
        return (
          <AdminGcManagement
            onBack={() => navigateToView('dashboard')}
          />
        );
      case 'inspection-management':
        return (
          <InspectionManagement
            project={selectedProject}
            onBack={() => navigateToView('project-management')}
          />
        );
      default:
        return <PinLogin onLogin={handleLogin} onGcLogin={handleGcLogin} />;
    }
  };

  return (
    <div className={`min-h-screen transition-all duration-300 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100'
    } text-white`}>
      {renderCurrentView()}
      <Toaster />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;