import React, { useState, useEffect } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { AnimatedCard, CardContent } from './ui/animated-card';
import {
  MapPin,
  TrendingUp,
  Activity,
  Users,
  FileText,
  Package,
  CheckCircle,
  Calendar,
  Clock,
  Wrench,
  Zap,
  Building,
  Sun,
  Moon,
  AlertCircle
} from 'lucide-react';

const GcDashboard = ({ projectId, keyId, adminAccess, onLogout }) => {
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (projectId) {
      loadDashboardData();
    }
  }, [projectId]);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/gc/dashboard/${projectId}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log('GC Dashboard data:', data);
        setDashboardData(data);
      } else {
        throw new Error('Failed to load dashboard data');
      }
    } catch (error) {
      console.error('Error loading GC dashboard:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const getPhaseIcon = (phase) => {
    const icons = {
      design: Activity,
      approval: CheckCircle,
      mobilization: Wrench,
      installation: Building,
      inspection: AlertCircle,
      closeout: FileText
    };
    return icons[phase] || Activity;
  };

  const getStatusBadge = (status) => {
    const statusColors = {
      pending: 'secondary',
      scheduled: 'default',
      passed: 'success',
      failed: 'destructive',
      active: 'default'
    };
    
    return (
      <Badge variant={statusColors[status] || 'secondary'}>
        {status?.charAt(0).toUpperCase() + status?.slice(1)}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className={`text-center ${themeClasses.text.secondary}`}>
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p>Loading project dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className={themeClasses.card.primary}>
          <CardContent className="p-8 text-center">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
            <h3 className={`text-lg font-semibold mb-2 ${themeClasses.text.primary}`}>
              Unable to Load Dashboard
            </h3>
            <p className={themeClasses.text.secondary}>{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!dashboardData) {
    return null;
  }

  return (
    <div className={`min-h-screen ${
      isDarkMode 
        ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100'
    }`}>
      {/* Header - matches main Dashboard */}
      <div className="backdrop-blur-sm bg-white/10 border-b border-white/20">
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
                  {dashboardData.projectName}
                </h1>
                {dashboardData.projectLocation && (
                  <p className={`flex items-center gap-2 text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    <MapPin className="w-4 h-4" />
                    {dashboardData.projectLocation}
                  </p>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="flex items-center gap-2 mb-2">
                  {getStatusBadge(dashboardData.projectStatus)}
                  {adminAccess && (
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary" className="text-xs bg-purple-100 text-purple-800 border-purple-300 dark:bg-purple-900 dark:text-purple-200 dark:border-purple-700">
                        Admin Access
                      </Badge>
                      <button
                        onClick={() => window.close()}
                        className={`text-xs px-2 py-1 rounded border transition-colors ${
                          isDarkMode 
                            ? 'text-gray-300 border-gray-600 hover:text-white hover:bg-white/10' 
                            : 'text-gray-600 border-gray-300 hover:text-gray-900 hover:bg-gray-100'
                        }`}
                      >
                        Close Tab
                      </button>
                    </div>
                  )}
                </div>
                <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  Last Updated: {new Date(dashboardData.lastUpdated).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Overall Progress - using AnimatedCard */}
        <AnimatedCard 
          delay={100}
          className={`cursor-default hover:shadow-2xl transition-all duration-300 ease-out backdrop-blur-md border-0 shadow-xl ${
            isDarkMode 
              ? 'bg-white/10 text-white' 
              : 'bg-white/70 text-gray-900'
          }`}
        >
          <CardContent className="p-6">
            <div className={`flex items-center gap-2 mb-4`}>
              <TrendingUp className="w-5 h-5 text-blue-500" />
              <h2 className={`text-lg font-semibold ${themeClasses.text.primary}`}>Overall Project Progress</h2>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                  {Math.round(dashboardData.overallProgress)}%
                </span>
                <span className={themeClasses.text.secondary}>Complete</span>
              </div>
              <Progress value={dashboardData.overallProgress} className="h-3" />
            </div>
          </CardContent>
        </AnimatedCard>

        {/* Project Phases - using AnimatedCard */}
        <AnimatedCard 
          delay={200}
          className={`cursor-default hover:shadow-2xl transition-all duration-300 ease-out backdrop-blur-md border-0 shadow-xl ${
            isDarkMode 
              ? 'bg-white/10 text-white' 
              : 'bg-white/70 text-gray-900'
          }`}
        >
          <CardContent className="p-6">
            <div className={`flex items-center gap-2 mb-4`}>
              <Activity className="w-5 h-5 text-blue-500" />
              <h2 className={`text-lg font-semibold ${themeClasses.text.primary}`}>Project Phases</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dashboardData.phases.map((phase, index) => {
                const PhaseIcon = getPhaseIcon(phase.phase);
                return (
                  <AnimatedCard 
                    key={phase.id}
                    delay={300 + index * 50}
                    className={`cursor-default transition-all duration-300 ease-out backdrop-blur-sm border-0 shadow-md ${
                      isDarkMode ? 'bg-white/5 text-white hover:bg-white/10' : 'bg-gray-50/50 text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <AnimatedCardContent className="p-4">
                      <div className="flex items-center gap-3 mb-3">
                        <PhaseIcon className="w-5 h-5 text-blue-500" />
                        <h4 className={`font-semibold ${themeClasses.text.primary}`}>
                          {phase.phase.charAt(0).toUpperCase() + phase.phase.slice(1)}
                        </h4>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className={`text-sm ${themeClasses.text.secondary}`}>Progress</span>
                          <span className={`text-sm font-medium ${themeClasses.text.primary}`}>
                            {Math.round(phase.percentComplete)}%
                          </span>
                        </div>
                        <Progress value={phase.percentComplete} className="h-2" />
                        {phase.plannedDate && (
                          <p className={`text-xs ${themeClasses.text.secondary}`}>
                            Planned: {new Date(phase.plannedDate).toLocaleDateString()}
                          </p>
                        )}
                        {phase.actualDate && (
                          <p className={`text-xs text-green-400`}>
                            Completed: {new Date(phase.actualDate).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    </AnimatedCardContent>
                  </AnimatedCard>
                );
              })}
            </div>
          </CardContent>
        </AnimatedCard>

        {/* Summary Cards - using AnimatedCard pattern */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Crew Summary */}
          <AnimatedCard 
            delay={400}
            className={`cursor-default hover:shadow-2xl transition-all duration-300 ease-out backdrop-blur-md border-0 shadow-xl ${
              isDarkMode 
                ? 'bg-white/10 text-white hover:bg-white/20' 
                : 'bg-white/70 text-gray-900 hover:bg-white/90'
            }`}
          >
            <CardContent className="p-6">
              <div className={`flex items-center gap-2 mb-4`}>
                <Users className="w-5 h-5 text-blue-500" />
                <h3 className={`text-lg font-semibold ${themeClasses.text.primary}`}>Crew Activity</h3>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                      {dashboardData.crewSummary.totalHours.toFixed(0)}
                    </p>
                    <p className={`text-sm ${themeClasses.text.secondary}`}>Total Hours</p>
                  </div>
                  <div className="text-center">
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                      {dashboardData.crewSummary.totalDays}
                    </p>
                    <p className={`text-sm ${themeClasses.text.secondary}`}>Work Days</p>
                  </div>
                </div>
                <div className="pt-2 border-t border-white/20">
                  <p className={`text-sm font-medium mb-2 ${themeClasses.text.primary}`}>
                    Active Crew: {dashboardData.crewSummary.activeCrewMembers} members
                  </p>
                  {dashboardData.crewSummary.recentDescriptions.length > 0 && (
                    <div>
                      <p className={`text-xs font-medium mb-1 ${themeClasses.text.secondary}`}>
                        Recent Work:
                      </p>
                      {dashboardData.crewSummary.recentDescriptions.slice(0, 2).map((desc, index) => (
                        <p key={index} className={`text-xs ${themeClasses.text.secondary} mb-1 truncate`}>
                          • {desc}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </AnimatedCard>

          {/* T&M Tags Summary */}
          <AnimatedCard 
            delay={500}
            className={`cursor-default hover:shadow-2xl transition-all duration-300 ease-out backdrop-blur-md border-0 shadow-xl ${
              isDarkMode 
                ? 'bg-white/10 text-white hover:bg-white/20' 
                : 'bg-white/70 text-gray-900 hover:bg-white/90'
            }`}
          >
            <AnimatedCardContent className="p-6">
              <div className={`flex items-center gap-2 mb-4`}>
                <FileText className="w-5 h-5 text-blue-500" />
                <h3 className={`text-lg font-semibold ${themeClasses.text.primary}`}>Daily Reports</h3>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                      {dashboardData.tmTagSummary.totalTags}
                    </p>
                    <p className={`text-sm ${themeClasses.text.secondary}`}>Total Tags</p>
                  </div>
                  <div className="text-center">
                    <p className={`text-2xl font-bold text-green-400`}>
                      {dashboardData.tmTagSummary.approvedTags}
                    </p>
                    <p className={`text-sm ${themeClasses.text.secondary}`}>Approved</p>
                  </div>
                </div>
                <div className="pt-2 border-t border-white/20">
                  <p className={`text-sm ${themeClasses.text.secondary}`}>
                    Submitted: {dashboardData.tmTagSummary.submittedTags} tags
                  </p>
                  <p className={`text-sm ${themeClasses.text.secondary}`}>
                    Total Hours: {dashboardData.tmTagSummary.totalHours.toFixed(0)} hrs
                  </p>
                </div>
              </div>
            </AnimatedCardContent>
          </AnimatedCard>

          {/* Materials Summary */}
          <AnimatedCard 
            delay={600}
            className={`cursor-default hover:shadow-2xl transition-all duration-300 ease-out backdrop-blur-md border-0 shadow-xl ${
              isDarkMode 
                ? 'bg-white/10 text-white hover:bg-white/20' 
                : 'bg-white/70 text-gray-900 hover:bg-white/90'
            }`}
          >
            <AnimatedCardContent className="p-6">
              <div className={`flex items-center gap-2 mb-4`}>
                <Package className="w-5 h-5 text-blue-500" />
                <h3 className={`text-lg font-semibold ${themeClasses.text.primary}`}>Materials</h3>
              </div>
              <div className="space-y-3">
                {dashboardData.materials.length === 0 ? (
                  <p className={`text-sm ${themeClasses.text.secondary}`}>
                    No materials logged yet
                  </p>
                ) : (
                  dashboardData.materials.slice(0, 4).map((material, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <div>
                        <p className={`text-sm font-medium ${themeClasses.text.primary}`}>
                          {material.item}
                        </p>
                        <p className={`text-xs ${themeClasses.text.secondary}`}>
                          {material.vendor}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className={`text-sm ${themeClasses.text.primary}`}>
                          {material.quantity}
                        </p>
                        <p className={`text-xs ${themeClasses.text.secondary}`}>
                          {new Date(material.date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))
                )}
                {dashboardData.materials.length > 4 && (
                  <p className={`text-xs ${themeClasses.text.secondary} text-center pt-2`}>
                    +{dashboardData.materials.length - 4} more items
                  </p>
                )}
              </div>
            </AnimatedCardContent>
          </AnimatedCard>
        </div>

        {/* Inspections - using AnimatedCard */}
        {dashboardData.inspections.length > 0 && (
          <AnimatedCard 
            delay={700}
            className={`cursor-default hover:shadow-2xl transition-all duration-300 ease-out backdrop-blur-md border-0 shadow-xl ${
              isDarkMode 
                ? 'bg-white/10 text-white' 
                : 'bg-white/70 text-gray-900'
            }`}
          >
            <AnimatedCardContent className="p-6">
              <div className={`flex items-center gap-2 mb-4`}>
                <CheckCircle className="w-5 h-5 text-blue-500" />
                <h2 className={`text-lg font-semibold ${themeClasses.text.primary}`}>Inspections</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dashboardData.inspections.map((inspection, index) => (
                  <AnimatedCard 
                    key={inspection.id}
                    delay={750 + index * 50}
                    className={`cursor-default transition-all duration-300 ease-out backdrop-blur-sm border-0 shadow-md ${
                      isDarkMode ? 'bg-white/5 text-white hover:bg-white/10' : 'bg-gray-50/50 text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <AnimatedCardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className={`font-semibold ${themeClasses.text.primary}`}>
                          {inspection.inspectionType}
                        </h4>
                        {getStatusBadge(inspection.result)}
                      </div>
                      {inspection.scheduledDate && (
                        <p className={`text-sm ${themeClasses.text.secondary} flex items-center gap-1`}>
                          <Calendar className="w-3 h-3" />
                          {new Date(inspection.scheduledDate).toLocaleDateString()}
                        </p>
                      )}
                      {inspection.notes && (
                        <p className={`text-xs mt-2 ${themeClasses.text.secondary}`}>
                          {inspection.notes}
                        </p>
                      )}
                    </AnimatedCardContent>
                  </AnimatedCard>
                ))}
              </div>
            </AnimatedCardContent>
          </AnimatedCard>
        )}

        {/* Project Narrative - using AnimatedCard */}
        {dashboardData.narrative && (
          <AnimatedCard 
            delay={800}
            className={`cursor-default hover:shadow-2xl transition-all duration-300 ease-out backdrop-blur-md border-0 shadow-xl ${
              isDarkMode 
                ? 'bg-white/10 text-white' 
                : 'bg-white/70 text-gray-900'
            }`}
          >
            <AnimatedCardContent className="p-6">
              <div className={`flex items-center gap-2 mb-4`}>
                <FileText className="w-5 h-5 text-blue-500" />
                <h2 className={`text-lg font-semibold ${themeClasses.text.primary}`}>Project Summary</h2>
              </div>
              <AnimatedCard 
                delay={850}
                className={`cursor-default transition-all duration-300 ease-out backdrop-blur-sm border-0 shadow-sm ${
                  isDarkMode 
                    ? 'bg-blue-900/20 text-blue-200 border-blue-500/30' 
                    : 'bg-blue-50/50 text-blue-800 border-blue-200/50'
                }`}
              >
                <AnimatedCardContent className="p-4">
                  <p className={`${themeClasses.text.primary} leading-relaxed`}>
                    {dashboardData.narrative}
                  </p>
                </AnimatedCardContent>
              </AnimatedCard>
            </AnimatedCardContent>
          </AnimatedCard>
        )}

        {/* Footer */}
        <div className="text-center py-8">
          <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            This dashboard provides project progress information only.
          </p>
          <p className={`text-xs mt-1 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            For questions, contact your project manager • Powered by Rhino Fire Protection
          </p>
        </div>
      </div>
    </div>
  );
};

export default GcDashboard;