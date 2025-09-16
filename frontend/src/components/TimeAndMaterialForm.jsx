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
import { CalendarIcon, Plus, Trash2, Info } from 'lucide-react';
import { cn } from '../lib/utils';
import RichTextEditor from './RichTextEditor';
import LaborTable from './LaborTable';
import MaterialTable from './MaterialTable';
import { mockData } from '../data/mock';

const TimeAndMaterialForm = () => {
  const [formData, setFormData] = useState({
    projectName: mockData.projects[0].name,
    costCode: 'FP-Install',
    dateOfWork: new Date(),
    customerReference: '',
    tmTagTitle: 'Sprinkler Rough-In - 4 Tech, 32 hrs',
    descriptionOfWork: 'Started Working on wrapping up 2nd floor core in units.',
    laborEntries: mockData.laborEntries,
    materialEntries: []
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = () => {
    console.log('Saving form data:', formData);
    // TODO: Implement save functionality
  };

  const handlePreview = () => {
    console.log('Previewing form data:', formData);
    // TODO: Implement preview functionality
  };

  const handleCollectSignatures = () => {
    console.log('Collecting signatures for:', formData);
    // TODO: Implement signature collection
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">
            Create A Time & Material Tag
          </h1>
        </div>

        <Card className="shadow-sm">
          <CardContent className="p-6 space-y-6">
            {/* Project Name */}
            <div className="space-y-2">
              <Label htmlFor="projectName" className="text-sm font-medium text-gray-700">
                Project Name*
              </Label>
              <Select 
                value={formData.projectName} 
                onValueChange={(value) => handleInputChange('projectName', value)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {mockData.projects.map((project) => (
                    <SelectItem key={project.id} value={project.name}>
                      {project.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Cost Code */}
            <div className="space-y-2">
              <Label htmlFor="costCode" className="text-sm font-medium text-gray-700">
                Cost Code
              </Label>
              <Input
                id="costCode"
                value={formData.costCode}
                onChange={(e) => handleInputChange('costCode', e.target.value)}
                className="w-full"
              />
            </div>

            {/* Date of Work Performed */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700">
                Date Of Work Performed*
              </Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !formData.dateOfWork && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {formData.dateOfWork ? format(formData.dateOfWork, "MM/dd/yyyy") : "Pick a date"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={formData.dateOfWork}
                    onSelect={(date) => handleInputChange('dateOfWork', date)}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </div>

            {/* Customer Reference Number */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700 flex items-center gap-1">
                Customer Reference Number
                <Info className="w-4 h-4 text-gray-400" />
              </Label>
              <Select 
                value={formData.customerReference} 
                onValueChange={(value) => handleInputChange('customerReference', value)}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Enter or select reference number" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ref1">Reference 1</SelectItem>
                  <SelectItem value="ref2">Reference 2</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Title of T&M Tag */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700 flex items-center gap-1">
                Title Of T&M Tag*
                <Info className="w-4 h-4 text-gray-400" />
              </Label>
              <Input
                value={formData.tmTagTitle}
                onChange={(e) => handleInputChange('tmTagTitle', e.target.value)}
                className="w-full"
              />
            </div>

            {/* Description of Work */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700 flex items-center gap-1">
                Description Of Work*
                <Info className="w-4 h-4 text-gray-400" />
              </Label>
              <RichTextEditor
                value={formData.descriptionOfWork}
                onChange={(value) => handleInputChange('descriptionOfWork', value)}
              />
            </div>

            {/* Add Labor Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Add Labor</h3>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="text-green-700 border-green-300">
                    Select from list
                  </Button>
                  <Button variant="outline" size="sm" className="text-green-700 border-green-300">
                    Add empty row
                  </Button>
                </div>
              </div>
              
              <LaborTable 
                entries={formData.laborEntries}
                onChange={(entries) => handleInputChange('laborEntries', entries)}
              />
            </div>

            {/* Add Material Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-900">Add Material</h3>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="text-green-700 border-green-300">
                    Select from list
                  </Button>
                  <Button variant="outline" size="sm" className="text-green-700 border-green-300">
                    Add empty row
                  </Button>
                </div>
              </div>
              
              <MaterialTable 
                entries={formData.materialEntries}
                onChange={(entries) => handleInputChange('materialEntries', entries)}
              />
            </div>

            {/* Action Buttons */}
            <div className="flex justify-between pt-6 border-t">
              <div className="flex gap-3">
                <Button variant="outline" className="text-gray-600">
                  Cancel
                </Button>
                <Button 
                  variant="outline" 
                  onClick={handleSave}
                  className="text-gray-600"
                >
                  Save
                </Button>
              </div>
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  onClick={handlePreview}
                  className="text-gray-600"
                >
                  Preview
                </Button>
                <Button 
                  onClick={handleCollectSignatures}
                  className="bg-green-600 hover:bg-green-700 text-white"
                >
                  Collect Signatures
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TimeAndMaterialForm;