import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { 
  Key, 
  Plus, 
  Shield, 
  Activity,
  Clock,
  Globe,
  CheckCircle, 
  XCircle,
  Eye,
  Calendar
} from 'lucide-react';
import { useToast } from '../hooks/use-toast';
import { useTheme } from '../contexts/ThemeContext';

const AdminGcManagement = ({ onBack }) => {
  const { toast } = useToast();
  const { isDarkMode, getThemeClasses } = useTheme();
  const themeClasses = getThemeClasses();
  
  const [projects, setProjects] = useState([]);
  const [gcKeys, setGcKeys] = useState([]);
  const [accessLogs, setAccessLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateKeyModal, setShowCreateKeyModal] = useState(false);
  
  const [newKey, setNewKey] = useState({
    projectId: '',
    key: '',
    expiresAt: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      
      // Load projects, GC keys, and access logs in parallel
      const [projectsRes, keysRes, logsRes] = await Promise.all([
        fetch(`${backendUrl}/api/projects`),
        fetch(`${backendUrl}/api/gc/keys/admin`),
        fetch(`${backendUrl}/api/gc/access-logs/admin`)
      ]);

      if (projectsRes.ok) {
        const projectsData = await projectsRes.json();
        setProjects(projectsData);
      }
      
      if (keysRes.ok) {
        const keysData = await keysRes.json();
        setGcKeys(keysData);
      }
      
      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setAccessLogs(logsData);
      }
      
    } catch (error) {
      console.error('Error loading admin data:', error);
      toast({
        title: "Loading Error",
        description: "Failed to load GC management data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const generateRandomKey = () => {
    const key = Math.floor(1000 + Math.random() * 9000).toString();
    setNewKey(prev => ({ ...prev, key }));
  };

  const handleCreateKey = async () => {
    if (!newKey.projectId || !newKey.key || !newKey.expiresAt) {
      toast({
        title: "Missing Information",
        description: "Please fill all fields",
        variant: "destructive"
      });
      return;
    }

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL;
      const response = await fetch(`${backendUrl}/api/gc/keys`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          projectId: newKey.projectId,
          key: newKey.key,
          expiresAt: new Date(newKey.expiresAt).toISOString()
        })
      });

      if (response.ok) {
        toast({
          title: "GC Key Created",
          description: `Access key ${newKey.key} created successfully`,
        });
        
        setShowCreateKeyModal(false);
        setNewKey({ projectId: '', key: '', expiresAt: '' });
        loadData(); // Reload data
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create key');
      }
    } catch (error) {
      console.error('Error creating GC key:', error);
      toast({
        title: "Creation Failed",
        description: error.message,
        variant: "destructive"
      });
    }
  };

  const getStatusBadge = (status, used = false, expired = false) => {
    if (expired) return <Badge variant="destructive">Expired</Badge>;
    if (used) return <Badge variant="secondary">Used</Badge>;
    if (status === 'success') return <Badge variant="default">Success</Badge>;
    if (status === 'failed') return <Badge variant="destructive">Failed</Badge>;
    return <Badge variant="default">Active</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className={`text-center ${themeClasses.text.secondary}`}>
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          Loading GC management data...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className={`text-2xl font-bold ${themeClasses.text.primary}`}>
          GC Access Management
        </h2>
        <Button variant="outline" onClick={onBack}>
          Back to Dashboard
        </Button>
      </div>

      <Tabs defaultValue="keys" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="keys" className="flex items-center gap-2">
            <Key className="w-4 h-4" />
            Access Keys
          </TabsTrigger>
          <TabsTrigger value="logs" className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Access Logs
          </TabsTrigger>
        </TabsList>

        <TabsContent value="keys" className="mt-6">
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className={`text-lg font-semibold ${themeClasses.text.primary}`}>
                GC Access Keys
              </h3>
              <Dialog open={showCreateKeyModal} onOpenChange={setShowCreateKeyModal}>
                <DialogTrigger asChild>
                  <Button className="flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    Generate New Key
                  </Button>
                </DialogTrigger>
                <DialogContent className={`sm:max-w-[500px] ${themeClasses.modal}`}>
                  <DialogHeader>
                    <DialogTitle className={`flex items-center gap-2 ${themeClasses.text.primary}`}>
                      <Key className="w-5 h-5" />
                      Generate GC Access Key
                    </DialogTitle>
                  </DialogHeader>
                  
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <Label className={themeClasses.text.primary}>Project</Label>
                      <Select value={newKey.projectId} onValueChange={(value) => setNewKey(prev => ({ ...prev, projectId: value }))}>
                        <SelectTrigger className={themeClasses.input.primary}>
                          <SelectValue placeholder="Select project" />
                        </SelectTrigger>
                        <SelectContent>
                          {projects.map((project) => (
                            <SelectItem key={project.id} value={project.id}>
                              {project.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div className="space-y-2">
                      <Label className={themeClasses.text.primary}>4-Digit Key</Label>
                      <div className="flex gap-2">
                        <Input
                          type="text"
                          placeholder="0000"
                          maxLength={4}
                          value={newKey.key}
                          onChange={(e) => {
                            const value = e.target.value.replace(/\D/g, '');
                            setNewKey(prev => ({ ...prev, key: value }));
                          }}
                          className={`${themeClasses.input.primary} text-center text-lg tracking-widest`}
                        />
                        <Button 
                          type="button" 
                          variant="outline" 
                          onClick={generateRandomKey}
                          className="flex-shrink-0"
                        >
                          Generate
                        </Button>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label className={themeClasses.text.primary}>Expires At</Label>
                      <Input
                        type="datetime-local"
                        value={newKey.expiresAt}
                        onChange={(e) => setNewKey(prev => ({ ...prev, expiresAt: e.target.value }))}
                        className={themeClasses.input.primary}
                      />
                    </div>
                    
                    <div className={`p-3 rounded-lg border ${
                      isDarkMode 
                        ? 'bg-blue-900/20 border-blue-500/30 text-blue-200' 
                        : 'bg-blue-50 border-blue-200 text-blue-800'
                    }`}>
                      <p className="text-sm">
                        <Shield className="w-4 h-4 inline mr-2" />
                        <strong>Security Note:</strong> Keys are single-use and will be deactivated after first login.
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-end gap-2">
                    <Button 
                      variant="outline" 
                      onClick={() => setShowCreateKeyModal(false)}
                    >
                      Cancel
                    </Button>
                    <Button onClick={handleCreateKey}>
                      Create Key
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <Card className={themeClasses.card.primary}>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                      <TableHead className={themeClasses.text.primary}>Project</TableHead>
                      <TableHead className={themeClasses.text.primary}>Key</TableHead>
                      <TableHead className={themeClasses.text.primary}>Expires</TableHead>
                      <TableHead className={themeClasses.text.primary}>Status</TableHead>
                      <TableHead className={themeClasses.text.primary}>Used At</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {gcKeys.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} className={`text-center py-8 ${themeClasses.text.secondary}`}>
                          <Key className="w-12 h-12 mx-auto mb-2 opacity-50" />
                          No GC keys generated yet. Create your first key to get started.
                        </TableCell>
                      </TableRow>
                    ) : (
                      gcKeys.map((key) => {
                        const isExpired = new Date(key.expiresAt) < new Date();
                        return (
                          <TableRow key={key.id} className={`${isDarkMode ? 'border-white/10' : 'border-gray-100'} hover:bg-gray-50 dark:hover:bg-white/5`}>
                            <TableCell className={themeClasses.text.primary}>
                              {key.projectName}
                            </TableCell>
                            <TableCell className={`font-mono ${themeClasses.text.primary}`}>
                              ****{key.keyLastFour}
                            </TableCell>
                            <TableCell className={themeClasses.text.secondary}>
                              <div className="flex items-center gap-2">
                                <Calendar className="w-3 h-3" />
                                {new Date(key.expiresAt).toLocaleDateString()}
                              </div>
                            </TableCell>
                            <TableCell>
                              {getStatusBadge(null, key.used, isExpired)}
                            </TableCell>
                            <TableCell className={themeClasses.text.secondary}>
                              {key.usedAt ? new Date(key.usedAt).toLocaleString() : '-'}
                            </TableCell>
                          </TableRow>
                        );
                      })
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="logs" className="mt-6">
          <div className="space-y-6">
            <h3 className={`text-lg font-semibold ${themeClasses.text.primary}`}>
              GC Access Logs
            </h3>

            <Card className={themeClasses.card.primary}>
              <CardContent className="p-0">
                <Table>
                  <TableHeader>
                    <TableRow className={isDarkMode ? 'border-white/20' : 'border-gray-200'}>
                      <TableHead className={themeClasses.text.primary}>Project</TableHead>
                      <TableHead className={themeClasses.text.primary}>Key</TableHead>
                      <TableHead className={themeClasses.text.primary}>Timestamp</TableHead>
                      <TableHead className={themeClasses.text.primary}>IP Address</TableHead>
                      <TableHead className={themeClasses.text.primary}>Status</TableHead>
                      <TableHead className={themeClasses.text.primary}>User Agent</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {accessLogs.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className={`text-center py-8 ${themeClasses.text.secondary}`}>
                          <Activity className="w-12 h-12 mx-auto mb-2 opacity-50" />
                          No access attempts logged yet.
                        </TableCell>
                      </TableRow>
                    ) : (
                      accessLogs.map((log) => (
                        <TableRow key={log.id} className={`${isDarkMode ? 'border-white/10' : 'border-gray-100'} hover:bg-gray-50 dark:hover:bg-white/5`}>
                          <TableCell className={themeClasses.text.primary}>
                            {log.projectName}
                          </TableCell>
                          <TableCell className={`font-mono ${themeClasses.text.primary}`}>
                            ****{log.keyLastFour}
                          </TableCell>
                          <TableCell className={themeClasses.text.secondary}>
                            <div className="flex items-center gap-2">
                              <Clock className="w-3 h-3" />
                              {new Date(log.timestamp).toLocaleString()}
                            </div>
                          </TableCell>
                          <TableCell className={`font-mono text-sm ${themeClasses.text.secondary}`}>
                            <div className="flex items-center gap-2">
                              <Globe className="w-3 h-3" />
                              {log.ip}
                            </div>
                          </TableCell>
                          <TableCell>
                            {getStatusBadge(log.status)}
                          </TableCell>
                          <TableCell className={`text-xs ${themeClasses.text.secondary} max-w-[200px] truncate`}>
                            {log.userAgent || '-'}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AdminGcManagement;