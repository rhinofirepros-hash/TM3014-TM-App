import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  ArrowLeft, 
  Building, 
  DollarSign, 
  Clock, 
  Users, 
  TrendingUp, 
  FileText,
  Calculator,
  PieChart,
  Calendar,
  Plus,
  Package,
  UserCheck,
  Activity,
  Settings
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import CrewLogging from './CrewLogging';
import MaterialTracking from './MaterialTracking';
import EmployeeManagement from './EmployeeManagement';

const ProjectOverview = ({ project, onBack, onViewTMTags }) => {
  const [currentView, setCurrentView] = useState('overview'); // overview, crew, materials, employees
  const [projectStats, setProjectStats] = useState({
    totalHoursLogged: 0,
    totalLaborCost: 0,
    totalMaterialCost: 0,
    totalCrewExpenses: 0,
    contractAmount: 0,
    trueEmployeeCost: 0,
    profit: 0,
    profitMargin: 0,
    tmTagCount: 0,
    crewLogCount: 0,
    materialPurchaseCount: 0
  });
  
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();

  useEffect(() => {
    if (currentView === 'overview') {
      loadProjectAnalytics();
    }
  }, [project, currentView]);

  const loadProjectAnalytics = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (backendUrl && project) {
        const response = await fetch(`${backendUrl}/api/projects/${project.id}/analytics`);
        if (response.ok) {
          const analytics = await response.json();
          setProjectStats({
            totalHoursLogged: analytics.total_hours || 0,
            totalLaborCost: analytics.total_labor_cost_gc || 0,
            totalMaterialCost: analytics.total_material_cost || 0,
            totalCrewExpenses: analytics.total_crew_expenses || 0,
            contractAmount: analytics.contract_amount || 0,
            trueEmployeeCost: analytics.true_employee_cost || 0,
            laborMarkupProfit: analytics.labor_markup_profit || 0,
            profit: analytics.profit || 0,
            profitMargin: analytics.profit_margin || 0,
            tmTagCount: analytics.tm_tag_count || 0,
            crewLogCount: analytics.crew_log_count || 0,
            materialPurchaseCount: analytics.material_purchase_count || 0
          });
        }
      }
    } catch (error) {
      console.warn('Failed to load project analytics:', error);
    }
  };

  const handleNavigation = (view) => {
    setCurrentView(view);
  };

  const handleBackToOverview = () => {
    setCurrentView('overview');
    // Always refresh analytics when returning to overview
    setTimeout(() => {
      loadProjectAnalytics();
    }, 500); // Small delay to ensure backend sync is complete
  };

  // Function to refresh analytics (can be called from child components)
  const refreshProjectData = () => {
    loadProjectAnalytics();
  };

  // Render different views based on currentView
  if (currentView === 'crew') {
    return (
      <CrewLogging 
        project={project} 
        onBack={handleBackToOverview}
        onDataUpdate={refreshProjectData} // Pass refresh function
      />
    );
  }

  if (currentView === 'materials') {
    return (
      <MaterialTracking 
        project={project} 
        onBack={handleBackToOverview}
      />
    );
  }

  if (currentView === 'employees') {
    return (
      <EmployeeManagement 
        onBack={handleBackToOverview}
      />
    );
  }

  // Default overview view
  return (
    <div className={`min-h-screen p-4 transition-all duration-300 ${themeClasses.background}`}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
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
                {project.name}
              </h1>
              <p className={themeClasses.text.secondary}>Project Overview & Profitability Analysis</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
              {project.status}
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleNavigation('employees')}
              className={themeClasses.button.secondary}
            >
              <Settings className="w-4 h-4 mr-1" />
              Manage Employees
            </Button>
          </div>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          {/* Total Revenue */}
          <Card className={`${themeClasses.card} shadow-xl`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                    Total Revenue
                  </p>
                  <p className="text-3xl font-bold text-green-500">
                    ${(projectStats.totalLaborCost + projectStats.totalMaterialCost * 1.2).toLocaleString()}
                  </p>
                </div>
                <DollarSign className="w-8 h-8 text-green-500" />
              </div>
            </CardContent>
          </Card>

          {/* True Costs */}
          <Card className={`${themeClasses.card} shadow-xl`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                    True Costs
                  </p>
                  <p className="text-3xl font-bold text-red-500">
                    ${(projectStats.trueEmployeeCost + projectStats.totalMaterialCost + projectStats.totalCrewExpenses).toLocaleString()}
                  </p>
                </div>
                <Calculator className="w-8 h-8 text-red-500" />
              </div>
            </CardContent>
          </Card>

          {/* Labor Markup Profit */}
          <Card className={`${themeClasses.card} shadow-xl`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                    Labor Markup
                  </p>
                  <p className="text-3xl font-bold text-blue-500">
                    ${projectStats.laborMarkupProfit?.toLocaleString() || '0'}
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          {/* Net Profit */}
          <Card className={`${themeClasses.card} shadow-xl`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                    Net Profit
                  </p>
                  <p className={`text-3xl font-bold ${projectStats.profit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    ${projectStats.profit.toLocaleString()}
                  </p>
                </div>
                <TrendingUp className={`w-8 h-8 ${projectStats.profit >= 0 ? 'text-green-500' : 'text-red-500'}`} />
              </div>
            </CardContent>
          </Card>

          {/* Profit Margin */}
          <Card className={`${themeClasses.card} shadow-xl`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                    Profit Margin
                  </p>
                  <p className={`text-3xl font-bold ${projectStats.profitMargin >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {(projectStats.profitMargin || 0).toFixed(1)}%
                  </p>
                </div>
                <PieChart className={`w-8 h-8 ${projectStats.profitMargin >= 0 ? 'text-green-500' : 'text-red-500'}`} />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Activity Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className={`${themeClasses.card} shadow-xl cursor-pointer hover:shadow-2xl transition-all duration-300`}
                onClick={() => handleNavigation('crew')}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                    Crew Activity Logs
                  </p>
                  <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                    {projectStats.crewLogCount}
                  </p>
                </div>
                <Users className="w-8 h-8 text-blue-500" />
              </div>
              <div className="flex justify-between items-center">
                <span className={`text-sm ${themeClasses.text.secondary}`}>Total Hours:</span>
                <span className={`font-semibold ${themeClasses.text.primary}`}>
                  {projectStats.totalHoursLogged.toFixed(1)}
                </span>
              </div>
              <div className="flex justify-between items-center mt-1">
                <span className={`text-sm ${themeClasses.text.secondary}`}>Expenses:</span>
                <span className={`font-semibold ${themeClasses.text.primary}`}>
                  ${projectStats.totalCrewExpenses.toLocaleString()}
                </span>
              </div>
              <Button 
                variant="ghost" 
                className={`w-full mt-3 ${themeClasses.button.ghost}`}
              >
                <Activity className="w-4 h-4 mr-2" />
                Manage Crew Logs
              </Button>
            </CardContent>
          </Card>

          <Card className={`${themeClasses.card} shadow-xl cursor-pointer hover:shadow-2xl transition-all duration-300`}
                onClick={() => handleNavigation('materials')}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                    Material Purchases
                  </p>
                  <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                    {projectStats.materialPurchaseCount}
                  </p>
                </div>
                <Package className="w-8 h-8 text-purple-500" />
              </div>
              <div className="flex justify-between items-center">
                <span className={`text-sm ${themeClasses.text.secondary}`}>Total Cost:</span>
                <span className={`font-semibold ${themeClasses.text.primary}`}>
                  ${projectStats.totalMaterialCost.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center mt-1">
                <span className={`text-sm ${themeClasses.text.secondary}`}>With Markup:</span>
                <span className={`font-semibold text-green-600`}>
                  ${(projectStats.totalMaterialCost * 1.2).toLocaleString()}
                </span>
              </div>
              <Button 
                variant="ghost" 
                className={`w-full mt-3 ${themeClasses.button.ghost}`}
              >
                <Package className="w-4 h-4 mr-2" />
                Track Materials
              </Button>
            </CardContent>
          </Card>

          <Card className={`${themeClasses.card} shadow-xl`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                    T&M Tags
                  </p>
                  <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                    {projectStats.tmTagCount}
                  </p>
                </div>
                <FileText className="w-8 h-8 text-orange-500" />
              </div>
              <div className="flex justify-between items-center">
                <span className={`text-sm ${themeClasses.text.secondary}`}>Labor Cost:</span>
                <span className={`font-semibold ${themeClasses.text.primary}`}>
                  ${projectStats.totalLaborCost.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center mt-1">
                <span className={`text-sm ${themeClasses.text.secondary}`}>True Cost:</span>
                <span className={`font-semibold text-red-600`}>
                  ${projectStats.trueEmployeeCost.toLocaleString()}
                </span>
              </div>
              <Button 
                variant="ghost" 
                className={`w-full mt-3 ${themeClasses.button.ghost}`}
                onClick={onViewTMTags}
              >
                <FileText className="w-4 h-4 mr-2" />
                View T&M Tags
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Cost Breakdown */}
          <Card className={`${themeClasses.card} shadow-xl`}>
            <CardHeader>
              <CardTitle className={themeClasses.text.primary}>Cost Breakdown Analysis</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className={themeClasses.text.secondary}>Labor (GC Rate @ $95/hr)</span>
                  <span className={`font-semibold ${themeClasses.text.primary}`}>
                    ${projectStats.totalLaborCost.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className={themeClasses.text.secondary}>Labor (True Employee Cost)</span>
                  <span className={`font-semibold text-red-500`}>
                    ${projectStats.trueEmployeeCost.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className={themeClasses.text.secondary}>Materials (Cost)</span>
                  <span className={`font-semibold ${themeClasses.text.primary}`}>
                    ${projectStats.totalMaterialCost.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className={themeClasses.text.secondary}>Materials (w/ 20% Markup)</span>
                  <span className={`font-semibold text-green-600`}>
                    ${(projectStats.totalMaterialCost * 1.2).toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className={themeClasses.text.secondary}>Crew Expenses</span>
                  <span className={`font-semibold ${themeClasses.text.primary}`}>
                    ${projectStats.totalCrewExpenses.toLocaleString()}
                  </span>
                </div>
                
                <hr className={`${isDarkMode ? 'border-white/20' : 'border-gray-300'}`} />
                
                <div className="flex justify-between items-center text-lg font-bold">
                  <span className={themeClasses.text.primary}>Labor Markup Profit</span>
                  <span className="text-green-500">
                    ${(projectStats.totalLaborCost - projectStats.trueEmployeeCost).toLocaleString()}
                  </span>
                </div>

                <div className="flex justify-between items-center text-lg font-bold">
                  <span className={themeClasses.text.primary}>Material Markup Profit</span>
                  <span className="text-green-500">
                    ${(projectStats.totalMaterialCost * 0.2).toLocaleString()}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Project Progress */}
          <Card className={`${themeClasses.card} shadow-xl`}>
            <CardHeader>
              <CardTitle className={themeClasses.text.primary}>Project Progress & Health</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className={themeClasses.text.secondary}>Hours Logged</span>
                    <span className={themeClasses.text.primary}>{projectStats.totalHoursLogged.toFixed(1)} hrs</span>
                  </div>
                  <Progress value={Math.min(100, (projectStats.totalHoursLogged / 1000) * 100)} className="h-2" />
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className={themeClasses.text.secondary}>Budget Utilization</span>
                    <span className={themeClasses.text.primary}>
                      {projectStats.contractAmount > 0 ? ((projectStats.totalLaborCost + projectStats.totalMaterialCost) / projectStats.contractAmount * 100).toFixed(1) : 0}%
                    </span>
                  </div>
                  <Progress 
                    value={projectStats.contractAmount > 0 ? Math.min(100, ((projectStats.totalLaborCost + projectStats.totalMaterialCost) / projectStats.contractAmount) * 100) : 0} 
                    className="h-2" 
                  />
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className={themeClasses.text.secondary}>Profit Health</span>
                    <span className={`${projectStats.profitMargin >= 15 ? 'text-green-500' : projectStats.profitMargin >= 5 ? 'text-yellow-500' : 'text-red-500'}`}>
                      {projectStats.profitMargin >= 15 ? 'Excellent' : projectStats.profitMargin >= 5 ? 'Good' : 'Needs Attention'}
                    </span>
                  </div>
                  <Progress 
                    value={Math.min(100, Math.max(0, projectStats.profitMargin * 2))} 
                    className="h-2" 
                  />
                </div>
              </div>

              {/* Contract Information */}
              {projectStats.contractAmount > 0 && (
                <div className={`mt-6 p-4 rounded-lg border ${
                  isDarkMode 
                    ? 'bg-white/5 border-white/20' 
                    : 'bg-gray-50 border-gray-200'
                }`}>
                  <div className="flex justify-between items-center">
                    <span className={`font-medium ${themeClasses.text.secondary}`}>Contract Amount:</span>
                    <span className={`text-lg font-bold ${themeClasses.text.primary}`}>
                      ${projectStats.contractAmount.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <span className={`text-sm ${themeClasses.text.secondary}`}>Remaining Budget:</span>
                    <span className={`font-semibold ${
                      (projectStats.contractAmount - projectStats.totalLaborCost - projectStats.totalMaterialCost) >= 0 
                        ? 'text-green-600' 
                        : 'text-red-600'
                    }`}>
                      ${(projectStats.contractAmount - projectStats.totalLaborCost - projectStats.totalMaterialCost).toLocaleString()}
                    </span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Button 
            onClick={onViewTMTags} 
            className={`${themeClasses.button.primary} h-12`}
          >
            <FileText className="w-4 h-4 mr-2" />
            View T&M Tags
          </Button>
          
          <Button 
            onClick={() => handleNavigation('crew')} 
            className={`${themeClasses.button.primary} h-12`}
          >
            <Users className="w-4 h-4 mr-2" />
            Log Crew Activity
          </Button>
          
          <Button 
            onClick={() => handleNavigation('materials')} 
            className={`${themeClasses.button.primary} h-12`}
          >
            <Package className="w-4 h-4 mr-2" />
            Track Materials
          </Button>
          
          <Button 
            onClick={() => handleNavigation('employees')} 
            className={`${themeClasses.button.secondary} h-12`}
          >
            <UserCheck className="w-4 h-4 mr-2" />
            Manage Employees
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProjectOverview;