import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, MessageSquare, Upload, Search, Clock } from 'lucide-react';

const BASE_API_URL = 'http://localhost:5000';

export const RecentActivity: React.FC = () => {
  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchActivities = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('jwt_token');
        // Fetch recent documents
        const docsRes = await fetch(`${BASE_API_URL}/documents`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        });
        let docs: any[] = [];
        if (docsRes.ok) {
          docs = await docsRes.json();
        }
        // Map document uploads/processing
        const docActivities = docs.slice(0, 5).map((doc: any) => ({
          id: `doc-${doc.id}`,
          type: 'upload',
          title: doc.summary && doc.summary !== 'Processing...' ? 'Contract Analysis Completed' : 'Document Uploaded',
          description: `${doc.title} ${doc.summary && doc.summary !== 'Processing...' ? 'has been processed' : 'uploaded for analysis'}`,
          timestamp: new Date(doc.upload_time).toLocaleString(),
          icon: doc.summary && doc.summary !== 'Processing...' ? FileText : Upload,
          status: doc.summary && doc.summary !== 'Processing...' ? 'completed' : 'processing',
        }));
        // Fetch recent questions for the most recent document
        let qaActivities: any[] = [];
        if (docs.length > 0) {
          const docId = docs[0].id;
          const qaRes = await fetch(`${BASE_API_URL}/previous-questions/${docId}`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
          });
          if (qaRes.ok) {
            const qaData = await qaRes.json();
            if (qaData.success && qaData.questions) {
              qaActivities = qaData.questions.slice(0, 3).map((q: any) => ({
                id: `qa-${q.id}`,
                type: 'question',
                title: 'New Question Answered',
                description: q.question,
                timestamp: new Date(q.timestamp).toLocaleString(),
                icon: MessageSquare,
                status: 'answered',
              }));
            }
          }
        }
        // Mock search activity
        const searchActivities = [
          {
            id: 'search-1',
            type: 'search',
            title: 'Search Performed',
            description: 'Searched for "intellectual property clauses"',
            timestamp: new Date().toLocaleString(),
            icon: Search,
            status: 'completed',
          },
        ];
        setActivities([...docActivities, ...qaActivities, ...searchActivities]);
      } catch (err: any) {
        setError(err.message || 'Error fetching recent activity.');
      } finally {
        setLoading(false);
      }
    };
    fetchActivities();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-accent/10 text-accent';
      case 'processing':
        return 'bg-destructive/10 text-destructive';
      case 'answered':
        return 'bg-primary/10 text-primary';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  const getIconColor = (type: string) => {
    switch (type) {
      case 'upload':
        return 'text-accent bg-accent/10';
      case 'question':
        return 'text-primary bg-primary/10';
      case 'search':
        return 'text-accent bg-accent/10';
      default:
        return 'text-muted-foreground bg-muted';
    }
  };

  if (loading) {
    return <Card><CardHeader><CardTitle>Recent Activity</CardTitle></CardHeader><CardContent>Loading...</CardContent></Card>;
  }
  if (error) {
    return <Card><CardHeader><CardTitle>Recent Activity</CardTitle></CardHeader><CardContent className="text-destructive">{error}</CardContent></Card>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Recent Activity
          <button className="text-sm text-accent hover:text-accent/80 font-medium">
            View All
          </button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity) => {
            const Icon = activity.icon;
            return (
              <div key={activity.id} className="flex items-start space-x-3 p-3 rounded-lg hover:bg-accent/5 transition-colors">
                <div className={`p-2 rounded-lg ${getIconColor(activity.type)}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-foreground truncate">
                      {activity.title}
                    </p>
                    <Badge variant="secondary" className={getStatusColor(activity.status)}>
                      {activity.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground truncate">
                    {activity.description}
                  </p>
                  <div className="flex items-center mt-1">
                    <Clock className="h-3 w-3 text-muted-foreground mr-1" />
                    <span className="text-xs text-muted-foreground">{activity.timestamp}</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};
