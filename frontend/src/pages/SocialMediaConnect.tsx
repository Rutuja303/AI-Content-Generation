import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Twitter, 
  Instagram, 
  Facebook, 
  Linkedin, 
  Mail, 
  ArrowLeft, 
  ExternalLink,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

interface PlatformConfig {
  name: string;
  icon: React.ComponentType<any>;
  color: string;
  description: string;
  steps: string[];
  apiEndpoint: string;
  scopes: string[];
}

const platformConfigs: Record<string, PlatformConfig> = {
  twitter: {
    name: 'Twitter',
    icon: Twitter,
    color: 'bg-blue-500',
    description: 'Connect your Twitter account to post tweets and threads directly from the platform.',
    steps: [
      'Click the "Connect Twitter" button below',
      'You will be redirected to Twitter for authorization',
      'Grant permission to post on your behalf',
      'Return to the platform to complete setup'
    ],
    apiEndpoint: '/auth/twitter',
    scopes: ['tweet.read', 'tweet.write', 'users.read']
  },
  instagram: {
    name: 'Instagram',
    icon: Instagram,
    color: 'bg-gradient-to-r from-purple-500 to-pink-500',
    description: 'Connect your Instagram account to post images and stories with AI-generated captions.',
    steps: [
      'Click the "Connect Instagram" button below',
      'You will be redirected to Meta for authorization',
      'Grant permission to post on your behalf',
      'Return to the platform to complete setup'
    ],
    apiEndpoint: '/auth/instagram',
    scopes: ['instagram_basic', 'instagram_content_publish']
  },
  facebook: {
    name: 'Facebook',
    icon: Facebook,
    color: 'bg-blue-600',
    description: 'Connect your Facebook account to post updates and engage with your audience.',
    steps: [
      'Click the "Connect Facebook" button below',
      'You will be redirected to Meta for authorization',
      'Grant permission to post on your behalf',
      'Return to the platform to complete setup'
    ],
    apiEndpoint: '/auth/facebook',
    scopes: ['pages_manage_posts', 'pages_read_engagement']
  },
  linkedin: {
    name: 'LinkedIn',
    icon: Linkedin,
    color: 'bg-blue-700',
    description: 'Connect your LinkedIn account to share professional content and articles.',
    steps: [
      'Click the "Connect LinkedIn" button below',
      'You will be redirected to LinkedIn for authorization',
      'Grant permission to post on your behalf',
      'Return to the platform to complete setup'
    ],
    apiEndpoint: '/auth/linkedin',
    scopes: ['r_liteprofile', 'w_member_social']
  },
  email: {
    name: 'Email',
    icon: Mail,
    color: 'bg-gray-600',
    description: 'Connect your email account to send newsletters and email campaigns.',
    steps: [
      'Enter your email service provider (Gmail, Outlook, etc.)',
      'Configure SMTP settings or use OAuth',
      'Test the connection with a sample email',
      'Save your email configuration'
    ],
    apiEndpoint: '/auth/email',
    scopes: ['send', 'compose']
  }
};

const SocialMediaConnect: React.FC = () => {
  const { platform } = useParams<{ platform: string }>();
  const navigate = useNavigate();
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'connecting' | 'success' | 'error'>('idle');

  const platformConfig = platformConfigs[platform || 'twitter'];

  if (!platformConfig) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Platform Not Found</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">The requested social media platform is not supported.</p>
          <button
            onClick={() => navigate('/profile')}
            className="btn-primary"
          >
            Back to Profile
          </button>
        </div>
      </div>
    );
  }

  const handleConnect = async () => {
    setIsConnecting(true);
    setConnectionStatus('connecting');

    try {
      console.log(`Attempting to connect to ${platform}...`);
      
      // Call the backend to initiate OAuth flow
      const response = await fetch(`http://localhost:8000/oauth/${platform}/connect`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json',
        },
      });

      console.log(`Response status: ${response.status}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('OAuth initiation failed:', errorData);
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('OAuth response:', data);
      
      if (data.status === 'connected') {
        // User is already connected
        setConnectionStatus('success');
        toast.success(`Already connected to ${platformConfig.name}!`);
        setTimeout(() => {
          navigate('/profile');
        }, 2000);
      } else if (data.auth_url) {
        // Redirect to OAuth URL
        console.log(`Redirecting to OAuth URL: ${data.auth_url}`);
        toast.success(`Redirecting to ${platformConfig.name} for authorization...`);
        setTimeout(() => {
          window.location.href = data.auth_url;
        }, 1000);
      } else {
        throw new Error('No OAuth URL received from backend');
      }
      
    } catch (error) {
      console.error('Connection error:', error);
      setConnectionStatus('error');
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      toast.error(`Failed to connect to ${platformConfig.name}: ${errorMessage}`);
      setIsConnecting(false);
    }
  };

  const getStatusIcon = () => {
    switch (connectionStatus) {
      case 'connecting':
        return <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>;
      case 'success':
        return <CheckCircle className="h-8 w-8 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-8 w-8 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (connectionStatus) {
      case 'connecting':
        return 'Connecting...';
      case 'success':
        return 'Connected Successfully!';
      case 'error':
        return 'Connection Failed';
      default:
        return '';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/profile')}
            className="flex items-center text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-4 transition-colors"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Profile
          </button>
          
          <div className="flex items-center space-x-4">
            <div className={`p-3 rounded-lg ${platformConfig.color}`}>
              <platformConfig.icon className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Connect {platformConfig.name}
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                {platformConfig.description}
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Connection Steps */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Connection Steps
            </h2>
            
            <div className="space-y-4">
              {platformConfig.steps.map((step, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-300 rounded-full flex items-center justify-center text-sm font-medium">
                    {index + 1}
                  </div>
                  <p className="text-gray-700 dark:text-gray-300">{step}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                What you'll be able to do:
              </h3>
              <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                <li>• Post content directly to {platformConfig.name}</li>
                <li>• Schedule posts in advance</li>
                <li>• Track engagement and performance</li>
                <li>• Manage multiple accounts from one dashboard</li>
              </ul>
            </div>
          </div>

          {/* Connection Panel */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Connect Your Account
            </h2>

            {connectionStatus === 'idle' && (
              <div className="text-center py-8">
                <div className={`p-4 rounded-full ${platformConfig.color} w-20 h-20 mx-auto mb-4 flex items-center justify-center`}>
                  <platformConfig.icon className="h-10 w-10 text-white" />
                </div>
                
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Ready to connect?
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Click the button below to start the connection process.
                </p>

                <button
                  onClick={handleConnect}
                  disabled={isConnecting}
                  className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Connect {platformConfig.name}
                </button>
              </div>
            )}

            {connectionStatus !== 'idle' && (
              <div className="text-center py-8">
                {getStatusIcon()}
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mt-4 mb-2">
                  {getStatusText()}
                </h3>
                
                {connectionStatus === 'connecting' && (
                  <p className="text-gray-600 dark:text-gray-400">
                    Please wait while we connect your account...
                  </p>
                )}
                
                {connectionStatus === 'success' && (
                  <p className="text-green-600 dark:text-green-400">
                    Redirecting you back to your profile...
                  </p>
                )}
                
                {connectionStatus === 'error' && (
                  <div className="space-y-3">
                    <p className="text-red-600 dark:text-red-400">
                      Something went wrong. Please try again.
                    </p>
                    <button
                      onClick={() => setConnectionStatus('idle')}
                      className="btn-secondary"
                    >
                      Try Again
                    </button>
                  </div>
                )}
              </div>
            )}

            <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <h3 className="font-medium text-gray-900 dark:text-white mb-2">
                Need Help?
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                If you encounter any issues during the connection process, please check our documentation or contact support.
              </p>
              <div className="flex space-x-3">
                <button className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center">
                  <ExternalLink className="h-4 w-4 mr-1" />
                  Documentation
                </button>
                <button className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 flex items-center">
                  <ExternalLink className="h-4 w-4 mr-1" />
                  Contact Support
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SocialMediaConnect;
