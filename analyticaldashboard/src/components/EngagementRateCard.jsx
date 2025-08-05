import React, { useState, useEffect } from 'react';
import { ThumbsUp, ArrowUp, ArrowDown, Info } from 'lucide-react';

const EngagementRateCard = () => {
  const [engagementData, setEngagementData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showTooltip, setShowTooltip] = useState(false);

  const API_BASE_URL = 'http://localhost:5000/api';

  const fetchEngagementData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/engagement-rate`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      setEngagementData(data);
    } catch (err) {
      setError(`Failed to fetch engagement data: ${err.message}`);
      console.error('Engagement data fetch error:', err);
      
      // Fallback data
      setEngagementData({
        engagementRate: 7.14,
        likes: 1250,
        comments: 89,
        views: 18750,
        totalEngagements: 1339,
        trend: { change: 2.1, direction: 'up' },
        calculation: '(1,250 likes + 89 comments) / 18,750 views × 100'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEngagementData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchEngagementData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getTrendIcon = () => {
    if (!engagementData?.trend) return null;
    
    if (engagementData.trend.direction === 'up') {
      return <ArrowUp className="h-3 w-3" />;
    } else if (engagementData.trend.direction === 'down') {
      return <ArrowDown className="h-3 w-3" />;
    }
    return null;
  };

  const getTrendColor = () => {
    if (!engagementData?.trend) return 'text-white/60';
    
    return engagementData.trend.direction === 'up' 
      ? 'text-green-100' 
      : engagementData.trend.direction === 'down' 
      ? 'text-red-100' 
      : 'text-white/60';
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl text-white shadow-lg p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-12 -mt-12"></div>
        <div className="relative">
          <div className="flex items-center justify-between mb-4">
            <ThumbsUp className="h-7 w-7 text-white/90" />
            <div className="animate-pulse bg-white/20 rounded-full px-2 py-1 w-16 h-6"></div>
          </div>
          <div className="animate-pulse bg-white/20 rounded w-20 h-8 mb-1"></div>
          <div className="text-white/80 text-sm">Engagement Rate</div>
          <div className="text-white/60 text-xs mt-1">loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.01] p-6 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -mr-12 -mt-12"></div>
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <ThumbsUp className="h-7 w-7 text-white/90" />
            <div className="relative">
              <Info 
                className="h-4 w-4 text-white/70 cursor-help" 
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
              />
              {showTooltip && (
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg whitespace-nowrap z-10">
                  <div className="font-medium mb-1">Engagement Rate Calculation:</div>
                  <div>{engagementData?.calculation || 'Loading...'}</div>
                  <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                </div>
              )}
            </div>
          </div>
          {engagementData?.trend && (
            <div className={`flex items-center gap-1 px-2 py-1 rounded-full bg-white/20 text-xs font-medium ${getTrendColor()}`}>
              {getTrendIcon()}
              {engagementData.trend.direction === 'up' ? '+' : engagementData.trend.direction === 'down' ? '-' : ''}{engagementData.trend.change}%
            </div>
          )}
        </div>
        
        <div className="text-2xl font-bold mb-1">
          {engagementData?.engagementRate ? `${engagementData.engagementRate}%` : 'N/A'}
        </div>
        
        <div className="text-white/80 text-sm">Engagement Rate</div>
        
        <div className="text-white/60 text-xs mt-1">
          {engagementData ? (
            <>
              {engagementData.likes?.toLocaleString()} likes + {engagementData.comments?.toLocaleString()} comments
              <br />
              from {engagementData.views?.toLocaleString()} views
            </>
          ) : (
            'likes + comments'
          )}
        </div>
        
        {error && (
          <div className="text-red-200 text-xs mt-2 opacity-75">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default EngagementRateCard;
