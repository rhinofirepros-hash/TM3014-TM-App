import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Label } from './ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import PDFGenerator from './PDFGenerator';
import { 
  ArrowLeft, 
  FileText, 
  Calendar, 
  DollarSign, 
  Users, 
  Download,
  Search,
  Filter,
  BarChart3,
  X,
  Building,
  Mail,
  Clock,
  User
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { useTheme } from '../contexts/ThemeContext';

const Reports = ({ onBack }) => {
  const [tmTags, setTmTags] = useState([]);
  const [filteredTags, setFilteredTags] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('all');
  const [selectedTag, setSelectedTag] = useState(null);
  const [showTagModal, setShowTagModal] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();

  useEffect(() => {
    // Clear any old mock data from localStorage
    localStorage.removeItem('tm_tags_history');
    localStorage.removeItem('recent_tm_tags');
    loadTMTags();
  }, []);

  const loadTMTags = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      if (backendUrl) {
        // Try to load T&M tags from backend
        const response = await fetch(`${backendUrl}/api/tm-tags?limit=100`);
        if (response.ok) {
          const tmTagsData = await response.json();
          const formattedTags = tmTagsData.map(tag => ({
            id: tag.id,
            project: tag.project_name,
            title: tag.tm_tag_title,
            date: new Date(tag.date_of_work).toISOString().split('T')[0],
            foreman: tag.foreman_name || 'Jesus Garcia',
            totalHours: tag.labor_entries?.reduce((sum, entry) => sum + (entry.total_hours || 0), 0) || 0,
            laborCost: tag.labor_entries?.reduce((sum, entry) => sum + (entry.total_hours || 0) * 95, 0) || 0,
            materialCost: tag.material_entries?.reduce((sum, entry) => sum + (entry.total || 0), 0) || 0,
            status: tag.status || 'completed',
            gcEmail: tag.gc_email,
            costCode: tag.cost_code,
            description: tag.description_of_work,
            companyName: tag.company_name || '',
            submittedAt: tag.submitted_at || tag.created_at
          }));
          setTmTags(formattedTags);
          setFilteredTags(formattedTags);
        } else {
          console.warn('Failed to load T&M tags from backend, using localStorage fallback');
          loadLocalStorageData();
        }
      } else {
        loadLocalStorageData();
      }
    } catch (error) {
      console.warn('Backend connection failed, using localStorage fallback:', error);
      loadLocalStorageData();
    }
  };

  const loadLocalStorageData = () => {
    // Load T&M tags from localStorage (fallback)
    const savedTags = localStorage.getItem('tm_tags_history');
    if (savedTags) {
      const tags = JSON.parse(savedTags);
      setTmTags(tags);
      setFilteredTags(tags);
    } else {
      // No sample data - start clean
      setTmTags([]);
      setFilteredTags([]);
    }
  };

  useEffect(() => {
    // Filter tags based on search term and date filter
    let filtered = tmTags;

    if (searchTerm) {
      filtered = filtered.filter(tag => 
        tag.project.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tag.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tag.foreman.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (dateFilter !== 'all') {
      const now = new Date();
      const filterDate = new Date();
      
      switch (dateFilter) {
        case 'today':
          filterDate.setHours(0, 0, 0, 0);
          filtered = filtered.filter(tag => new Date(tag.date) >= filterDate);
          break;
        case 'week':
          filterDate.setDate(now.getDate() - 7);
          filtered = filtered.filter(tag => new Date(tag.date) >= filterDate);
          break;
        case 'month':
          filterDate.setMonth(now.getMonth() - 1);
          filtered = filtered.filter(tag => new Date(tag.date) >= filterDate);
          break;
        default:
          break;
      }
    }

    setFilteredTags(filtered);
  }, [searchTerm, dateFilter, tmTags]);

  const getTotalStats = () => {
    const total = filteredTags.reduce((acc, tag) => ({
      hours: acc.hours + tag.totalHours,
      laborCost: acc.laborCost + tag.laborCost,
      materialCost: acc.materialCost + tag.materialCost,
      totalCost: acc.totalCost + tag.laborCost + tag.materialCost
    }), { hours: 0, laborCost: 0, materialCost: 0, totalCost: 0 });

    return total;
  };

  const convertTagToPDFFormat = (tag) => {
    // Convert the tag data from Reports format to PDFGenerator expected format
    return {
      projectName: tag.project,
      costCode: tag.costCode || '',
      dateOfWork: new Date(tag.date),
      companyName: tag.companyName || '',
      tmTagTitle: tag.title,
      descriptionOfWork: tag.description || '',
      laborEntries: [],
      materialEntries: [],
      equipmentEntries: [],
      otherEntries: [],
      gcEmail: tag.gcEmail,
      signature: '', // No signature data available in reports view
      signerName: '',
      signerTitle: '',
      foremanName: tag.foreman
    };
  };

  const handleGeneratePDF = async (tag, preview = false) => {
    try {
      const formData = convertTagToPDFFormat(tag);
      const pdfGenerator = PDFGenerator({ formData });
      const result = await pdfGenerator.generatePDF();
      
      if (result.success) {
        if (preview) {
          // Open PDF in new tab for preview
          const newWindow = window.open();
          if (newWindow) {
            newWindow.document.write(`
              <html>
                <head><title>T&M Tag Preview - ${tag.title}</title></head>
                <body style="margin:0; background:#f5f5f5;">
                  <div style="text-align:center; padding:20px;">
                    <h2 style="color:#333;">T&M Tag Preview</h2>
                    <p style="color:#666;">Project: ${tag.project} | Date: ${tag.date}</p>
                  </div>
                  <embed src="${result.pdfData}" type="application/pdf" width="100%" height="90%" />
                </body>
              </html>
            `);
            toast({
              title: "PDF Preview Opened",
              description: "PDF opened in new tab for preview",
            });
          } else {
            toast({
              title: "Popup Blocked",
              description: "Please allow popups to preview the PDF",
              variant: "destructive"
            });
          }
        } else {
          toast({
            title: "PDF Downloaded",
            description: `T&M tag PDF downloaded as ${result.filename}`,
          });
        }
      } else {
        toast({
          title: "PDF Generation Failed",
          description: result.error || "Failed to generate PDF",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error('Error generating PDF:', error);
      toast({
        title: "PDF Generation Failed",
        description: "An error occurred while generating the PDF",
        variant: "destructive"
      });
    }
  };

  const handleViewTag = (tag) => {
    setSelectedTag(tag);
    setShowTagModal(true);
  };

  const handleDeleteTag = async (tagToDelete) => {
    setIsDeleting(true);
    
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      // Try to delete from backend first
      if (backendUrl) {
        try {
          const response = await fetch(`${backendUrl}/api/tm-tags/${tagToDelete.id}`, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            }
          });
          
          if (!response.ok) {
            console.warn('Failed to delete from backend, continuing with local deletion');
          }
        } catch (backendError) {
          console.warn('Backend deletion failed, continuing with local deletion:', backendError);
        }
      }
      
      // Remove from local state
      const updatedTags = tmTags.filter(tag => tag.id !== tagToDelete.id);
      setTmTags(updatedTags);
      setFilteredTags(updatedTags.filter(tag => {
        const matchesSearch = !searchTerm || (
          tag.project.toLowerCase().includes(searchTerm.toLowerCase()) ||
          tag.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          tag.foreman.toLowerCase().includes(searchTerm.toLowerCase())
        );
        return matchesSearch;
      }));
      
      // Update localStorage as fallback
      const savedTags = JSON.parse(localStorage.getItem('tm_tags_history') || '[]');
      const updatedSavedTags = savedTags.filter(tag => tag.id !== tagToDelete.id);
      localStorage.setItem('tm_tags_history', JSON.stringify(updatedSavedTags));
      
      // Close modals and show success message
      setShowDeleteDialog(false);
      setShowTagModal(false);
      
      toast({
        title: "T&M Tag Deleted",
        description: `"${tagToDelete.title}" has been permanently deleted.`,
      });
      
    } catch (error) {
      console.error('Error deleting T&M tag:', error);
      toast({
        title: "Delete Failed",
        description: "Failed to delete T&M tag. Please try again.",
        variant: "destructive"
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const handleExportData = () => {
    const dataStr = JSON.stringify(filteredTags, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tm_tags_report_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    toast({
      title: "Export Complete",
      description: "T&M tags report has been downloaded.",
    });
  };

  const handleExportAllPDFs = async () => {
    if (filteredTags.length === 0) {
      toast({
        title: "No Data to Export",
        description: "There are no T&M tags to export.",
        variant: "destructive"
      });
      return;
    }

    toast({
      title: "Generating PDFs",
      description: `Starting bulk export of ${filteredTags.length} T&M tag PDFs...`,
    });

    let successCount = 0;
    let errorCount = 0;

    for (const tag of filteredTags) {
      try {
        const formData = convertTagToPDFFormat(tag);
        const pdfGenerator = PDFGenerator({ formData });
        const result = await pdfGenerator.generatePDF();
        
        if (result.success) {
          successCount++;
        } else {
          errorCount++;
        }
        
        // Small delay to prevent overwhelming the browser
        await new Promise(resolve => setTimeout(resolve, 100));
      } catch (error) {
        console.error('Error generating PDF for tag:', tag.id, error);
        errorCount++;
      }
    }

    toast({
      title: "Bulk Export Complete",
      description: `Successfully generated ${successCount} PDFs. ${errorCount > 0 ? `${errorCount} failed.` : ''}`,
      variant: errorCount > 0 ? "destructive" : "default"
    });
  };

  const stats = getTotalStats();

  return (
    <>
    <div className={`min-h-screen transition-all duration-300 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100'
    }`}>
      {/* Header */}
      <div className={`${isDarkMode ? 'backdrop-blur-xl bg-white/10 border-b border-white/20' : 'backdrop-blur-xl bg-white/30 border-b border-white/40'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={onBack} className={`flex items-center gap-2 ${themeClasses.button.secondary}`}>
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </Button>
              <div className="flex items-center space-x-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isDarkMode ? 'bg-blue-600' : 'bg-blue-600'}`}>
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className={`text-xl font-semibold ${themeClasses.text.primary}`}>T&M Reports</h1>
                  <p className={`text-sm ${themeClasses.text.secondary}`}>View and analyze T&M tag history</p>
                </div>
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleExportData} variant="outline" className={`flex items-center gap-2 ${themeClasses.button.secondary}`}>
                <Download className="w-4 h-4" />
                Export JSON
              </Button>
              <Button onClick={handleExportAllPDFs} className={`flex items-center gap-2 ${themeClasses.button.primary}`}>
                <FileText className="w-4 h-4" />
                Export All PDFs
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className={`${
            isDarkMode 
              ? 'backdrop-blur-xl border-0 shadow-2xl bg-white/10 text-white border border-white/20' 
              : 'backdrop-blur-xl border-0 shadow-2xl bg-white/40 text-gray-900 border border-white/30'
          } shadow-xl`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Total T&M Tags</p>
                  <p className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>{filteredTags.length}</p>
                </div>
                <FileText className={`w-8 h-8 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
              </div>
            </CardContent>
          </Card>
          
          <Card className={`${
            isDarkMode 
              ? 'backdrop-blur-xl border-0 shadow-2xl bg-white/10 text-white border border-white/20' 
              : 'backdrop-blur-xl border-0 shadow-2xl bg-white/40 text-gray-900 border border-white/30'
          } shadow-xl`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Total Hours</p>
                  <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>{stats.hours}</p>
                </div>
                <Users className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card className={`${
            isDarkMode 
              ? 'backdrop-blur-xl border-0 shadow-2xl bg-white/10 text-white border border-white/20' 
              : 'backdrop-blur-xl border-0 shadow-2xl bg-white/40 text-gray-900 border border-white/30'
          } shadow-xl`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Labor Cost</p>
                  <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>${stats.laborCost.toLocaleString()}</p>
                </div>
                <DollarSign className={`w-8 h-8 ${isDarkMode ? 'text-purple-400' : 'text-purple-600'}`} />
              </div>
            </CardContent>
          </Card>
          
          <Card className={`${
            isDarkMode 
              ? 'backdrop-blur-xl border-0 shadow-2xl bg-white/10 text-white border border-white/20' 
              : 'backdrop-blur-xl border-0 shadow-2xl bg-white/40 text-gray-900 border border-white/30'
          } shadow-xl`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>Total Cost</p>
                  <p className={`text-2xl font-bold ${themeClasses.text.primary}`}>${stats.totalCost.toLocaleString()}</p>
                </div>
                <BarChart3 className={`w-8 h-8 ${isDarkMode ? 'text-red-400' : 'text-red-600'}`} />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className={`${
          isDarkMode 
            ? 'backdrop-blur-xl border-0 shadow-2xl bg-white/10 text-white border border-white/20' 
            : 'backdrop-blur-xl border-0 shadow-2xl bg-white/40 text-gray-900 border border-white/30'
        } mb-6`}>
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="Search by project, title, or foreman..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className={`pl-10 ${themeClasses.input}`}
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <select
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  className={`px-3 py-2 border rounded-md text-sm ${themeClasses.input}`}
                >
                  <option value="all">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">Last 7 Days</option>
                  <option value="month">Last 30 Days</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* T&M Tags Table */}
        <Card className={`${
          isDarkMode 
            ? 'backdrop-blur-xl border-0 shadow-2xl bg-white/10 text-white border border-white/20' 
            : 'backdrop-blur-xl border-0 shadow-2xl bg-white/40 text-gray-900 border border-white/30'
        }`}>
          <CardHeader>
            <CardTitle className={isDarkMode ? 'text-white' : 'text-gray-900'}>T&M Tag History</CardTitle>
          </CardHeader>
          <CardContent>
            {filteredTags.length === 0 ? (
              <div className="text-center py-12">
                <FileText className={`w-12 h-12 mx-auto mb-4 ${themeClasses.text.muted}`} />
                <h3 className={`text-lg font-medium mb-2 ${themeClasses.text.primary}`}>No T&M tags found</h3>
                <p className={`mb-4 ${themeClasses.text.secondary}`}>
                  {searchTerm || dateFilter !== 'all' 
                    ? 'Try adjusting your search filters'
                    : 'Create your first T&M tag to see reports here'
                  }
                </p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Project</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Foreman</TableHead>
                    <TableHead>Hours</TableHead>
                    <TableHead>Labor Cost</TableHead>
                    <TableHead>Material Cost</TableHead>
                    <TableHead>Total</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>GC Email</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTags.map((tag) => (
                    <TableRow 
                      key={tag.id} 
                      className={`cursor-pointer transition-colors ${
                        isDarkMode 
                          ? 'hover:bg-white/10' 
                          : 'hover:bg-gray-50'
                      }`}
                      onClick={() => handleViewTag(tag)}
                    >
                      <TableCell>{new Date(tag.date).toLocaleDateString()}</TableCell>
                      <TableCell className="font-medium">{tag.project}</TableCell>
                      <TableCell>{tag.title}</TableCell>
                      <TableCell>{tag.foreman}</TableCell>
                      <TableCell>{tag.totalHours} hrs</TableCell>
                      <TableCell>${tag.laborCost.toLocaleString()}</TableCell>
                      <TableCell>${tag.materialCost.toLocaleString()}</TableCell>
                      <TableCell className="font-medium">
                        ${(tag.laborCost + tag.materialCost).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Badge variant={tag.status === 'completed' ? 'default' : 'secondary'}>
                          {tag.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-gray-600">{tag.gcEmail}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>

    {/* T&M Tag Details Modal - Responsive Version */}
    <Dialog open={showTagModal} onOpenChange={setShowTagModal}>
      <DialogContent className={`sm:max-w-[900px] max-w-[95vw] max-h-[90vh] overflow-y-auto ${themeClasses.modal}`}>
        <DialogHeader className={`border-b pb-4 ${isDarkMode ? 'border-white/20' : 'border-gray-200/50'}`}>
          <DialogTitle className={`flex items-center justify-between text-xl ${themeClasses.text.primary}`}>
            <div className="flex items-center gap-3">
              <FileText className={`w-6 h-6 ${isDarkMode ? 'text-blue-400' : 'text-blue-600'}`} />
              <span>T&M Tag Review</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowTagModal(false)}
              className={`h-8 w-8 p-0 ${themeClasses.button.ghost}`}
            >
              <X className="h-5 w-5" />
            </Button>
          </DialogTitle>
        </DialogHeader>

        {selectedTag && (
          <div className="space-y-4 sm:space-y-6 py-4">
            {/* Main Header Card */}
            <div className={`p-4 sm:p-6 rounded-lg border ${isDarkMode ? 'bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-white/20' : 'bg-gradient-to-r from-blue-50/80 to-purple-50/80 border-gray-200/50'}`}>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                <div>
                  <Label className={`text-sm font-medium ${themeClasses.text.secondary}`}>Project Name</Label>
                  <p className={`font-bold text-base sm:text-lg ${themeClasses.text.primary}`}>{selectedTag.project}</p>
                </div>
                <div>
                  <Label className={`text-sm font-medium ${themeClasses.text.secondary}`}>Date of Work</Label>
                  <p className={`font-semibold text-sm sm:text-base ${themeClasses.text.primary}`}>{new Date(selectedTag.date).toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Status</Label>
                  <div className="flex items-center gap-2">
                    <Badge variant={selectedTag.status === 'completed' ? 'default' : 'secondary'} className="text-sm">
                      {selectedTag.status?.toUpperCase()}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>

            {/* T&M Tag Title & Description */}
            <div className="space-y-4">
              <div>
                <Label className={`text-base font-semibold ${themeClasses.text.secondary}`}>T&M Tag Title</Label>
                <p className={`text-xl font-bold mt-1 ${themeClasses.text.primary}`}>{selectedTag.title}</p>
              </div>

              {selectedTag.description && (
                <div>
                  <Label className={`text-base font-semibold ${themeClasses.text.secondary}`}>Description of Work</Label>
                  <div className={`mt-2 p-4 rounded-lg border ${
                    isDarkMode 
                      ? 'bg-white/5 border-white/20' 
                      : 'bg-gray-50 border-gray-200'
                  }`}>
                    <p className={`leading-relaxed ${themeClasses.text.primary}`}>{selectedTag.description}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Project & Contact Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className={`space-y-4 p-4 rounded-lg border ${
                isDarkMode 
                  ? 'bg-white/5 border-white/20' 
                  : 'bg-white border-gray-200'
              }`}>
                <h3 className={`font-semibold flex items-center gap-2 ${themeClasses.text.primary}`}>
                  <Building className="w-5 h-5 text-blue-600" />
                  Project Information
                </h3>
                <div className="space-y-3">
                  <div>
                    <Label className={`text-sm font-medium ${themeClasses.text.secondary}`}>Company Name</Label>
                    <p className={`font-medium ${themeClasses.text.primary}`}>{selectedTag.companyName || 'Not specified'}</p>
                  </div>
                  <div>
                    <Label className={`text-sm font-medium ${themeClasses.text.secondary}`}>Cost Code</Label>
                    <p className={`font-medium ${themeClasses.text.primary}`}>{selectedTag.costCode || 'Not specified'}</p>
                  </div>
                  <div>
                    <Label className={`text-sm font-medium ${themeClasses.text.secondary}`}>Foreman</Label>
                    <p className={`font-medium ${themeClasses.text.primary}`}>{selectedTag.foreman}</p>
                  </div>
                </div>
              </div>

              <div className={`space-y-4 p-4 rounded-lg border ${
                isDarkMode 
                  ? 'bg-white/5 border-white/20' 
                  : 'bg-white border-gray-200'
              }`}>
                <h3 className={`font-semibold flex items-center gap-2 ${themeClasses.text.primary}`}>
                  <Mail className="w-5 h-5 text-green-600" />
                  Contact Information
                </h3>
                <div className="space-y-3">
                  <div>
                    <Label className={`text-sm font-medium ${themeClasses.text.secondary}`}>GC Email</Label>
                    <p className={`font-medium ${themeClasses.text.primary}`}>{selectedTag.gcEmail || 'Not provided'}</p>
                  </div>
                  <div>
                    <Label className={`text-sm font-medium ${themeClasses.text.secondary}`}>Submitted</Label>
                    <p className={`text-sm ${themeClasses.text.secondary}`}>
                      {selectedTag.submittedAt ? new Date(selectedTag.submittedAt).toLocaleString() : 'Not available'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Cost Summary - Larger Cards */}
            <div className="space-y-4">
              <h3 className={`font-semibold flex items-center gap-2 ${themeClasses.text.primary}`}>
                <DollarSign className="w-5 h-5 text-green-600" />
                Cost Summary
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className={`text-center p-6 rounded-lg border ${
                  isDarkMode 
                    ? 'bg-blue-900/30 border-blue-500/30' 
                    : 'bg-blue-50 border-blue-200'
                }`}>
                  <Clock className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                  <div className="text-3xl font-bold text-blue-600">{selectedTag.totalHours}</div>
                  <div className="text-sm font-medium text-blue-700">Total Hours</div>
                </div>
                <div className={`text-center p-6 rounded-lg border ${
                  isDarkMode 
                    ? 'bg-green-900/30 border-green-500/30' 
                    : 'bg-green-50 border-green-200'
                }`}>
                  <User className="w-8 h-8 text-green-600 mx-auto mb-2" />
                  <div className="text-3xl font-bold text-green-600">${selectedTag.laborCost?.toLocaleString() || 0}</div>
                  <div className="text-sm font-medium text-green-700">Labor Cost</div>
                </div>
                <div className={`text-center p-6 rounded-lg border ${
                  isDarkMode 
                    ? 'bg-purple-900/30 border-purple-500/30' 
                    : 'bg-purple-50 border-purple-200'
                }`}>
                  <Building className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                  <div className="text-3xl font-bold text-purple-600">${selectedTag.materialCost?.toLocaleString() || 0}</div>
                  <div className="text-sm font-medium text-purple-700">Material Cost</div>
                </div>
                <div className={`text-center p-6 rounded-lg border ${
                  isDarkMode 
                    ? 'bg-gray-800 text-white border-gray-600' 
                    : 'bg-gray-900 text-white border-gray-700'
                }`}>
                  <DollarSign className="w-8 h-8 text-white mx-auto mb-2" />
                  <div className="text-3xl font-bold">${((selectedTag.laborCost || 0) + (selectedTag.materialCost || 0)).toLocaleString()}</div>
                  <div className="text-sm font-medium text-gray-300">Total Cost</div>
                </div>
              </div>
            </div>

            {/* Additional Details */}
            {(selectedTag.equipmentCost || selectedTag.otherCost) && (
              <div className="space-y-4">
                <h3 className={`font-semibold ${themeClasses.text.primary}`}>Additional Costs</h3>
                <div className="grid grid-cols-2 gap-4">
                  {selectedTag.equipmentCost && (
                    <div className={`text-center p-4 rounded-lg border ${
                      isDarkMode 
                        ? 'bg-orange-900/30 border-orange-500/30' 
                        : 'bg-orange-50 border-orange-200'
                    }`}>
                      <div className="text-2xl font-bold text-orange-600">${selectedTag.equipmentCost.toLocaleString()}</div>
                      <div className="text-sm text-orange-700">Equipment</div>
                    </div>
                  )}
                  {selectedTag.otherCost && (
                    <div className={`text-center p-4 rounded-lg border ${
                      isDarkMode 
                        ? 'bg-yellow-900/30 border-yellow-500/30' 
                        : 'bg-yellow-50 border-yellow-200'
                    }`}>
                      <div className="text-2xl font-bold text-yellow-600">${selectedTag.otherCost.toLocaleString()}</div>
                      <div className="text-sm text-yellow-700">Other</div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        <DialogFooter className={`border-t pt-4 mt-6 ${isDarkMode ? 'border-white/20' : 'border-gray-200'}`}>
          <div className="flex justify-between w-full">
            <div className="flex gap-3">
              <Button variant="outline" size="lg" onClick={() => setShowTagModal(false)} className={themeClasses.button.secondary}>
                <X className="w-4 h-4 mr-2" />
                Close
              </Button>
              <Button 
                variant="outline"
                size="lg"
                onClick={() => setShowDeleteDialog(true)}
                className={`text-red-600 border-red-600 hover:bg-red-50 ${isDarkMode ? 'hover:bg-red-900/20' : 'hover:bg-red-50'}`}
              >
                <X className="w-4 h-4 mr-2" />
                Delete Tag
              </Button>
            </div>
            <div className="flex gap-3">
              <Button 
                variant="outline"
                size="lg"
                onClick={() => {
                  toast({
                    title: "Edit Feature",
                    description: "T&M tag editing coming soon!",
                  });
                }}
                className={themeClasses.button.secondary}
              >
                <FileText className="w-4 h-4 mr-2" />
                Edit Tag
              </Button>
              <Button 
                variant="outline"
                size="lg"
                onClick={() => selectedTag && handleGeneratePDF(selectedTag, true)}
                className={`${themeClasses.button.primary}`}
              >
                <FileText className="w-4 h-4 mr-2" />
                Preview PDF
              </Button>
              <Button 
                size="lg"
                onClick={() => selectedTag && handleGeneratePDF(selectedTag, false)}
                className={`${themeClasses.button.primary}`}
              >
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </Button>
            </div>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>

    {/* Delete Confirmation Dialog */}
    <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-red-600">
            <X className="w-5 h-5" />
            Delete T&M Tag
          </DialogTitle>
        </DialogHeader>
        
        <div className="py-4">
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 font-medium">⚠️ This action cannot be undone!</p>
          </div>
          
          {selectedTag && (
            <div className="space-y-3">
              <p className="text-gray-700">
                Are you sure you want to permanently delete this T&M tag?
              </p>
              
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="font-semibold text-gray-900">{selectedTag.title}</p>
                <p className="text-sm text-gray-600">
                  Project: {selectedTag.project} • Date: {new Date(selectedTag.date).toLocaleDateString()}
                </p>
                <p className="text-sm text-gray-600">
                  Total Cost: ${((selectedTag.laborCost || 0) + (selectedTag.materialCost || 0)).toLocaleString()}
                </p>
              </div>
              
              <p className="text-sm text-gray-600">
                This will remove the T&M tag from all reports and cannot be recovered.
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button 
            variant="outline" 
            onClick={() => setShowDeleteDialog(false)}
            disabled={isDeleting}
          >
            Cancel
          </Button>
          <Button 
            variant="destructive" 
            onClick={() => selectedTag && handleDeleteTag(selectedTag)}
            disabled={isDeleting}
            className="bg-red-600 hover:bg-red-700"
          >
            {isDeleting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                Deleting...
              </>
            ) : (
              <>
                <X className="w-4 h-4 mr-2" />
                Delete Permanently
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    </>
  );
};

export default Reports;