import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  Building, 
  Users, 
  Clock, 
  FileText,
  Package,
  CheckCircle,
  AlertCircle,
  Calendar,
  MapPin,
  TrendingUp,
  Activity,
  Wrench
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const GcDashboard = ({ projectId, keyId }) => {
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <Card className={themeClasses.card.primary}>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                  {dashboardData.projectName}
                </h1>
                {dashboardData.projectLocation && (
                  <p className={`flex items-center gap-2 mt-2 ${themeClasses.text.secondary}`}>
                    <MapPin className="w-4 h-4" />
                    {dashboardData.projectLocation}
                  </p>
                )}
              </div>
              <div className="text-right">
                {getStatusBadge(dashboardData.projectStatus)}
                <p className={`text-sm mt-2 ${themeClasses.text.secondary}`}>
                  Last Updated: {new Date(dashboardData.lastUpdated).toLocaleDateString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Overall Progress */}
        <Card className={themeClasses.card.primary}>
          <CardHeader>
            <CardTitle className={`${themeClasses.text.primary} flex items-center gap-2`}>
              <TrendingUp className="w-5 h-5" />
              Overall Project Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                  {Math.round(dashboardData.overallProgress)}%
                </span>
                <span className={themeClasses.text.secondary}>Complete</span>
              </div>
              <Progress value={dashboardData.overallProgress} className="h-3" />
            </div>
          </CardContent>
        </Card>

        {/* Project Phases */}
        <Card className={themeClasses.card.primary}>
          <CardHeader>
            <CardTitle className={`${themeClasses.text.primary} flex items-center gap-2`}>
              <Activity className="w-5 h-5" />
              Project Phases
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {dashboardData.phases.map((phase) => {
                const PhaseIcon = getPhaseIcon(phase.phase);
                return (
                  <div key={phase.id} className={`p-4 rounded-lg border ${
                    isDarkMode ? 'border-white/20 bg-white/5' : 'border-gray-200 bg-gray-50'
                  }`}>
                    <div className="flex items-center gap-3 mb-3">
                      <PhaseIcon className="w-5 h-5 text-blue-600" />
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
                        <p className={`text-xs text-green-600`}>
                          Completed: {new Date(phase.actualDate).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Crew Summary */}
          <Card className={themeClasses.card.primary}>
            <CardHeader>
              <CardTitle className={`${themeClasses.text.primary} flex items-center gap-2`}>
                <Users className="w-5 h-5" />
                Crew Activity
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
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
              <div className="pt-2 border-t">
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
            </CardContent>
          </Card>

          {/* T&M Tags Summary */}
          <Card className={themeClasses.card.primary}>
            <CardHeader>
              <CardTitle className={`${themeClasses.text.primary} flex items-center gap-2`}>
                <FileText className="w-5 h-5" />
                Daily Reports
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                    {dashboardData.tmTagSummary.totalTags}
                  </p>
                  <p className={`text-sm ${themeClasses.text.secondary}`}>Total Tags</p>
                </div>
                <div className="text-center">
                  <p className={`text-2xl font-bold text-green-600`}>
                    {dashboardData.tmTagSummary.approvedTags}
                  </p>
                  <p className={`text-sm ${themeClasses.text.secondary}`}>Approved</p>
                </div>
              </div>
              <div className="pt-2 border-t">
                <p className={`text-sm ${themeClasses.text.secondary}`}>
                  Submitted: {dashboardData.tmTagSummary.submittedTags} tags
                </p>
                <p className={`text-sm ${themeClasses.text.secondary}`}>
                  Total Hours: {dashboardData.tmTagSummary.totalHours.toFixed(0)} hrs
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Materials Summary */}
          <Card className={themeClasses.card.primary}>
            <CardHeader>
              <CardTitle className={`${themeClasses.text.primary} flex items-center gap-2`}>
                <Package className="w-5 h-5" />
                Materials
              </CardTitle>
            </CardHeader>
            <CardContent>
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
            </CardContent>
          </Card>
        </div>

        {/* Inspections */}
        {dashboardData.inspections.length > 0 && (
          <Card className={themeClasses.card.primary}>
            <CardHeader>
              <CardTitle className={`${themeClasses.text.primary} flex items-center gap-2`}>
                <CheckCircle className="w-5 h-5" />
                Inspections
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {dashboardData.inspections.map((inspection) => (
                  <div key={inspection.id} className={`p-4 rounded-lg border ${
                    isDarkMode ? 'border-white/20 bg-white/5' : 'border-gray-200 bg-gray-50'
                  }`}>
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
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Project Narrative */}
        {dashboardData.narrative && (
          <Card className={themeClasses.card.primary}>
            <CardHeader>
              <CardTitle className={`${themeClasses.text.primary} flex items-center gap-2`}>
                <FileText className="w-5 h-5" />
                Project Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`p-4 rounded-lg ${
                isDarkMode 
                  ? 'bg-blue-900/20 border border-blue-500/30' 
                  : 'bg-blue-50 border border-blue-200'
              }`}>
                <p className={`${themeClasses.text.primary} leading-relaxed`}>
                  {dashboardData.narrative}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center py-8">
          <p className={`text-sm ${themeClasses.text.secondary}`}>
            This dashboard provides project progress information only.
          </p>
          <p className={`text-xs mt-1 ${themeClasses.text.secondary}`}>
            For questions, contact your project manager • Powered by Rhino Fire Protection
          </p>
        </div>
      </div>
    </div>
  );
};

export default GcDashboard;