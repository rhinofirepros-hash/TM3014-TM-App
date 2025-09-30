import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';

const ProjectIntelligence = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [emailInput, setEmailInput] = useState({
    subject: '',
    body: '',
    from_addr: 'test@example.com'
  });
  const [processingResult, setProcessingResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [reviewQueue, setReviewQueue] = useState([]);

  // Sample email templates for testing
  const sampleEmails = {
    rfp: {
      subject: "RFP: Fire Sprinkler System - Downtown Office Building",
      body: `Dear Rhino Fire Protection,

We are seeking bids for a complete fire sprinkler system installation for our new downtown office building project.

Project Details:
- Project Name: Downtown Office Complex
- Address: 1200 Broadway, San Diego, CA 92101
- Client: Downtown Development LLC
- Billing: Time & Material preferred at $95/hour
- Due Date: October 15, 2025

Please submit your proposal by October 1st. We look forward to working with you.

Best regards,
John Smith
Project Manager
Downtown Development LLC
john.smith@downtowndev.com`,
      from_addr: "john.smith@downtowndev.com"
    },
    invoice: {
      subject: "Invoice #INV-2025-0123 - $15,500",
      body: `Invoice Details:

Invoice Number: INV-2025-0123
Date: September 30, 2025
Amount: $15,500.00
Project: 3rd Ave Fire Protection
Payment Terms: Net 30

Services:
- Fire sprinkler head installation: $12,000
- Testing and certification: $2,500  
- Materials: $1,000

Payment due by October 30, 2025.

Thank you for your business.`,
      from_addr: "billing@supplies.com"
    },
    progress: {
      subject: "Project Update - Oregon St Sprinkler Installation 75% Complete",
      body: `Project Progress Update:

Project: Oregon St Fire Sprinkler System
Status: 75% Complete
Milestone: Main line installation completed
Next Phase: Head installation and testing

Completed this week:
- Installed main sprinkler lines on floors 1-3
- Completed rough inspection with AHJ
- Ordered remaining heads and fittings

Upcoming:
- Install sprinkler heads (targeting next week)
- System testing scheduled for October 5th
- Final inspection October 10th

No issues or delays at this time.`,
      from_addr: "foreman@rhinofirepro.com"
    }
  };

  useEffect(() => {
    fetchDashboardData();
    fetchReviewQueue();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligence/dashboard`);
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const fetchReviewQueue = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/review-queue`);
      const data = await response.json();
      setReviewQueue(data);
    } catch (error) {
      console.error('Error fetching review queue:', error);
    }
  };

  const processEmail = async () => {
    setLoading(true);
    setProcessingResult(null);
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/intelligence/process-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(emailInput)
      });
      
      const result = await response.json();
      setProcessingResult(result);
      
      // Refresh dashboard and review queue
      fetchDashboardData();
      fetchReviewQueue();
    } catch (error) {
      console.error('Error processing email:', error);
      setProcessingResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const loadSampleEmail = (type) => {
    setEmailInput(sampleEmails[type]);
  };

  const approveReviewItem = async (itemId) => {
    try {
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/review-queue/${itemId}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action: 'approve', notes: 'Approved via UI' })
      });
      
      fetchReviewQueue();
      fetchDashboardData();
    } catch (error) {
      console.error('Error approving item:', error);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold text-white mb-6">🧠 Project Intelligence System</h1>
      
      {/* Dashboard Overview */}
      {dashboardData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-slate-300 text-sm">Active Projects</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-blue-400">{dashboardData.active_projects}</p>
              <p className="text-xs text-slate-500">of {dashboardData.total_projects} total</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-slate-300 text-sm">Pending Reviews</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-yellow-400">{dashboardData.pending_reviews}</p>
              <p className="text-xs text-slate-500">items need attention</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-slate-300 text-sm">Overdue Tasks</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-red-400">{dashboardData.overdue_tasks}</p>
              <p className="text-xs text-slate-500">tasks past due</p>
            </CardContent>
          </Card>
          
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-slate-300 text-sm">Outstanding</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-green-400">${dashboardData.total_outstanding.toLocaleString()}</p>
              <p className="text-xs text-slate-500">invoices pending</p>
            </CardContent>
          </Card>
        </div>
      )}
      
      {/* Email Processing */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            📧 Email Intelligence Processing
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Sample Email Buttons */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => loadSampleEmail('rfp')}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
            >
              Load RFP Sample
            </button>
            <button
              onClick={() => loadSampleEmail('invoice')}
              className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm"
            >
              Load Invoice Sample
            </button>
            <button
              onClick={() => loadSampleEmail('progress')}
              className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-sm"
            >
              Load Progress Update
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 text-sm mb-2">Email Subject</label>
              <input
                type="text"
                value={emailInput.subject}
                onChange={(e) => setEmailInput({...emailInput, subject: e.target.value})}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-600 text-white rounded focus:border-blue-500"
                placeholder="Enter email subject..."
              />
            </div>
            <div>
              <label className="block text-slate-300 text-sm mb-2">From Address</label>
              <input
                type="email"
                value={emailInput.from_addr}
                onChange={(e) => setEmailInput({...emailInput, from_addr: e.target.value})}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-600 text-white rounded focus:border-blue-500"
                placeholder="sender@example.com"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-slate-300 text-sm mb-2">Email Body</label>
            <textarea
              value={emailInput.body}
              onChange={(e) => setEmailInput({...emailInput, body: e.target.value})}
              className="w-full px-3 py-2 bg-slate-900 border border-slate-600 text-white rounded focus:border-blue-500 h-32"
              placeholder="Paste or type email content here..."
            />
          </div>
          
          <button
            onClick={processEmail}
            disabled={loading || !emailInput.subject || !emailInput.body}
            className="w-full py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white rounded transition-colors"
          >
            {loading ? 'Processing with AI...' : '🧠 Process Email'}
          </button>
        </CardContent>
      </Card>
      
      {/* Processing Results */}
      {processingResult && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">🔍 AI Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            {processingResult.error ? (
              <div className="text-red-400">Error: {processingResult.error}</div>
            ) : (
              <div className="space-y-4">
                {/* Classification */}
                <div className="bg-slate-900 p-4 rounded">
                  <h3 className="text-lg font-semibold text-white mb-2">Classification</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <span className="text-slate-400">Label:</span>
                      <p className="text-white font-medium">{processingResult.classification?.label}</p>
                    </div>
                    <div>
                      <span className="text-slate-400">Confidence:</span>
                      <p className={`font-medium ${
                        processingResult.classification?.confidence >= 0.85 ? 'text-green-400' :
                        processingResult.classification?.confidence >= 0.6 ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {(processingResult.classification?.confidence * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <span className="text-slate-400">Status:</span>
                      <p className={`font-medium ${
                        processingResult.classification?.confidence >= 0.85 ? 'text-green-400' : 'text-yellow-400'
                      }`}>
                        {processingResult.classification?.confidence >= 0.85 ? 'Auto-Processed' : 'Needs Review'}
                      </p>
                    </div>
                  </div>
                </div>
                
                {/* Extracted Project Data */}
                {processingResult.project && (
                  <div className="bg-slate-900 p-4 rounded">
                    <h3 className="text-lg font-semibold text-white mb-2">Extracted Project Data</h3>
                    <div className="grid grid-cols-2 gap-4">
                      {Object.entries(processingResult.project).map(([key, value]) => (
                        value && (
                          <div key={key}>
                            <span className="text-slate-400 capitalize">{key.replace('_', ' ')}:</span>
                            <p className="text-white">{value}</p>
                          </div>
                        )
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Action Items */}
                {processingResult.action_items && processingResult.action_items.length > 0 && (
                  <div className="bg-slate-900 p-4 rounded">
                    <h3 className="text-lg font-semibold text-white mb-2">Action Items</h3>
                    <ul className="space-y-2">
                      {processingResult.action_items.map((item, index) => (
                        <li key={index} className="text-yellow-400 flex items-start gap-2">
                          <span>⚠️</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Suggested Tasks */}
                {processingResult.tasks && processingResult.tasks.length > 0 && (
                  <div className="bg-slate-900 p-4 rounded">
                    <h3 className="text-lg font-semibold text-white mb-2">Suggested Tasks</h3>
                    <ul className="space-y-2">
                      {processingResult.tasks.map((task, index) => (
                        <li key={index} className="text-blue-400 flex items-start gap-2">
                          <span>✅</span>
                          <span>{task}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
      
      {/* Review Queue */}
      {reviewQueue.length > 0 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">📋 Review Queue ({reviewQueue.length} items)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {reviewQueue.slice(0, 5).map((item) => (
                <div key={item.id} className="bg-slate-900 p-4 rounded border border-slate-600">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h4 className="text-white font-medium">{item.entity.replace('_', ' ')}</h4>
                      <p className="text-slate-400 text-sm">{item.reason}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => approveReviewItem(item.id)}
                        className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm"
                      >
                        Approve
                      </button>
                    </div>
                  </div>
                  {item.confidence && (
                    <div className="text-sm text-slate-400">
                      Confidence: {(item.confidence * 100).toFixed(1)}%
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ProjectIntelligence;