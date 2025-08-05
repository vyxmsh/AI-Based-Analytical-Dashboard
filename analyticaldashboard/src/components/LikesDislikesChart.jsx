import React, { useState, useEffect } from 'react';
import { ThumbsUp, ThumbsDown, TrendingUp } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const LikesDislikesChart = () => {
  const [likesDislikesData, setLikesDislikesData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const API_BASE_URL = 'http://localhost:5000/api';

  const fetchLikesDislikesData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/likes-dislikes`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      setLikesDislikesData(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(`Failed to fetch likes/dislikes data: ${err.message}`);
      console.error('Likes/dislikes data fetch error:', err);
      
      // Fallback data
      setLikesDislikesData({
        likes: 12456,
        dislikes: 234,
        total_reactions: 12690,
        like_percentage: 98.2,
        dislike_percentage: 1.8,
        ratio: 53.2,
        ratio_text: "53.2:1",
        chart_data: [
          { name: 'Likes', value: 12456, color: '#10b981' },
          { name: 'Dislikes', value: 234, color: '#ef4444' }
        ]
      });
      setLastUpdated(new Date());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLikesDislikesData();
    
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchLikesDislikesData, 60000);
    return () => clearInterval(interval);
  }, []);

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toLocaleString();
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-48 mb-6"></div>
          <div className="space-y-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-blue-500" />
          Like vs Dislike Analysis
        </h3>
        <button
          onClick={fetchLikesDislikesData}
          className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Ratio Display */}
      <div className="text-center mb-6">
        <div className="text-3xl font-bold text-gray-900 mb-2">
          {likesDislikesData?.ratio_text || '0:0'}
        </div>
        <p className="text-gray-600">Like to Dislike Ratio</p>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="flex items-center justify-center gap-2 mb-2">
            <ThumbsUp className="h-4 w-4 text-green-600" />
            <span className="text-sm font-medium text-green-700">Likes</span>
          </div>
          <div className="text-xl font-bold text-green-600">
            {formatNumber(likesDislikesData?.likes || 0)}
          </div>
          <div className="text-xs text-green-600">
            {likesDislikesData?.like_percentage || 0}%
          </div>
        </div>
        
        <div className="text-center p-3 bg-red-50 rounded-lg">
          <div className="flex items-center justify-center gap-2 mb-2">
            <ThumbsDown className="h-4 w-4 text-red-600" />
            <span className="text-sm font-medium text-red-700">Dislikes</span>
          </div>
          <div className="text-xl font-bold text-red-600">
            {formatNumber(likesDislikesData?.dislikes || 0)}
          </div>
          <div className="text-xs text-red-600">
            {likesDislikesData?.dislike_percentage || 0}%
          </div>
        </div>
      </div>

      {/* Pie Chart */}
      {likesDislikesData?.chart_data && (
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={likesDislikesData.chart_data}
              cx="50%"
              cy="50%"
              outerRadius={80}
              innerRadius={40}
              paddingAngle={5}
              dataKey="value"
            >
              {likesDislikesData.chart_data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value) => [formatNumber(value), '']}
              contentStyle={{
                backgroundColor: 'white',
                border: 'none',
                borderRadius: '12px',
                boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
              }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}

      {/* Last Updated */}
      {lastUpdated && (
        <div className="mt-4 text-xs text-gray-500 text-center">
          Last updated: {lastUpdated.toLocaleTimeString()}
        </div>
      )}
    </div>
  );
};

export default LikesDislikesChart;
