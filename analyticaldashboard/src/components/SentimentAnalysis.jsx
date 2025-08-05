import React, { useState, useEffect } from 'react';
import { 
  Heart, 
  Star, 
  TrendingUp, 
  MessageCircle, 
  ThumbsUp, 
  ThumbsDown, 
  Meh, 
  RefreshCw, 
  BarChart3, 
  Download 
} from 'lucide-react';

const SentimentAnalysis = () => {
  const [sentimentData, setSentimentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const API_BASE_URL = 'http://localhost:5000/api';

  const fetchSentimentData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/sentiment-analysis`);
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      const data = await response.json();
      setSentimentData(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(`Failed to fetch sentiment data: ${err.message}`);
      console.error('Sentiment data fetch error:', err);
      
      // Fallback data
      setSentimentData({
        overview: {
          positive_percentage: 72.3,
          neutral_percentage: 18.7,
          negative_percentage: 9.0,
          overall_rating: 4.2,
          total_comments: 20,
          avg_compound_score: 0.342
        },
        summary: {
          dominant_sentiment: 'positive'
        }
      });
      setLastUpdated(new Date());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSentimentData();
    
    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchSentimentData, 60000);
    return () => clearInterval(interval);
  }, []);

  const getSentimentIcon = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return <ThumbsUp className="h-5 w-5 text-green-600" />;
      case 'negative':
        return <ThumbsDown className="h-5 w-5 text-red-600" />;
      default:
        return <Meh className="h-5 w-5 text-yellow-600" />;
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive':
        return 'text-green-600';
      case 'negative':
        return 'text-red-600';
      default:
        return 'text-yellow-600';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-48 mb-6"></div>
          <div className="space-y-4">
            <div className="h-4 bg-gray-200 rounded w-full"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Heart className="h-5 w-5 text-red-500" />
          Sentiment Overview
        </h3>
        <button
          onClick={fetchSentimentData}
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

      <div className="space-y-4">
        {/* Sentiment Breakdown */}
        <div className="flex items-center justify-between">
          <span className="text-gray-600 flex items-center gap-2">
            <ThumbsUp className="h-4 w-4 text-green-600" />
            Positive
          </span>
          <div className="flex items-center gap-2">
            <div className="w-32 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full transition-all duration-500" 
                style={{ width: `${sentimentData?.overview?.positive_percentage || 0}%` }}
              ></div>
            </div>
            <span className="text-sm font-medium">
              {sentimentData?.overview?.positive_percentage || 0}%
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-600 flex items-center gap-2">
            <Meh className="h-4 w-4 text-yellow-600" />
            Neutral
          </span>
          <div className="flex items-center gap-2">
            <div className="w-32 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-yellow-500 h-2 rounded-full transition-all duration-500" 
                style={{ width: `${sentimentData?.overview?.neutral_percentage || 0}%` }}
              ></div>
            </div>
            <span className="text-sm font-medium">
              {sentimentData?.overview?.neutral_percentage || 0}%
            </span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-gray-600 flex items-center gap-2">
            <ThumbsDown className="h-4 w-4 text-red-600" />
            Negative
          </span>
          <div className="flex items-center gap-2">
            <div className="w-32 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-red-500 h-2 rounded-full transition-all duration-500" 
                style={{ width: `${sentimentData?.overview?.negative_percentage || 0}%` }}
              ></div>
            </div>
            <span className="text-sm font-medium">
              {sentimentData?.overview?.negative_percentage || 0}%
            </span>
          </div>
        </div>
      </div>

      {/* Video Information */}
      {sentimentData?.video_info && (
        <div className="mt-6 p-4 bg-blue-50 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <MessageCircle className="h-5 w-5 text-blue-600" />
            <span className="font-semibold text-blue-900">Video Analysis</span>
          </div>
          <div className="text-sm text-blue-700">
            <p className="font-medium truncate" title={sentimentData.video_info.video_title}>
              {sentimentData.video_info.video_title}
            </p>
            <p className="mt-1">
              Analyzed {sentimentData.video_info.comments_analyzed} comments
            </p>
            <div className="mt-2 flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${
                sentimentData.video_info.data_source === 'youtube_api' ? 'bg-green-500' : 'bg-yellow-500'
              }`}></div>
              <p className="font-medium">
                {sentimentData.video_info.analysis_method === 'gemini_llm' ? 'Google Gemini AI Analysis' : 'VADER Fallback Analysis'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Overall Rating */}
      <div className="mt-6 p-4 bg-green-50 rounded-xl">
        <div className="flex items-center gap-2 mb-2">
          <Star className="h-5 w-5 text-green-600" />
          <span className="font-semibold text-green-900">Overall Rating</span>
        </div>
        <div className="text-2xl font-bold text-green-600">
          {sentimentData?.overview?.overall_rating || 0}/5.0
        </div>
        <p className="text-sm text-green-700">
          Based on {sentimentData?.overview?.total_comments || 0} comments
        </p>
      </div>

      {/* Dominant Sentiment */}
      {sentimentData?.summary?.dominant_sentiment && (
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            {getSentimentIcon(sentimentData.summary.dominant_sentiment)}
            <span className="text-sm font-medium text-gray-700">
              Dominant Sentiment: 
            </span>
            <span className={`text-sm font-semibold capitalize ${getSentimentColor(sentimentData.summary.dominant_sentiment)}`}>
              {sentimentData.summary.dominant_sentiment}
            </span>
          </div>
        </div>
      )}

      {/* Sample Comments with LLM Results */}
      <div className="mt-6">
        <div className="flex items-center gap-2 mb-4">
          <MessageCircle className="h-5 w-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">LLM Analyzed Comments</h3>
        </div>
        <div className="space-y-3">
          {sentimentData?.detailed_sentiments?.slice(0, 8).map((comment, index) => (
            <div key={index} className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-700 mb-2">
                {comment.comment_text || comment.comment}
              </p>
              <div className="flex items-center gap-4 flex-wrap">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  comment.sentiment === 'positive' || comment.sentiment?.classification === 'positive' ? 'bg-green-100 text-green-800' :
                  comment.sentiment === 'negative' || comment.sentiment?.classification === 'negative' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {comment.sentiment || comment.sentiment?.classification}
                </span>
                {comment.confidence && (
                  <span className="text-xs text-gray-500">
                    Confidence: {(comment.confidence * 100).toFixed(1)}%
                  </span>
                )}
                {comment.sentiment?.compound && (
                  <span className="text-xs text-gray-500">
                    Score: {comment.sentiment.compound.toFixed(2)}
                  </span>
                )}
                {comment.source && (
                  <span className={`px-1 py-0.5 rounded text-xs ${
                    comment.source === 'gemini_api' ? 'bg-purple-100 text-purple-700' :
                    comment.source === 'vader_fallback' ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {comment.source === 'gemini_api' ? 'Gemini' : 
                     comment.source === 'vader_fallback' ? 'VADER' : 'Mock'}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CSV Download Link */}
      {sentimentData?.csv_results && (
        <div className="mt-6 p-4 bg-gray-50 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <Download className="h-5 w-5 text-gray-600" />
            <span className="font-semibold text-gray-900">Export Results</span>
          </div>
          <p className="text-sm text-gray-600 mb-3">
            Download the complete sentiment analysis results as CSV
          </p>
          <button
            onClick={() => {
              const blob = new Blob([sentimentData.csv_results], { type: 'text/csv' });
              const url = window.URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `sentiment_analysis_${sentimentData.video_info?.video_id || 'results'}.csv`;
              document.body.appendChild(a);
              a.click();
              window.URL.revokeObjectURL(url);
              document.body.removeChild(a);
            }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            Download CSV Results
          </button>
        </div>
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

export default SentimentAnalysis;
