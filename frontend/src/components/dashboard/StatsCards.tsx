import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, CheckCircle, Clock, MessageSquare, TrendingUp, TrendingDown } from 'lucide-react';

const stats = [
  {
    title: 'Total Documents',
    value: '1,247',
    change: '+12%',
    trend: 'up',
    icon: FileText,
    color: 'accent'
  },
  {
    title: 'Processed Documents',
    value: '1,189',
    change: '+8%',
    trend: 'up',
    icon: CheckCircle,
    color: 'accent'
  },
  {
    title: 'Pending Analysis',
    value: '58',
    change: '-15%',
    trend: 'down',
    icon: Clock,
    color: 'destructive'
  },
  {
    title: 'Recent Questions',
    value: '342',
    change: '+23%',
    trend: 'up',
    icon: MessageSquare,
    color: 'accent'
  }
];

export const StatsCards: React.FC = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => {
        const Icon = stat.icon;
        const TrendIcon = stat.trend === 'up' ? TrendingUp : TrendingDown;
        
        return (
          <Card key={stat.title} className="hover:shadow-md transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <div className={`p-2 rounded-lg bg-${stat.color}/10`}>
                <Icon className={`h-4 w-4 text-${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stat.value}</div>
              <div className="flex items-center mt-1">
                <TrendIcon className={`h-3 w-3 mr-1 ${
                  stat.trend === 'up' ? 'text-accent' : 'text-destructive'
                }`} />
                <span className={`text-xs font-medium ${
                  stat.trend === 'up' ? 'text-accent' : 'text-destructive'
                }`}>
                  {stat.change}
                </span>
                <span className="text-xs text-muted-foreground ml-1">from last month</span>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};
