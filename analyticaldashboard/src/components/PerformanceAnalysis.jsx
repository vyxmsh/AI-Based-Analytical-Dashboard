import React, { useState, useEffect } from 'react';
import { TrendingUp, RefreshCw, AlertTriangle, CheckCircle, Target } from 'lucide-react';

const PerformanceAnalysis = ({ 
  refreshInterval = 30000, // 30 seconds default
  onDataUpdate = null,
  className = ""
}) => {
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [error, setError] = useState(null);

  // API Configuration
  const API_BASE_URL = 'http://localhost:5000/api';

  // Fetch performance data from API
  const fetchPerformanceData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch Gemini AI-powered performance data from backend
      const performanceResponse = await fetch(`${API_BASE_URL}/performance`);
      if (!performanceResponse.ok) {
        throw new Error(`Performance API error: ${performanceResponse.status}`);
      }
      const responseData = await performanceResponse.json();
      
      // Extract Gemini analysis data
      const geminiAnalysis = responseData.gemini_analysis || {};
      const traditionalAnalysis = responseData.traditional_analysis || {};
      const videoInfo = responseData.video_info || {};
      
      // Combine the data in the format expected by the component
      const combinedData = {
        // Primary data from Gemini AI analysis
        overallScore: geminiAnalysis.overall_score || traditionalAnalysis.overallScore || 75,
        grade: geminiAnalysis.grade || traditionalAnalysis.grade || 'B',
        scores: geminiAnalysis.scores || traditionalAnalysis.scores || {
          views: 70,
          engagement: 75,
          watchTime: 70,
          ctr: 75
        },
        
        // Enhanced Gemini AI data
        analysis: geminiAnalysis.analysis || {},
        recommendations: geminiAnalysis.recommendations || [],
        keyInsights: geminiAnalysis.key_insights || [],
        growthPotential: geminiAnalysis.growth_potential || 'medium',
        analysisMethod: geminiAnalysis.analysis_method || 'traditional',
        
        // Video information
        videoInfo: videoInfo,
        
        // Traditional analysis for comparison
        traditionalAnalysis: traditionalAnalysis,
        
        // Legacy fields for backward compatibility
        trends: traditionalAnalysis.trends || {},
        benchmarks: traditionalAnalysis.benchmarks || {},
        bonuses: traditionalAnalysis.bonuses || {},
        channelMaturity: traditionalAnalysis.channelMaturity || 0
      };
      
      setPerformanceData(combinedData);
      setLastUpdated(new Date());
      
      if (onDataUpdate) {
        onDataUpdate(combinedData);
      }
    } catch (err) {
      setError(`Failed to fetch performance data: ${err.message}`);
      console.error('Performance data fetch error:', err);
      
      // Fallback to mock data if API fails
      const fallbackData = {
        overallScore: 78,
        grade: 'B+',
        scores: {
          views: 100,
          engagement: 71.4,
          watchTime: 56.7,
          ctr: 87
        },
        trends: {
          views: { change: 5.2, direction: 'up' },
          engagement: { change: -2.1, direction: 'down' },
          watchTime: { change: -8.3, direction: 'down' },
          ctr: { change: 12.5, direction: 'up' }
        },
        recommendations: [
          {
            id: 1,
            type: 'warning',
            title: 'API Connection Failed',
            description: 'Unable to connect to the analytics API. Using fallback data for demonstration.',
            priority: 'high',
            impact: 'medium'
          }
        ]
      };
      
      setPerformanceData(fallbackData);
      setLastUpdated(new Date());
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchPerformanceData();
  }, []);

  // Auto-refresh functionality
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(fetchPerformanceData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getGradeColor = (grade) => {
    if (grade.startsWith('A')) return 'text-green-600';
    if (grade.startsWith('B')) return 'text-blue-600';
    if (grade.startsWith('C')) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'info':
        return <Target className="h-4 w-4 text-blue-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getRecommendationBgColor = (type) => {
    switch (type) {
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'info':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  if (error) {
    return (
      <div className={`bg-white rounded-2xl border border-gray-200 shadow-lg p-6 ${className}`}>
        <div className="text-center py-8">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Performance Data</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchPerformanceData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-2xl border border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
            <Target className="h-6 w-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">AI Performance Analysis</h3>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span>Last updated: {lastUpdated ? lastUpdated.toLocaleTimeString() : 'Never'}</span>
              {performanceData?.analysisMethod && (
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  performanceData.analysisMethod === 'gemini_ai' 
                    ? 'bg-purple-100 text-purple-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {performanceData.analysisMethod === 'gemini_ai' ? '🤖 Gemini AI' : '📊 Traditional'}
                </span>
              )}
            </div>
          </div>
        </div>
        <button
          onClick={fetchPerformanceData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Content */}
      {loading && !performanceData ? (
        <div className="flex items-center justify-center py-12">
          <RefreshCw className="h-8 w-8 text-blue-600 animate-spin" />
          <span className="ml-2 text-gray-600">Loading performance data...</span>
        </div>
      ) : error ? (
        <div className="text-center py-8">
          <div className="text-red-600 mb-2">⚠️ Analysis Error</div>
          <div className="text-sm text-gray-600">{error}</div>
        </div>
      ) : performanceData ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Overall Score */}
          <div className="text-center">
            <div className={`text-4xl font-bold mb-2 ${getScoreColor(performanceData?.overallScore || 0)}`}>
              {performanceData?.overallScore || 0}
            </div>
            <div className="text-lg font-semibold text-gray-700 mb-1">Overall Score</div>
            <div className={`text-2xl font-bold ${getGradeColor(performanceData?.grade || 'F')}`}>
              {performanceData?.grade || 'F'}
            </div>
            {performanceData?.trends?.overall && (
              <div className={`text-sm mt-2 ${performanceData.trends.overall.direction === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {performanceData.trends.overall.direction === 'up' ? '↗' : '↘'} {Math.abs(performanceData.trends.overall.change)}%
              </div>
            )}
          </div>

          {/* Individual Scores */}
          <div className="space-y-3">
            {performanceData?.scores && Object.entries(performanceData.scores).map(([key, value]) => (
              <div key={key} className="flex items-center justify-between">
                <span className="text-gray-600 capitalize">
                  {key === 'ctr' ? 'CTR Score' : `${key} Score`}
                </span>
                <div className="flex items-center gap-2">
                  <span className="font-semibold">{Math.round(value * 10) / 10}</span>
                  {performanceData.trends?.[key] && (
                    <span className={`text-xs ${performanceData.trends[key].direction === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                      {performanceData.trends[key].direction === 'up' ? '↗' : '↘'}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Recommendations */}
          <div className="space-y-3">
            <h4 className="font-semibold text-gray-900 mb-3">Recommendations</h4>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {performanceData?.recommendations?.map((rec, index) => (
                <div
                  key={rec.id || rec.title || index}
                  className={`p-3 rounded-lg border ${getRecommendationBgColor(rec.type)}`}
                >
                  <div className="flex items-start gap-2">
                    {getRecommendationIcon(rec.type)}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm text-gray-900 mb-1">
                        {rec.title}
                      </div>
                      <div className="text-xs text-gray-700 leading-relaxed mb-2">
                        {rec.description}
                      </div>
                      
                      {/* Action Items */}
                      {rec.actionItems && rec.actionItems.length > 0 && (
                        <div className="mt-2">
                          <div className="text-xs font-medium text-gray-600 mb-1">Action Items:</div>
                          <ul className="text-xs text-gray-600 space-y-1">
                            {rec.actionItems.slice(0, 3).map((item, index) => (
                              <li key={index} className="flex items-start gap-1">
                                <span className="text-gray-400 mt-0.5">•</span>
                                <span>{item}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-2 mt-2">
                        {rec.priority && (
                          <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                            rec.priority === 'high' 
                              ? 'bg-red-100 text-red-800' 
                              : rec.priority === 'medium'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-green-100 text-green-800'
                          }`}>
                            {rec.priority} priority
                          </span>
                        )}
                        {rec.impact && (
                          <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                            rec.impact === 'high' 
                              ? 'bg-blue-100 text-blue-800' 
                              : rec.impact === 'medium'
                              ? 'bg-indigo-100 text-indigo-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {rec.impact} impact
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};

export default PerformanceAnalysis;
