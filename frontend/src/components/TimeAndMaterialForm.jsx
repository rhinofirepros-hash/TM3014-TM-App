import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Calendar } from './ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { format } from 'date-fns';
import { CalendarIcon, Plus, Trash2, Info, Download, Eye, PenTool, Mail, FileText, ArrowLeft, Sun, Moon, Users, Package, Truck } from 'lucide-react';
import { cn } from '../lib/utils';
import RichTextEditor from './RichTextEditor';
import LaborTable from './LaborTable';
import MaterialTable from './MaterialTable';
import EquipmentTable from './EquipmentTable';
import OtherTable from './OtherTable';
import SignatureCapture from './SignatureCapture';
import PDFGenerator from './PDFGenerator';
import EmailComposer from './EmailComposer';
import { mockData } from '../data/mock';
import { useToast } from '../hooks/use-toast';
import { useTheme } from '../contexts/ThemeContext';

const TimeAndMaterialForm = ({ selectedProject, onBack, onSave, project, tmTag }) => {
  const { toast } = useToast();
  const { isDarkMode, toggleTheme, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const [availableProjects, setAvailableProjects] = useState([]);
  const [selectedProjectData, setSelectedProjectData] = useState(null);
  const [formData, setFormData] = useState({
    projectName: selectedProject?.name || project?.name || "",
    projectId: selectedProject?.id || project?.id || null,
    costCode: tmTag?.cost_code || '',
    dateOfWork: tmTag?.date_of_work ? new Date(tmTag.date_of_work) : new Date(),
    companyName: selectedProject?.client_company || project?.client_company || '',
    tmTagTitle: tmTag?.tm_tag_title || '',
    descriptionOfWork: tmTag?.description_of_work || '',
    laborEntries: tmTag?.labor_entries || [],
    materialEntries: tmTag?.material_entries || [],
    equipmentEntries: tmTag?.equipment_entries || [],
    otherEntries: tmTag?.other_entries || [],
    gcEmail: selectedProject?.gc_email || project?.gc_email || tmTag?.gc_email || '',
    autoEmail: false,
    downloadPDF: true,
    signature: tmTag?.signature || null,
    signerName: tmTag?.foreman_name || '',
    signerTitle: 'Foreman'
  });
  
  const [showPreview, setShowPreview] = useState(false);
  const [showSignature, setShowSignature] = useState(false);
  const [showEmailComposer, setShowEmailComposer] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [calculatedTotals, setCalculatedTotals] = useState({
    labor: 0,
    materials: 0,
    equipment: 0,
    other: 0,
    total: 0
  });

  // Load projects and set up form
  useEffect(() => {
    loadProjects();
    if (tmTag) {
      // If editing existing T&M tag, populate form
      populateFormFromTmTag(tmTag);
    }
  }, [tmTag]);

  const loadProjects = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '/api';
      const response = await fetch(`${backendUrl}/projects`);
      
      if (response.ok) {
        const projects = await response.json();
        setAvailableProjects(projects);
        
        // Find the selected project data
        if (formData.projectId) {
          const projectData = projects.find(p => p.id === formData.projectId);
          setSelectedProjectData(projectData);
        }
      } else {
        // Fallback to localStorage
        const savedProjects = localStorage.getItem('projects');
        if (savedProjects) {
          const projects = JSON.parse(savedProjects);
          setAvailableProjects(projects);
        }
      }
    } catch (error) {
      console.error('Error loading projects:', error);
      // Fallback to mock data or localStorage
      setAvailableProjects(mockData.projects || []);
    }
  };

  const populateFormFromTmTag = (tmTag) => {
    setFormData(prev => ({
      ...prev,
      projectName: tmTag.project_name || prev.projectName,
      projectId: tmTag.project_id || prev.projectId,
      costCode: tmTag.cost_code || '',
      dateOfWork: tmTag.date_of_work ? new Date(tmTag.date_of_work) : new Date(),
      companyName: tmTag.company_name || prev.companyName,
      tmTagTitle: tmTag.tm_tag_title || '',
      descriptionOfWork: tmTag.description_of_work || '',
      laborEntries: tmTag.labor_entries || [],
      materialEntries: tmTag.material_entries || [],
      equipmentEntries: tmTag.equipment_entries || [],
      otherEntries: tmTag.other_entries || [],
      gcEmail: tmTag.gc_email || prev.gcEmail,
      signature: tmTag.signature || null,
      signerName: tmTag.foreman_name || 'Jesus Garcia'
    }));
  };

  // Calculate totals whenever entries change
  useEffect(() => {
    calculateTotals();
  }, [formData.laborEntries, formData.materialEntries, formData.equipmentEntries, formData.otherEntries]);

  const calculateTotals = () => {
    const labor = formData.laborEntries.reduce((sum, entry) => 
      sum + (parseFloat(entry.total) || 0), 0);
    const materials = formData.materialEntries.reduce((sum, entry) => 
      sum + (parseFloat(entry.total) || 0), 0);
    const equipment = formData.equipmentEntries.reduce((sum, entry) => 
      sum + (parseFloat(entry.total) || 0), 0);
    const other = formData.otherEntries.reduce((sum, entry) => 
      sum + (parseFloat(entry.total) || 0), 0);
    
    const total = labor + materials + equipment + other;
    
    setCalculatedTotals({ labor, materials, equipment, other, total });
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleProjectChange = (projectId) => {
    const project = availableProjects.find(p => p.id === projectId);
    if (project) {
      setSelectedProjectData(project);
      setFormData(prev => ({
        ...prev,
        projectId: project.id,
        projectName: project.name,
        companyName: project.client_company || project.client || '',
        gcEmail: project.gc_email || ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.projectId) {
      toast({
        title: "Missing Information",
        description: "Please select a project",
        variant: "destructive"
      });
      return;
    }

    if (!formData.tmTagTitle.trim()) {
      toast({
        title: "Missing Information", 
        description: "Please enter a T&M tag title",
        variant: "destructive"
      });
      return;
    }

    setIsSubmitting(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '/api';
      const tagData = {
        id: tmTag?.id || `tm_${Date.now()}`,
        project_id: formData.projectId,
        project_name: formData.projectName,  
        cost_code: formData.costCode,
        date_of_work: formData.dateOfWork.toISOString(),
        company_name: formData.companyName,
        tm_tag_title: formData.tmTagTitle,
        description_of_work: formData.descriptionOfWork,
        labor_entries: formData.laborEntries,
        material_entries: formData.materialEntries,
        equipment_entries: formData.equipmentEntries,
        other_entries: formData.otherEntries,
        gc_email: formData.gcEmail,
        signature: formData.signature,
        foreman_name: formData.signerName,
        status: "completed",
        created_at: tmTag?.created_at || new Date().toISOString(),
        total_cost: calculatedTotals.total
      };

      let response;
      if (tmTag) {
        // Update existing T&M tag
        response = await fetch(`${backendUrl}/tm-tags/${tmTag.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(tagData)
        });
      } else {
        // Create new T&M tag
        response = await fetch(`${backendUrl}/tm-tags`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(tagData)
        });
      }
      
      if (response.ok) {
        // Also save to localStorage as backup
        const existingTags = JSON.parse(localStorage.getItem('tmTags') || '[]');
        if (tmTag) {
          const index = existingTags.findIndex(tag => tag.id === tmTag.id);
          if (index !== -1) {
            existingTags[index] = tagData;
          }
        } else {
          existingTags.push(tagData);
        }
        localStorage.setItem('tmTags', JSON.stringify(existingTags));
        
        toast({
          title: tmTag ? "T&M Tag Updated" : "T&M Tag Created",
          description: tmTag ? "T&M tag has been updated successfully" : "T&M tag has been created and saved",
        });
        
        if (onSave) onSave();
      } else {
        throw new Error('Failed to save T&M tag');
      }
    } catch (error) {
      console.error('Error saving T&M tag:', error);
      
      // Save to localStorage as fallback
      const tagData = {
        id: tmTag?.id || `tm_${Date.now()}`,
        project_id: formData.projectId,
        project_name: formData.projectName,
        cost_code: formData.costCode,
        date_of_work: formData.dateOfWork.toISOString(),
        company_name: formData.companyName,
        tm_tag_title: formData.tmTagTitle,
        description_of_work: formData.descriptionOfWork,
        labor_entries: formData.laborEntries,
        material_entries: formData.materialEntries,
        equipment_entries: formData.equipmentEntries,
        other_entries: formData.otherEntries,
        gc_email: formData.gcEmail,
        signature: formData.signature,
        foreman_name: formData.signerName,
        status: "completed",
        created_at: tmTag?.created_at || new Date().toISOString(),
        total_cost: calculatedTotals.total
      };
      
      const existingTags = JSON.parse(localStorage.getItem('tmTags') || '[]');
      if (tmTag) {
        const index = existingTags.findIndex(tag => tag.id === tmTag.id);
        if (index !== -1) {
          existingTags[index] = tagData;
        }
      } else {
        existingTags.push(tagData);
      }
      localStorage.setItem('tmTags', JSON.stringify(existingTags));
      
      toast({
        title: tmTag ? "T&M Tag Updated" : "T&M Tag Saved",
        description: tmTag ? "T&M tag updated and saved locally" : "T&M tag saved locally (offline mode)",
      });
      
      if (onSave) onSave();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSignatureComplete = (signatureData) => {
    setFormData(prev => ({
      ...prev,
      signature: signatureData
    }));
    setShowSignature(false);
    
    toast({
      title: "Signature Captured",
      description: "Digital signature has been added to the T&M tag",
    });
  };

  return (
    <div className={`min-h-screen ${themeClasses.background}`}>
      {/* Mobile-First Header */}
      <div className={themeClasses.header}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex items-center space-x-4 w-full sm:w-auto">
              <Button 
                variant="ghost" 
                onClick={onBack}
                className="shrink-0"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                <span className="hidden xs:inline">Back</span>
              </Button>
              <div className="min-w-0 flex-1">
                <h1 className={`text-xl sm:text-2xl font-bold ${themeClasses.text.primary} truncate`}>
                  {tmTag ? 'Edit' : 'Create'} T&M Tag
                </h1>
                <p className={`text-sm ${themeClasses.text.secondary} truncate`}>
                  {formData.projectName || 'Time & Material Daily Tag'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2 w-full sm:w-auto">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleTheme}
                className="shrink-0"
              >
                {isDarkMode ? <Sun className="w-4 h-4" style={{ color: '#FEF08A' }} /> : <Moon className="w-4 h-4" />}
              </Button>
              
              <Button
                type="submit"
                form="tm-form"
                disabled={isSubmitting}
                className="flex-1 sm:flex-none"
              >
                {isSubmitting ? 'Saving...' : (tmTag ? 'Update' : 'Save')} Tag
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        <form id="tm-form" onSubmit={handleSubmit} className="space-y-6">
          {/* Project Information - Mobile Responsive */}
          <Card className={`${themeClasses.card} rounded-lg`}>
            <CardHeader className="pb-4">
              <CardTitle className={`${themeClasses.text.primary} text-lg sm:text-xl`}>
                Project Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className={themeClasses.text.primary}>Project *</Label>
                  <Select 
                    value={formData.projectId || ""} 
                    onValueChange={handleProjectChange}
                    disabled={!!selectedProject}
                  >
                    <SelectTrigger className={`${themeClasses.input.primary} w-full`}>
                      <SelectValue placeholder="Select a project" />
                    </SelectTrigger>
                    <SelectContent className={themeClasses.dropdown}>
                      {availableProjects.map((project) => (
                        <SelectItem key={project.id} value={project.id}>
                          {project.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label className={themeClasses.text.primary}>Cost Code</Label>
                  <Input
                    value={formData.costCode}
                    onChange={(e) => handleInputChange('costCode', e.target.value)}
                    placeholder="Enter cost code"
                    className={themeClasses.input.primary}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className={themeClasses.text.primary}>Date of Work *</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant="outline"
                        className={cn(
                          "w-full justify-start text-left font-normal",
                          themeClasses.input.primary,
                          !formData.dateOfWork && "text-muted-foreground"
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {formData.dateOfWork ? format(formData.dateOfWork, "PPP") : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className={`w-auto p-0 ${themeClasses.dropdown}`}>
                      <Calendar
                        mode="single"
                        selected={formData.dateOfWork}
                        onSelect={(date) => handleInputChange('dateOfWork', date)}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
                
                <div className="space-y-2">
                  <Label className={themeClasses.text.primary}>Company Name</Label>
                  <Input
                    value={formData.companyName}
                    onChange={(e) => handleInputChange('companyName', e.target.value)}
                    placeholder="Client company name"
                    className={themeClasses.input.primary}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>T&M Tag Title *</Label>
                <Input
                  value={formData.tmTagTitle}
                  onChange={(e) => handleInputChange('tmTagTitle', e.target.value)}
                  placeholder="Brief title for this T&M tag"
                  className={themeClasses.input.primary}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Description of Work</Label>
                <Textarea
                  value={formData.descriptionOfWork}
                  onChange={(e) => handleInputChange('descriptionOfWork', e.target.value)}
                  placeholder="Detailed description of work performed"
                  className={`${themeClasses.input.primary} min-h-20`}
                  rows={4}
                />
              </div>

              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>General Contractor Email</Label>
                <Input
                  type="email"
                  value={formData.gcEmail}
                  onChange={(e) => handleInputChange('gcEmail', e.target.value)}
                  placeholder="GC email for automatic sending"
                  className={themeClasses.input.primary}
                />
              </div>
            </CardContent>
          </Card>

          {/* Labor Entries - Mobile Responsive */}
          <Card className={`${themeClasses.card} rounded-lg`}>
            <CardHeader className="pb-4">
              <CardTitle className={`${themeClasses.text.primary} text-lg sm:text-xl flex items-center`}>
                <Users className="w-5 h-5 mr-2" />
                Labor Entries
                <span className={`ml-auto text-sm font-normal ${themeClasses.text.secondary}`}>
                  Total: ${calculatedTotals.labor.toFixed(2)}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <LaborTable
                  entries={formData.laborEntries}
                  onChange={(entries) => handleInputChange('laborEntries', entries)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Material Entries - Mobile Responsive */}
          <Card className={`${themeClasses.card} rounded-lg`}>
            <CardHeader className="pb-4">
              <CardTitle className={`${themeClasses.text.primary} text-lg sm:text-xl flex items-center`}>
                <Package className="w-5 h-5 mr-2" />
                Material Entries
                <span className={`ml-auto text-sm font-normal ${themeClasses.text.secondary}`}>
                  Total: ${calculatedTotals.materials.toFixed(2)}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <MaterialTable
                  entries={formData.materialEntries}
                  onChange={(entries) => handleInputChange('materialEntries', entries)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Equipment Entries - Mobile Responsive */}
          <Card className={`${themeClasses.card} rounded-lg`}>
            <CardHeader className="pb-4">
              <CardTitle className={`${themeClasses.text.primary} text-lg sm:text-xl flex items-center`}>
                <Truck className="w-5 h-5 mr-2" />
                Equipment Entries
                <span className={`ml-auto text-sm font-normal ${themeClasses.text.secondary}`}>
                  Total: ${calculatedTotals.equipment.toFixed(2)}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <EquipmentTable
                  entries={formData.equipmentEntries}
                  onChange={(entries) => handleInputChange('equipmentEntries', entries)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Other Entries - Mobile Responsive */}
          <Card className={`${themeClasses.card} rounded-lg`}>
            <CardHeader className="pb-4">
              <CardTitle className={`${themeClasses.text.primary} text-lg sm:text-xl flex items-center`}>
                <FileText className="w-5 h-5 mr-2" />
                Other Entries
                <span className={`ml-auto text-sm font-normal ${themeClasses.text.secondary}`}>
                  Total: ${calculatedTotals.other.toFixed(2)}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <OtherTable
                  entries={formData.otherEntries}
                  onChange={(entries) => handleInputChange('otherEntries', entries)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Signature Section - Mobile Responsive */}
          <Card className={`${themeClasses.card} rounded-lg`}>
            <CardHeader className="pb-4">
              <CardTitle className={`${themeClasses.text.primary} text-lg sm:text-xl`}>
                Digital Signature
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className={themeClasses.text.primary}>Signer Name</Label>
                  <Input
                    value={formData.signerName}
                    onChange={(e) => handleInputChange('signerName', e.target.value)}
                    placeholder="Enter signer name"
                    className={themeClasses.input.primary}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label className={themeClasses.text.primary}>Title</Label>
                  <Input
                    value={formData.signerTitle}
                    onChange={(e) => handleInputChange('signerTitle', e.target.value)}
                    placeholder="Enter signer title"
                    className={themeClasses.input.primary}
                  />
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowSignature(true)}
                  className="flex-1 sm:flex-none"
                >
                  <PenTool className="w-4 h-4 mr-2" />
                  {formData.signature ? 'Update Signature' : 'Add Signature'}
                </Button>
                
                {formData.signature && (
                  <div className={`p-4 rounded-lg border ${
                    isDarkMode ? 'border-white/20 bg-white/5' : 'border-gray-200 bg-gray-50'
                  } flex-1`}>
                    <img 
                      src={formData.signature} 
                      alt="Digital Signature" 
                      className="max-h-20 max-w-full object-contain mx-auto"
                    />
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Summary Card - Mobile Responsive */}
          <Card className={`${themeClasses.card} rounded-lg`}>
            <CardHeader className="pb-4">
              <CardTitle className={`${themeClasses.text.primary} text-lg sm:text-xl`}>
                T&M Tag Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 text-center">
                <div className={`p-3 sm:p-4 rounded-lg ${
                  isDarkMode ? 'bg-white/5' : 'bg-gray-50'
                }`}>
                  <div className={`text-lg sm:text-xl font-bold ${themeClasses.text.primary}`}>
                    ${calculatedTotals.labor.toFixed(2)}
                  </div>
                  <div className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Labor</div>
                </div>
                
                <div className={`p-3 sm:p-4 rounded-lg ${
                  isDarkMode ? 'bg-white/5' : 'bg-gray-50'
                }`}>
                  <div className={`text-lg sm:text-xl font-bold ${themeClasses.text.primary}`}>
                    ${calculatedTotals.materials.toFixed(2)}
                  </div>
                  <div className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Materials</div>
                </div>
                
                <div className={`p-3 sm:p-4 rounded-lg ${
                  isDarkMode ? 'bg-white/5' : 'bg-gray-50'
                }`}>
                  <div className={`text-lg sm:text-xl font-bold ${themeClasses.text.primary}`}>
                    ${calculatedTotals.equipment.toFixed(2)}
                  </div>
                  <div className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Equipment</div>
                </div>
                
                <div className={`p-3 sm:p-4 rounded-lg ${
                  isDarkMode ? 'bg-white/5' : 'bg-gray-50'
                }`}>
                  <div className={`text-lg sm:text-xl font-bold ${themeClasses.text.primary}`}>
                    ${calculatedTotals.other.toFixed(2)}
                  </div>
                  <div className={`text-xs sm:text-sm ${themeClasses.text.secondary}`}>Other</div>
                </div>
                
                <div className={`p-3 sm:p-4 rounded-lg ${
                  isDarkMode ? 'bg-blue-500/20 border border-blue-500/30' : 'bg-blue-50 border border-blue-200'
                }`}>
                  <div className={`text-xl sm:text-2xl font-bold ${
                    isDarkMode ? 'text-blue-400' : 'text-blue-600'
                  }`}>
                    ${calculatedTotals.total.toFixed(2)}
                  </div>
                  <div className={`text-xs sm:text-sm ${
                    isDarkMode ? 'text-blue-300' : 'text-blue-600'
                  }`}>Total</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons - Mobile Responsive */}
          <div className="flex flex-col sm:flex-row gap-4 pt-6">
            <Button
              type="button"
              variant="outline"
              onClick={() => setShowPreview(true)}
              className="flex-1 sm:flex-none order-2 sm:order-1"
            >
              <Eye className="w-4 h-4 mr-2" />
              Preview
            </Button>
            
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 order-1 sm:order-2"
            >
              {isSubmitting ? 'Saving...' : (tmTag ? 'Update' : 'Save')} T&M Tag
            </Button>
            
            {formData.gcEmail && (
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowEmailComposer(true)}
                className="flex-1 sm:flex-none order-3"
                disabled={!calculatedTotals.total}
              >
                <Mail className="w-4 h-4 mr-2" />
                Send Email
              </Button>
            )}
          </div>
        </form>
      </div>

      {/* Modals */}
      {showSignature && (
        <SignatureCapture
          onComplete={handleSignatureComplete}
          onClose={() => setShowSignature(false)}
          signerName={formData.signerName}
          signerTitle={formData.signerTitle}
        />
      )}

      {showPreview && (
        <PDFGenerator
          formData={formData}
          calculatedTotals={calculatedTotals}
          onClose={() => setShowPreview(false)}
          mode="preview"
        />
      )}

      {showEmailComposer && (
        <EmailComposer
          formData={formData}
          calculatedTotals={calculatedTotals}
          onClose={() => setShowEmailComposer(false)}
          onSent={() => {
            setShowEmailComposer(false);
            toast({
              title: "Email Sent",
              description: "T&M tag has been sent to the General Contractor",
            });
          }}
        />
      )}
    </div>
  );
};

export default TimeAndMaterialForm;