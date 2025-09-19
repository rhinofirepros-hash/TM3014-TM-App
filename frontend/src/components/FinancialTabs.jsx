import React, { useState, useEffect } from 'react';
import { AnimatedCard, CardContent, CardHeader, CardTitle } from './ui/animated-card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { 
  DollarSign, 
  FileText, 
  Calculator, 
  TrendingUp,
  PlusCircle,
  Edit,
  Trash2,
  Download,
  Filter,
  Search,
  ArrowLeft
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useToast } from '../hooks/use-toast';

const FinancialTabs = ({ project, onBack }) => {
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  const { toast } = useToast();
  
  const [activeTab, setActiveTab] = useState('invoices');
  const [loading, setLoading] = useState(true);
  
  // Financial data states
  const [invoices, setInvoices] = useState([]);
  const [payables, setPayables] = useState([]);
  const [cashflowData, setCashflowData] = useState(null);
  const [profitabilityData, setProfitabilityData] = useState(null);

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);

  useEffect(() => {
    fetchFinancialData();
  }, [project.id]);

  const fetchFinancialData = async () => {
    try {
      setLoading(true);
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      // Fetch all financial data concurrently
      const [invoicesRes, payablesRes, cashflowRes, profitabilityRes] = await Promise.all([
        fetch(`${backendUrl}/api/invoices?projectId=${project.id}`),
        fetch(`${backendUrl}/api/payables?projectId=${project.id}`),
        fetch(`${backendUrl}/api/cashflow?projectId=${project.id}`),
        fetch(`${backendUrl}/api/profitability?projectId=${project.id}`)
      ]);
      
      // Process responses
      if (invoicesRes.ok) {
        const invoicesData = await invoicesRes.json();
        setInvoices(invoicesData);
      } else {
        console.error('Invoices API error:', invoicesRes.status, await invoicesRes.text());
        setInvoices([]); // Set empty array on error
      }
      
      if (payablesRes.ok) {
        const payablesData = await payablesRes.json();
        setPayables(payablesData);
      } else {
        console.error('Payables API error:', payablesRes.status, await payablesRes.text());
        setPayables([]); // Set empty array on error
      }
      
      if (cashflowRes.ok) {
        const cashflowResData = await cashflowRes.json();
        setCashflowData(cashflowResData);
      } else {
        console.error('Cashflow API error:', cashflowRes.status, await cashflowRes.text());
        setCashflowData(null);
      }
      
      if (profitabilityRes.ok) {
        const profitabilityResData = await profitabilityRes.json();
        setProfitabilityData(profitabilityResData);
      } else {
        console.error('Profitability API error:', profitabilityRes.status, await profitabilityRes.text());
        setProfitabilityData(null);
      }

    } catch (error) {
      console.error('Error fetching financial data:', error);
      toast({
        title: "Error",
        description: "Failed to load financial data",
        variant: "destructive"
      });
      // Set default empty states
      setInvoices([]);
      setPayables([]);
      setCashflowData(null);
      setProfitabilityData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateItem = async (itemData) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const endpoint = activeTab === 'invoices' ? 'invoices' : 'payables';
      
      const response = await fetch(`${backendUrl}/api/${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...itemData,
          projectId: project.id
        })
      });

      if (response.ok) {
        const newItem = await response.json();
        
        if (activeTab === 'invoices') {
          setInvoices([...invoices, newItem]);
        } else {
          setPayables([...payables, newItem]);
        }
        
        setShowCreateModal(false);
        toast({
          title: "Success",
          description: `${activeTab.slice(0, -1)} created successfully`
        });
      } else {
        throw new Error(`Failed to create ${activeTab.slice(0, -1)}`);
      }
    } catch (error) {
      console.error('Error creating item:', error);
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const handleDeleteItem = async (itemId) => {
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const endpoint = activeTab === 'invoices' ? 'invoices' : 'payables';
      
      const response = await fetch(`${backendUrl}/api/${endpoint}/${itemId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        if (activeTab === 'invoices') {
          setInvoices(invoices.filter(item => item.id !== itemId));
        } else {
          setPayables(payables.filter(item => item.id !== itemId));
        }
        
        toast({
          title: "Success",
          description: `${activeTab.slice(0, -1)} deleted successfully`
        });
      } else {
        throw new Error(`Failed to delete ${activeTab.slice(0, -1)}`);
      }
    } catch (error) {
      console.error('Error deleting item:', error);
      toast({
        title: "Error",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const tabs = [
    { id: 'invoices', label: 'Invoices', icon: FileText, data: invoices },
    { id: 'payables', label: 'Payables', icon: Calculator, data: payables },
    { id: 'cashflow', label: 'Cashflow', icon: TrendingUp, data: cashflowData },
    { id: 'profitability', label: 'Profitability', icon: DollarSign, data: profitabilityData }
  ];

  const renderTabContent = () => {
    if (loading) {
      return (
        <div className="flex items-center justify-center py-12">
          <div className={`text-center ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            Loading financial data...
          </div>
        </div>
      );
    }

    const currentTab = tabs.find(tab => tab.id === activeTab);
    
    switch (activeTab) {
      case 'invoices':
        return <InvoicesTab invoices={invoices} onDelete={handleDeleteItem} />;
      case 'payables':
        return <PayablesTab payables={payables} onDelete={handleDeleteItem} />;
      case 'cashflow':
        return <CashflowTab data={cashflowData} />;
      case 'profitability':
        return <ProfitabilityTab data={profitabilityData} />;
      default:
        return <div>Select a tab</div>;
    }
  };

  const InvoicesTab = ({ invoices, onDelete }) => (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className={`text-xl md:text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          Project Invoices
        </h2>
        <Button 
          onClick={() => setShowCreateModal(true)}
          className="w-full sm:w-auto"
        >
          <PlusCircle className="w-4 h-4 mr-2" />
          Create Invoice
        </Button>
      </div>

      {invoices.length === 0 ? (
        <div className={`text-center py-12 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg md:text-xl">No invoices found</p>
          <p className="text-sm md:text-base">Create your first invoice to get started</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className={`w-full rounded-lg overflow-hidden ${
            isDarkMode ? 'bg-slate-800' : 'bg-white'
          }`}>
            <thead className={isDarkMode ? 'bg-slate-700' : 'bg-gray-50'}>
              <tr>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Invoice #</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Status</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Total</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Due Date</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {invoices.map((invoice) => (
                <tr key={invoice.id} className={isDarkMode ? 'hover:bg-slate-700/50' : 'hover:bg-gray-50'}>
                  <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    {invoice.invoiceNumber || `INV-${invoice.id.slice(-6)}`}
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={invoice.status === 'paid' ? 'default' : 'secondary'}>
                      {invoice.status || 'pending'}
                    </Badge>
                  </td>
                  <td className={`px-4 py-3 text-sm font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    ${(invoice.total || 0).toLocaleString()}
                  </td>
                  <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    {invoice.dueDate ? new Date(invoice.dueDate).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setEditingItem(invoice)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onDelete(invoice.id)}
                        className="text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const PayablesTab = ({ payables, onDelete }) => (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h2 className={`text-xl md:text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
          Accounts Payable
        </h2>
        <Button 
          onClick={() => setShowCreateModal(true)}
          className="w-full sm:w-auto"
        >
          <PlusCircle className="w-4 h-4 mr-2" />
          Add Payable
        </Button>
      </div>

      {payables.length === 0 ? (
        <div className={`text-center py-12 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          <Calculator className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg md:text-xl">No payables found</p>
          <p className="text-sm md:text-base">Add your first payable to get started</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className={`w-full rounded-lg overflow-hidden ${
            isDarkMode ? 'bg-slate-800' : 'bg-white'
          }`}>
            <thead className={isDarkMode ? 'bg-slate-700' : 'bg-gray-50'}>
              <tr>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Vendor</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Description</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Amount</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Due Date</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Status</th>
                <th className={`px-4 py-3 text-left text-sm font-medium ${
                  isDarkMode ? 'text-gray-300' : 'text-gray-700'
                }`}>Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {payables.map((payable) => (
                <tr key={payable.id} className={isDarkMode ? 'hover:bg-slate-700/50' : 'hover:bg-gray-50'}>
                  <td className={`px-4 py-3 text-sm font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    {payable.vendor}
                  </td>
                  <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    {payable.description}
                  </td>
                  <td className={`px-4 py-3 text-sm font-medium ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                    ${(payable.amount || 0).toLocaleString()}
                  </td>
                  <td className={`px-4 py-3 text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    {payable.dueDate ? new Date(payable.dueDate).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant={payable.status === 'paid' ? 'default' : 'secondary'}>
                      {payable.status || 'pending'}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setEditingItem(payable)}
                      >
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onDelete(payable.id)}
                        className="text-red-600 hover:bg-red-50"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const CashflowTab = ({ data }) => (
    <div className="space-y-6">
      <h2 className={`text-xl md:text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
        Project Cashflow
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <AnimatedCard className={isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-200'}>
          <CardHeader className="pb-2">
            <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              Total Inflow
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold text-green-600`}>
              ${data?.totalInflow || 0}
            </div>
          </CardContent>
        </AnimatedCard>

        <AnimatedCard className={isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-200'}>
          <CardHeader className="pb-2">
            <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              Total Outflow
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold text-red-600`}>
              ${data?.totalOutflow || 0}
            </div>
          </CardContent>
        </AnimatedCard>

        <AnimatedCard className={isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-200'}>
          <CardHeader className="pb-2">
            <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              Net Cashflow
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              (data?.netCashflow || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              ${data?.netCashflow || 0}
            </div>
          </CardContent>
        </AnimatedCard>
      </div>

      {!data && (
        <div className={`text-center py-12 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          <TrendingUp className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg md:text-xl">No cashflow data available</p>
          <p className="text-sm md:text-base">Cashflow analysis will appear here once you have invoices and payables</p>
        </div>
      )}
    </div>
  );

  const ProfitabilityTab = ({ data }) => (
    <div className="space-y-6">
      <h2 className={`text-xl md:text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
        Project Profitability
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <AnimatedCard className={isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-200'}>
          <CardHeader className="pb-2">
            <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              Total Revenue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              ${data?.totalRevenue || 0}
            </div>
          </CardContent>
        </AnimatedCard>

        <AnimatedCard className={isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-200'}>
          <CardHeader className="pb-2">
            <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              Total Costs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              ${data?.totalCosts || 0}
            </div>
          </CardContent>
        </AnimatedCard>

        <AnimatedCard className={isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-200'}>
          <CardHeader className="pb-2">
            <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              Gross Profit
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-xl font-bold ${
              (data?.grossProfit || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              ${data?.grossProfit || 0}
            </div>
          </CardContent>
        </AnimatedCard>

        <AnimatedCard className={isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-gray-200'}>
          <CardHeader className="pb-2">
            <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              Profit Margin
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-xl font-bold ${
              (data?.profitMargin || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {data?.profitMargin || 0}%
            </div>
          </CardContent>
        </AnimatedCard>
      </div>

      {!data && (
        <div className={`text-center py-12 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          <DollarSign className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg md:text-xl">No profitability data available</p>
          <p className="text-sm md:text-base">Profitability analysis will appear here once you have financial data</p>
        </div>
      )}
    </div>
  );

  return (
    <div className={`min-h-screen transition-all duration-300 ${
      isDarkMode 
        ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 md:py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6 md:mb-8">
          <div className="flex items-center gap-4">
            <Button 
              variant="outline" 
              onClick={onBack}
              className={`${isDarkMode ? 'border-slate-600 text-gray-300 hover:bg-slate-800' : 'border-gray-300'}`}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Project
            </Button>
            <div>
              <h1 className={`text-xl md:text-2xl lg:text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                Financial Management
              </h1>
              <p className={`text-sm md:text-base ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                {project.name}
              </p>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className={`p-4 md:p-6 rounded-xl mb-6 ${
          isDarkMode ? 'bg-slate-800/50 border border-slate-700' : 'bg-white border border-gray-200'
        }`}>
          <h3 className={`text-lg font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
            System Status:
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className={isDarkMode ? 'text-gray-300' : 'text-gray-600'}>
              Invoices: {invoices.length} records
            </div>
            <div className={isDarkMode ? 'text-gray-300' : 'text-gray-600'}>
              Payables: {payables.length} records
            </div>
            <div className={isDarkMode ? 'text-gray-300' : 'text-gray-600'}>
              Cashflow: {cashflowData ? '1' : '0'} records
            </div>
            <div className={isDarkMode ? 'text-gray-300' : 'text-gray-600'}>
              Profitability: {profitabilityData ? '1' : '0'} records
            </div>
          </div>
          <div className={`text-xs mt-2 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            Project ID: {project.id}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-6 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-colors ${
                  isActive
                    ? isDarkMode
                      ? 'bg-blue-600 text-white'
                      : 'bg-blue-600 text-white'
                    : isDarkMode
                      ? 'bg-slate-800 text-gray-300 hover:bg-slate-700'
                      : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className={`rounded-xl ${
          isDarkMode ? 'bg-slate-800/30 border border-slate-700' : 'bg-white/70 border border-gray-200'
        } p-4 md:p-6`}>
          {renderTabContent()}
        </div>
      </div>

      {/* Create Modal would go here */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className={`max-w-md w-full rounded-lg ${
            isDarkMode ? 'bg-slate-800 border border-slate-700' : 'bg-white border border-gray-200'
          } p-6`}>
            <h3 className={`text-lg font-semibold mb-4 ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
              Create {activeTab.slice(0, -1)}
            </h3>
            <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'} mb-4`}>
              Create form for {activeTab} would be implemented here.
            </p>
            <div className="flex gap-2">
              <Button onClick={() => setShowCreateModal(false)} variant="outline" className="flex-1">
                Cancel
              </Button>
              <Button onClick={() => setShowCreateModal(false)} className="flex-1">
                Create
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FinancialTabs;