import React, { useState, useEffect } from 'react';
import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle 
} from './ui/card';
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

const FinancialTabs = ({ projectId, onBack }) => {
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  
  // State for each financial module
  const [invoices, setInvoices] = useState([]);
  const [payables, setPayables] = useState([]);
  const [cashflowData, setCashflowData] = useState([]);
  const [profitabilityData, setProfitabilityData] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('invoices');

  useEffect(() => {
    if (projectId) {
      loadFinancialData();
    }
  }, [projectId]);

  const loadFinancialData = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      // Load all financial data in parallel
      const [invoicesRes, payablesRes, cashflowRes, profitabilityRes] = await Promise.all([
        fetch(`${backendUrl}/api/invoices/${projectId}`),
        fetch(`${backendUrl}/api/payables/${projectId}`),
        fetch(`${backendUrl}/api/cashflow/${projectId}`),
        fetch(`${backendUrl}/api/profitability/${projectId}`)
      ]);

      if (invoicesRes.ok) {
        const invoicesData = await invoicesRes.json();
        setInvoices(invoicesData);
      }
      
      if (payablesRes.ok) {
        const payablesData = await payablesRes.json();
        setPayables(payablesData);
      }
      
      if (cashflowRes.ok) {
        const cashflowResData = await cashflowRes.json();
        setCashflowData(cashflowResData);
      }
      
      if (profitabilityRes.ok) {
        const profitabilityResData = await profitabilityRes.json();
        setProfitabilityData(profitabilityResData);
      }
      
    } catch (error) {
      console.error('Error loading financial data:', error);
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

      <Card className={themeClasses.card.primary}>
        <CardContent className="p-0">
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

      <Card className={themeClasses.card.primary}>
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
          <Card className={themeClasses.card.primary}>
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

          <Card className={themeClasses.card.primary}>
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

          <Card className={themeClasses.card.primary}>
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

          <Card className={themeClasses.card.primary}>
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
          <Card className={themeClasses.card.primary}>
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
          <Card className={themeClasses.card.primary}>
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
              <Card className={themeClasses.card.primary}>
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

              <Card className={themeClasses.card.primary}>
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

              <Card className={themeClasses.card.primary}>
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

              <Card className={themeClasses.card.primary}>
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
              <Card className={themeClasses.card.primary}>
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
          <Card className={themeClasses.card.primary}>
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className={`text-center ${themeClasses.text.secondary}`}>
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          Loading financial data...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className={`text-2xl font-bold ${themeClasses.text.primary}`}>
          Financial Management
        </h2>
        <Button variant="outline" onClick={onBack}>
          Back to Project
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
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
        </TabsList>

        <TabsContent value="invoices" className="mt-6">
          <InvoicesTab />
        </TabsContent>

        <TabsContent value="payables" className="mt-6">
          <PayablesTab />
        </TabsContent>

        <TabsContent value="cashflow" className="mt-6">
          <CashflowTab />
        </TabsContent>

        <TabsContent value="profitability" className="mt-6">
          <ProfitabilityTab />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FinancialTabs;