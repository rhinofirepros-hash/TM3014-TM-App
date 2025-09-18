import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from './ui/dialog';
import { Calendar } from './ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Badge } from './ui/badge';
import { format } from 'date-fns';
import { 
  ArrowLeft, 
  Plus, 
  Package, 
  Calendar as CalendarIcon,
  DollarSign,
  TrendingUp,
  Edit,
  Trash2,
  Receipt,
  Building,
  Filter,
  Upload,
  Eye
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../hooks/use-toast';
import { cn } from '../lib/utils';

const MaterialTracking = ({ project, onBack }) => {
  const [materials, setMaterials] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedMaterial, setSelectedMaterial] = useState(null);
  const [filterCategory, setFilterCategory] = useState('');
  const [filterVendor, setFilterVendor] = useState('');
  const [newMaterial, setNewMaterial] = useState({
    purchase_date: new Date(),
    vendor: '',
    material_name: '',
    quantity: '',
    unit_cost: '',
    total_cost: '',
    invoice_number: '',
    receipt_image: '',
    category: 'general'
  });
  
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();

  const materialCategories = [
    { value: 'general', label: 'General' },
    { value: 'pipe', label: 'Pipe & Tubing' },
    { value: 'fittings', label: 'Fittings' },
    { value: 'valves', label: 'Valves' },
    { value: 'equipment', label: 'Equipment' },
    { value: 'electrical', label: 'Electrical' },
    { value: 'safety', label: 'Safety Equipment' },
    { value: 'consumables', label: 'Consumables' },
    { value: 'tools', label: 'Tools' }
  ];

  useEffect(() => {
    loadMaterials();
  }, [project]);

  const loadMaterials = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (backendUrl && project) {
        const response = await fetch(`${backendUrl}/api/materials?project_id=${project.id}`);
        if (response.ok) {
          const materialsData = await response.json();
          setMaterials(materialsData);
        }
      }
    } catch (error) {
      console.warn('Failed to load materials:', error);
    }
  };

  const handleCreateMaterial = async () => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl) {
        toast({
          title: "Backend Error",
          description: "Backend URL not configured",
          variant: "destructive"
        });
        return;
      }

      const materialData = {
        project_id: project.id,
        project_name: project.name,
        purchase_date: newMaterial.purchase_date.toISOString(),
        vendor: newMaterial.vendor,
        material_name: newMaterial.material_name,
        quantity: parseFloat(newMaterial.quantity) || 0,
        unit_cost: parseFloat(newMaterial.unit_cost) || 0,
        total_cost: parseFloat(newMaterial.total_cost) || 0,
        invoice_number: newMaterial.invoice_number,
        receipt_image: newMaterial.receipt_image,
        category: newMaterial.category
      };

      const response = await fetch(`${backendUrl}/api/materials`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(materialData)
      });

      if (response.ok) {
        const createdMaterial = await response.json();
        setMaterials(prev => [createdMaterial, ...prev]);
        setShowCreateModal(false);
        resetNewMaterial();
        
        toast({
          title: "Material Added",
          description: `${createdMaterial.material_name} has been added to the project.`,
        });
      } else {
        throw new Error('Failed to create material entry');
      }
    } catch (error) {
      toast({
        title: "Creation Failed",
        description: "Failed to add material. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleDeleteMaterial = async (materialId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      if (!backendUrl) return;

      const response = await fetch(`${backendUrl}/api/materials/${materialId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setMaterials(prev => prev.filter(material => material.id !== materialId));
        toast({
          title: "Material Deleted",
          description: "Material entry has been deleted successfully.",
        });
      }
    } catch (error) {
      toast({
        title: "Deletion Failed",
        description: "Failed to delete material entry.",
        variant: "destructive"
      });
    }
  };

  const resetNewMaterial = () => {
    setNewMaterial({
      purchase_date: new Date(),
      vendor: '',
      material_name: '',
      quantity: '',
      unit_cost: '',
      total_cost: '',
      invoice_number: '',
      receipt_image: '',
      category: 'general'
    });
  };

  const handleInputChange = (field, value) => {
    setNewMaterial(prev => {
      const updated = { ...prev, [field]: value };
      
      // Auto-calculate total cost when quantity or unit cost changes
      if (field === 'quantity' || field === 'unit_cost') {
        const quantity = parseFloat(field === 'quantity' ? value : updated.quantity) || 0;
        const unitCost = parseFloat(field === 'unit_cost' ? value : updated.unit_cost) || 0;
        updated.total_cost = (quantity * unitCost).toFixed(2);
      }
      
      return updated;
    });
  };

  const handleReceiptUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        toast({
          title: "File Too Large",
          description: "Please select a file smaller than 5MB.",
          variant: "destructive"
        });
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        handleInputChange('receipt_image', e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const getUniqueVendors = () => {
    return [...new Set(materials.map(m => m.vendor).filter(Boolean))];
  };

  const getCategoryLabel = (category) => {
    const cat = materialCategories.find(c => c.value === category);
    return cat ? cat.label : category;
  };

  const getCategoryColor = (category) => {
    const colors = {
      general: 'bg-gray-100 text-gray-800',
      pipe: 'bg-blue-100 text-blue-800',
      fittings: 'bg-green-100 text-green-800',
      valves: 'bg-purple-100 text-purple-800',
      equipment: 'bg-orange-100 text-orange-800',
      electrical: 'bg-yellow-100 text-yellow-800',
      safety: 'bg-red-100 text-red-800',
      consumables: 'bg-pink-100 text-pink-800',
      tools: 'bg-indigo-100 text-indigo-800'
    };
    return colors[category] || colors.general;
  };

  const filteredMaterials = materials.filter(material => {
    const matchesCategory = filterCategory === '' || filterCategory === 'all' || material.category === filterCategory;
    const matchesVendor = filterVendor === '' || filterVendor === 'all' || material.vendor === filterVendor;
    return matchesCategory && matchesVendor;
  });

  const totalMaterialCost = filteredMaterials.reduce((sum, material) => sum + (material.total_cost || 0), 0);

  return (
    <>
      <div className={`min-h-screen transition-all duration-300 ${themeClasses.background}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-4">
              <Button 
                variant="outline" 
                onClick={onBack}
                className={`flex items-center gap-2 ${themeClasses.button.secondary}`}
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Project
              </Button>
              <div>
                <h1 className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                  Material Tracking
                </h1>
                <p className={themeClasses.text.secondary}>
                  {project.name} - Track material purchases and costs
                </p>
              </div>
            </div>
            
            <Button 
              onClick={() => setShowCreateModal(true)}
              className={themeClasses.button.primary}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Material Purchase
            </Button>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Total Purchases
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {filteredMaterials.length}
                    </p>
                  </div>
                  <Package className="w-8 h-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Total Cost
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      ${totalMaterialCost.toLocaleString()}
                    </p>
                  </div>
                  <DollarSign className="w-8 h-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Unique Vendors
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      {getUniqueVendors().length}
                    </p>
                  </div>
                  <Building className="w-8 h-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>

            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className={`text-sm font-medium ${themeClasses.text.secondary}`}>
                      Avg Purchase
                    </p>
                    <p className={`text-3xl font-bold ${themeClasses.text.primary}`}>
                      ${filteredMaterials.length > 0 
                        ? (totalMaterialCost / filteredMaterials.length).toLocaleString()
                        : '0'
                      }
                    </p>
                  </div>
                  <TrendingUp className="w-8 h-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <div className="mb-6">
            <div className="flex gap-4 items-center flex-wrap">
              <div className="flex items-center gap-2">
                <Filter className={`w-4 h-4 ${themeClasses.text.secondary}`} />
                <Label className={themeClasses.text.secondary}>Filters:</Label>
              </div>
              
              <Select value={filterCategory} onValueChange={setFilterCategory}>
                <SelectTrigger className={`w-48 ${themeClasses.input}`}>
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  <SelectItem value="all">All Categories</SelectItem>
                  {materialCategories.map((category) => (
                    <SelectItem key={category.value} value={category.value}>
                      {category.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select value={filterVendor} onValueChange={setFilterVendor}>
                <SelectTrigger className={`w-48 ${themeClasses.input}`}>
                  <SelectValue placeholder="All Vendors" />
                </SelectTrigger>
                <SelectContent className={themeClasses.modal}>
                  <SelectItem value="all">All Vendors</SelectItem>
                  {getUniqueVendors().map((vendor) => (
                    <SelectItem key={vendor} value={vendor}>
                      {vendor}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {(filterCategory || filterVendor) && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    setFilterCategory('');
                    setFilterVendor('');
                  }}
                  className={themeClasses.button.secondary}
                >
                  Clear Filters
                </Button>
              )}
            </div>
          </div>

          {/* Materials Table */}
          {filteredMaterials.length === 0 ? (
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardContent className="p-12 text-center">
                <Package className={`w-16 h-16 mx-auto mb-4 ${themeClasses.text.muted}`} />
                <h3 className={`text-lg font-medium mb-2 ${themeClasses.text.primary}`}>
                  {materials.length === 0 ? 'No Material Purchases Yet' : 'No Materials Match Filters'}
                </h3>
                <p className={`mb-6 ${themeClasses.text.secondary}`}>
                  {materials.length === 0 
                    ? 'Start tracking material purchases for this project.'
                    : 'Try adjusting your filter criteria.'
                  }
                </p>
                <Button 
                  onClick={() => setShowCreateModal(true)}
                  className={themeClasses.button.primary}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add First Material
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Card className={`${themeClasses.card} shadow-xl`}>
              <CardHeader>
                <CardTitle className={themeClasses.text.primary}>
                  Material Purchases ({filteredMaterials.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                        <TableHead className={themeClasses.text.primary}>Date</TableHead>
                        <TableHead className={themeClasses.text.primary}>Material</TableHead>
                        <TableHead className={themeClasses.text.primary}>Vendor</TableHead>
                        <TableHead className={themeClasses.text.primary}>Category</TableHead>
                        <TableHead className={themeClasses.text.primary}>Quantity</TableHead>
                        <TableHead className={themeClasses.text.primary}>Unit Cost</TableHead>
                        <TableHead className={themeClasses.text.primary}>Total Cost</TableHead>
                        <TableHead className={themeClasses.text.primary}>Invoice</TableHead>
                        <TableHead className={themeClasses.text.primary}>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredMaterials.map((material) => (
                        <TableRow key={material.id} className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                          <TableCell className={themeClasses.text.primary}>
                            {format(new Date(material.purchase_date), 'MM/dd/yyyy')}
                          </TableCell>
                          <TableCell className={`font-medium ${themeClasses.text.primary}`}>
                            {material.material_name}
                          </TableCell>
                          <TableCell className={themeClasses.text.primary}>
                            {material.vendor}
                          </TableCell>
                          <TableCell>
                            <Badge className={getCategoryColor(material.category)}>
                              {getCategoryLabel(material.category)}
                            </Badge>
                          </TableCell>
                          <TableCell className={themeClasses.text.primary}>
                            {material.quantity}
                          </TableCell>
                          <TableCell className={themeClasses.text.primary}>
                            ${material.unit_cost.toFixed(2)}
                          </TableCell>
                          <TableCell className={`font-semibold ${themeClasses.text.primary}`}>
                            ${material.total_cost.toLocaleString()}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              {material.invoice_number && (
                                <Badge variant="outline" className="text-xs">
                                  {material.invoice_number}
                                </Badge>
                              )}
                              {material.receipt_image && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => setSelectedMaterial(material)}
                                  className="p-1"
                                >
                                  <Receipt className="w-4 h-4" />
                                </Button>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  // TODO: Implement edit functionality
                                  toast({
                                    title: "Edit Feature",
                                    description: "Edit functionality coming soon!",
                                  });
                                }}
                                className={themeClasses.button.secondary}
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDeleteMaterial(material.id)}
                                className="text-red-600 hover:bg-red-50"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Create Material Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className={`sm:max-w-[600px] ${themeClasses.modal}`}>
          <DialogHeader>
            <DialogTitle className={themeClasses.text.primary}>Add Material Purchase</DialogTitle>
          </DialogHeader>
          
          <div className="grid gap-4 py-4 max-h-96 overflow-y-auto">
            {/* Purchase Date and Category */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Purchase Date*</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        `w-full justify-start text-left font-normal ${themeClasses.button.secondary}`,
                        !newMaterial.purchase_date && "text-muted-foreground"
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {newMaterial.purchase_date ? format(newMaterial.purchase_date, "MM/dd/yyyy") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className={`w-auto p-0 ${themeClasses.modal}`} align="start">
                    <Calendar
                      mode="single"
                      selected={newMaterial.purchase_date}
                      onSelect={(date) => handleInputChange('purchase_date', date)}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Category*</Label>
                <Select value={newMaterial.category} onValueChange={(value) => handleInputChange('category', value)}>
                  <SelectTrigger className={themeClasses.input}>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className={themeClasses.modal}>
                    {materialCategories.map((category) => (
                      <SelectItem key={category.value} value={category.value}>
                        {category.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Material Name and Vendor */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Material Name*</Label>
                <Input
                  value={newMaterial.material_name}
                  onChange={(e) => handleInputChange('material_name', e.target.value)}
                  className={themeClasses.input}
                  placeholder="e.g., 3/4 inch Copper Pipe"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Vendor*</Label>
                <Input
                  value={newMaterial.vendor}
                  onChange={(e) => handleInputChange('vendor', e.target.value)}
                  className={themeClasses.input}
                  placeholder="e.g., ABC Supply Co"
                />
              </div>
            </div>

            {/* Quantity, Unit Cost, Total Cost */}
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Quantity*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newMaterial.quantity}
                  onChange={(e) => handleInputChange('quantity', e.target.value)}
                  className={themeClasses.input}
                  placeholder="100"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Unit Cost ($)*</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newMaterial.unit_cost}
                  onChange={(e) => handleInputChange('unit_cost', e.target.value)}
                  className={themeClasses.input}
                  placeholder="5.50"
                />
              </div>
              
              <div className="space-y-2">
                <Label className={themeClasses.text.primary}>Total Cost ($)</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={newMaterial.total_cost}
                  onChange={(e) => handleInputChange('total_cost', e.target.value)}
                  className={`${themeClasses.input} bg-gray-50`}
                  placeholder="Auto-calculated"
                  readOnly
                />
              </div>
            </div>

            {/* Invoice Number */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Invoice Number</Label>
              <Input
                value={newMaterial.invoice_number}
                onChange={(e) => handleInputChange('invoice_number', e.target.value)}
                className={themeClasses.input}
                placeholder="INV-12345"
              />
            </div>

            {/* Receipt Upload */}
            <div className="space-y-2">
              <Label className={themeClasses.text.primary}>Receipt Image</Label>
              <div className="flex items-center gap-4">
                <Input
                  type="file"
                  accept="image/*"
                  onChange={handleReceiptUpload}
                  className={themeClasses.input}
                />
                {newMaterial.receipt_image && (
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      // Open image in new tab
                      window.open(newMaterial.receipt_image, '_blank');
                    }}
                    className={themeClasses.button.secondary}
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    Preview
                  </Button>
                )}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setShowCreateModal(false);
                resetNewMaterial();
              }}
              className={themeClasses.button.secondary}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleCreateMaterial}
              disabled={!newMaterial.material_name || !newMaterial.vendor || !newMaterial.quantity || !newMaterial.unit_cost}
              className={themeClasses.button.primary}
            >
              Add Material
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Receipt View Modal */}
      {selectedMaterial && selectedMaterial.receipt_image && (
        <Dialog open={!!selectedMaterial} onOpenChange={() => setSelectedMaterial(null)}>
          <DialogContent className={`sm:max-w-[800px] ${themeClasses.modal}`}>
            <DialogHeader>
              <DialogTitle className={themeClasses.text.primary}>
                Receipt - {selectedMaterial.material_name}
              </DialogTitle>
            </DialogHeader>
            
            <div className="flex justify-center p-4">
              <img 
                src={selectedMaterial.receipt_image} 
                alt="Receipt" 
                className="max-w-full max-h-96 object-contain rounded-lg border"
              />
            </div>

            <DialogFooter>
              <Button 
                onClick={() => setSelectedMaterial(null)}
                className={themeClasses.button.secondary}
              >
                Close
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </>
  );
};

export default MaterialTracking;