
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, MessageSquare, Search, Plus } from 'lucide-react';

const actions = [
  {
    title: 'Upload Document',
    description: 'Upload and analyze new legal documents',
    icon: Upload,
    color: 'blue',
    action: 'upload'
  },
  {
    title: 'Ask Question',
    description: 'Get answers from your documents',
    icon: MessageSquare,
    color: 'purple',
    action: 'question'
  },
  {
    title: 'Search Documents',
    description: 'Find specific information quickly',
    icon: Search,
    color: 'green',
    action: 'search'
  }
];

interface QuickActionsProps {
  onNavigate?: (page: string) => void;
}

export const QuickActions: React.FC<QuickActionsProps> = ({ onNavigate }) => {
  const handleAction = (action: string) => {
    console.log(`Performing action: ${action}`);
    
    switch (action) {
      case 'upload':
        onNavigate?.('documents');
        break;
      case 'question':
        onNavigate?.('question-answering');
        break;
      case 'search':
        onNavigate?.('search');
        break;
      case 'new-project':
        console.log('Starting new project...');
        // Implement new project creation
        break;
    }
  };

  return (
    <Card className="dark:bg-gray-800 dark:border-gray-700">
      <CardHeader>
        <CardTitle className="dark:text-white">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {actions.map((action) => {
          const Icon = action.icon;
          
          return (
            <Button
              key={action.action}
              variant="outline"
              className="w-full h-auto p-4 flex items-center justify-start space-x-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors dark:border-gray-600 dark:text-white"
              onClick={() => handleAction(action.action)}
            >
              <div className={`p-2 rounded-lg bg-${action.color}-100 dark:bg-${action.color}-900 flex-shrink-0`}>
                <Icon className={`h-4 w-4 text-${action.color}-600 dark:text-${action.color}-400`} />
              </div>
              <div className="text-left flex-1">
                <div className="font-medium text-gray-900 dark:text-white">{action.title}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">{action.description}</div>
              </div>
            </Button>
          );
        })}
        
        <Button 
          className="w-full bg-blue-600 hover:bg-blue-700 text-white"
          onClick={() => handleAction('new-project')}
        >
          <Plus className="h-4 w-4 mr-2" />
          Start New Project
        </Button>
      </CardContent>
    </Card>
  );
};
