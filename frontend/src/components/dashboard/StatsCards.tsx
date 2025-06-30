import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, CheckCircle, Clock, MessageSquare, TrendingUp, TrendingDown } from 'lucide-react';

const BASE_API_URL = 'http://localhost:5000';

export const StatsCards: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('jwt_token');
        const response = await fetch(`${BASE_API_URL}/dashboard-stats`, {
          headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        });
        if (!response.ok) {
          throw new Error('Failed to fetch dashboard stats.');
        }
        const data = await response.json();
        setStats(data);
      } catch (err: any) {
        setError(err.message || 'Error fetching dashboard stats.');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const statConfig = [
    {
      title: 'Total Documents',
      key: 'total_documents',
      icon: FileText,
      color: 'accent',
      trend: 'up',
      change: '+0%'
    },
    {
      title: 'Processed Documents',
      key: 'processed_documents',
      icon: CheckCircle,
      color: 'accent',
      trend: 'up',
      change: '+0%'
    },
    {
      title: 'Pending Analysis',
      key: 'pending_analysis',
      icon: Clock,
      color: 'destructive',
      trend: 'down',
      change: '-0%'
    },
    {
      title: 'Recent Questions',
      key: 'recent_questions',
      icon: MessageSquare,
      color: 'accent',
      trend: 'up',
      change: '+0%'
    }
  ];

  if (loading) {
    return <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">Loading stats...</div>;
  }
  if (error) {
    return <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-destructive">{error}</div>;
  }
  if (!stats) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statConfig.map((stat) => {
        const Icon = stat.icon;
        const TrendIcon = stat.trend === 'up' ? TrendingUp : TrendingDown;
        const value = stats[stat.key] ?? 0;
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
              <div className="text-2xl font-bold text-foreground">{value}</div>
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
