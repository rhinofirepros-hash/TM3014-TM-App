import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import TimeAndMaterialForm from "./components/TimeAndMaterialForm";
import PinLogin from "./components/PinLogin";
import Dashboard from "./components/Dashboard";
import WorkerManagement from "./components/WorkerManagement";
import Reports from "./components/Reports";
import ProjectManagement from "./components/ProjectManagement";
import { Toaster } from "./components/ui/toaster";
import { ThemeProvider } from "./contexts/ThemeContext";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState('dashboard'); // 'dashboard', 'form', 'workers', 'reports', or 'projects'
  const [selectedProject, setSelectedProject] = useState(null);

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

  const handleLoginSuccess = () => {
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

  const handleManageWorkers = () => {
    setCurrentView('workers');
  };

  const handleViewReports = () => {
    setCurrentView('reports');
  };

  if (!isAuthenticated) {
    return (
      <ThemeProvider>
        <div className="App">
          <PinLogin onLoginSuccess={handleLoginSuccess} />
          <Toaster />
        </div>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <div className="App">
        <BrowserRouter>
          {currentView === 'dashboard' ? (
            <Dashboard 
              onCreateNew={handleCreateNew}
              onOpenProject={handleOpenProject}
              onManageWorkers={handleManageWorkers}
              onViewReports={handleViewReports}
              onManageProjects={() => setCurrentView('projects')}
              onLogout={handleLogout}
            />
          ) : currentView === 'workers' ? (
            <WorkerManagement 
              onBack={handleBackToDashboard}
            />
          ) : currentView === 'reports' ? (
            <Reports 
              onBack={handleBackToDashboard}
            />
          ) : (
            <TimeAndMaterialForm 
              selectedProject={selectedProject}
              onBackToDashboard={handleBackToDashboard}
            />
          )}
        </BrowserRouter>
        <Toaster />
      </div>
    </ThemeProvider>
  );
}

export default App;