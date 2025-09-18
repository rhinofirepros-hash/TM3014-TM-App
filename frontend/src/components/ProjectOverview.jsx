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
  Plus
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const ProjectOverview = ({ project, onBack, onAddCrewLog, onAddMaterial, onViewTMTags }) => {
  const [projectStats, setProjectStats] = useState({
    totalHoursLogged: 0,
    totalLaborCost: 0,
    totalMaterialCost: 0,
    totalCrewExpenses: 0,
    contractAmount: 0,
    trueEmployeeCost: 0,
    profit: 0,
    profitMargin: 0
  });
  
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();

  useEffect(() => {
    loadProjectData();
  }, [project]);

  const loadProjectData = async () => {
    // Load comprehensive project data
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (backendUrl && project) {
        // Load T&M tags for this project
        const tmResponse = await fetch(`${backendUrl}/api/tm-tags?project=${project.name}`);
        const tmTags = tmResponse.ok ? await tmResponse.json() : [];
        
        // Load crew logs for this project
        const crewResponse = await fetch(`${backendUrl}/api/crew-logs?project=${project.name}`);
        const crewLogs = crewResponse.ok ? await crewResponse.json() : [];
        
        // Load materials for this project
        const materialResponse = await fetch(`${backendUrl}/api/materials?project=${project.name}`);
        const materials = materialResponse.ok ? await materialResponse.json() : [];
        
        // Load employee costs
        const employeeResponse = await fetch(`${backendUrl}/api/employees`);
        const employees = employeeResponse.ok ? await employeeResponse.json() : [];
        
        calculateProjectStats(tmTags, crewLogs, materials, employees);
      }
    } catch (error) {
      console.warn('Failed to load project data:', error);
    }
  };

  const calculateProjectStats = (tmTags, crewLogs, materials, employees) => {
    // Calculate total hours from T&M tags
    const totalHours = tmTags.reduce((sum, tag) => {
      return sum + (tag.labor_entries?.reduce((laborSum, entry) => laborSum + (entry.total_hours || 0), 0) || 0);
    }, 0);

    // Calculate labor cost at GC rate ($95/hr)
    const totalLaborCost = totalHours * 95;

    // Calculate material costs
    const totalMaterialCost = materials.reduce((sum, material) => sum + (material.cost || 0), 0);

    // Calculate crew expenses (per diem, hotels, etc.)
    const totalCrewExpenses = crewLogs.reduce((sum, log) => {
      return sum + (log.per_diem || 0) + (log.hotel_cost || 0) + (log.other_expenses || 0);
    }, 0);

    // Calculate true employee costs
    const trueEmployeeCost = tmTags.reduce((sum, tag) => {
      return sum + (tag.labor_entries?.reduce((laborSum, entry) => {
        const employee = employees.find(emp => emp.name === entry.worker_name);
        const trueCost = employee ? (employee.base_pay + employee.burden_cost) : 50; // Default $50/hr if not found
        return laborSum + (entry.total_hours || 0) * trueCost;
      }, 0) || 0);
    }, 0);

    // Calculate profit
    const totalRevenue = totalLaborCost + (totalMaterialCost * 1.2); // Assume 20% material markup
    const totalCosts = trueEmployeeCost + totalMaterialCost + totalCrewExpenses;
    const profit = totalRevenue - totalCosts;
    const profitMargin = totalRevenue > 0 ? (profit / totalRevenue) * 100 : 0;

    setProjectStats({
      totalHoursLogged: totalHours,
      totalLaborCost,
      totalMaterialCost,
      totalCrewExpenses,
      contractAmount: project.contractAmount || totalRevenue,
      trueEmployeeCost,
      profit,
      profitMargin
    });
  };

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
              <p className={themeClasses.text.secondary}>Project Overview & Profitability</p>
            </div>
          </div>
          <Badge variant={project.status === 'active' ? 'default' : 'secondary'}>
            {project.status}
          </Badge>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
                    {projectStats.profitMargin.toFixed(1)}%
                  </p>
                </div>
                <PieChart className={`w-8 h-8 ${projectStats.profitMargin >= 0 ? 'text-green-500' : 'text-red-500'}`} />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Cost Breakdown */}
          <Card className={`${themeClasses.card} shadow-xl`}>
            <CardHeader>
              <CardTitle className={themeClasses.text.primary}>Cost Breakdown</CardTitle>
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
                  <span className={themeClasses.text.secondary}>Labor (True Cost)</span>
                  <span className={`font-semibold text-red-500`}>
                    ${projectStats.trueEmployeeCost.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className={themeClasses.text.secondary}>Materials</span>
                  <span className={`font-semibold ${themeClasses.text.primary}`}>
                    ${projectStats.totalMaterialCost.toLocaleString()}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className={themeClasses.text.secondary}>Crew Expenses</span>
                  <span className={`font-semibold ${themeClasses.text.primary}`}>
                    ${projectStats.totalCrewExpenses.toLocaleString()}
                  </span>
                </div>
                
                <hr className="border-gray-300" />
                
                <div className="flex justify-between items-center text-lg font-bold">
                  <span className={themeClasses.text.primary}>Labor Markup</span>
                  <span className="text-green-500">
                    ${(projectStats.totalLaborCost - projectStats.trueEmployeeCost).toLocaleString()}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Project Progress */}
          <Card className={`${themeClasses.card} shadow-xl`}>
            <CardHeader>
              <CardTitle className={themeClasses.text.primary}>Project Progress</CardTitle>
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
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Button onClick={onViewTMTags} className={themeClasses.button.primary}>
            <FileText className="w-4 h-4 mr-2" />
            View T&M Tags
          </Button>
          
          <Button onClick={onAddCrewLog} className={themeClasses.button.primary}>
            <Users className="w-4 h-4 mr-2" />
            Add Crew Log
          </Button>
          
          <Button onClick={onAddMaterial} className={themeClasses.button.primary}>
            <Plus className="w-4 h-4 mr-2" />
            Add Material
          </Button>
          
          <Button onClick={() => {}} className={themeClasses.button.secondary}>
            <Calendar className="w-4 h-4 mr-2" />
            Schedule
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ProjectOverview;