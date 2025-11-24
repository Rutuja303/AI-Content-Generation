import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  BarChart3, 
  FileText, 
  Calendar, 
  TrendingUp,
  Sparkles,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { analyticsAPI } from '../services/api';
import toast from 'react-hot-toast';

interface DashboardData {
  total_posts: number;
  published_posts: number;
  scheduled_posts: number;
  platform_breakdown: Record<string, number>;
  recent_activity: Array<{
    id: number;
    platform: string;
    status: string;
    created_at: string;
    content_preview: string;
  }>;
}

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await analyticsAPI.getDashboard();
      setDashboardData(response.data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'published':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'scheduled':
        return <Clock className="h-4 w-4 text-blue-500" />;
      case 'draft':
        return <FileText className="h-4 w-4 text-gray-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'text-green-600 bg-green-100';
      case 'scheduled':
        return 'text-blue-600 bg-blue-100';
      case 'draft':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-red-600 bg-red-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Overview of your content generation and publishing activity
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <FileText className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Total Posts</dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">{dashboardData?.total_posts || 0}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Published</dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">{dashboardData?.published_posts || 0}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Calendar className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Scheduled</dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">{dashboardData?.scheduled_posts || 0}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Engagement Rate</dt>
                <dd className="text-lg font-medium text-gray-900 dark:text-white">2.4%</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Platform Breakdown */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Platform Breakdown</h3>
          <div className="space-y-3">
            {dashboardData?.platform_breakdown && Object.entries(dashboardData.platform_breakdown).map(([platform, count]) => (
              <div key={platform} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">{platform}</span>
                <span className="text-sm text-gray-500 dark:text-gray-400">{count} posts</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Link
              to="/generate"
              className="flex items-center p-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              <Sparkles className="h-5 w-5 text-primary-600 mr-3" />
              Generate New Content
            </Link>
            <Link
              to="/posts"
              className="flex items-center p-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              <FileText className="h-5 w-5 text-primary-600 mr-3" />
              View All Posts
            </Link>
            <Link
              to="/schedule"
              className="flex items-center p-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              <Calendar className="h-5 w-5 text-primary-600 mr-3" />
              Manage Schedule
            </Link>
            <Link
              to="/analytics"
              className="flex items-center p-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            >
              <BarChart3 className="h-5 w-5 text-primary-600 mr-3" />
              View Analytics
            </Link>
          </div>
        </div>
      </div>

      {/* Social Media Connection Call-to-Action */}
      <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-700">
        <div className="text-center">
          <h3 className="text-lg font-medium text-blue-900 dark:text-blue-100 mb-2">
            Connect Your Social Media Accounts
          </h3>
          <p className="text-sm text-blue-800 dark:text-blue-200 mb-4">
            Unlock the full potential of AI-powered content generation by connecting your social media platforms.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              to="/profile"
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
            >
              Connect Accounts
            </Link>
            <Link
              to="/generate"
              className="inline-flex items-center px-4 py-2 bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 border border-blue-600 dark:border-blue-400 text-sm font-medium rounded-md hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors"
            >
              Start Generating Content
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Recent Activity</h3>
        <div className="space-y-4">
          {dashboardData?.recent_activity && dashboardData.recent_activity.length > 0 ? (
            dashboardData.recent_activity.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3">
                {getStatusIcon(activity.status)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900 dark:text-white">{activity.content_preview}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(activity.status)}`}>
                      {activity.status}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">{activity.platform}</span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(activity.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500 dark:text-gray-400">No recent activity</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
