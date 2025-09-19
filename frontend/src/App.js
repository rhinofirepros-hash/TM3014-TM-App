import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import TimeAndMaterialForm from "./components/TimeAndMaterialForm";
import PinLogin from "./components/PinLogin";
import Dashboard from "./components/Dashboard";
import CrewManagement from "./components/CrewManagement";
import Reports from "./components/Reports";
import ProjectManagement from "./components/ProjectManagement";
import EmployeeManagement from "./components/EmployeeManagement";
import FinancialTabs from "./components/FinancialTabs";
import GcPortal from "./components/GcPortal";
import GcOnlyLogin from "./components/GcOnlyLogin";
import AdminGcManagement from "./components/AdminGcManagement";
import { Toaster } from "./components/ui/toaster";
import { ThemeProvider } from "./contexts/ThemeContext";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, form, crew, reports, projects, employees
  const [selectedProject, setSelectedProject] = useState(null);

  // Check for GC routes
  const isGcRoute = window.location.pathname.startsWith('/gc');
  const isGcLoginRoute = window.location.pathname === '/gc-login';

  useEffect(() => {
    // Check if user is already authenticated
    const authStatus = localStorage.getItem('tm_app_authenticated');
    const loginTime = localStorage.getItem('tm_app_login_time');
    
    if (authStatus === 'true' && loginTime) {
      // Check if login is still valid (24 hours)
      const loginTimeMs = parseInt(loginTime);
      const now = new Date().getTime();
      const hoursDiff = (now - loginTimeMs) / (1000 * 60 * 60);
      
      if (hoursDiff < 24) {
        setIsAuthenticated(true);
      } else {
        // Session expired
        localStorage.removeItem('tm_app_authenticated');
        localStorage.removeItem('tm_app_login_time');
      }
    }
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentView('dashboard');
    setSelectedProject(null);
  };

  const handleCreateNew = () => {
    setCurrentView('form');
    setSelectedProject(null);
  };

  const handleOpenProject = (project) => {
    setSelectedProject(project);
    setCurrentView('form');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setSelectedProject(null);
  };

  const handleManageCrew = () => {
    setCurrentView('crew');
  };

  const handleManageEmployees = () => {
    setCurrentView('employees');
  };

  const handleViewTMTags = () => {
    setCurrentView('reports');
  };

  const handleViewReports = () => {
    setCurrentView('reports');
  };



  return (
    <ThemeProvider>
      <div className="App min-h-screen w-full overflow-x-hidden">
        {/* GC Routes */}
        {isGcLoginRoute ? (
          <GcOnlyLogin onLoginSuccess={() => {
            // For GC login, we handle the redirect inside the component
            // No additional action needed here
          }} />
        ) : isGcRoute ? (
          <GcPortal />
        ) : (
          <>
            {!isAuthenticated ? (
              <PinLogin onLoginSuccess={handleLogin} />
            ) : (
              <div className="main-content">
                <BrowserRouter>
                  {currentView === 'dashboard' ? (
                    <Dashboard 
                      onCreateNew={handleCreateNew}
                      onOpenProject={handleOpenProject}
                      onManageCrew={handleManageCrew}
                      onViewReports={handleViewReports}
                      onManageProjects={() => setCurrentView('projects')}
                      onLogout={handleLogout}
                      onAdminGc={() => setCurrentView('admin-gc')}
                      onFinancialManagement={() => setCurrentView('financial')}
                    />
                  ) : currentView === 'crew' ? (
                    <CrewManagement 
                      onBack={handleBackToDashboard}
                    />
                  ) : currentView === 'reports' ? (
                    <Reports 
                      onBack={handleBackToDashboard}
                    />
                  ) : currentView === 'projects' ? (
                    <ProjectManagement 
                      onBack={handleBackToDashboard}
                      onViewReports={handleViewReports}
                    />
                  ) : currentView === 'employees' ? (
                    <EmployeeManagement 
                      onBack={handleBackToDashboard}
                    />
                  ) : currentView === 'admin-gc' ? (
                    <AdminGcManagement onBack={() => setCurrentView('dashboard')} />
                  ) : currentView === 'financial' ? (
                    <FinancialTabs 
                      project={selectedProject || { id: 'default', name: 'Default Project' }}
                      onBack={() => setCurrentView('dashboard')} 
                    />
                  ) : (
                    <TimeAndMaterialForm 
                      selectedProject={selectedProject}
                      onBackToDashboard={handleBackToDashboard}
                    />
                  )}
                </BrowserRouter>
              </div>
            )}
          </>
        )}
        <Toaster />
      </div>
    </ThemeProvider>
  );
}

export default App;