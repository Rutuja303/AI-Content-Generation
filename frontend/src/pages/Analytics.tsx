import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, FileText, CheckCircle } from 'lucide-react';
import { analyticsAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Twitter, Instagram, Linkedin, Facebook } from 'lucide-react';

interface PlatformData {
  platform: string;
  generated: number;
  posted: number;
}

interface PlatformSummary {
  platforms: PlatformData[];
  total_generated: number;
  total_posted: number;
}

const platformIcons: Record<string, React.ComponentType<any>> = {
  twitter: Twitter,
  instagram: Instagram,
  linkedin: Linkedin,
  facebook: Facebook,
};

const platformColors: Record<string, string> = {
  twitter: 'bg-blue-400',
  instagram: 'bg-pink-400',
  linkedin: 'bg-blue-600',
  facebook: 'bg-blue-700',
};

const platformNames: Record<string, string> = {
  twitter: 'Twitter',
  instagram: 'Instagram',
  linkedin: 'LinkedIn',
  facebook: 'Facebook',
};

const Analytics: React.FC = () => {
  const [platformData, setPlatformData] = useState<PlatformSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await analyticsAPI.getPlatformSummary();
      setPlatformData(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const getMaxValue = () => {
    if (!platformData) return 0;
    return Math.max(
      ...platformData.platforms.map(p => Math.max(p.generated, p.posted)),
      platformData.total_generated,
      platformData.total_posted
    );
  };

  const getBarHeight = (value: number, maxValue: number) => {
    if (maxValue === 0) return 0;
    return (value / maxValue) * 100;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!platformData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            View performance metrics and engagement insights
          </p>
        </div>
        <div className="card">
          <div className="flex items-center justify-center h-64 text-gray-500">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium">No data available</p>
              <p className="text-sm">Start generating content to see analytics</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const maxValue = getMaxValue();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          View performance metrics and engagement insights
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <FileText className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Generated</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {platformData.total_generated}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Posted</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {platformData.total_posted}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className="h-8 w-8 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Posting Rate</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {platformData.total_generated > 0
                  ? Math.round((platformData.total_posted / platformData.total_generated) * 100)
                  : 0}%
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BarChart3 className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Platforms Used</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {platformData.platforms.filter(p => p.generated > 0).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Platform Breakdown Chart */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-6">
          Posts by Platform
        </h3>
        
        <div className="space-y-6">
          {platformData.platforms.map((platform) => {
            const Icon = platformIcons[platform.platform] || BarChart3;
            const generatedHeight = getBarHeight(platform.generated, maxValue);
            const postedHeight = getBarHeight(platform.posted, maxValue);
            
            return (
              <div key={platform.platform} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Icon className={`h-5 w-5 ${platformColors[platform.platform]?.replace('bg-', 'text-') || 'text-gray-400'}`} />
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {platformNames[platform.platform] || platform.platform}
                    </span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm">
                    <span className="text-gray-600 dark:text-gray-400">
                      Generated: <span className="font-semibold text-gray-900 dark:text-white">{platform.generated}</span>
                    </span>
                    <span className="text-gray-600 dark:text-gray-400">
                      Posted: <span className="font-semibold text-green-600">{platform.posted}</span>
                    </span>
                  </div>
                </div>
                
                <div className="relative h-8 bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
                  {/* Generated bar */}
                  <div
                    className={`absolute left-0 top-0 h-full ${platformColors[platform.platform] || 'bg-gray-400'} opacity-60`}
                    style={{ width: `${generatedHeight}%` }}
                    title={`Generated: ${platform.generated}`}
                  />
                  
                  {/* Posted bar (overlay) */}
                  <div
                    className="absolute left-0 top-0 h-full bg-green-500"
                    style={{ width: `${postedHeight}%` }}
                    title={`Posted: ${platform.posted}`}
                  />
                  
                  {/* Value labels */}
                  {platform.generated > 0 && (
                    <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-gray-900 dark:text-white">
                      {platform.generated} generated • {platform.posted} posted
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {platformData.platforms.every(p => p.generated === 0) && (
          <div className="text-center py-12">
            <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-500 dark:text-gray-400">No posts generated yet</p>
            <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">
              Start generating content to see analytics
            </p>
          </div>
        )}
      </div>

      {/* Platform Details Table */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Platform Statistics
        </h3>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Platform
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Generated
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Posted
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Posting Rate
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-700 divide-y divide-gray-200 dark:divide-gray-600">
              {platformData.platforms.map((platform) => {
                const Icon = platformIcons[platform.platform] || BarChart3;
                const postingRate = platform.generated > 0
                  ? Math.round((platform.posted / platform.generated) * 100)
                  : 0;
                
                return (
                  <tr key={platform.platform}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Icon className={`h-5 w-5 mr-2 ${platformColors[platform.platform]?.replace('bg-', 'text-') || 'text-gray-400'}`} />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {platformNames[platform.platform] || platform.platform}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      {platform.generated}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 dark:text-green-400 font-semibold">
                      {platform.posted}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 dark:bg-gray-600 rounded-full h-2 mr-2">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${postingRate}%` }}
                          />
                        </div>
                        <span>{postingRate}%</span>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
