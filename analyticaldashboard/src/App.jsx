import React, { useState, useEffect } from 'react';
import { 
  Play, 
  ThumbsUp, 
  ThumbsDown, 
  MessageCircle, 
  Eye,
  Share2,
  Clock,
  TrendingUp,
  BarChart3,
  PieChart,
  Users,
  Calendar,
  Target,
  Globe,
  Heart,
  Download,
  Filter,
  Search,
  Bell,
  Settings,
  RefreshCw,
  Zap,
  Brain,
  FileText,
  Headphones,
  Video,
  MoreVertical,
  ArrowUp,
  ArrowDown,
  Sparkles,
  Activity,
  Monitor,
  Smartphone,
  Tablet,
  MapPin,
  Star,
  AlertTriangle,
  CheckCircle,
  Youtube,
  ExternalLink,
  Loader2
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart as RechartsPie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  Legend, 
  Pie,
  ComposedChart
} from 'recharts';
import PerformanceAnalysis from './components/PerformanceAnalysis';
import EngagementRateCard from './components/EngagementRateCard';
import SentimentAnalysis from './components/SentimentAnalysis';

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Data fetching functions
const fetchYouTubeData = async (channelUrl) => {
  try {
    const response = await fetch(`${API_BASE_URL}/fetch-youtube-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ channelUrl }),
    });
    if (!response.ok) throw new Error('Failed to fetch YouTube data');
    return await response.json();
  } catch (error) {
    console.error('Error fetching YouTube data:', error);
    return null;
  }
};

const fetchOverviewData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/overview`);
    if (!response.ok) throw new Error('Failed to fetch overview data');
    return await response.json();
  } catch (error) {
    console.error('Error fetching overview data:', error);
    return null;
  }
};

const fetchMetrics = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/metrics`);
    if (!response.ok) throw new Error('Failed to fetch metrics');
    return await response.json();
  } catch (error) {
    console.error('Error fetching metrics:', error);
    return null;
  }
};

const fetchViewsTrend = async (days = 7) => {
  try {
    const response = await fetch(`${API_BASE_URL}/views-trend?days=${days}`);
    if (!response.ok) throw new Error('Failed to fetch views trend');
    return await response.json();
  } catch (error) {
    console.error('Error fetching views trend:', error);
    return null;
  }
};

const fetchPerformance = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/performance`);
    if (!response.ok) throw new Error('Failed to fetch performance data');
    return await response.json();
  } catch (error) {
    console.error('Error fetching performance data:', error);
    return null;
  }
};

const fetchRecommendations = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/recommendations`);
    if (!response.ok) throw new Error('Failed to fetch recommendations');
    return await response.json();
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    return null;
  }
};

const refreshData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) throw new Error('Failed to refresh data');
    return await response.json();
  } catch (error) {
    console.error('Error refreshing data:', error);
    return null;
  }
};

// Fallback mock data for when API is not available
const mockYouTubeData = {
  currentVideo: {
    id: 'dQw4w9WgXcQ',
    title: 'How to Build Amazing React Applications - Complete Tutorial',
    thumbnail: 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=450&fit=crop',
    duration: '24:35',
    publishedAt: '2024-07-15T10:30:00Z',
    views: 156789,
    likes: 12456,
    dislikes: 234,
    comments: 1876,
    shares: 892,
    subscribers: 45230,
    watchTime: '2.1M hours',
    avgViewDuration: '18:42',
    clickThroughRate: 8.7,
    impressions: 2.1e6
  },
  
  viewsOverTime: [
    { date: '2024-07-15', views: 1234, watchTime: 25.4 },
    { date: '2024-07-16', views: 5678, watchTime: 102.3 },
    { date: '2024-07-17', views: 8901, watchTime: 187.6 },
    { date: '2024-07-18', views: 12345, watchTime: 298.7 },
    { date: '2024-07-19', views: 15678, watchTime: 389.2 },
    { date: '2024-07-20', views: 18920, watchTime: 445.8 },
    { date: '2024-07-21', views: 21234, watchTime: 501.9 }
  ],

  sentimentAnalysis: {
    positive: 89.2,
    neutral: 8.3,
    negative: 2.5,
    overallScore: 4.4,
    totalEngagements: 14566,
    likeToDislikeRatio: 53.2
  },

  mostPlayedSections: [
    { timestamp: '2:15', percentage: 95.2, section: 'Introduction Hook' },
    { timestamp: '8:30', percentage: 87.4, section: 'Key Concept Explanation' },
    { timestamp: '15:45', percentage: 92.1, section: 'Practical Demo' },
    { timestamp: '20:10', percentage: 78.6, section: 'Advanced Tips' },
    { timestamp: '23:20', percentage: 85.3, section: 'Conclusion & CTA' }
  ],

  transcription: {
    totalWords: 3452,
    readingTime: '14 minutes',
    keyTopics: ['React', 'JavaScript', 'Web Development', 'Tutorial', 'Programming'],
    sentiment: 'Positive',
    confidence: 94.7,
    summary: 'Comprehensive tutorial covering React application development with practical examples and best practices.'
  },

  performanceComparison: [
    { videoTitle: 'Current Video', views: 156789, likes: 12456, comments: 1876, performance: 100 },
    { videoTitle: 'Video 2', views: 142350, likes: 11200, comments: 1654, performance: 91 },
    { videoTitle: 'Video 3', views: 134567, likes: 10890, comments: 1532, performance: 86 },
    { videoTitle: 'Video 4', views: 128945, likes: 9876, comments: 1423, performance: 82 },
    { videoTitle: 'Video 5', views: 145231, likes: 11567, comments: 1789, performance: 93 },
    { videoTitle: 'Video 6', views: 112456, likes: 8901, comments: 1234, performance: 72 },
    { videoTitle: 'Video 7', views: 167890, likes: 13245, comments: 2012, performance: 107 },
    { videoTitle: 'Video 8', views: 98765, likes: 7654, comments: 987, performance: 63 },
    { videoTitle: 'Video 9', views: 156234, likes: 12890, comments: 1876, performance: 100 },
    { videoTitle: 'Video 10', views: 189345, likes: 15234, comments: 2134, performance: 121 }
  ],

  demographics: [
    { ageGroup: '13-17', percentage: 12.5, color: '#3b82f6' },
    { ageGroup: '18-24', percentage: 28.7, color: '#10b981' },
    { ageGroup: '25-34', percentage: 34.2, color: '#8b5cf6' },
    { ageGroup: '35-44', percentage: 18.3, color: '#f59e0b' },
    { ageGroup: '45-54', percentage: 4.8, color: '#ef4444' },
    { ageGroup: '55+', percentage: 1.5, color: '#6b7280' }
  ],

  deviceBreakdown: [
    { device: 'Mobile', percentage: 67.8, color: '#3b82f6' },
    { device: 'Desktop', percentage: 24.1, color: '#10b981' },
    { device: 'Tablet', percentage: 5.9, color: '#8b5cf6' },
    { device: 'TV', percentage: 2.2, color: '#f59e0b' }
  ],

  topCountries: [
    { country: 'United States', views: 45234, percentage: 28.8 },
    { country: 'India', views: 31456, percentage: 20.1 },
    { country: 'United Kingdom', views: 18765, percentage: 12.0 },
    { country: 'Canada', views: 12890, percentage: 8.2 },
    { country: 'Australia', views: 9876, percentage: 6.3 }
  ],

  revenueData: [
    { date: '2024-07-15', revenue: 12.45, cpm: 2.30 },
    { date: '2024-07-16', revenue: 28.90, cpm: 2.45 },
    { date: '2024-07-17', revenue: 45.67, cpm: 2.52 },
    { date: '2024-07-18', revenue: 62.34, cpm: 2.61 },
    { date: '2024-07-19', revenue: 78.90, cpm: 2.68 },
    { date: '2024-07-20', revenue: 89.23, cpm: 2.71 },
    { date: '2024-07-21', revenue: 95.67, cpm: 2.75 }
  ]
};

// Reusable Components
const Card = ({ children, className = '', onClick }) => (
  <div 
    className={`bg-white rounded-2xl border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 ${onClick ? 'cursor-pointer hover:scale-[1.01]' : ''} ${className}`}
    onClick={onClick}
  >
    {children}
  </div>
);

const GradientCard = ({ children, className = '', gradient = 'from-red-500 to-pink-600', isDarkMode = false }) => (
  <div className={
    `bg-gradient-to-br ${gradient} rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.01] ${className} ` +
    (isDarkMode ? 'bg-black border border-gray-700 text-white' : 'text-white')
  }>
    {children}
  </div>
);

const Button = ({ children, variant = 'primary', size = 'md', onClick, className = '', disabled = false }) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white shadow-lg hover:shadow-xl focus:ring-red-500',
    secondary: 'bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 hover:text-gray-900 shadow-sm hover:shadow-md focus:ring-gray-500',
    ghost: 'bg-transparent hover:bg-gray-100 text-gray-600 hover:text-gray-900 focus:ring-gray-500'
  };
  
  const sizes = {
    sm: 'px-3 py-2 text-sm gap-2',
    md: 'px-4 py-2.5 text-sm gap-2',
    lg: 'px-6 py-3 text-base gap-3'
  };
  
  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

const MetricCard = ({ title, value, change, changeType, icon: Icon, gradient, subtitle, isDarkMode = false }) => (
  <GradientCard gradient={gradient} className={`p-6 relative overflow-hidden ${isDarkMode ? 'border border-gray-700 bg-black text-white' : ''}`} isDarkMode={isDarkMode}>
    <div className={`absolute top-0 right-0 w-24 h-24 ${isDarkMode ? 'bg-white/10' : 'bg-white/10'} rounded-full -mr-12 -mt-12`}></div>
    <div className="relative">
      <div className="flex items-center justify-between mb-4">
        <Icon className={`h-7 w-7 ${isDarkMode ? 'text-white' : 'text-white/90'}`} />
        {change && (
          <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${isDarkMode ? 'bg-white/10 text-white border border-white/20' : 'bg-white/20'} text-xs font-medium ${
            changeType === 'increase' ? (isDarkMode ? 'text-green-300' : 'text-green-100') : changeType === 'decrease' ? (isDarkMode ? 'text-red-300' : 'text-red-100') : (isDarkMode ? 'text-white' : 'text-white/80')
          }`}>
            {changeType === 'increase' && <ArrowUp className="h-3 w-3" />}
            {changeType === 'decrease' && <ArrowDown className="h-3 w-3" />}
            {change}
          </div>
        )}
      </div>
      <div className={`text-2xl font-bold mb-1 ${isDarkMode ? 'text-white' : ''}`}>{value}</div>
      <div className={`text-sm ${isDarkMode ? 'text-white/80' : 'text-white/80'}`}>{title}</div>
      {subtitle && <div className={`text-xs mt-1 ${isDarkMode ? 'text-white/60' : 'text-white/60'}`}>{subtitle}</div>}
    </div>
  </GradientCard>
);

const ChartCard = ({ title, children, actions, className = '' }) => (
  <Card className={`p-6 ${className}`}>
    <div className="flex items-center justify-between mb-6">
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
      <div className="flex items-center gap-2">
        {actions}
      </div>
    </div>
    <div className="h-80">
      {children}
    </div>
  </Card>
);

const TabButton = ({ active, onClick, children, icon: Icon }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
      active 
        ? 'bg-red-100 text-red-700 shadow-sm' 
        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
    }`}
  >
    {Icon && <Icon className="h-4 w-4" />}
    {children}
  </button>
);

// YouTube Channel Input Component
const YouTubeChannelInput = ({ onDataFetched, loading, setLoading, isDarkMode = false }) => {
  const [channelUrl, setChannelUrl] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!channelUrl.trim()) {
      setError('Please enter a YouTube channel URL');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const data = await fetchYouTubeData(channelUrl);
      if (data && data.success) {
        setSuccess('YouTube data fetched successfully!');
        onDataFetched(data);
      } else {
        setError(data?.error || 'Failed to fetch YouTube data');
      }
    } catch (err) {
      setError('Failed to connect to the server');
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = () => {
    setChannelUrl('https://www.youtube.com/@GoogleDevelopers');
  };

  return (
    <Card className="p-6 mb-8">
      <div className="text-center mb-6">
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="p-3 bg-red-600 rounded-xl">
            <Youtube className="h-8 w-8 text-white" />
          </div>
          <div>
            <h2 className={`text-2xl font-bold ${isDarkMode ? 'text-gray-900' : 'text-gray-900'}`}>YouTube Channel Analytics</h2>
            <p className={`${isDarkMode ? 'text-gray-700' : 'text-gray-600'}`}>Enter a YouTube channel URL to fetch real data</p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="channelUrl" className="block text-sm font-medium text-gray-700 mb-2">
            YouTube Channel URL
          </label>
          <div className="flex gap-3">
            <input
              type="url"
              id="channelUrl"
              value={channelUrl}
              onChange={(e) => setChannelUrl(e.target.value)}
              placeholder="https://www.youtube.com/@channelname or https://www.youtube.com/channel/CHANNEL_ID"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors"
              disabled={loading}
            />
            <Button
              type="submit"
              variant="primary"
              disabled={loading || !channelUrl.trim()}
              className="px-6"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Fetching...
                </>
              ) : (
                <>
                  <ExternalLink className="h-4 w-4" />
                  Fetch Data
                </>
              )}
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={handleExampleClick}
            disabled={loading}
          >
            Try Example
          </Button>
          <span className="text-sm text-gray-500">
            Supports: @username, /channel/, /c/, /user/ URLs
          </span>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <span className="text-red-800 font-medium">{error}</span>
            </div>
          </div>
        )}

        {success && (
          <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-green-800 font-medium">{success}</span>
            </div>
          </div>
        )}
      </form>

      <div className="mt-6 p-4 bg-blue-50 rounded-xl">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Sparkles className="h-4 w-4 text-white" />
          </div>
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">What you'll get:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Channel statistics (subscribers, views, video count)</li>
              <li>• Recent videos with performance metrics</li>
              <li>• Engagement analytics and recommendations</li>
              <li>• Performance scoring and insights</li>
            </ul>
          </div>
        </div>
      </div>
    </Card>
  );
};

// Channel Info Component
const ChannelInfo = ({ channelData }) => {
  if (!channelData) return null;

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  return (
    <Card className="p-6 mb-8">
      <div className="flex items-start gap-6">
        <div className="flex-shrink-0">
          <img
            src={channelData.thumbnail}
            alt={channelData.title}
            className="w-24 h-24 object-cover rounded-xl shadow-md"
          />
        </div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{channelData.title}</h2>
          <p className="text-gray-600 mb-4 line-clamp-2">{channelData.description}</p>
          
          <div className="grid grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{formatNumber(channelData.subscriberCount)}</div>
              <div className="text-sm text-gray-600">Subscribers</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{formatNumber(channelData.videoCount)}</div>
              <div className="text-sm text-gray-600">Videos</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{formatNumber(channelData.viewCount)}</div>
              <div className="text-sm text-gray-600">Total Views</div>
            </div>
          </div>

          <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
            <span>Created: {new Date(channelData.publishedAt).toLocaleDateString()}</span>
            {channelData.country && (
              <>
                <span>•</span>
                <span>Country: {channelData.country}</span>
              </>
            )}
            {channelData.customUrl && (
              <>
                <span>•</span>
                <span>Custom URL: {channelData.customUrl}</span>
              </>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
};

// Main YouTube Dashboard Component
const YouTubeDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [dashboardData, setDashboardData] = useState(mockYouTubeData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiConnected, setApiConnected] = useState(false);
  const [channelData, setChannelData] = useState(null);
  const [hasFetchedData, setHasFetchedData] = useState(false);

  // Load data from API on component mount
  useEffect(() => {
    loadDashboardData();
  }, []);

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 30000);
    return () => clearInterval(timer);
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const overviewData = await fetchOverviewData();
      if (overviewData) {
        setDashboardData(prevData => ({
          ...prevData,
          ...overviewData,
          // Keep other tabs data as fallback
          sentimentAnalysis: prevData.sentimentAnalysis,
          mostPlayedSections: prevData.mostPlayedSections,
          transcription: prevData.transcription,
          performanceComparison: prevData.performanceComparison,
          demographics: prevData.demographics,
          deviceBreakdown: prevData.deviceBreakdown,
          topCountries: prevData.topCountries,
          revenueData: prevData.revenueData
        }));
        setApiConnected(true);
      } else {
        setApiConnected(false);
        setError('Unable to connect to backend API. Using mock data.');
      }
    } catch (err) {
      setApiConnected(false);
      setError('Failed to load data from API. Using mock data.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    await loadDashboardData();
  };

  const handleDataFetched = (data) => {
    setChannelData(data.channelData);
    setDashboardData(prevData => ({
      ...prevData,
      ...data.analytics,
      // Keep other tabs data as fallback
      sentimentAnalysis: prevData.sentimentAnalysis,
      mostPlayedSections: prevData.mostPlayedSections,
      transcription: prevData.transcription,
      performanceComparison: prevData.performanceComparison,
      demographics: prevData.demographics,
      deviceBreakdown: prevData.deviceBreakdown,
      topCountries: prevData.topCountries,
      revenueData: prevData.revenueData
    }));
    setHasFetchedData(true);
    setApiConnected(true);
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Export handler for sentiment and performance data
  const handleExport = () => {
    // Collect data
    const sentiment = dashboardData.sentimentAnalysis || {};
    const performance = dashboardData.performanceScore || {};

    // Flatten data for CSV
    const sentimentRows = [
      ['Metric', 'Value'],
      ...Object.entries(sentiment)
    ];
    const performanceRows = [
      ['Metric', 'Value'],
      ...Object.entries(performance)
    ];

    // Combine sections with headers
    let csv = 'Sentiment Analysis Data\n';
    csv += sentimentRows.map(row => row.join(',')).join('\n');
    csv += '\n\nPerformance Analysis Data\n';
    csv += performanceRows.map(row => row.join(',')).join('\n');

    // Download as file
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'youtube_analytics_export.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Night mode toggle state
  const [isDarkMode, setIsDarkMode] = useState(false);

  return (
    <div className={
      `min-h-screen transition-colors duration-500 ${isDarkMode ? 'bg-black' : 'bg-gradient-to-br from-gray-50 via-red-50 to-pink-50'}`
    }>

      {/* Header */}
      <header className={
        `${isDarkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-b border-gray-200'} sticky top-0 z-40 shadow-sm`
      }>
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-red-600 to-pink-600 rounded-xl">
                  <Play className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className={`text-2xl font-bold ${isDarkMode ? 'text-white' : 'text-gray-900'}`}>YouTube Analytics</h1>
                  <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-gray-500'}`}>
                    Last updated: {currentTime.toLocaleTimeString()}
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">

                <Button 
                  variant="secondary" 
                  size="sm" 
                  onClick={handleRefresh}
                  disabled={loading}
                >
                  <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                  {loading ? 'Loading...' : 'Refresh'}
                </Button>
                <Button variant="primary" size="sm" onClick={handleExport}>
                  <Download className="h-4 w-4" />
                  Export Data
                </Button>
                <Button variant="secondary" size="sm" onClick={() => setIsDarkMode(d => !d)}>
                  {isDarkMode ? 'Day Mode' : 'Night Mode'}
                </Button>
              </div>
              
              {/* API Connection Status */}
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${apiConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-600">
                  {apiConnected ? 'API Connected' : 'Using Mock Data'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="p-6">
        {/* YouTube Channel Input */}
        <YouTubeChannelInput 
          onDataFetched={handleDataFetched}
          loading={loading}
          setLoading={setLoading}
          isDarkMode={isDarkMode}
        />

        {/* Channel Info */}
        {channelData && <ChannelInfo channelData={channelData} />}

        {/* Error Notification */}
        {error && (
          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
              <span className="text-yellow-800 font-medium">{error}</span>
            </div>
          </div>
        )}

        {/* Show dashboard content only if data has been fetched or we have mock data */}
        {(hasFetchedData || !apiConnected) && (
          <>
            {/* Video Overview */}
            <Card className="p-6 mb-8">
              <div className="flex items-start gap-6">
                <div className="flex-shrink-0">
                  <div className="relative">
                    <img
                      src={dashboardData.currentVideo.thumbnail}
                      alt={dashboardData.currentVideo.title}
                      className="w-48 h-28 object-cover rounded-xl shadow-md"
                    />
                    <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
                      {dashboardData.currentVideo.duration}
                    </div>
                  </div>
                </div>
                <div className="flex-1">
                  <h2 className="text-xl font-bold text-gray-900 mb-2">
                    {dashboardData.currentVideo.title}
                  </h2>
                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                    <span>Published: {new Date(dashboardData.currentVideo.publishedAt).toLocaleDateString()}</span>
                    <span>•</span>
                    <span>Video ID: {dashboardData.currentVideo.id}</span>
                  </div>
                  <div className="grid grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900">{formatNumber(dashboardData.currentVideo.views)}</div>
                      <div className="text-sm text-gray-600">Views</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{formatNumber(dashboardData.currentVideo.likes)}</div>
                      <div className="text-sm text-gray-600">Likes</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{formatNumber(dashboardData.currentVideo.comments)}</div>
                      <div className="text-sm text-gray-600">Comments</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">{dashboardData.currentVideo.avgViewDuration}</div>
                      <div className="text-sm text-gray-600">Avg Duration</div>
                    </div>
                  </div>
                </div>
              </div>
            </Card>

            {/* Navigation Tabs */}
            <div className="flex items-center gap-2 mb-8 bg-white p-2 rounded-xl shadow-sm">
              <TabButton 
                active={activeTab === 'overview'} 
                onClick={() => setActiveTab('overview')}
                icon={Eye}
              >
                Overview
              </TabButton>
              <TabButton 
                active={activeTab === 'sentiment'} 
                onClick={() => setActiveTab('sentiment')}
                icon={Heart}
              >
                Sentiment Analysis
              </TabButton>


              <TabButton 
                active={activeTab === 'performance'} 
                onClick={() => setActiveTab('performance')}
                icon={TrendingUp}
              >
                Performance
              </TabButton>
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && (
              <div className="space-y-8">
                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <MetricCard
                    title="Last Video vs Total Channel Views"
                    value={`${formatNumber(dashboardData.currentVideo.lastVideoViews || dashboardData.currentVideo.views)} vs ${formatNumber(dashboardData.currentVideo.channelTotalViews || dashboardData.currentVideo.views)}`}
                    change="+12.5%"
                    changeType="increase"
                    icon={Eye}
                    gradient="from-blue-500 to-indigo-600"
                    subtitle="individual vs total"
                    isDarkMode={isDarkMode}
                  />
                  <MetricCard
                    title="Watch Time"
                    value={dashboardData.currentVideo.watchTime}
                    change="+8.3%"
                    changeType="increase"
                    icon={Clock}
                    gradient="from-green-500 to-emerald-600"
                    subtitle="total hours"
                    isDarkMode={isDarkMode}
                  />
                  <EngagementRateCard />
                </div>

                {/* Performance Score Card */}
                {dashboardData.performanceScore && (
                  <Card className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-green-600" />
                      Performance Analysis
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="text-center">
                        <div className="text-4xl font-bold text-green-600 mb-2">
                          {dashboardData.performanceScore?.overallScore || 'N/A'}
                        </div>
                        <div className="text-lg font-semibold text-gray-700 mb-1">
                          Overall Score
                        </div>
                        <div className="text-2xl font-bold text-blue-600">
                          {dashboardData.performanceScore?.grade || 'N/A'}
                        </div>
                      </div>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Views Score</span>
                          <span className="font-semibold">{dashboardData.performanceScore?.scores?.views || 'N/A'}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Engagement Score</span>
                          <span className="font-semibold">{dashboardData.performanceScore?.scores?.engagement || 'N/A'}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">Watch Time Score</span>
                          <span className="font-semibold">{dashboardData.performanceScore?.scores?.watchTime || 'N/A'}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-gray-600">CTR Score</span>
                          <span className="font-semibold">{dashboardData.performanceScore?.scores?.ctr || 'N/A'}</span>
                        </div>
                      </div>
                      <div className="space-y-3">
                        <h4 className="font-semibold text-gray-900 mb-3">Recommendations</h4>
                        {dashboardData.recommendations?.slice(0, 3).map((rec, index) => (
                          <div key={index} className="p-3 bg-blue-50 rounded-lg">
                            <div className="font-medium text-blue-900 text-sm">{rec.title}</div>
                            <div className="text-xs text-blue-700 mt-1">{rec.description}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Card>
                )}

                {/* Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  

                  
                </div>
              </div>
            )}

            {activeTab === 'sentiment' && (
              <div className="space-y-8">
                <div className="max-w-4xl mx-auto">
                  <SentimentAnalysis />
                </div>
              </div>
            )}

            {activeTab === 'engagement' && (
              <div className="space-y-8">
                <Card className="p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                    <Activity className="h-5 w-5 text-purple-500" />
                    Most Played Sections
                  </h3>
                  <div className="space-y-4">
                    {mockYouTubeData.mostPlayedSections.map((section, index) => (
                      <div key={index} className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                        <div className="flex-shrink-0 w-16 text-center">
                          <div className="text-sm font-mono bg-purple-100 text-purple-700 px-2 py-1 rounded">
                            {section.timestamp}
                          </div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-gray-900">{section.section}</span>
                            <span className="text-sm font-medium text-purple-600">{section.percentage}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-purple-600 h-2 rounded-full transition-all duration-300" 
                              style={{ width: `${section.percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-6">Audience Retention</h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={mockYouTubeData.mostPlayedSections.map((section, index) => ({
                        time: section.timestamp,
                        retention: section.percentage,
                        index: index
                      }))}>
                        <defs>
                          <linearGradient id="retentionGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                        <XAxis dataKey="time" tick={{ fill: '#64748b', fontSize: 12 }} />
                        <YAxis tick={{ fill: '#64748b', fontSize: 12 }} domain={[0, 100]} />
                        <Tooltip 
                          contentStyle={{
                            backgroundColor: 'white',
                            border: 'none',
                            borderRadius: '12px',
                            boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
                          }}
                          formatter={(value) => [`${value}%`, 'Retention']}
                        />
                        <Area
                          type="monotone"
                          dataKey="retention"
                          stroke="#8b5cf6"
                          strokeWidth={3}
                          fill="url(#retentionGradient)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </Card>

                  <Card className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-6">Engagement Hotspots</h3>
                    <div className="space-y-3">
                      {mockYouTubeData.mostPlayedSections.slice(0, 3).map((section, index) => (
                        <div key={index} className="flex items-center gap-3 p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                              {index + 1}
                            </div>
                          </div>
                          <div className="flex-1">
                            <div className="font-medium text-gray-900">{section.section}</div>
                            <div className="text-sm text-gray-600">Peak at {section.timestamp}</div>
                          </div>
                          <div className="text-lg font-bold text-purple-600">
                            {section.percentage}%
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>
              </div>
            )}



            {activeTab === 'performance' && (
              <div className="space-y-8">
                {/* Dynamic Performance Analysis Component */}
                <PerformanceAnalysis 
                  refreshInterval={30000}
                  onDataUpdate={(data) => {
                    console.log('Performance data updated:', data);
                    // You can handle the updated data here if needed
                  }}
                  className="mb-6"
                />

              </div>
            )}

            {activeTab === 'audience' && (
              <div className="space-y-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                </div>
              </div>
            )}


          </>
        )}
      </div>
    </div>
  );
};

export default YouTubeDashboard;