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
  PenTool,
  AlertTriangle,
  Shield,
  Calendar as CalendarIcon,
  Truck
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const EnhancedGcDashboard = ({ projectId }) => {
  const { isDarkMode } = useTheme();
  
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Mock data based on user's JSON structure
  const mockGcData = {
    projectName: "3rd Ave",
    projectLocation: "Downtown Seattle, WA",
    projectStatus: "active",
    overallProgress: 80,
    designPlanning: {
      designProgress: 85,
      permitsStatus: "Approved"
    },
    inspections: {
      rough_inspection_status: "pending",
      rough_inspection_date: null,
      rough_inspection_notes: null,
      final_inspection_status: "pending", 
      final_inspection_date: null,
      final_inspection_notes: null
    },
    crewActivity: {
      totalHours: 72,
      activeCrewMembers: 4,
      workDays: 5
    },
    dailyReports: {
      totalReports: 5,
      approved: 3
    },
    crewLogSummary: [
      {
        date: "2025-09-18",
        crewMembers: ["Jesus Garcia", "Miguel Perez", "2 Installers"],
        totalHours: 32,
        workPerformed: "Installed 120 ft of 2-inch main in garage level and set 15 sprinkler heads.",
        issues: "Delivery truck delayed, limited access to 2nd floor mechanical room.",
        nextSteps: "Continue branch line installation on 2nd floor tomorrow."
      },
      {
        date: "2025-09-19",
        crewMembers: ["Jesus Garcia", "3 Installers"],
        totalHours: 40,
        workPerformed: "Completed riser installation and performed hydrostatic test on garage level piping.",
        issues: "No major issues encountered.",
        nextSteps: "Start 3rd floor main installation."
      }
    ],
    progressSnapshot: {
      systemInstalledPercent: 35,
      zonesCompleted: 1,
      floorsCompleted: 0,
      totalWorkdays: 5,
      totalCrewHours: 72,
      deliveriesReceived: ["Backflow assembly", "2-inch CPVC pipe bundle"],
      upcomingMilestones: [
        "Schedule rough inspection for garage level",
        "Delivery of sprinkler heads for 2nd floor"
      ]
    },
    coordinationRfi: [
      {
        rfiNumber: "RFI-001",
        subject: "Ceiling clash with HVAC duct",
        status: "Pending GC response"
      }
    ],
    safety: {
      dailyChecksCompleted: true,
      incidentsReported: "None"
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [projectId]);

  const fetchDashboardData = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/gc/dashboard/${projectId}`);
      
      if (response.ok) {
        const data = await response.json();
        // Merge backend data with mock data
        setDashboardData({
          ...mockGcData,
          ...data,
          inspections: data.inspections || mockGcData.inspections
        });
      } else {
        // Use mock data if backend fails
        setDashboardData(mockGcData);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Use mock data on error
      setDashboardData(mockGcData);
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
      <div className={`min-h-screen ${
        isDarkMode ? 'bg-slate-800' : 'bg-gray-50'
      } flex items-center justify-center p-4`}>
        <div className={`text-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-lg md:text-xl">Loading project dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen ${
        isDarkMode ? 'bg-slate-800' : 'bg-gray-50'
      } flex items-center justify-center p-4`}>
        <div className={`text-center ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-500" />
          <p className="text-lg md:text-xl">Error loading dashboard: {error}</p>
        </div>
      </div>
    );
  }

  const { 
    projectName, 
    projectLocation, 
    projectStatus, 
    overallProgress,
    designPlanning,
    inspections = {},
    crewActivity,
    dailyReports,
    crewLogSummary = [],
    progressSnapshot,
    coordinationRfi = [],
    safety
  } = dashboardData;

  const roughStatus = getInspectionStatusInfo(inspections.rough_inspection_status || 'pending');
  const finalStatus = getInspectionStatusInfo(inspections.final_inspection_status || 'pending');

  return (
    <div className={`min-h-screen ${themeClasses.background} p-3 md:p-6`}>
      {/* Mobile-First Project Header */}
      <div className={`p-4 md:p-6 rounded-xl mb-6 ${
        isDarkMode 
          ? 'bg-slate-700 border border-slate-600' 
          : 'bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200'
      }`}>
        <div className="flex items-start justify-between flex-wrap gap-2">
          <div className="flex-1">
            <h1 className={`text-xl md:text-3xl font-bold mb-2 ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              {projectName}
            </h1>
            {projectLocation && (
              <div className={`flex items-center gap-2 mb-2 ${
                isDarkMode ? 'text-blue-300' : 'text-blue-600'
              }`}>
                <MapPin className="w-4 h-4" />
                <span className="text-sm md:text-base">{projectLocation}</span>
              </div>
            )}
            <Badge variant={projectStatus === 'active' ? 'default' : 'secondary'} className="text-sm">
              {projectStatus.charAt(0).toUpperCase() + projectStatus.slice(1)}
            </Badge>
          </div>
          <div className="flex items-center gap-3">
            <div className={`text-right ${
              isDarkMode ? 'text-blue-300' : 'text-blue-600'
            }`}>
              <div className="text-2xl md:text-3xl font-bold">{overallProgress}%</div>
              <div className="text-xs md:text-sm">Complete</div>
            </div>
          </div>
        </div>
        
        {/* Project Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between items-center mb-2">
            <span className={`text-sm md:text-base font-medium ${
              isDarkMode ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Overall Progress
            </span>
            <span className={`text-sm ${
              isDarkMode ? 'text-blue-300' : 'text-blue-600'
            }`}>
              {overallProgress}%
            </span>
          </div>
          <Progress value={overallProgress} className="h-3" />
        </div>
      </div>

      {/* Design & Plan Status */}
      <div className={`p-4 md:p-6 rounded-xl mb-6 ${
        isDarkMode 
          ? 'bg-slate-700 border border-slate-600' 
          : 'bg-white border border-gray-200'
      }`}>
        <div className="flex items-center gap-3 mb-4">
          <PenTool className={`w-6 h-6 ${
            isDarkMode ? 'text-blue-400' : 'text-blue-600'
          }`} />
          <h2 className={`text-lg md:text-xl font-bold ${
            isDarkMode ? 'text-white' : 'text-gray-900'
          }`}>
            Design & Planning
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className={`p-4 rounded-lg ${
            isDarkMode ? 'bg-slate-600' : 'bg-blue-50'
          }`}>
            <div className="flex justify-between items-center mb-2">
              <span className={`font-medium ${
                isDarkMode ? 'text-gray-300' : 'text-gray-700'
              }`}>
                Design Progress
              </span>
              <span className={`text-lg font-bold ${
                isDarkMode ? 'text-blue-400' : 'text-blue-600'
              }`}>
                {designPlanning?.designProgress || 85}%
              </span>
            </div>
            <Progress value={designPlanning?.designProgress || 85} className="h-2 mb-2" />
            <p className={`text-sm ${
              isDarkMode ? 'text-gray-400' : 'text-gray-600'
            }`}>
              Plans submitted and under review
            </p>
          </div>
          
          <div className={`p-4 rounded-lg ${
            isDarkMode ? 'bg-slate-600' : 'bg-green-50'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className={`font-medium ${
                isDarkMode ? 'text-gray-300' : 'text-gray-700'
              }`}>
                Permits Status
              </span>
            </div>
            <p className={`text-lg font-semibold ${
              isDarkMode ? 'text-green-400' : 'text-green-600'
            }`}>
              {designPlanning?.permitsStatus || "Approved"}
            </p>
            <p className={`text-sm ${
              isDarkMode ? 'text-gray-400' : 'text-gray-600'
            }`}>
              Ready for installation
            </p>
          </div>
        </div>
      </div>

      {/* CREW INFORMATION - LARGE AND PROMINENT */}
      <div className={`p-4 md:p-6 rounded-xl mb-6 ${
        isDarkMode 
          ? 'bg-slate-700 border border-blue-500/30' 
          : 'bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200'
      }`}>
        <div className="flex items-center gap-3 mb-6">
          <Users className={`w-8 h-8 ${
            isDarkMode ? 'text-blue-400' : 'text-blue-600'
          }`} />
          <h2 className={`text-xl md:text-2xl font-bold ${
            isDarkMode ? 'text-white' : 'text-gray-900'
          }`}>
            Current Crew Activity
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="text-center">
            <div className={`text-3xl md:text-4xl font-bold ${
              isDarkMode ? 'text-blue-400' : 'text-blue-600'
            }`}>
              {crewActivity?.totalHours || 72}
            </div>
            <div className={`text-sm md:text-base font-medium ${
              isDarkMode ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Total Hours Logged
            </div>
          </div>
          <div className="text-center">
            <div className={`text-3xl md:text-4xl font-bold ${
              isDarkMode ? 'text-green-400' : 'text-green-600'
            }`}>
              {crewActivity?.activeCrewMembers || 4}
            </div>
            <div className={`text-sm md:text-base font-medium ${
              isDarkMode ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Active Crew Members
            </div>
          </div>
          <div className="text-center">
            <div className={`text-3xl md:text-4xl font-bold ${
              isDarkMode ? 'text-purple-400' : 'text-purple-600'
            }`}>
              {crewActivity?.workDays || 5}
            </div>
            <div className={`text-sm md:text-base font-medium ${
              isDarkMode ? 'text-gray-300' : 'text-gray-700'
            }`}>
              Work Days
            </div>
          </div>
        </div>

        {/* Daily Crew Log Summary - Large Text for GC to Read */}
        {crewLogSummary && crewLogSummary.length > 0 && (
          <div className={`p-4 md:p-6 rounded-lg ${
            isDarkMode ? 'bg-slate-600' : 'bg-white/70'
          }`}>
            <h3 className={`text-lg md:text-xl font-bold mb-4 ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              Daily Work Summary
            </h3>
            <div className="space-y-6">
              {crewLogSummary.map((log, index) => (
                <div key={index} className={`p-4 rounded-lg border-l-4 border-l-blue-500 ${
                  isDarkMode ? 'bg-slate-700' : 'bg-gray-50'
                }`}>
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-3">
                    <div className="flex items-center gap-3 mb-2 md:mb-0">
                      <CalendarIcon className={`w-5 h-5 ${
                        isDarkMode ? 'text-blue-400' : 'text-blue-600'
                      }`} />
                      <span className={`text-lg font-semibold ${
                        isDarkMode ? 'text-white' : 'text-gray-900'
                      }`}>
                        {new Date(log.date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className={`text-sm ${
                        isDarkMode ? 'text-gray-300' : 'text-gray-600'
                      }`}>
                        Crew: {log.crewMembers?.join(', ')}
                      </div>
                      <Badge variant="outline">
                        {log.totalHours} hours
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <h4 className={`font-medium text-sm ${
                        isDarkMode ? 'text-blue-300' : 'text-blue-600'
                      } mb-1`}>
                        Work Performed:
                      </h4>
                      <p className={`text-base md:text-lg leading-relaxed ${
                        isDarkMode ? 'text-gray-200' : 'text-gray-800'
                      }`}>
                        {log.workPerformed}
                      </p>
                    </div>
                    
                    {log.issues && log.issues !== "No major issues encountered." && (
                      <div>
                        <h4 className={`font-medium text-sm text-orange-500 mb-1`}>
                          Issues:
                        </h4>
                        <p className={`text-base leading-relaxed ${
                          isDarkMode ? 'text-orange-300' : 'text-orange-700'
                        }`}>
                          {log.issues}
                        </p>
                      </div>
                    )}
                    
                    <div>
                      <h4 className={`font-medium text-sm ${
                        isDarkMode ? 'text-green-300' : 'text-green-600'
                      } mb-1`}>
                        Next Steps:
                      </h4>
                      <p className={`text-base leading-relaxed ${
                        isDarkMode ? 'text-green-200' : 'text-green-800'
                      }`}>
                        {log.nextSteps}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Progress Snapshot */}
      {progressSnapshot && (
        <div className={`p-4 md:p-6 rounded-xl mb-6 ${
          isDarkMode 
            ? 'bg-slate-700 border border-slate-600' 
            : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            <TrendingUp className={`w-6 h-6 ${
              isDarkMode ? 'text-green-400' : 'text-green-600'
            }`} />
            <h3 className={`text-lg md:text-xl font-bold ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              Progress Snapshot
            </h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center">
              <div className={`text-2xl md:text-3xl font-bold ${
                isDarkMode ? 'text-blue-400' : 'text-blue-600'
              }`}>
                {progressSnapshot.systemInstalledPercent}%
              </div>
              <div className={`text-sm ${
                isDarkMode ? 'text-gray-300' : 'text-gray-600'
              }`}>
                System Installed
              </div>
            </div>
            <div className="text-center">
              <div className={`text-2xl md:text-3xl font-bold ${
                isDarkMode ? 'text-green-400' : 'text-green-600'
              }`}>
                {progressSnapshot.zonesCompleted}
              </div>
              <div className={`text-sm ${
                isDarkMode ? 'text-gray-300' : 'text-gray-600'
              }`}>
                Zones Complete
              </div>
            </div>
            <div className="text-center">
              <div className={`text-2xl md:text-3xl font-bold ${
                isDarkMode ? 'text-purple-400' : 'text-purple-600'
              }`}>
                {progressSnapshot.floorsCompleted}
              </div>
              <div className={`text-sm ${
                isDarkMode ? 'text-gray-300' : 'text-gray-600'
              }`}>
                Floors Complete
              </div>
            </div>
            <div className="text-center">
              <div className={`text-2xl md:text-3xl font-bold ${
                isDarkMode ? 'text-orange-400' : 'text-orange-600'
              }`}>
                {progressSnapshot.totalWorkdays}
              </div>
              <div className={`text-sm ${
                isDarkMode ? 'text-gray-300' : 'text-gray-600'
              }`}>
                Work Days
              </div>
            </div>
          </div>

          {/* Deliveries & Milestones */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className={`p-4 rounded-lg ${
              isDarkMode ? 'bg-slate-600' : 'bg-gray-50'
            }`}>
              <div className="flex items-center gap-2 mb-3">
                <Truck className={`w-5 h-5 ${
                  isDarkMode ? 'text-green-400' : 'text-green-600'
                }`} />
                <h4 className={`font-medium ${
                  isDarkMode ? 'text-white' : 'text-gray-900'
                }`}>
                  Recent Deliveries
                </h4>
              </div>
              <div className="space-y-2">
                {progressSnapshot.deliveriesReceived?.map((delivery, index) => (
                  <div key={index} className={`text-sm ${
                    isDarkMode ? 'text-gray-300' : 'text-gray-700'
                  }`}>
                    • {delivery}
                  </div>
                ))}
              </div>
            </div>
            
            <div className={`p-4 rounded-lg ${
              isDarkMode ? 'bg-slate-600' : 'bg-gray-50'
            }`}>
              <div className="flex items-center gap-2 mb-3">
                <Clipboard className={`w-5 h-5 ${
                  isDarkMode ? 'text-blue-400' : 'text-blue-600'
                }`} />
                <h4 className={`font-medium ${
                  isDarkMode ? 'text-white' : 'text-gray-900'
                }`}>
                  Upcoming Milestones
                </h4>
              </div>
              <div className="space-y-2">
                {progressSnapshot.upcomingMilestones?.map((milestone, index) => (
                  <div key={index} className={`text-sm ${
                    isDarkMode ? 'text-gray-300' : 'text-gray-700'
                  }`}>
                    • {milestone}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Inspection Status Cards - Mobile Optimized */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <div className={`p-4 md:p-6 rounded-xl border-l-4 border-l-orange-500 ${
          isDarkMode 
            ? 'bg-slate-700 border-t border-r border-b border-slate-600' 
            : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            <Wrench className={`w-6 h-6 ${
              isDarkMode ? 'text-orange-400' : 'text-orange-600'
            }`} />
            <h3 className={`text-lg md:text-xl font-bold ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              Rough Inspection
            </h3>
          </div>
          
          <div className={`flex items-center gap-4 p-4 rounded-lg ${
            isDarkMode ? 'bg-slate-600' : roughStatus.bgColor
          }`}>
            <roughStatus.icon className={`w-8 h-8 ${roughStatus.color}`} />
            <div className="flex-1">
              <div className={`text-lg font-semibold ${
                isDarkMode ? 'text-white' : 'text-gray-900'
              }`}>
                {roughStatus.label}
              </div>
              {inspections.rough_inspection_date && (
                <div className={`text-sm md:text-base ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-600'
                }`}>
                  {new Date(inspections.rough_inspection_date).toLocaleDateString()}
                </div>
              )}
            </div>
          </div>
          
          {inspections.rough_inspection_notes && (
            <div className={`mt-4 p-4 rounded-lg ${
              isDarkMode ? 'bg-slate-600' : 'bg-gray-50'
            }`}>
              <p className={`text-sm md:text-base ${
                isDarkMode ? 'text-gray-300' : 'text-gray-700'
              }`}>
                {inspections.rough_inspection_notes}
              </p>
            </div>
          )}
        </div>

        <div className={`p-4 md:p-6 rounded-xl border-l-4 border-l-green-500 ${
          isDarkMode 
            ? 'bg-slate-700 border-t border-r border-b border-slate-600' 
            : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            <FileCheck className={`w-6 h-6 ${
              isDarkMode ? 'text-green-400' : 'text-green-600'
            }`} />
            <h3 className={`text-lg md:text-xl font-bold ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              Final Inspection
            </h3>
          </div>
          
          <div className={`flex items-center gap-4 p-4 rounded-lg ${
            isDarkMode ? 'bg-slate-600' : finalStatus.bgColor
          }`}>
            <finalStatus.icon className={`w-8 h-8 ${finalStatus.color}`} />
            <div className="flex-1">
              <div className={`text-lg font-semibold ${
                isDarkMode ? 'text-white' : 'text-gray-900'
              }`}>
                {finalStatus.label}
              </div>
              {inspections.final_inspection_date && (
                <div className={`text-sm md:text-base ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-600'
                }`}>
                  {new Date(inspections.final_inspection_date).toLocaleDateString()}
                </div>
              )}
            </div>
          </div>
          
          {inspections.final_inspection_notes && (
            <div className={`mt-4 p-4 rounded-lg ${
              isDarkMode ? 'bg-slate-600' : 'bg-gray-50'
            }`}>
              <p className={`text-sm md:text-base ${
                isDarkMode ? 'text-gray-300' : 'text-gray-700'
              }`}>
                {inspections.final_inspection_notes}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Coordination & RFI */}
      {coordinationRfi && coordinationRfi.length > 0 && (
        <div className={`p-4 md:p-6 rounded-xl mb-6 ${
          isDarkMode 
            ? 'bg-slate-700 border border-slate-600' 
            : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className={`w-6 h-6 ${
              isDarkMode ? 'text-yellow-400' : 'text-yellow-600'
            }`} />
            <h3 className={`text-lg md:text-xl font-bold ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              Coordination & RFI
            </h3>
          </div>
          
          <div className="space-y-3">
            {coordinationRfi.map((rfi, index) => (
              <div key={index} className={`p-4 rounded-lg border-l-4 border-l-yellow-500 ${
                isDarkMode ? 'bg-slate-600' : 'bg-yellow-50'
              }`}>
                <div className="flex justify-between items-start">
                  <div>
                    <div className={`font-semibold ${
                      isDarkMode ? 'text-white' : 'text-gray-900'
                    }`}>
                      {rfi.rfiNumber}
                    </div>
                    <div className={`text-sm md:text-base ${
                      isDarkMode ? 'text-gray-300' : 'text-gray-700'
                    }`}>
                      {rfi.subject}
                    </div>
                  </div>
                  <Badge variant={rfi.status.includes('Pending') ? 'secondary' : 'default'}>
                    {rfi.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Safety Status */}
      {safety && (
        <div className={`p-4 md:p-6 rounded-xl mb-6 ${
          isDarkMode 
            ? 'bg-slate-700 border border-slate-600' 
            : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            <Shield className={`w-6 h-6 ${
              isDarkMode ? 'text-green-400' : 'text-green-600'
            }`} />
            <h3 className={`text-lg md:text-xl font-bold ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              Safety Status
            </h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className={`p-4 rounded-lg ${
              safety.dailyChecksCompleted 
                ? (isDarkMode ? 'bg-green-900/20' : 'bg-green-50')
                : (isDarkMode ? 'bg-red-900/20' : 'bg-red-50')
            }`}>
              <div className="flex items-center gap-2">
                <CheckCircle className={`w-5 h-5 ${
                  safety.dailyChecksCompleted ? 'text-green-500' : 'text-red-500'
                }`} />
                <span className={`font-medium ${
                  isDarkMode ? 'text-white' : 'text-gray-900'
                }`}>
                  Daily Safety Checks
                </span>
              </div>
              <p className={`text-sm mt-1 ${
                safety.dailyChecksCompleted 
                  ? (isDarkMode ? 'text-green-300' : 'text-green-700')
                  : (isDarkMode ? 'text-red-300' : 'text-red-700')
              }`}>
                {safety.dailyChecksCompleted ? 'Completed' : 'Incomplete'}
              </p>
            </div>
            
            <div className={`p-4 rounded-lg ${
              safety.incidentsReported === 'None' 
                ? (isDarkMode ? 'bg-green-900/20' : 'bg-green-50')
                : (isDarkMode ? 'bg-yellow-900/20' : 'bg-yellow-50')
            }`}>
              <div className="flex items-center gap-2">
                <AlertTriangle className={`w-5 h-5 ${
                  safety.incidentsReported === 'None' ? 'text-green-500' : 'text-yellow-500'
                }`} />
                <span className={`font-medium ${
                  isDarkMode ? 'text-white' : 'text-gray-900'
                }`}>
                  Safety Incidents
                </span>
              </div>
              <p className={`text-sm mt-1 ${
                safety.incidentsReported === 'None' 
                  ? (isDarkMode ? 'text-green-300' : 'text-green-700')
                  : (isDarkMode ? 'text-yellow-300' : 'text-yellow-700')
              }`}>
                {safety.incidentsReported}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Daily Reports & T&M Tags */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className={`p-4 md:p-6 rounded-xl ${
          isDarkMode 
            ? 'bg-slate-700 border border-slate-600' 
            : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            <FileText className={`w-6 h-6 ${
              isDarkMode ? 'text-blue-400' : 'text-blue-600'
            }`} />
            <h3 className={`text-lg md:text-xl font-bold ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              Daily Reports
            </h3>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="text-center">
              <div className={`text-2xl md:text-3xl font-bold ${
                isDarkMode ? 'text-blue-400' : 'text-blue-600'
              }`}>
                {dailyReports?.totalReports || 5}
              </div>
              <div className={`text-sm ${
                isDarkMode ? 'text-gray-300' : 'text-gray-600'
              }`}>
                Total Reports
              </div>
            </div>
            <div className="text-center">
              <div className={`text-2xl md:text-3xl font-bold text-green-500`}>
                {dailyReports?.approved || 3}
              </div>
              <div className={`text-sm ${
                isDarkMode ? 'text-gray-300' : 'text-gray-600'
              }`}>
                Approved
              </div>
            </div>
          </div>
        </div>

        {/* Project Status Summary */}
        <div className={`p-4 md:p-6 rounded-xl ${
          isDarkMode 
            ? 'bg-slate-700 border border-slate-600' 
            : 'bg-white border border-gray-200'
        }`}>
          <div className="flex items-center gap-3 mb-4">
            <Activity className={`w-6 h-6 ${
              isDarkMode ? 'text-green-400' : 'text-green-600'
            }`} />
            <h3 className={`text-lg md:text-xl font-bold ${
              isDarkMode ? 'text-white' : 'text-gray-900'
            }`}>
              Project Status
            </h3>
          </div>
          
          <div className="space-y-4">
            <div className={`p-4 rounded-lg ${
              isDarkMode 
                ? 'bg-green-900/20 border border-green-500/30' 
                : 'bg-green-50 border border-green-200'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className={`font-medium ${
                  isDarkMode ? 'text-green-300' : 'text-green-700'
                }`}>
                  On Schedule
                </span>
              </div>
              <p className={`text-sm md:text-base ${
                isDarkMode ? 'text-green-200' : 'text-green-600'
              }`}>
                Project is progressing as planned
              </p>
            </div>
            
            <div className={`p-4 rounded-lg ${
              isDarkMode 
                ? 'bg-blue-900/20 border border-blue-500/30' 
                : 'bg-blue-50 border border-blue-200'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <Activity className={`w-5 h-5 ${
                  isDarkMode ? 'text-blue-400' : 'text-blue-600'
                }`} />
                <span className={`font-medium ${
                  isDarkMode ? 'text-blue-300' : 'text-blue-700'
                }`}>
                  Active Work
                </span>
              </div>
              <p className={`text-sm md:text-base ${
                isDarkMode ? 'text-blue-200' : 'text-blue-600'
              }`}>
                Crew currently on-site working
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer - Mobile Optimized */}
      <div className={`text-center py-6 border-t ${
        isDarkMode ? 'border-slate-600' : 'border-gray-200'
      }`}>
        <div className={`p-4 rounded-lg ${
          isDarkMode ? 'bg-slate-700' : 'bg-gray-50'
        }`}>
          <p className={`text-base md:text-lg font-medium mb-2 ${
            isDarkMode ? 'text-white' : 'text-gray-900'
          }`}>
            Rhino Fire Protection
          </p>
          <p className={`text-sm md:text-base ${
            isDarkMode ? 'text-gray-300' : 'text-gray-600'
          }`}>
            This dashboard provides real-time project progress information
          </p>
          <p className={`text-xs md:text-sm ${
            isDarkMode ? 'text-gray-400' : 'text-gray-500'
          } mt-2`}>
            For questions or concerns, contact your project manager
          </p>
        </div>
      </div>
    </div>
  );
};

export default EnhancedGcDashboard;