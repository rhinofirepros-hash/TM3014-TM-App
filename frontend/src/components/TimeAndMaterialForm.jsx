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
import { CalendarIcon, Plus, Trash2, Info, Download, Eye, PenTool } from 'lucide-react';
import { cn } from '../lib/utils';
import RichTextEditor from './RichTextEditor';
import LaborTable from './LaborTable';
import MaterialTable from './MaterialTable';
import EquipmentTable from './EquipmentTable';
import OtherTable from './OtherTable';
import SignatureCapture from './SignatureCapture';
import PDFGenerator from './PDFGenerator';
import { mockData } from '../data/mock';
import { useToast } from '../hooks/use-toast';

const TimeAndMaterialForm = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    projectName: "3rd Ave",
    costCode: 'FP-Install',
    dateOfWork: new Date(),
    customerReference: '',
    tmTagTitle: 'Sprinkler Rough-In - 4 Tech, 32 hrs',
    descriptionOfWork: 'Started Working on wrapping up 2nd floor core in units.',
    laborEntries: mockData.laborEntries,
    materialEntries: [],
    equipmentEntries: [],
    otherEntries: [],
    signature: null
  });
  
  const [showSignatureModal, setShowSignatureModal] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [isCustomProject, setIsCustomProject] = useState(false);
  const [customProjectName, setCustomProjectName] = useState('');
  const [savedProjects, setSavedProjects] = useState(() => {
    const saved = localStorage.getItem('saved_projects');
    return saved ? JSON.parse(saved) : [{ id: 1, name: "3rd Ave" }];
  });

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = () => {
    // Save to localStorage as a draft
    const savedData = {
      ...formData,
      savedAt: new Date().toISOString()
    };
    localStorage.setItem('tm_tag_draft', JSON.stringify(savedData));
    
    toast({
      title: "Draft Saved",
      description: "Your T&M tag has been saved as a draft.",
    });
  };

  const handlePreview = async () => {
    if (!validateForm()) return;
    
    setIsGeneratingPDF(true);
    try {
      const pdfGenerator = PDFGenerator({ formData });
      const result = await pdfGenerator.generatePDF();
      
      if (result.success) {
        toast({
          title: "PDF Generated",
          description: `Preview saved as ${result.filename}`,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to generate PDF preview.",
        variant: "destructive"
      });
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  const handleCollectSignatures = () => {
    if (!validateForm()) return;
    setShowSignatureModal(true);
  };

  const handleSignatureSave = (signatureData) => {
    setFormData(prev => ({
      ...prev,
      signature: signatureData
    }));
    
    toast({
      title: "Signature Captured",
      description: "Foreman signature has been saved.",
    });
  };

  const validateForm = () => {
    if (!formData.projectName) {
      toast({
        title: "Validation Error",
        description: "Please select a project name.",
        variant: "destructive"
      });
      return false;
    }
    
    if (!formData.tmTagTitle) {
      toast({
        title: "Validation Error", 
        description: "Please enter a T&M tag title.",
        variant: "destructive"
      });
      return false;
    }
    
    if (formData.laborEntries.length === 0) {
      toast({
        title: "Validation Error",
        description: "Please add at least one labor entry.",
        variant: "destructive"
      });
      return false;
    }
    
    return true;
  };

  const handleSubmitAndEmail = async () => {
    if (!validateForm()) return;
    
    if (!formData.signature) {
      toast({
        title: "Signature Required",
        description: "Please collect foreman signature before submitting.",
        variant: "destructive"
      });
      return;
    }

    setIsGeneratingPDF(true);
    try {
      const pdfGenerator = PDFGenerator({ formData });
      const result = await pdfGenerator.generatePDF();
      
      if (result.success) {
        // TODO: Implement email functionality
        toast({
          title: "T&M Tag Submitted",
          description: `PDF generated and ready to email to GC: ${result.filename}`,
        });
        
        // Clear form after successful submission
        setFormData({
          projectName: "3rd Ave",
          costCode: 'FP-Install',
          dateOfWork: new Date(),
          customerReference: '',
          tmTagTitle: '',
          descriptionOfWork: '',
          laborEntries: [],
          materialEntries: [],
          signature: null
        });
      }
    } catch (error) {
      toast({
        title: "Submission Error",
        description: "Failed to generate and submit T&M tag.",
        variant: "destructive"
      });
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  const handleSaveCustomProject = () => {
    if (!customProjectName.trim()) {
      toast({
        title: "Project Name Required",
        description: "Please enter a project name.",
        variant: "destructive"
      });
      return;
    }

    const newProject = {
      id: Date.now(),
      name: customProjectName.trim()
    };

    const updatedProjects = [...savedProjects, newProject];
    setSavedProjects(updatedProjects);
    localStorage.setItem('saved_projects', JSON.stringify(updatedProjects));
    
    setFormData(prev => ({ ...prev, projectName: newProject.name }));
    setCustomProjectName('');
    setIsCustomProject(false);
    
    toast({
      title: "Project Saved",
      description: `"${newProject.name}" has been added to your project list.`,
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-2 sm:p-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-4 sm:mb-6">
          <h1 className="text-lg sm:text-2xl font-semibold text-gray-900">
            Create A Time & Material Tag
          </h1>
        </div>

        <Card className="shadow-sm">
          <CardContent className="p-3 sm:p-6 space-y-4 sm:space-y-6">
            {/* Project Name */}
            <div className="space-y-2">
              <Label htmlFor="projectName" className="text-sm font-medium text-gray-700 flex items-center justify-between">
                Project Name*
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setIsCustomProject(!isCustomProject)}
                  className="text-xs h-6 px-2"
                >
                  {isCustomProject ? 'Cancel' : 'Add New'}
                </Button>
              </Label>
              
              {isCustomProject ? (
                <div className="flex gap-2">
                  <Input
                    value={customProjectName}
                    onChange={(e) => setCustomProjectName(e.target.value)}
                    placeholder="Enter new project name"
                    className="flex-1"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSaveCustomProject();
                      }
                    }}
                  />
                  <Button
                    type="button"
                    onClick={handleSaveCustomProject}
                    size="sm"
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    Save
                  </Button>
                </div>
              ) : (
                <Select 
                  value={formData.projectName} 
                  onValueChange={(value) => handleInputChange('projectName', value)}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {savedProjects.map((project) => (
                      <SelectItem key={project.id} value={project.name}>
                        {project.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
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
                      "w-full justify-start text-left font-normal min-w-[160px] h-10",
                      !formData.dateOfWork && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4 flex-shrink-0" />
                    <span className="truncate">
                      {formData.dateOfWork ? format(formData.dateOfWork, "MM/dd/yyyy") : "Pick a date"}
                    </span>
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
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
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <h3 className="text-lg font-medium text-gray-900">Add Labor</h3>
                <div className="flex flex-col sm:flex-row gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="text-green-700 border-green-300 hover:bg-green-50 h-9 px-3"
                    onClick={() => {
                      const jesusEntry = {
                        id: Date.now(),
                        workerName: 'Jesus Garcia',
                        quantity: 1,
                        stHours: 8.00,
                        otHours: 0,
                        dtHours: 0,
                        potHours: 0,
                        totalHours: 8.00,
                        date: new Date().toLocaleDateString()
                      };
                      handleInputChange('laborEntries', [...formData.laborEntries, jesusEntry]);
                    }}
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Jesus Garcia
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="text-green-700 border-green-300 hover:bg-green-50 h-9 px-3"
                    onClick={() => {
                      const newEntry = {
                        id: Date.now(),
                        workerName: '',
                        quantity: 1,
                        stHours: 0,
                        otHours: 0,
                        dtHours: 0,
                        potHours: 0,
                        totalHours: 0,
                        date: new Date().toLocaleDateString()
                      };
                      handleInputChange('laborEntries', [...formData.laborEntries, newEntry]);
                    }}
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Worker
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
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <h3 className="text-lg font-medium text-gray-900">Add Material</h3>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="text-green-700 border-green-300 hover:bg-green-50 h-9 px-3"
                    onClick={() => {
                      const newMaterial = {
                        id: Date.now(),
                        materialName: '',
                        unitOfMeasure: '',
                        quantity: 0,
                        unitCost: 0,
                        total: 0,
                        dateOfWork: new Date().toLocaleDateString()
                      };
                      handleInputChange('materialEntries', [...formData.materialEntries, newMaterial]);
                    }}
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add Material
                  </Button>
                </div>
              </div>
              
              <MaterialTable 
                entries={formData.materialEntries}
                onChange={(entries) => handleInputChange('materialEntries', entries)}
              />
            </div>

            {/* Add Equipment Section */}
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <h3 className="text-lg font-medium text-gray-900">Add Equipment</h3>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="text-green-700 border-green-300 hover:bg-green-50 h-9 px-3"
                    onClick={() => {
                      const newEquipment = {
                        id: Date.now(),
                        equipmentName: '',
                        piecesOfEquipment: 1,
                        unitOfMeasure: '',
                        quantity: 0,
                        total: 0,
                        dateOfWork: new Date().toLocaleDateString()
                      };
                      handleInputChange('equipmentEntries', [...formData.equipmentEntries, newEquipment]);
                    }}
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add empty row
                  </Button>
                </div>
              </div>
              
              <EquipmentTable 
                entries={formData.equipmentEntries}
                onChange={(entries) => handleInputChange('equipmentEntries', entries)}
              />
            </div>

            {/* Add Other Section */}
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <h3 className="text-lg font-medium text-gray-900">Add Other</h3>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="text-green-700 border-green-300 hover:bg-green-50 h-9 px-3"
                    onClick={() => {
                      const newOther = {
                        id: Date.now(),
                        otherName: '',
                        quantityOfOther: 1,
                        unitOfMeasure: '',
                        quantityOfUnit: 0,
                        total: 0,
                        dateOfWork: new Date().toLocaleDateString()
                      };
                      handleInputChange('otherEntries', [...formData.otherEntries, newOther]);
                    }}
                  >
                    <Plus className="w-4 h-4 mr-1" />
                    Add empty row
                  </Button>
                </div>
              </div>
              
              <OtherTable 
                entries={formData.otherEntries}
                onChange={(entries) => handleInputChange('otherEntries', entries)}
              />
            </div>

            {/* Signature Status */}
            {formData.signature && (
              <div className="bg-green-50 border border-green-200 rounded-md p-4">
                <div className="flex items-center gap-2 text-green-700">
                  <PenTool className="w-4 h-4" />
                  <span className="font-medium">Foreman Signature Collected</span>
                </div>
                <p className="text-sm text-green-600 mt-1">
                  Ready to generate final PDF and submit to General Contractor
                </p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row justify-between pt-6 border-t gap-4">
              <div className="flex flex-col sm:flex-row gap-3">
                <Button 
                  variant="outline" 
                  className="text-gray-600 h-10"
                  onClick={() => {
                    setFormData({
                      projectName: "3rd Ave",
                      costCode: 'FP-Install',
                      dateOfWork: new Date(),
                      customerReference: '',
                      tmTagTitle: '',
                      descriptionOfWork: '',
                      laborEntries: [],
                      materialEntries: [],
                      signature: null
                    });
                    setIsCustomProject(false);
                    setCustomProjectName('');
                  }}
                >
                  Cancel
                </Button>
                <Button 
                  variant="outline" 
                  onClick={handleSave}
                  className="text-gray-600 h-10"
                >
                  Save Draft
                </Button>
              </div>
              <div className="flex flex-col sm:flex-row gap-3">
                <Button 
                  variant="outline" 
                  onClick={handlePreview}
                  disabled={isGeneratingPDF}
                  className="text-gray-600 flex items-center justify-center gap-2 h-10"
                >
                  <Eye className="w-4 h-4" />
                  <span className="hidden sm:inline">{isGeneratingPDF ? 'Generating...' : 'Preview PDF'}</span>
                  <span className="sm:hidden">{isGeneratingPDF ? 'Generating...' : 'Preview'}</span>
                </Button>
                
                {!formData.signature ? (
                  <Button 
                    onClick={handleCollectSignatures}
                    className="bg-green-600 hover:bg-green-700 text-white flex items-center justify-center gap-2 h-10"
                  >
                    <PenTool className="w-4 h-4" />
                    <span className="hidden sm:inline">Collect Signatures</span>
                    <span className="sm:hidden">Sign</span>
                  </Button>
                ) : (
                  <Button 
                    onClick={handleSubmitAndEmail}
                    disabled={isGeneratingPDF}
                    className="bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center gap-2 h-10"
                  >
                    <Download className="w-4 h-4" />
                    <span className="hidden sm:inline">{isGeneratingPDF ? 'Submitting...' : 'Submit & Email GC'}</span>
                    <span className="sm:hidden">{isGeneratingPDF ? 'Submitting...' : 'Submit'}</span>
                  </Button>
                )}
              </div>
            </div>

            {/* Signature Modal */}
            <SignatureCapture
              isOpen={showSignatureModal}
              onClose={() => setShowSignatureModal(false)}
              onSave={handleSignatureSave}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TimeAndMaterialForm;