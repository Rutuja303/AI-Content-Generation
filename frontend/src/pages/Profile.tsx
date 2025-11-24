import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { User, Mail, Lock, Key, AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';
import toast from 'react-hot-toast';

interface PasswordChangeData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

interface SocialMediaConnection {
  platform: string;
  connected: boolean;
  username?: string;
  last_connected?: string;
}

const Profile: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [passwordData, setPasswordData] = useState<PasswordChangeData>({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [socialConnections, setSocialConnections] = useState<SocialMediaConnection[]>([
    { platform: 'Twitter', connected: false },
    { platform: 'Instagram', connected: false },
    { platform: 'Facebook', connected: false },
    { platform: 'LinkedIn', connected: false },
    { platform: 'Email', connected: false }
  ]);

  useEffect(() => {
    fetchSocialConnections();
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = () => {
    const connection = searchParams.get('connection');
    const platform = searchParams.get('platform');
    const username = searchParams.get('username');
    const error = searchParams.get('error');

    if (connection === 'success' && platform) {
      const displayUsername = username || `user_${platform}`;
      toast.success(`Successfully connected to ${platform} as ${displayUsername}!`);
      // Update the connection status immediately
      setSocialConnections(prev => 
        prev.map(conn => 
          conn.platform.toLowerCase() === platform.toLowerCase()
            ? { ...conn, connected: true, username: displayUsername }
            : conn
        )
      );
      // Refresh connections from API to get real data
      fetchSocialConnections();
      // Clear URL parameters after a short delay
      setTimeout(() => {
        navigate('/profile', { replace: true });
      }, 1000);
    } else if (connection === 'error' && error) {
      toast.error(`Failed to connect to ${platform}: ${error}`);
      // Clear URL parameters after showing error
      setTimeout(() => {
        navigate('/profile', { replace: true });
      }, 2000);
    }
  };

  const fetchSocialConnections = async () => {
    try {
      const response = await api.get('/oauth/connections');
      if (response.data) {
        // Update social connections based on API response
        const updatedConnections = socialConnections.map(conn => {
          const apiConnection = response.data.find(
            (apiConn: any) => apiConn.platform.toLowerCase() === conn.platform.toLowerCase()
          );
          return {
            ...conn,
            connected: !!apiConnection,
            username: apiConnection?.platform_username || undefined,
            last_connected: apiConnection?.created_at || undefined
          };
        });
        setSocialConnections(updatedConnections);
      }
    } catch (error) {
      console.log('No social connections found yet');
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }

    if (passwordData.new_password.length < 8) {
      toast.error('New password must be at least 8 characters long');
      return;
    }

    setIsChangingPassword(true);
    try {
      await api.post('/auth/change-password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      
      toast.success('Password changed successfully');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: ''
      });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const togglePasswordVisibility = (field: keyof typeof showPasswords) => {
    setShowPasswords(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  const getConnectionStatusIcon = (connected: boolean) => {
    return connected ? (
      <CheckCircle className="h-5 w-5 text-green-500" />
    ) : (
      <AlertCircle className="h-5 w-5 text-gray-400" />
    );
  };

  const getConnectionStatusText = (connected: boolean) => {
    return connected ? 'Connected' : 'Not Connected';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Profile Settings</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Manage your account information and social media connections
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* User Information */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            <User className="h-5 w-5 mr-2" />
            Account Information
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="form-label">Full Name</label>
              <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                <User className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-gray-900 dark:text-white">{user?.name || 'Not provided'}</span>
              </div>
            </div>

            <div>
              <label className="form-label">Email Address</label>
              <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                <Mail className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-gray-900 dark:text-white">{user?.email}</span>
              </div>
            </div>

            <div>
              <label className="form-label">Account Type</label>
              <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
                <Key className="h-5 w-5 text-gray-400 mr-3" />
                <span className="text-gray-900 dark:text-white">Standard User</span>
              </div>
            </div>
          </div>
        </div>

        {/* Password Change */}
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
            <Lock className="h-5 w-5 mr-2" />
            Change Password
          </h3>
          
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div>
              <label className="form-label">Current Password</label>
              <div className="relative">
                <input
                  type={showPasswords.current ? 'text' : 'password'}
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, current_password: e.target.value }))}
                  className="input-field pr-10"
                  placeholder="Enter current password"
                  required
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('current')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPasswords.current ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            <div>
              <label className="form-label">New Password</label>
              <div className="relative">
                <input
                  type={showPasswords.new ? 'text' : 'password'}
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, new_password: e.target.value }))}
                  className="input-field pr-10"
                  placeholder="Enter new password"
                  required
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('new')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPasswords.new ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            <div>
              <label className="form-label">Confirm New Password</label>
              <div className="relative">
                <input
                  type={showPasswords.confirm ? 'text' : 'password'}
                  value={passwordData.confirm_password}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, confirm_password: e.target.value }))}
                  className="input-field pr-10"
                  placeholder="Confirm new password"
                  required
                />
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility('confirm')}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPasswords.confirm ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isChangingPassword}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isChangingPassword ? 'Changing Password...' : 'Change Password'}
            </button>
          </form>
        </div>
      </div>

      {/* Social Media Connections */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Social Media Platform Connections
        </h3>
        
        <div className="mb-4">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Connect your social media accounts to enable direct publishing and scheduling of your generated content.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {socialConnections.map((connection) => (
            <div
              key={connection.platform}
              className={`p-4 rounded-lg border-2 transition-colors ${
                connection.connected
                  ? 'border-green-200 dark:border-green-700 bg-green-50 dark:bg-green-900/20'
                  : 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-medium text-gray-900 dark:text-white">
                  {connection.platform}
                </h4>
                {getConnectionStatusIcon(connection.connected)}
              </div>
              
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {getConnectionStatusText(connection.connected)}
              </p>
              
              {connection.connected && connection.username && (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  @{connection.username}
                </p>
              )}
              
              <button
                className={`mt-3 w-full px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  connection.connected
                    ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-300 dark:hover:bg-red-900/50'
                    : 'bg-primary-100 text-primary-700 hover:bg-primary-200 dark:bg-primary-900/30 dark:text-primary-300 dark:hover:bg-primary-900/50'
                }`}
                                 onClick={async () => {
                   if (connection.connected) {
                     // Disconnect logic
                     try {
                       await api.delete(`/oauth/connections/${connection.platform.toLowerCase()}`);
                       toast.success(`Disconnected from ${connection.platform}`);
                       // Update local state
                       setSocialConnections(prev => 
                         prev.map(conn => 
                           conn.platform === connection.platform
                             ? { ...conn, connected: false, username: undefined }
                             : conn
                         )
                       );
                     } catch (error) {
                       toast.error(`Failed to disconnect from ${connection.platform}`);
                     }
                   } else {
                     // Connect logic - navigate to connection page
                     navigate(`/connect/${connection.platform.toLowerCase()}`);
                   }
                 }}
              >
                {connection.connected ? 'Disconnect' : 'Connect'}
              </button>
            </div>
          ))}
        </div>

        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
            Why Connect Social Media?
          </h4>
          <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
            <li>• Direct publishing to your social media accounts</li>
            <li>• Schedule posts in advance</li>
            <li>• Track engagement and performance</li>
            <li>• Manage multiple platforms from one dashboard</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Profile;
