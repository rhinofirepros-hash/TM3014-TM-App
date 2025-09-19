import React, { useState, useEffect } from 'react';
import { AnimatedCard, CardContent, CardHeader, CardTitle } from './ui/animated-card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Progress } from './ui/progress';
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
  ExternalLink,
  TrendingUp,
  MapPin,
  Hammer,
  Clipboard,
  PenTool
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
      <div className={`min-h-screen ${isDarkMode ? 'bg-slate-900' : 'bg-gray-50'} flex items-center justify-center p-4`}>
        <div className={`text-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-lg md:text-xl">Loading project dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen ${isDarkMode ? 'bg-slate-900' : 'bg-gray-50'} flex items-center justify-center p-4`}>
        <div className={`text-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-500" />
          <p className="text-lg md:text-xl">Error loading dashboard: {error}</p>
        </div>
      </div>
    );
  }

  const { projectName, crewSummary, tmTagSummary, inspections = {}, projectLocation = "", projectStatus = "active" } = dashboardData;
  const roughStatus = getInspectionStatusInfo(inspections.rough_inspection_status || 'pending');
  const finalStatus = getInspectionStatusInfo(inspections.final_inspection_status || 'pending');

  // Calculate project progress
  const overallProgress = Math.floor(Math.random() * 40) + 60; // Mock progress between 60-100%
  const designProgress = inspections.rough_inspection_status === 'rough_approved' ? 100 : 85;
  
  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-slate-900' : 'bg-gray-50'} p-3 md:p-6`}>
      {/* Mobile-First Project Header */}
      <div className={`p-4 md:p-6 rounded-xl mb-6 ${
        isDarkMode 
          ? 'bg-gradient-to-r from-blue-900/30 to-indigo-900/30 border border-blue-500/20' 
          : 'bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200'
      }`}>
        <div className="flex items-start justify-between flex-wrap gap-2">
          <div className="flex-1">
            <h1 className={`text-xl md:text-3xl font-bold mb-2 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              {projectName}
            </h1>
            {projectLocation && (
              <div className={`flex items-center gap-2 mb-2 ${isDarkMode ? 'text-blue-300' : 'text-blue-600'}`}>
                <MapPin className="w-4 h-4" />
                <span className="text-sm md:text-base">{projectLocation}</span>
              </div>
            )}
            <Badge variant={projectStatus === 'active' ? 'default' : 'secondary'} className="text-sm">
              {projectStatus.charAt(0).toUpperCase() + projectStatus.slice(1)}
            </Badge>
          </div>
          <div className="flex items-center gap-3">
            <div className={`text-right ${isDarkMode ? 'text-blue-300' : 'text-blue-600'}`}>
              <div className="text-2xl md:text-3xl font-bold">{overallProgress}%</div>
              <div className="text-xs md:text-sm">Complete</div>
            </div>
          </div>
        </div>
        
        {/* Project Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between items-center mb-2">
            <span className={`text-sm md:text-base font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
              Overall Progress
            </span>
            <span className={`text-sm ${isDarkMode ? 'text-blue-300' : 'text-blue-600'}`}>
              {overallProgress}%
            </span>
          </div>
          <Progress value={overallProgress} className="h-3" />
        </div>
      </div>

      {/* Design & Plan Status */}
      <div className={`p-4 md:p-6 rounded-xl mb-6 ${
        isDarkMode 
          ? 'bg-slate-800/50 border border-slate-700' 
          : 'bg-white border border-gray-200'
      }`}>
        <div className="flex items-center gap-3 mb-4">
          <PenTool className={`w-6 h-6 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
          <h2 className={`text-lg md:text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            Design & Planning
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-slate-700/50' : 'bg-blue-50'}`}>
            <div className="flex justify-between items-center mb-2">
              <span className={`font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                Design Progress
              </span>
              <span className={`text-lg font-bold ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`}>
                {designProgress}%
              </span>
            </div>
            <Progress value={designProgress} className="h-2 mb-2" />
            <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              Plans submitted and under review
            </p>
          </div>
          
          <div className={`p-4 rounded-lg ${isDarkMode ? 'bg-slate-700/50' : 'bg-green-50'}`}>
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className={`font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                Permits Status
              </span>
            </div>
            <p className={`text-lg font-semibold ${isDarkMode ? 'text-green-400' : 'text-green-600'}`}>
              Approved
            </p>
            <p className={`text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              Ready for installation
            </p>
          </div>
        </div>
      </div>

      {/* CREW INFORMATION - LARGE AND PROMINENT */}
      <div className={`p-4 md:p-6 rounded-xl mb-6 ${
        isDarkMode 
          ? 'bg-gradient-to-r from-blue-900/20 to-indigo-900/20 border border-blue-500/30' 
          : 'bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200'
      }`}>
        <div className="flex items-center gap-3 mb-6">
          <Users className={`w-8 h-8 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
          <h2 className={`text-xl md:text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            Current Crew Activity
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="text-center">
            <div className={`text-3xl md:text-4xl font-bold ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`}>
              {crewSummary?.totalHours || 0}
            </div>
            <div className={`text-sm md:text-base font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
              Total Hours Logged
            </div>
          </div>
          <div className="text-center">
            <div className={`text-3xl md:text-4xl font-bold ${isDarkMode ? 'text-green-400' : 'text-green-600'}`}>
              {crewSummary?.activeCrewMembers || 0}
            </div>
            <div className={`text-sm md:text-base font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
              Active Crew Members
            </div>
          </div>
          <div className="text-center">
            <div className={`text-3xl md:text-4xl font-bold ${isDarkMode ? 'text-purple-400' : 'text-purple-600'}`}>
              {crewSummary?.totalDays || 0}
            </div>
            <div className={`text-sm md:text-base font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
              Work Days
            </div>
          </div>
        </div>

        {/* Recent Work - Large Text for GC to Read */}
        {crewSummary?.recentDescriptions && crewSummary.recentDescriptions.length > 0 && (
          <div className={`p-4 md:p-6 rounded-lg ${isDarkMode ? 'bg-slate-800/50' : 'bg-white/70'}`}>
            <h3 className={`text-lg md:text-xl font-bold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              Recent Work Activities
            </h3>
            <div className="space-y-3">
              {crewSummary.recentDescriptions.slice(0, 5).map((desc, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className={`w-2 h-2 rounded-full mt-3 ${isDarkMode ? 'bg-blue-400' : 'bg-blue-600'}`} />
                  <p className={`text-base md:text-lg leading-relaxed ${isDarkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                    {desc}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Inspection Status Cards - Mobile Optimized */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className={`p-4 md:p-6 rounded-xl border-l-4 border-l-orange-500 ${
          isDarkMode ? 'bg-slate-800/50 border-t border-r border-b border-slate-700' : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            <Wrench className={`w-6 h-6 ${isDarkMode ? 'text-orange-400' : 'text-orange-600'}`} />
            <h3 className={`text-lg md:text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              Rough Inspection
            </h3>
          </div>
          
          <div className={`flex items-center gap-4 p-4 rounded-lg ${
            isDarkMode ? 'bg-slate-700/50' : roughStatus.bgColor
          }`}>
            <roughStatus.icon className={`w-8 h-8 ${roughStatus.color}`} />
            <div className="flex-1">
              <div className={`text-lg font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                {roughStatus.label}
              </div>
              {inspections.rough_inspection_date && (
                <div className={`text-sm md:text-base ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  {new Date(inspections.rough_inspection_date).toLocaleDateString()}
                </div>
              )}
            </div>
          </div>
          
          {inspections.rough_inspection_notes && (
            <div className={`mt-4 p-4 rounded-lg ${isDarkMode ? 'bg-slate-700/30' : 'bg-gray-50'}`}>
              <p className={`text-sm md:text-base ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                {inspections.rough_inspection_notes}
              </p>
            </div>
          )}
        </div>

        <div className={`p-4 md:p-6 rounded-xl border-l-4 border-l-green-500 ${
          isDarkMode ? 'bg-slate-800/50 border-t border-r border-b border-slate-700' : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            <FileCheck className={`w-6 h-6 ${isDarkMode ? 'text-green-400' : 'text-green-600'}`} />
            <h3 className={`text-lg md:text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              Final Inspection
            </h3>
          </div>
          
          <div className={`flex items-center gap-4 p-4 rounded-lg ${
            isDarkMode ? 'bg-slate-700/50' : finalStatus.bgColor
          }`}>
            <finalStatus.icon className={`w-8 h-8 ${finalStatus.color}`} />
            <div className="flex-1">
              <div className={`text-lg font-semibold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                {finalStatus.label}
              </div>
              {inspections.final_inspection_date && (
                <div className={`text-sm md:text-base ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  {new Date(inspections.final_inspection_date).toLocaleDateString()}
                </div>
              )}
            </div>
          </div>
          
          {inspections.final_inspection_notes && (
            <div className={`mt-4 p-4 rounded-lg ${isDarkMode ? 'bg-slate-700/30' : 'bg-gray-50'}`}>
              <p className={`text-sm md:text-base ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                {inspections.final_inspection_notes}
              </p>
            </div>
          )}
        </div>
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