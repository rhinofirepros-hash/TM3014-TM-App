import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Calendar } from './ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { format } from 'date-fns';
import { CalendarIcon, CheckCircle, Clock, AlertCircle, Wrench, FileCheck } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';

const InspectionManagement = ({ project, onProjectUpdate }) => {
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();
  
  const [inspectionData, setInspectionData] = useState({
    rough_inspection_status: project.rough_inspection_status || 'pending',
    rough_inspection_date: project.rough_inspection_date ? new Date(project.rough_inspection_date) : null,
    rough_inspection_notes: project.rough_inspection_notes || '',
    final_inspection_status: project.final_inspection_status || 'pending',
    final_inspection_date: project.final_inspection_date ? new Date(project.final_inspection_date) : null,
    final_inspection_notes: project.final_inspection_notes || ''
  });

  const inspectionStatuses = [
    { value: 'pending', label: 'Pending', icon: Clock, color: 'text-yellow-500' },
    { value: 'rough_requested', label: 'Rough Requested', icon: AlertCircle, color: 'text-blue-500' },
    { value: 'rough_approved', label: 'Rough Approved', icon: CheckCircle, color: 'text-green-500' },
    { value: 'rough_partial', label: 'Rough Partial Approval', icon: Wrench, color: 'text-orange-500' },
    { value: 'final_requested', label: 'Final Requested', icon: AlertCircle, color: 'text-blue-500' },
    { value: 'final_approved', label: 'Final Approved', icon: CheckCircle, color: 'text-green-500' },
    { value: 'final_partial', label: 'Final Partial Approval', icon: FileCheck, color: 'text-orange-500' }
  ];

  const getStatusInfo = (status) => {
    return inspectionStatuses.find(s => s.value === status) || inspectionStatuses[0];
  };

  const handleUpdateInspection = async (type) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      const updateData = {
        [`${type}_inspection_status`]: inspectionData[`${type}_inspection_status`],
        [`${type}_inspection_date`]: inspectionData[`${type}_inspection_date`]?.toISOString(),
        [`${type}_inspection_notes`]: inspectionData[`${type}_inspection_notes`]
      };

      const response = await fetch(`${backendUrl}/api/projects/${project.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
      });

      if (response.ok) {
        const updatedProject = await response.json();
        onProjectUpdate(updatedProject);
        toast({
          title: "Inspection Updated",
          description: `${type.charAt(0).toUpperCase() + type.slice(1)} inspection status updated successfully`,
        });
      } else {
        throw new Error('Failed to update inspection');
      }
    } catch (error) {
      console.error('Error updating inspection:', error);
      toast({
        title: "Update Failed",
        description: "Failed to update inspection status",
        variant: "destructive"
      });
    }
  };

  const InspectionCard = ({ type, title, icon: Icon }) => {
    const statusInfo = getStatusInfo(inspectionData[`${type}_inspection_status`]);
    const StatusIcon = statusInfo.icon;
    
    return (
      <Card className={`${themeClasses.card} border-l-4 ${
        statusInfo.value === 'pending' ? 'border-l-yellow-500' :
        statusInfo.value.includes('approved') ? 'border-l-green-500' :
        statusInfo.value.includes('partial') ? 'border-l-orange-500' :
        'border-l-blue-500'
      }`}>
        <CardHeader className="pb-3">
          <CardTitle className={`flex items-center gap-2 text-lg ${themeClasses.text.primary}`}>
            <Icon className="w-5 h-5" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Status */}
          <div className="space-y-2">
            <Label className={themeClasses.text.primary}>Status</Label>
            <Select
              value={inspectionData[`${type}_inspection_status`]}
              onValueChange={(value) => setInspectionData(prev => ({
                ...prev,
                [`${type}_inspection_status`]: value
              }))}
            >
              <SelectTrigger className={themeClasses.input.primary}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {inspectionStatuses.map((status) => (
                  <SelectItem key={status.value} value={status.value}>
                    <div className="flex items-center gap-2">
                      <status.icon className={`w-4 h-4 ${status.color}`} />
                      {status.label}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Date */}
          <div className="space-y-2">
            <Label className={themeClasses.text.primary}>Date</Label>
            <Popover>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  className={cn(
                    "w-full justify-start text-left font-normal",
                    !inspectionData[`${type}_inspection_date`] && "text-muted-foreground"
                  )}
                >
                  <CalendarIcon className="mr-2 h-4 w-4" />
                  {inspectionData[`${type}_inspection_date`] ? 
                    format(inspectionData[`${type}_inspection_date`], "PPP") : 
                    "Select date"
                  }
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0">
                <Calendar
                  mode="single"
                  selected={inspectionData[`${type}_inspection_date`]}
                  onSelect={(date) => setInspectionData(prev => ({
                    ...prev,
                    [`${type}_inspection_date`]: date
                  }))}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label className={themeClasses.text.primary}>Notes</Label>
            <Textarea
              value={inspectionData[`${type}_inspection_notes`]}
              onChange={(e) => setInspectionData(prev => ({
                ...prev,
                [`${type}_inspection_notes`]: e.target.value
              }))}
              placeholder="Inspection notes..."
              className={themeClasses.input.primary}
              rows={3}
            />
          </div>

          {/* Current Status Display */}
          <div className={`flex items-center gap-2 p-3 rounded-lg ${
            isDarkMode ? 'bg-white/5' : 'bg-gray-50'
          }`}>
            <StatusIcon className={`w-5 h-5 ${statusInfo.color}`} />
            <span className={`font-medium ${themeClasses.text.primary}`}>
              {statusInfo.label}
            </span>
          </div>

          {/* Update Button */}
          <Button
            onClick={() => handleUpdateInspection(type)}
            className="w-full"
          >
            Update {title}
          </Button>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <InspectionCard 
          type="rough" 
          title="Rough Inspection" 
          icon={Wrench}
        />
        <InspectionCard 
          type="final" 
          title="Final Inspection" 
          icon={FileCheck}
        />
      </div>
    </div>
  );
};

export default InspectionManagement;