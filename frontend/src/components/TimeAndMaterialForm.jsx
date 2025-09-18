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
import { CalendarIcon, Plus, Trash2, Info, Download, Eye, PenTool, Mail, FileText } from 'lucide-react';
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

const TimeAndMaterialForm = ({ selectedProject, onBackToDashboard }) => {
  const { toast } = useToast();
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const [formData, setFormData] = useState({
    projectName: selectedProject?.name || "",
    costCode: '',
    dateOfWork: new Date(),
    companyName: '',
    tmTagTitle: '',
    descriptionOfWork: '',
    laborEntries: [],
    materialEntries: [],
    equipmentEntries: [],
    otherEntries: [],
    gcEmail: '',
    autoEmail: false, // Changed from true to false
    downloadPDF: true,
    signature: null,
    signerName: '',
    signerTitle: 'Foreman'
  });
  
  const [showSignatureModal, setShowSignatureModal] = useState(false);
  const [showEmailComposer, setShowEmailComposer] = useState(false);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [generatedPDFData, setGeneratedPDFData] = useState(null);
  const [isCustomProject, setIsCustomProject] = useState(false);
  const [customProjectName, setCustomProjectName] = useState('');
  const [savedProjects, setSavedProjects] = useState(() => {
    const saved = localStorage.getItem('saved_projects');
    return saved ? JSON.parse(saved) : [];
  });

  const [savedCompanies, setSavedCompanies] = useState(() => {
    const saved = localStorage.getItem('saved_companies');
    return saved ? JSON.parse(saved) : [];
  });

  const [isCustomCompany, setIsCustomCompany] = useState(false);
  const [customCompanyName, setCustomCompanyName] = useState('');

  const [savedEmails, setSavedEmails] = useState(() => {
    const saved = localStorage.getItem('saved_emails');
    return saved ? JSON.parse(saved) : [];
  });

  const [isCustomEmail, setIsCustomEmail] = useState(false);
  const [customEmail, setCustomEmail] = useState('');
  
  const [savedWorkers, setSavedWorkers] = useState(() => {
    const saved = localStorage.getItem('saved_workers');
    return saved ? JSON.parse(saved) : [
      { id: 1, name: "Jesus Garcia", rate: 95 },
      { id: 2, name: "Mike Rodriguez", rate: 95 },
      { id: 3, name: "Sarah Johnson", rate: 85 }
    ];
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

  const handleSignatureSave = (signatureData, signerName, signerTitle) => {
    setFormData(prev => ({
      ...prev,
      signature: signatureData,
      signerName: signerName || prev.signerName,
      signerTitle: signerTitle || prev.signerTitle
    }));
    
    toast({
      title: "Signature Captured",
      description: `Signature saved for ${signerName || 'signer'}`,
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

  const handleSubmitForm = async () => {
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
      // Save to backend database
      try {
        const tmTagData = {
          project_name: formData.projectName,
          cost_code: formData.costCode,
          date_of_work: formData.dateOfWork.toISOString(),
          company_name: formData.companyName,
          tm_tag_title: formData.tmTagTitle,
          description_of_work: formData.descriptionOfWork,
          labor_entries: formData.laborEntries.map(entry => ({
            id: entry.id.toString(),
            worker_name: entry.workerName,
            quantity: parseFloat(entry.quantity) || 1,
            st_hours: parseFloat(entry.stHours) || 0,
            ot_hours: parseFloat(entry.otHours) || 0,
            dt_hours: parseFloat(entry.dtHours) || 0,
            pot_hours: parseFloat(entry.potHours) || 0,
            total_hours: parseFloat(entry.totalHours) || 0,
            date: entry.date
          })),
          material_entries: formData.materialEntries.map(entry => ({
            id: entry.id.toString(),
            material_name: entry.materialName,
            unit_of_measure: entry.unitOfMeasure,
            quantity: parseFloat(entry.quantity) || 0,
            unit_cost: parseFloat(entry.unitCost) || 0,
            total: parseFloat(entry.total) || 0,
            date_of_work: entry.dateOfWork
          })),
          equipment_entries: formData.equipmentEntries.map(entry => ({
            id: entry.id.toString(),
            equipment_name: entry.equipmentName,
            pieces_of_equipment: parseInt(entry.piecesOfEquipment) || 1,
            unit_of_measure: entry.unitOfMeasure,
            quantity: parseFloat(entry.quantity) || 0,
            total: parseFloat(entry.total) || 0,
            date_of_work: entry.dateOfWork
          })),
          other_entries: formData.otherEntries.map(entry => ({
            id: entry.id.toString(),
            other_name: entry.otherName,
            quantity_of_other: parseInt(entry.quantityOfOther) || 1,
            unit_of_measure: entry.unitOfMeasure,
            quantity_of_unit: parseFloat(entry.quantityOfUnit) || 0,
            total: parseFloat(entry.total) || 0,
            date_of_work: entry.dateOfWork
          })),
          gc_email: formData.gcEmail,
          signature: formData.signature,
          foreman_name: formData.signerName || 'Jesus Garcia',
          submitted_at: new Date().toISOString()
        };

        // Save to backend API
        const backendUrl = process.env.REACT_APP_BACKEND_URL;
        if (backendUrl) {
          const response = await fetch(`${backendUrl}/api/tm-tags`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(tmTagData)
          });
          
          if (response.ok) {
            console.log('✅ T&M Tag saved to backend successfully');
            toast({
              title: "T&M Tag Submitted",
              description: "Your T&M tag has been saved successfully to the database.",
            });
          } else {
            console.warn('Backend save failed, using localStorage fallback');
            toast({
              title: "Warning",
              description: "Backend save failed, but tag was saved locally.",
              variant: "destructive"
            });
          }
        }
      } catch (backendError) {
        console.warn('Backend save failed:', backendError);
        toast({
          title: "Warning", 
          description: "Backend connection failed, but tag was saved locally.",
          variant: "destructive"
        });
      }
      
      // Also save to localStorage as backup
      const tmTag = {
        id: Date.now(),
        project: formData.projectName,
        title: formData.tmTagTitle,
        date: formData.dateOfWork.toISOString().split('T')[0],
        foreman: formData.signerName || 'Jesus Garcia',
        totalHours: formData.laborEntries.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0), 0),
        laborCost: formData.laborEntries.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0) * 95, 0),
        materialCost: formData.materialEntries.reduce((sum, entry) => sum + (parseFloat(entry.total) || 0), 0),
        status: 'completed',
        gcEmail: formData.gcEmail,
        costCode: formData.costCode,
        description: formData.descriptionOfWork,
        submittedAt: new Date().toISOString()
      };
      
      const existingHistory = JSON.parse(localStorage.getItem('tm_tags_history') || '[]');
      existingHistory.unshift(tmTag);
      localStorage.setItem('tm_tags_history', JSON.stringify(existingHistory));
      
      // Clear the draft after successful submission
      localStorage.removeItem('tm_tag_draft');
      
      // Reset form and go back to dashboard
      resetForm();
      if (onBackToDashboard) {
        onBackToDashboard();
      }
      
    } catch (error) {
      console.error('Submit error:', error);
      toast({
        title: "Submission Failed",
        description: "An error occurred while submitting the T&M tag.",
        variant: "destructive"
      });
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  const resetForm = () => {
    setFormData({
      projectName: selectedProject?.name || "",
      costCode: '',
      dateOfWork: new Date(),
      companyName: '',
      tmTagTitle: '',
      descriptionOfWork: '',
      laborEntries: [],
      materialEntries: [],
      equipmentEntries: [],
      otherEntries: [],
      gcEmail: '',
      autoEmail: false, // Changed from true to false
      downloadPDF: true,
      signature: null,
      signerName: '',
      signerTitle: 'Foreman'
    });
    setIsCustomProject(false);
    setCustomProjectName('');
    setIsCustomCompany(false);
    setCustomCompanyName('');
    setIsCustomEmail(false);
    setCustomEmail('');
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
        // Store PDF data for email composer
        setGeneratedPDFData(result.pdfData);
        
        // Save to backend database
        try {
          const tmTagData = {
            project_name: formData.projectName,
            cost_code: formData.costCode,
            date_of_work: formData.dateOfWork.toISOString(),
            company_name: formData.companyName,
            tm_tag_title: formData.tmTagTitle,
            description_of_work: formData.descriptionOfWork,
            labor_entries: formData.laborEntries.map(entry => ({
              id: entry.id.toString(),
              worker_name: entry.workerName,
              quantity: parseFloat(entry.quantity) || 1,
              st_hours: parseFloat(entry.stHours) || 0,
              ot_hours: parseFloat(entry.otHours) || 0,
              dt_hours: parseFloat(entry.dtHours) || 0,
              pot_hours: parseFloat(entry.potHours) || 0,
              total_hours: parseFloat(entry.totalHours) || 0,
              date: entry.date
            })),
            material_entries: formData.materialEntries.map(entry => ({
              id: entry.id.toString(),
              material_name: entry.materialName,
              unit_of_measure: entry.unitOfMeasure,
              quantity: parseFloat(entry.quantity) || 0,
              unit_cost: parseFloat(entry.unitCost) || 0,
              total: parseFloat(entry.total) || 0,
              date_of_work: entry.dateOfWork
            })),
            equipment_entries: formData.equipmentEntries.map(entry => ({
              id: entry.id.toString(),
              equipment_name: entry.equipmentName,
              pieces_of_equipment: parseInt(entry.piecesOfEquipment) || 1,
              unit_of_measure: entry.unitOfMeasure,
              quantity: parseFloat(entry.quantity) || 0,
              total: parseFloat(entry.total) || 0,
              date_of_work: entry.dateOfWork
            })),
            other_entries: formData.otherEntries.map(entry => ({
              id: entry.id.toString(),
              other_name: entry.otherName,
              quantity_of_other: parseInt(entry.quantityOfOther) || 1,
              unit_of_measure: entry.unitOfMeasure,
              quantity_of_unit: parseFloat(entry.quantityOfUnit) || 0,
              total: parseFloat(entry.total) || 0,
              date_of_work: entry.dateOfWork
            })),
            gc_email: formData.gcEmail,
            signature: formData.signature
          };

          // Save to backend API
          const backendUrl = process.env.REACT_APP_BACKEND_URL;
          if (backendUrl) {
            const response = await fetch(`${backendUrl}/api/tm-tags`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(tmTagData)
            });
            
            if (response.ok) {
              console.log('T&M Tag saved to backend successfully');
            } else {
              console.warn('Backend save failed, using localStorage fallback');
            }
          }
        } catch (backendError) {
          console.warn('Backend save failed:', backendError);
        }
        
        // Fallback: Save to localStorage (always works)
        const tmTag = {
          id: Date.now(),
          project: formData.projectName,
          title: formData.tmTagTitle,
          date: formData.dateOfWork.toISOString().split('T')[0],
          foreman: formData.laborEntries.length > 0 ? formData.laborEntries[0].workerName : 'Unknown',
          totalHours: formData.laborEntries.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0), 0),
          laborCost: formData.laborEntries.reduce((sum, entry) => sum + (parseFloat(entry.totalHours) || 0) * 95, 0),
          materialCost: formData.materialEntries.reduce((sum, entry) => sum + (parseFloat(entry.total) || 0), 0),
          status: 'completed',
          gcEmail: formData.gcEmail,
          costCode: formData.costCode,
          description: formData.descriptionOfWork,
          submittedAt: new Date().toISOString()
        };
        
        const existingHistory = JSON.parse(localStorage.getItem('tm_tags_history') || '[]');
        existingHistory.unshift(tmTag);
        localStorage.setItem('tm_tags_history', JSON.stringify(existingHistory));
        
        // Open email composer if auto-email is enabled
        if (formData.autoEmail) {
          setShowEmailComposer(true);
        } else {
          toast({
            title: "T&M Tag Generated",
            description: `PDF generated: ${result.filename}`,
          });
        }
        
        // Handle download
        if (formData.downloadPDF) {
          // PDF is already downloaded by jsPDF
        }
        
        // Clear form after successful submission
        setFormData({
          projectName: "",
          costCode: '',
          dateOfWork: new Date(),
          companyName: '',
          tmTagTitle: '',
          descriptionOfWork: '',
          laborEntries: [],
          materialEntries: [],
          equipmentEntries: [],
          otherEntries: [],
          gcEmail: '',
          autoEmail: false, // Changed from true to false
          downloadPDF: true,
          signature: null,
          signerName: '',
          signerTitle: 'Foreman'
        });
        setIsCustomProject(false);
        setCustomProjectName('');
        setIsCustomCompany(false);
        setCustomCompanyName('');
        setIsCustomEmail(false);
        setCustomEmail('');
        
        // Redirect back to dashboard after successful submission
        setTimeout(() => {
          onBackToDashboard();
        }, 2000); // Give user time to see success message
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

  const handleSaveCustomCompany = () => {
    if (!customCompanyName.trim()) {
      toast({
        title: "Company Name Required",
        description: "Please enter a company name.",
        variant: "destructive"
      });
      return;
    }

    // Check if company already exists
    const existingCompany = savedCompanies.find(c => 
      c.name.toLowerCase() === customCompanyName.trim().toLowerCase()
    );
    
    if (existingCompany) {
      setFormData(prev => ({ ...prev, companyName: existingCompany.name }));
      setCustomCompanyName('');
      setIsCustomCompany(false);
      toast({
        title: "Company Selected",
        description: `"${existingCompany.name}" selected from saved companies.`,
      });
      return;
    }

    const newCompany = {
      id: Date.now(),
      name: customCompanyName.trim()
    };

    const updatedCompanies = [...savedCompanies, newCompany];
    setSavedCompanies(updatedCompanies);
    localStorage.setItem('saved_companies', JSON.stringify(updatedCompanies));
    
    setFormData(prev => ({ ...prev, companyName: newCompany.name }));
    setCustomCompanyName('');
    setIsCustomCompany(false);
    
    toast({
      title: "Company Saved",
      description: `"${newCompany.name}" has been added to your company list.`,
    });
  };

  const handleSaveCustomEmail = () => {
    if (!customEmail.trim()) {
      toast({
        title: "Email Required",
        description: "Please enter an email address.",
        variant: "destructive"
      });
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(customEmail.trim())) {
      toast({
        title: "Invalid Email",
        description: "Please enter a valid email address.",
        variant: "destructive"
      });
      return;
    }

    // Check if email already exists
    const existingEmail = savedEmails.find(e => 
      e.email.toLowerCase() === customEmail.trim().toLowerCase()
    );
    
    if (existingEmail) {
      setFormData(prev => ({ ...prev, gcEmail: existingEmail.email }));
      setCustomEmail('');
      setIsCustomEmail(false);
      toast({
        title: "Email Selected",
        description: `"${existingEmail.email}" selected from saved emails.`,
      });
      return;
    }

    const newEmail = {
      id: Date.now(),
      email: customEmail.trim().toLowerCase(),
      name: customEmail.trim().split('@')[0] // Use part before @ as name
    };

    const updatedEmails = [...savedEmails, newEmail];
    setSavedEmails(updatedEmails);
    localStorage.setItem('saved_emails', JSON.stringify(updatedEmails));
    
    setFormData(prev => ({ ...prev, gcEmail: newEmail.email }));
    setCustomEmail('');
    setIsCustomEmail(false);
    
    toast({
      title: "Email Saved",
      description: `"${newEmail.email}" has been added to your email list.`,
    });
  };

  const handleSaveWorker = (workerName) => {
    if (!workerName.trim()) return;
    
    const existingWorker = savedWorkers.find(w => w.name.toLowerCase() === workerName.toLowerCase());
    if (existingWorker) return; // Worker already exists
    
    const newWorker = {
      id: Date.now(),
      name: workerName.trim(),
      rate: 95 // Default rate
    };
    
    const updatedWorkers = [...savedWorkers, newWorker];
    setSavedWorkers(updatedWorkers);
    localStorage.setItem('saved_workers', JSON.stringify(updatedWorkers));
    
    toast({
      title: "Worker Saved",
      description: `"${newWorker.name}" has been added to your worker list.`,
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-2 sm:p-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-4 sm:mb-6">
          <div className="flex items-center gap-4">
            <Button 
              variant="outline" 
              onClick={onBackToDashboard}
              className="flex items-center gap-2"
            >
              ← Dashboard
            </Button>
            <h1 className="text-lg sm:text-2xl font-semibold text-gray-900">
              Create A Time & Material Tag
            </h1>
          </div>
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

            {/* Company Name */}
            <div className="space-y-2">
              <Label className="text-sm font-medium text-gray-700 flex items-center justify-between">
                Company Name
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setIsCustomCompany(!isCustomCompany)}
                  className="text-xs h-6 px-2"
                >
                  {isCustomCompany ? 'Cancel' : 'Add New'}
                </Button>
              </Label>
              
              {isCustomCompany ? (
                <div className="flex gap-2">
                  <Input
                    value={customCompanyName}
                    onChange={(e) => setCustomCompanyName(e.target.value)}
                    placeholder="Enter new company name (e.g., ABC Construction)"
                    className="flex-1"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleSaveCustomCompany();
                      }
                    }}
                  />
                  <Button
                    type="button"
                    onClick={handleSaveCustomCompany}
                    size="sm"
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    Save
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  {savedCompanies.length > 0 ? (
                    <Select 
                      value={formData.companyName} 
                      onValueChange={(value) => handleInputChange('companyName', value)}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select a company or add new" />
                      </SelectTrigger>
                      <SelectContent>
                        {savedCompanies.map((company) => (
                          <SelectItem key={company.id} value={company.name}>
                            {company.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      value={formData.companyName}
                      onChange={(e) => handleInputChange('companyName', e.target.value)}
                      placeholder="Enter company name (e.g., ABC Construction)"
                      className="w-full"
                    />
                  )}
                  <p className="text-xs text-gray-500">
                    {savedCompanies.length > 0 
                      ? `${savedCompanies.length} saved companies available`
                      : 'Start typing to create your first company'
                    }
                  </p>
                </div>
              )}
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
                      const newEntry = {
                        id: Date.now(),
                        workerName: '',
                        quantity: 1,
                        stHours: 8.00,
                        otHours: 0,
                        dtHours: 0,
                        potHours: 0,
                        totalHours: 8.00,
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
                onSaveWorker={handleSaveWorker}
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

            {/* GC Email and Delivery Options */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">General Contractor Delivery</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-gray-700 flex items-center justify-between">
                    GC Email Address*
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setIsCustomEmail(!isCustomEmail)}
                      className="text-xs h-6 px-2"
                    >
                      {isCustomEmail ? 'Cancel' : 'Add New'}
                    </Button>
                  </Label>
                  
                  {isCustomEmail ? (
                    <div className="flex gap-2">
                      <Input
                        value={customEmail}
                        onChange={(e) => setCustomEmail(e.target.value)}
                        placeholder="Enter new GC email address"
                        type="email"
                        className="flex-1"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handleSaveCustomEmail();
                          }
                        }}
                      />
                      <Button
                        type="button"
                        onClick={handleSaveCustomEmail}
                        size="sm"
                        className="bg-green-600 hover:bg-green-700 text-white"
                      >
                        Save
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {savedEmails.length > 0 ? (
                        <Select 
                          value={formData.gcEmail} 
                          onValueChange={(value) => handleInputChange('gcEmail', value)}
                        >
                          <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select a GC email or add new" />
                          </SelectTrigger>
                          <SelectContent>
                            {savedEmails.map((email) => (
                              <SelectItem key={email.id} value={email.email}>
                                {email.email}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      ) : (
                        <Input
                          value={formData.gcEmail}
                          onChange={(e) => handleInputChange('gcEmail', e.target.value)}
                          placeholder="Enter GC email address"
                          type="email"
                          className="w-full"
                        />
                      )}
                      <p className="text-xs text-gray-500">
                        {savedEmails.length > 0 
                          ? `${savedEmails.length} saved emails available • PDF will be emailed to this address`
                          : 'PDF will be automatically emailed to this address'
                        }
                      </p>
                    </div>
                  )}
                </div>
                
                <div className="space-y-2">
                  <Label className="text-sm font-medium text-gray-700">
                    Delivery Options
                  </Label>
                  <div className="flex flex-col gap-2">
                    <label className="flex items-center space-x-2">
                      <input 
                        type="checkbox" 
                        checked={formData.autoEmail !== false}
                        onChange={(e) => handleInputChange('autoEmail', e.target.checked)}
                        className="rounded border-gray-300"
                      />
                      <span className="text-sm text-gray-700">Auto-email to GC</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input 
                        type="checkbox" 
                        checked={formData.downloadPDF !== false}
                        onChange={(e) => handleInputChange('downloadPDF', e.target.checked)}
                        className="rounded border-gray-300"
                      />
                      <span className="text-sm text-gray-700">Download PDF copy</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {/* Signature Status */}
            {formData.signature && (
              <div className="bg-green-50 border border-green-200 rounded-md p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 text-green-700 mb-2">
                      <PenTool className="w-4 h-4" />
                      <span className="font-medium">Signature Collected</span>
                    </div>
                    <div className="text-sm text-gray-700">
                      <p><strong>Name:</strong> {formData.signerName}</p>
                      <p><strong>Title:</strong> {formData.signerTitle}</p>
                      <p className="text-green-600 mt-1">Ready to generate final PDF and submit</p>
                    </div>
                  </div>
                  <div className="ml-4">
                    <div className="border border-gray-300 rounded bg-white p-2">
                      <img 
                        src={formData.signature} 
                        alt="Digital Signature" 
                        className="max-w-[120px] max-h-[60px] object-contain"
                      />
                    </div>
                    <p className="text-xs text-gray-500 text-center mt-1">Digital Signature</p>
                  </div>
                </div>
                <div className="flex gap-2 mt-3">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setFormData(prev => ({
                        ...prev,
                        signature: null,
                        signerName: '',
                        signerTitle: 'Foreman'
                      }));
                      toast({
                        title: "Signature Cleared",
                        description: "You can now collect a new signature.",
                      });
                    }}
                    className="text-red-600 hover:text-red-700"
                  >
                    Clear Signature
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCollectSignatures}
                  >
                    Update Signature
                  </Button>
                </div>
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
                      projectName: "",
                      costCode: '',
                      dateOfWork: new Date(),
                      companyName: '',
                      tmTagTitle: '',
                      descriptionOfWork: '',
                      laborEntries: [],
                      materialEntries: [],
                      equipmentEntries: [],
                      otherEntries: [],
                      gcEmail: '',
                      autoEmail: false, // Changed from true to false
                      downloadPDF: true,
                      signature: null,
                      signerName: '',
                      signerTitle: 'Foreman'
                    });
                    setIsCustomProject(false);
                    setCustomProjectName('');
                    setIsCustomCompany(false);
                    setCustomCompanyName('');
                    setIsCustomEmail(false);
                    setCustomEmail('');
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
                  <div className="flex flex-col sm:flex-row gap-2">
                    <Button 
                      onClick={handleSubmitForm}
                      disabled={isGeneratingPDF}
                      className="bg-green-600 hover:bg-green-700 text-white flex items-center justify-center gap-2 h-10"
                    >
                      <FileText className="w-4 h-4" />
                      <span className="hidden sm:inline">{isGeneratingPDF ? 'Submitting...' : 'Submit T&M Tag'}</span>
                      <span className="sm:hidden">{isGeneratingPDF ? 'Submitting...' : 'Submit'}</span>
                    </Button>
                    <Button 
                      onClick={() => setShowEmailComposer(true)}
                      disabled={isGeneratingPDF || !generatedPDFData}
                      className="bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center gap-2 h-10"
                    >
                      <Mail className="w-4 h-4" />
                      <span className="hidden sm:inline">Email GC</span>
                      <span className="sm:hidden">Email</span>
                    </Button>
                    <Button 
                      onClick={handleSubmitAndEmail}
                      disabled={isGeneratingPDF}
                      className="bg-purple-600 hover:bg-purple-700 text-white flex items-center justify-center gap-2 h-10"
                    >
                      <Download className="w-4 h-4" />
                      <span className="hidden sm:inline">{isGeneratingPDF ? 'Generating...' : 'Generate PDF'}</span>
                      <span className="sm:hidden">{isGeneratingPDF ? 'Generating...' : 'PDF'}</span>
                    </Button>
                  </div>
                )}
              </div>
            </div>

            {/* Signature Modal */}
            <SignatureCapture
              isOpen={showSignatureModal}
              onClose={() => setShowSignatureModal(false)}
              onSave={handleSignatureSave}
            />

            {/* Email Composer Modal */}
            <EmailComposer
              isOpen={showEmailComposer}
              onClose={() => setShowEmailComposer(false)}
              formData={formData}
              pdfData={generatedPDFData}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TimeAndMaterialForm;