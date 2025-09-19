import React, { useState, useEffect } from 'react';
import { AnimatedCard, AnimatedCardContent } from './ui/animated-card';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from './ui/table';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Plus, 
  Edit, 
  Trash2, 
  TrendingUp, 
  TrendingDown,
  AlertCircle,
  DollarSign,
  Receipt,
  CreditCard,
  BarChart3
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const FinancialTabs = ({ project, onBack }) => {
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  
  // State for each financial module
  const [invoices, setInvoices] = useState([]);
  const [payables, setPayables] = useState([]);
  const [cashflowData, setCashflowData] = useState([]);
  const [profitabilityData, setProfitabilityData] = useState([]);
  const [inspections, setInspections] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('invoices');

  const projectId = project?.id;

  useEffect(() => {
    if (projectId) {
      loadFinancialData();
    } else {
      setLoading(false);
      setError('No project ID available');
    }
  }, [projectId]);

  const loadFinancialData = async () => {
    setLoading(true);
    setError(null);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      console.log('Loading financial data for project:', projectId);
      console.log('Backend URL:', backendUrl);
      
      // Load all financial data in parallel
      const [invoicesRes, payablesRes, cashflowRes, profitabilityRes, inspectionsRes] = await Promise.all([
        fetch(`${backendUrl}/api/invoices/${projectId}`),
        fetch(`${backendUrl}/api/payables/${projectId}`),
        fetch(`${backendUrl}/api/cashflow/${projectId}`),
        fetch(`${backendUrl}/api/profitability/${projectId}`),
        fetch(`${backendUrl}/api/inspections/${projectId}`)
      ]);

      console.log('API Responses:', {
        invoices: invoicesRes.status,
        payables: payablesRes.status,
        cashflow: cashflowRes.status,
        profitability: profitabilityRes.status,
        inspections: inspectionsRes.status
      });

      if (invoicesRes.ok) {
        const invoicesData = await invoicesRes.json();
        console.log('Invoices data:', invoicesData);
        setInvoices(invoicesData);
      } else {
        console.error('Invoices API error:', invoicesRes.status, await invoicesRes.text());
      }
      
      if (payablesRes.ok) {
        const payablesData = await payablesRes.json();
        console.log('Payables data:', payablesData);
        setPayables(payablesData);
      } else {
        console.error('Payables API error:', payablesRes.status, await payablesRes.text());
      }
      
      if (cashflowRes.ok) {
        const cashflowResData = await cashflowRes.json();
        console.log('Cashflow data:', cashflowResData);
        setCashflowData(cashflowResData);
      } else {
        console.error('Cashflow API error:', cashflowRes.status, await cashflowRes.text());
      }
      
      if (profitabilityRes.ok) {
        const profitabilityResData = await profitabilityRes.json();
        console.log('Profitability data:', profitabilityResData);
        setProfitabilityData(profitabilityResData);
      } else {
        console.error('Profitability API error:', profitabilityRes.status, await profitabilityRes.text());
      }

      if (inspectionsRes.ok) {
        const inspectionsData = await inspectionsRes.json();
        console.log('Inspections data:', inspectionsData);
        setInspections(inspectionsData);
      } else {
        console.error('Inspections API error:', inspectionsRes.status, await inspectionsRes.text());
      }

      // If no data exists, show sample data for demonstration
      if (invoices.length === 0 && payables.length === 0 && cashflowData.length === 0 && profitabilityData.length === 0 && inspections.length === 0) {
        console.log('No financial data found, showing demo message');
      }
      
    } catch (error) {
      console.error('Error loading financial data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Status badge helper
  const getStatusBadge = (status, type = 'default') => {
    const statusColors = {
      draft: 'secondary',
      sent: 'default',
      paid: 'success',
      overdue: 'destructive',
      pending: 'secondary'
    };
    
    return (
      <Badge variant={statusColors[status] || 'secondary'}>
        {status?.charAt(0).toUpperCase() + status?.slice(1)}
      </Badge>
    );
  };

  // Invoices Tab Component
  const InvoicesTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className={`text-lg font-semibold ${themeClasses.text.primary}`}>
          Project Invoices
        </h3>
        <Button className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Create Invoice
        </Button>
      </div>

      <AnimatedCard 
        delay={100}
        className={`hover:shadow-2xl transition-all duration-300 ease-out backdrop-blur-md border-0 shadow-xl ${
          isDarkMode 
            ? 'bg-white/10 text-white' 
            : 'bg-white/70 text-gray-900'
        }`}
      >
        <AnimatedCardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                <TableHead className={themeClasses.text.primary}>Invoice #</TableHead>
                <TableHead className={themeClasses.text.primary}>Status</TableHead>
                <TableHead className={themeClasses.text.primary}>Total</TableHead>
                <TableHead className={themeClasses.text.primary}>Due Date</TableHead>
                <TableHead className={themeClasses.text.primary}>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {invoices.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className={`text-center py-8 ${themeClasses.text.secondary}`}>
                    <Receipt className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    No invoices found. Create your first invoice to get started.
                  </TableCell>
                </TableRow>
              ) : (
                invoices.map((invoice) => (
                  <TableRow key={invoice.id} className={`${isDarkMode ? 'border-white/10' : 'border-gray-100'} hover:bg-gray-50 dark:hover:bg-white/5`}>
                    <TableCell className={themeClasses.text.primary}>
                      {invoice.invoice_number}
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(invoice.status)}
                    </TableCell>
                    <TableCell className={themeClasses.text.primary}>
                      ${invoice.total?.toLocaleString() || '0.00'}
                    </TableCell>
                    <TableCell className={themeClasses.text.secondary}>
                      {new Date(invoice.due_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <Edit className="w-3 h-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  // Payables Tab Component
  const PayablesTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className={`text-lg font-semibold ${themeClasses.text.primary}`}>
          Project Payables
        </h3>
        <Button className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Payable
        </Button>
      </div>

      <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                <TableHead className={themeClasses.text.primary}>Vendor</TableHead>
                <TableHead className={themeClasses.text.primary}>Description</TableHead>
                <TableHead className={themeClasses.text.primary}>Amount</TableHead>
                <TableHead className={themeClasses.text.primary}>Status</TableHead>
                <TableHead className={themeClasses.text.primary}>Due Date</TableHead>
                <TableHead className={themeClasses.text.primary}>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {payables.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className={`text-center py-8 ${themeClasses.text.secondary}`}>
                    <CreditCard className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    No payables found. Add payables to track vendor payments.
                  </TableCell>
                </TableRow>
              ) : (
                payables.map((payable) => (
                  <TableRow key={payable.id} className={`${isDarkMode ? 'border-white/10' : 'border-gray-100'} hover:bg-gray-50 dark:hover:bg-white/5`}>
                    <TableCell className={themeClasses.text.primary}>
                      {payable.vendor_id}
                    </TableCell>
                    <TableCell className={themeClasses.text.primary}>
                      {payable.description}
                    </TableCell>
                    <TableCell className={themeClasses.text.primary}>
                      ${payable.amount?.toLocaleString() || '0.00'}
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(payable.status)}
                    </TableCell>
                    <TableCell className={themeClasses.text.secondary}>
                      {new Date(payable.due_date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <Edit className="w-3 h-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  // Cashflow Tab Component
  const CashflowTab = () => {
    const totalInflow = cashflowData.reduce((sum, item) => sum + (item.inflow || 0), 0);
    const totalOutflow = cashflowData.reduce((sum, item) => sum + (item.outflow || 0), 0);
    const netCashflow = totalInflow - totalOutflow;
    const avgRunwayWeeks = cashflowData.length > 0 ? 
      Math.round(cashflowData.reduce((sum, item) => sum + (item.runway_weeks || 0), 0) / cashflowData.length) : 0;

    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h3 className={`text-lg font-semibold ${themeClasses.text.primary}`}>
            Cashflow Forecasting
          </h3>
          <Button className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Add Forecast Entry
          </Button>
        </div>

        {/* Cashflow Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm ${themeClasses.text.secondary}`}>Total Inflow</p>
                  <p className={`text-2xl font-bold text-green-600`}>${totalInflow.toLocaleString()}</p>
                </div>
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm ${themeClasses.text.secondary}`}>Total Outflow</p>
                  <p className={`text-2xl font-bold text-red-600`}>${totalOutflow.toLocaleString()}</p>
                </div>
                <TrendingDown className="w-8 h-8 text-red-600" />
              </div>
            </CardContent>
          </Card>

          <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm ${themeClasses.text.secondary}`}>Net Cashflow</p>
                  <p className={`text-2xl font-bold ${netCashflow >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${netCashflow.toLocaleString()}
                  </p>
                </div>
                <DollarSign className={`w-8 h-8 ${netCashflow >= 0 ? 'text-green-600' : 'text-red-600'}`} />
              </div>
            </CardContent>
          </Card>

          <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className={`text-sm ${themeClasses.text.secondary}`}>Runway (Weeks)</p>
                  <p className={`text-2xl font-bold ${avgRunwayWeeks > 8 ? 'text-green-600' : 'text-yellow-600'}`}>
                    {avgRunwayWeeks}
                  </p>
                </div>
                <BarChart3 className={`w-8 h-8 ${avgRunwayWeeks > 8 ? 'text-green-600' : 'text-yellow-600'}`} />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Cashflow Chart */}
        {cashflowData.length > 0 && (
          <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
            <CardHeader>
              <CardTitle className={themeClasses.text.primary}>Cashflow Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={cashflowData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="week_start" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis tickFormatter={(value) => `$${value.toLocaleString()}`} />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value, name) => [`$${value.toLocaleString()}`, name]}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="inflow" stroke="#10b981" name="Inflow" />
                  <Line type="monotone" dataKey="outflow" stroke="#ef4444" name="Outflow" />
                  <Line type="monotone" dataKey="net" stroke="#3b82f6" name="Net" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        )}

        {cashflowData.length === 0 && (
          <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
            <CardContent className="p-8 text-center">
              <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className={themeClasses.text.secondary}>
                No cashflow data available. Add forecast entries to see cashflow projections.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  // Profitability Tab Component
  const ProfitabilityTab = () => {
    const latestProfitability = profitabilityData[profitabilityData.length - 1];
    
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h3 className={`text-lg font-semibold ${themeClasses.text.primary}`}>
            Profitability Analysis
          </h3>
          <Button className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Add Profitability Entry
          </Button>
        </div>

        {latestProfitability ? (
          <>
            {/* Profitability Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className={`text-sm ${themeClasses.text.secondary}`}>Revenue</p>
                      <p className={`text-2xl font-bold text-green-600`}>
                        ${latestProfitability.revenue?.toLocaleString() || '0'}
                      </p>
                    </div>
                    <DollarSign className="w-8 h-8 text-green-600" />
                  </div>
                </CardContent>
              </Card>

              <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className={`text-sm ${themeClasses.text.secondary}`}>Labor Cost</p>
                      <p className={`text-2xl font-bold text-red-600`}>
                        ${latestProfitability.labor_cost?.toLocaleString() || '0'}
                      </p>
                    </div>
                    <TrendingDown className="w-8 h-8 text-red-600" />
                  </div>
                </CardContent>
              </Card>

              <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className={`text-sm ${themeClasses.text.secondary}`}>Material Cost</p>
                      <p className={`text-2xl font-bold text-red-600`}>
                        ${latestProfitability.material_cost?.toLocaleString() || '0'}
                      </p>
                    </div>
                    <TrendingDown className="w-8 h-8 text-red-600" />
                  </div>
                </CardContent>
              </Card>

              <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className={`text-sm ${themeClasses.text.secondary}`}>Profit Margin</p>
                      <p className={`text-2xl font-bold ${latestProfitability.profit_margin >= 10 ? 'text-green-600' : 'text-red-600'}`}>
                        {latestProfitability.profit_margin?.toFixed(1) || '0'}%
                      </p>
                    </div>
                    <TrendingUp className={`w-8 h-8 ${latestProfitability.profit_margin >= 10 ? 'text-green-600' : 'text-red-600'}`} />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Alerts */}
            {latestProfitability.alerts && latestProfitability.alerts.length > 0 && (
              <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
                <CardHeader>
                  <CardTitle className={`${themeClasses.text.primary} flex items-center gap-2`}>
                    <AlertCircle className="w-5 h-5 text-yellow-600" />
                    Profitability Alerts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {latestProfitability.alerts.map((alert, index) => (
                      <div key={index} className={`p-3 rounded-lg border ${
                        alert.type === 'low_margin' 
                          ? 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-500/30' 
                          : 'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-500/30'
                      }`}>
                        <div className="flex items-center gap-2">
                          <AlertCircle className={`w-4 h-4 ${
                            alert.type === 'low_margin' ? 'text-yellow-600' : 'text-red-600'
                          }`} />
                          <span className={`font-medium ${
                            alert.type === 'low_margin' ? 'text-yellow-800 dark:text-yellow-200' : 'text-red-800 dark:text-red-200'
                          }`}>
                            {alert.type === 'low_margin' ? 'Low Margin Alert' : 'Over Budget Alert'}
                          </span>
                        </div>
                        <p className={`mt-1 text-sm ${
                          alert.type === 'low_margin' ? 'text-yellow-700 dark:text-yellow-300' : 'text-red-700 dark:text-red-300'
                        }`}>
                          {alert.message}
                        </p>
                        <p className={`text-xs mt-1 ${themeClasses.text.secondary}`}>
                          {new Date(alert.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        ) : (
          <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
            <CardContent className="p-8 text-center">
              <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className={themeClasses.text.secondary}>
                No profitability data available. Add profitability entries to track project performance.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  // Inspections Tab Component
  const InspectionsTab = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className={`text-lg font-semibold ${themeClasses.text.primary}`}>
          Project Inspections
        </h3>
        <Button className="flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add Inspection
        </Button>
      </div>

      <Card className={`backdrop-blur-md border-0 shadow-xl ${
        isDarkMode 
          ? 'bg-white/10 text-white' 
          : 'bg-white/70 text-gray-900'
      }`}>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                <TableHead className={themeClasses.text.primary}>Inspection Type</TableHead>
                <TableHead className={themeClasses.text.primary}>Status</TableHead>
                <TableHead className={themeClasses.text.primary}>Date</TableHead>
                <TableHead className={themeClasses.text.primary}>Notes</TableHead>
                <TableHead className={themeClasses.text.primary}>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {inspections.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className={`text-center py-8 ${themeClasses.text.secondary}`}>
                    <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    No inspections scheduled. Add inspections to track project progress.
                  </TableCell>
                </TableRow>
              ) : (
                inspections.map((inspection) => (
                  <TableRow key={inspection.id} className={`${isDarkMode ? 'border-white/10' : 'border-gray-100'} hover:bg-gray-50 dark:hover:bg-white/5`}>
                    <TableCell className={themeClasses.text.primary}>
                      {inspection.inspection_type?.replace('_', ' ')?.toUpperCase() || inspection.inspectionType?.replace('_', ' ')?.toUpperCase()}
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(inspection.status)}
                    </TableCell>
                    <TableCell className={themeClasses.text.secondary}>
                      {new Date(inspection.date).toLocaleDateString()}
                    </TableCell>
                    <TableCell className={themeClasses.text.secondary}>
                      {inspection.notes || '-'}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <Edit className="w-3 h-3" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className={`text-center ${themeClasses.text.secondary}`}>
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          Loading financial data...
          {projectId && (
            <p className="text-xs mt-2">Project ID: {projectId}</p>
          )}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className={`text-center ${themeClasses.text.secondary}`}>
          <AlertCircle className="w-12 h-12 mx-auto mb-2 text-red-500" />
          <p className="text-red-600">Error loading financial data: {error}</p>
          <p className="text-xs mt-2">Project ID: {projectId || 'Not available'}</p>
          <Button 
            onClick={loadFinancialData} 
            variant="outline" 
            className="mt-4"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${
      isDarkMode 
        ? 'bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900' 
        : 'bg-gradient-to-br from-blue-50 via-indigo-50 to-slate-100'
    }`}>
      {/* Header */}
      <div className="backdrop-blur-sm bg-white/10 border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <img 
                src="https://customer-assets.emergentagent.com/job_4a677f03-9858-4c3f-97bb-9e96952a200d/artifacts/ljd1o3d7_TITLEBLOCKRHINOFIRE.png" 
                alt="Rhino Fire Protection" 
                className="h-10 w-auto"
              />
              <div>
                <h2 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>
                  Financial Management
                </h2>
                <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  {project?.name || 'Project Financial Overview'}
                </p>
              </div>
            </div>
            <Button variant="outline" onClick={onBack} className="backdrop-blur-sm bg-white/10 border-white/20">
              Back to Project
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Debug panel for development */}
        <div className={`backdrop-blur-md border-0 shadow-xl rounded-lg p-4 ${
          isDarkMode 
            ? 'bg-white/10 text-white' 
            : 'bg-white/70 text-gray-900'
        }`}>
          <h3 className="font-semibold mb-2">System Status:</h3>
          <div className="grid grid-cols-5 gap-4 text-xs">
            <div>Invoices: {invoices.length} records</div>
            <div>Payables: {payables.length} records</div>
            <div>Cashflow: {cashflowData.length} records</div>
            <div>Profitability: {profitabilityData.length} records</div>
            <div>Inspections: {inspections.length} records</div>
          </div>
          <div className="mt-2 text-xs opacity-70">
            Project ID: {projectId || 'N/A'}
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5 backdrop-blur-md bg-white/10 border-white/20">
            <TabsTrigger value="invoices" className="flex items-center gap-2">
              <Receipt className="w-4 h-4" />
              Invoices
            </TabsTrigger>
            <TabsTrigger value="payables" className="flex items-center gap-2">
              <CreditCard className="w-4 h-4" />
              Payables
            </TabsTrigger>
            <TabsTrigger value="cashflow" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Cashflow
            </TabsTrigger>
            <TabsTrigger value="profitability" className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Profitability
            </TabsTrigger>
            <TabsTrigger value="inspections" className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4" />
              Inspections
            </TabsTrigger>
          </TabsList>

          <TabsContent value="invoices" className="space-y-4">
            <InvoicesTab />
          </TabsContent>
          <TabsContent value="payables" className="space-y-4">
            <PayablesTab />
          </TabsContent>
          <TabsContent value="cashflow" className="space-y-4">
            <CashflowTab />
          </TabsContent>
          <TabsContent value="profitability" className="space-y-4">
            <ProfitabilityTab />
          </TabsContent>
          <TabsContent value="inspections" className="space-y-4">
            <InspectionsTab />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default FinancialTabs;