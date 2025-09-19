import React, { useState, useEffect } from 'react';
import { AnimatedCard, CardContent, CardHeader, CardTitle } from './ui/animated-card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { 
  Calendar, 
  Users, 
  FileText, 
  Package, 
  Activity,
  Clock,
  CheckCircle,
  AlertCircle,
  Wrench,
  FileCheck,
  Info,
  ExternalLink
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const EnhancedGcDashboard = ({ projectId }) => {
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, [projectId]);

  const fetchDashboardData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/gc/dashboard/${projectId}`);
      
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        throw new Error('Failed to fetch dashboard data');
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const getInspectionStatusInfo = (status) => {
    const statusMap = {
      'pending': { icon: Clock, label: 'Pending', color: 'text-yellow-500', bgColor: 'bg-yellow-500/10' },
      'rough_requested': { icon: AlertCircle, label: 'Rough Requested', color: 'text-blue-500', bgColor: 'bg-blue-500/10' },
      'rough_approved': { icon: CheckCircle, label: 'Rough Approved', color: 'text-green-500', bgColor: 'bg-green-500/10' },
      'rough_partial': { icon: Wrench, label: 'Rough Partial', color: 'text-orange-500', bgColor: 'bg-orange-500/10' },
      'final_requested': { icon: AlertCircle, label: 'Final Requested', color: 'text-blue-500', bgColor: 'bg-blue-500/10' },
      'final_approved': { icon: CheckCircle, label: 'Final Approved', color: 'text-green-500', bgColor: 'bg-green-500/10' },
      'final_partial': { icon: FileCheck, label: 'Final Partial', color: 'text-orange-500', bgColor: 'bg-orange-500/10' }
    };
    return statusMap[status] || statusMap.pending;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className={`text-center ${themeClasses.text.secondary}`}>
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          Loading project dashboard...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className={`text-center ${themeClasses.text.secondary}`}>
          <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
          Error loading dashboard: {error}
        </div>
      </div>
    );
  }

  const { projectName, crewSummary, tmTagSummary, inspections = {} } = dashboardData;
  const roughStatus = getInspectionStatusInfo(inspections.rough_inspection_status || 'pending');
  const finalStatus = getInspectionStatusInfo(inspections.final_inspection_status || 'pending');

  return (
    <div className="space-y-6">
      {/* Project Header */}
      <div className={`p-6 rounded-lg ${
        isDarkMode 
          ? 'bg-gradient-to-r from-blue-900/20 to-indigo-900/20 border border-white/10' 
          : 'bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200'
      }`}>
        <h1 className={`text-2xl font-bold ${themeClasses.text.primary} mb-2`}>
          {projectName}
        </h1>
        <p className={themeClasses.text.secondary}>
          Project progress and status overview for authorized contractors
        </p>
      </div>

      {/* Inspection Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <AnimatedCard className={`${themeClasses.card} border-l-4 border-l-orange-500`}>
          <CardHeader className="pb-3">
            <CardTitle className={`flex items-center gap-2 ${themeClasses.text.primary}`}>
              <Wrench className="w-5 h-5" />
              Rough Inspection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`flex items-center gap-3 p-3 rounded-lg ${roughStatus.bgColor}`}>
              <roughStatus.icon className={`w-6 h-6 ${roughStatus.color}`} />
              <div>
                <div className={`font-semibold ${themeClasses.text.primary}`}>
                  {roughStatus.label}
                </div>
                {inspections.rough_inspection_date && (
                  <div className={`text-sm ${themeClasses.text.secondary}`}>
                    {new Date(inspections.rough_inspection_date).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
            {inspections.rough_inspection_notes && (
              <div className={`mt-3 p-3 rounded-lg ${isDarkMode ? 'bg-white/5' : 'bg-gray-50'}`}>
                <div className={`text-sm ${themeClasses.text.secondary}`}>
                  {inspections.rough_inspection_notes}
                </div>
              </div>
            )}
          </CardContent>
        </AnimatedCard>

        <AnimatedCard className={`${themeClasses.card} border-l-4 border-l-green-500`}>
          <CardHeader className="pb-3">
            <CardTitle className={`flex items-center gap-2 ${themeClasses.text.primary}`}>
              <FileCheck className="w-5 h-5" />
              Final Inspection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`flex items-center gap-3 p-3 rounded-lg ${finalStatus.bgColor}`}>
              <finalStatus.icon className={`w-6 h-6 ${finalStatus.color}`} />
              <div>
                <div className={`font-semibold ${themeClasses.text.primary}`}>
                  {finalStatus.label}
                </div>
                {inspections.final_inspection_date && (
                  <div className={`text-sm ${themeClasses.text.secondary}`}>
                    {new Date(inspections.final_inspection_date).toLocaleDateString()}
                  </div>
                )}
              </div>
            </div>
            {inspections.final_inspection_notes && (
              <div className={`mt-3 p-3 rounded-lg ${isDarkMode ? 'bg-white/5' : 'bg-gray-50'}`}>
                <div className={`text-sm ${themeClasses.text.secondary}`}>
                  {inspections.final_inspection_notes}
                </div>
              </div>
            )}
          </CardContent>
        </AnimatedCard>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Crew Activity - Enhanced */}
        <AnimatedCard className={`${themeClasses.card} cursor-pointer hover:shadow-lg transition-shadow`}>
          <CardHeader className="pb-3">
            <CardTitle className={`flex items-center gap-2 ${themeClasses.text.primary}`}>
              <Users className="w-5 h-5" />
              Crew Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className={themeClasses.text.secondary}>Total Hours</span>
                <span className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                  {crewSummary?.totalHours || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className={themeClasses.text.secondary}>Work Days</span>
                <span className={`text-lg font-semibold ${themeClasses.text.primary}`}>
                  {crewSummary?.totalDays || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className={themeClasses.text.secondary}>Active Crew</span>
                <span className={`text-lg font-semibold ${themeClasses.text.primary}`}>
                  {crewSummary?.activeCrewMembers || 0} members
                </span>
              </div>
              
              {/* Recent Work Descriptions */}
              {crewSummary?.recentDescriptions && crewSummary.recentDescriptions.length > 0 && (
                <div className={`mt-4 p-3 rounded-lg ${isDarkMode ? 'bg-white/5' : 'bg-gray-50'}`}>
                  <div className={`text-sm font-medium ${themeClasses.text.primary} mb-2`}>
                    Recent Work:
                  </div>
                  <div className="space-y-1">
                    {crewSummary.recentDescriptions.slice(0, 3).map((desc, index) => (
                      <div key={index} className={`text-xs ${themeClasses.text.secondary}`}>
                        • {desc}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </AnimatedCard>

        {/* T&M Reports - Enhanced */}
        <AnimatedCard className={`${themeClasses.card} cursor-pointer hover:shadow-lg transition-shadow`}>
          <CardHeader className="pb-3">
            <CardTitle className={`flex items-center gap-2 ${themeClasses.text.primary}`}>
              <FileText className="w-5 h-5" />
              Daily Reports
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className={themeClasses.text.secondary}>Total Tags</span>
                <span className={`text-2xl font-bold ${themeClasses.text.primary}`}>
                  {tmTagSummary?.totalTags || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className={themeClasses.text.secondary}>Approved</span>
                <span className={`text-lg font-semibold text-green-600`}>
                  {tmTagSummary?.approvedTags || 0}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className={themeClasses.text.secondary}>Total Hours</span>
                <span className={`text-lg font-semibold ${themeClasses.text.primary}`}>
                  {tmTagSummary?.totalHours || 0} hrs
                </span>
              </div>

              {/* Recent Tag Titles */}
              {tmTagSummary?.recentTagTitles && tmTagSummary.recentTagTitles.length > 0 && (
                <div className={`mt-4 p-3 rounded-lg ${isDarkMode ? 'bg-white/5' : 'bg-gray-50'}`}>
                  <div className={`text-sm font-medium ${themeClasses.text.primary} mb-2`}>
                    Recent Reports:
                  </div>
                  <div className="space-y-1">
                    {tmTagSummary.recentTagTitles.slice(0, 3).map((title, index) => (
                      <div key={index} className={`text-xs ${themeClasses.text.secondary}`}>
                        • {title}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </AnimatedCard>

        {/* Materials Overview */}
        <AnimatedCard className={`${themeClasses.card}`}>
          <CardHeader className="pb-3">
            <CardTitle className={`flex items-center gap-2 ${themeClasses.text.primary}`}>
              <Package className="w-5 h-5" />
              Materials
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className={`text-center py-8 ${themeClasses.text.secondary}`}>
                <Package className="w-12 h-12 mx-auto mb-2 opacity-50" />
                No material data available
              </div>
            </div>
          </CardContent>
        </AnimatedCard>
      </div>

      {/* Footer */}
      <div className={`text-center py-6 border-t ${
        isDarkMode ? 'border-white/10' : 'border-gray-200'
      }`}>
        <p className={`text-sm ${themeClasses.text.secondary}`}>
          This dashboard provides project progress information only.
        </p>
        <p className={`text-xs ${themeClasses.text.secondary} mt-1`}>
          For questions, contact your project manager • Powered by Rhino Fire Protection
        </p>
      </div>
    </div>
  );
};

export default EnhancedGcDashboard;