import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
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
  X
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const Reports = ({ onBack }) => {
  const [tmTags, setTmTags] = useState([]);
  const [filteredTags, setFilteredTags] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFilter, setDateFilter] = useState('all');
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

  const handleViewTag = (tag) => {
    // Show detailed view of the T&M tag
    toast({
      title: "T&M Tag Details",
      description: `${tag.project} - ${tag.title} (${tag.totalHours} hrs)`,
    });
    
    // You could implement a modal here to show full details
    console.log('Viewing T&M tag:', tag);
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

  const stats = getTotalStats();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={onBack} className="flex items-center gap-2">
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </Button>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">T&M Reports</h1>
                  <p className="text-sm text-gray-500">View and analyze T&M tag history</p>
                </div>
              </div>
            </div>
            <Button onClick={handleExportData} className="flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export Data
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total T&M Tags</p>
                  <p className="text-2xl font-bold text-gray-900">{filteredTags.length}</p>
                </div>
                <FileText className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Hours</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.hours}</p>
                </div>
                <Users className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Labor Cost</p>
                  <p className="text-2xl font-bold text-gray-900">${stats.laborCost.toLocaleString()}</p>
                </div>
                <DollarSign className="w-8 h-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Cost</p>
                  <p className="text-2xl font-bold text-gray-900">${stats.totalCost.toLocaleString()}</p>
                </div>
                <BarChart3 className="w-8 h-8 text-red-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    placeholder="Search by project, title, or foreman..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <select
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md text-sm"
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
        <Card>
          <CardHeader>
            <CardTitle>T&M Tag History</CardTitle>
          </CardHeader>
          <CardContent>
            {filteredTags.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No T&M tags found</h3>
                <p className="text-gray-500 mb-4">
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
                      className="cursor-pointer hover:bg-gray-50"
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
  );
};

export default Reports;