import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, MessageSquare, Upload, Search, Clock } from 'lucide-react';

const activities = [
  {
    id: 1,
    type: 'upload',
    title: 'Contract Analysis Completed',
    description: 'Employment_Contract_2024.pdf has been processed',
    timestamp: '2 minutes ago',
    icon: FileText,
    status: 'completed'
  },
  {
    id: 2,
    type: 'question',
    title: 'New Question Answered',
    description: 'What are the termination clauses in the contract?',
    timestamp: '5 minutes ago',
    icon: MessageSquare,
    status: 'answered'
  },
  {
    id: 3,
    type: 'upload',
    title: 'Document Uploaded',
    description: 'NDA_Agreement.pdf uploaded for analysis',
    timestamp: '12 minutes ago',
    icon: Upload,
    status: 'processing'
  },
  {
    id: 4,
    type: 'search',
    title: 'Search Performed',
    description: 'Searched for "intellectual property clauses"',
    timestamp: '25 minutes ago',
    icon: Search,
    status: 'completed'
  },
  {
    id: 5,
    type: 'upload',
    title: 'Bulk Upload Completed',
    description: '5 legal documents processed successfully',
    timestamp: '1 hour ago',
    icon: FileText,
    status: 'completed'
  }
];

export const RecentActivity: React.FC = () => {
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
