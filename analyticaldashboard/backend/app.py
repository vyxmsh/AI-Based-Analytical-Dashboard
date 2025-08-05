from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random
import json
from urllib.parse import urlparse, parse_qs
import re
from dataclasses import dataclass
import csv
import io
import requests
import time
import numpy as np
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
from config import config


# Download VADER lexicon if not already present
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config[config_name])

# Configure CORS to allow all origins during development
CORS(app, origins="*", supports_credentials=False)

class YouTubeAPI:
    """YouTube API wrapper for fetching channel and video data"""
    
    def __init__(self):
        self.api_key = os.environ.get('YOUTUBE_API_KEY')
        if self.api_key:
            try:
                from googleapiclient.discovery import build
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("YouTube API initialized successfully")
            except ImportError:
                self.youtube = None
                logger.warning("YouTube API libraries not installed. Using mock data.")
        else:
            self.youtube = None
            logger.warning("YouTube API key not found. Using mock data.")
    
    def extract_channel_id_from_url(self, url: str) -> str:
        """Extract channel ID from various YouTube URL formats"""
        patterns = [
            r'youtube\.com/@([^/\s?]+)',  # Handle @username format
            r'youtube\.com/channel/([^/\s?]+)',  # Channel ID format
            r'youtube\.com/c/([^/\s?]+)',  # Custom URL format
            r'youtube\.com/user/([^/\s?]+)',  # User format
            r'youtube\.com/watch\?.*v=.*&.*channel_id=([^&\s]+)',  # Video with channel_id
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                extracted = match.group(1)
                # If it's a handle pattern, add @ prefix
                if pattern.startswith(r'youtube\.com/@'):
                    return f"@{extracted}"
                return extracted
        
        return None
    
    def get_channel_info(self, channel_url: str) -> Dict[str, Any]:
        """Get channel information from YouTube URL"""
        if not self.youtube:
            return self._get_mock_channel_data()
        
        try:
            channel_id = self.extract_channel_id_from_url(channel_url)
            if not channel_id:
                return {"error": "Invalid YouTube channel URL"}
            
            logger.info(f"Fetching channel info for ID: {channel_id}")
            
            # Check if it's a handle (starts with @)
            if channel_id.startswith('@'):
                # Use forHandle parameter for YouTube handles
                channel_response = self.youtube.channels().list(
                    part='snippet,statistics,brandingSettings',
                    forHandle=channel_id
                ).execute()
            else:
                # Use id parameter for channel IDs
                channel_response = self.youtube.channels().list(
                    part='snippet,statistics,brandingSettings',
                    id=channel_id
                ).execute()
            
            # Debug: Log the response structure
            logger.info(f"API Response keys: {list(channel_response.keys())}")
            logger.info(f"API Response: {channel_response}")
            
            if 'items' not in channel_response:
                logger.error(f"API Response missing 'items' key: {channel_response}")
                return {"error": "Invalid API response from YouTube"}
            
            if not channel_response['items']:
                return {"error": "Channel not found"}
            
            channel = channel_response['items'][0]
            snippet = channel['snippet']
            statistics = channel.get('statistics', {})
            
            return {
                "channelId": channel['id'],  # Use the actual channel ID from response
                "title": snippet['title'],
                "description": snippet.get('description', ''),
                "thumbnail": snippet['thumbnails']['high']['url'],
                "subscriberCount": int(statistics.get('subscriberCount', 0)),
                "videoCount": int(statistics.get('videoCount', 0)),
                "viewCount": int(statistics.get('viewCount', 0)),
                "publishedAt": snippet['publishedAt'],
                "country": snippet.get('country', ''),
                "customUrl": snippet.get('customUrl', ''),
                "keywords": snippet.get('keywords', ''),
                "defaultLanguage": snippet.get('defaultLanguage', ''),
                "defaultTab": snippet.get('defaultTab', ''),
                "featuredChannelsTitle": snippet.get('featuredChannelsTitle', ''),
                "featuredChannelsUrls": snippet.get('featuredChannelsUrls', []),
                "unsubscribedTrailer": snippet.get('unsubscribedTrailer', ''),
                "banner": snippet.get('banner', ''),
                "topicCategories": snippet.get('topicCategories', []),
                "topicIds": snippet.get('topicIds', [])
            }
            
        except Exception as e:
            logger.error(f"Error fetching channel info: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {"error": "Failed to fetch channel information"}
    
    def get_channel_videos(self, channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get recent videos from a channel"""
        if not self.youtube:
            return self._get_mock_videos_data()
        
        try:
            logger.info(f"Fetching videos for channel: {channel_id}")
            
            # Get channel's uploads playlist
            channel_response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_response = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()
            
            videos = []
            for item in playlist_response['items']:
                video_id = item['contentDetails']['videoId']
                snippet = item['snippet']
                
                # Get video statistics
                video_response = self.youtube.videos().list(
                    part='statistics,contentDetails',
                    id=video_id
                ).execute()
                
                if video_response['items']:
                    video_stats = video_response['items'][0]['statistics']
                    content_details = video_response['items'][0]['contentDetails']
                    
                    videos.append({
                        "videoId": video_id,
                        "title": snippet['title'],
                        "description": snippet.get('description', ''),
                        "thumbnail": snippet['thumbnails']['high']['url'],
                        "publishedAt": snippet['publishedAt'],
                        "duration": content_details.get('duration', 'PT0S'),
                        "viewCount": int(video_stats.get('viewCount', 0)),
                        "likeCount": int(video_stats.get('likeCount', 0)),
                        "commentCount": int(video_stats.get('commentCount', 0)),
                        "favoriteCount": int(video_stats.get('favoriteCount', 0)),
                        "tags": snippet.get('tags', [])
                    })
            
            logger.info(f"Fetched {len(videos)} videos")
            return videos

        
        except Exception as e:
            logger.error(f"Error fetching channel videos: {e}")
            return []
    
    def _get_mock_channel_data(self) -> Dict[str, Any]:
        """Return mock channel data when API is not available"""
        return {
            "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
            "title": "Google Developers",
            "description": "The official YouTube channel for Google Developers.",
            "thumbnail": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=450&fit=crop",
            "subscriberCount": 4523000,
            "videoCount": 1250,
            "viewCount": 1250000000,
            "publishedAt": "2007-08-23T00:34:19Z",
            "country": "US",
            "customUrl": "@GoogleDevelopers",
            "keywords": "google,developers,programming,coding,technology",
            "defaultLanguage": "en",
            "defaultTab": "featured",
            "featuredChannelsTitle": "Featured Channels",
            "featuredChannelsUrls": [],
            "unsubscribedTrailer": "",
            "banner": "",
            "topicCategories": ["Science & Technology"],
            "topicIds": ["/m/02kfj", "/m/02cct"]
        }
    
    def _get_mock_videos_data(self) -> List[Dict[str, Any]]:
        """Return mock videos data when API is not available"""
        return [
            {
                "videoId": "dQw4w9WgXcQ",
                "title": "How to Build Amazing React Applications - Complete Tutorial",
                "description": "Learn how to build modern React applications with this comprehensive tutorial.",
                "thumbnail": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=450&fit=crop",
                "publishedAt": "2024-07-15T10:30:00Z",
                "duration": "PT24M35S",
                "viewCount": 156789,
                "likeCount": 12456,
                "commentCount": 1876,
                "favoriteCount": 892,
                "tags": ["react", "javascript", "tutorial", "web development"]
            }
        ]
    
    def get_video_comments(self, video_id: str, max_results: int = 50) -> List[str]:
        """Get comments from a specific video"""
        if not self.youtube:
            return self._get_mock_comments()
        
        try:
            logger.info(f"Fetching comments for video: {video_id}")
            
            # Get comment threads for the video
            comments_response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                order='relevance'  # Get most relevant comments first
            ).execute()
            
            comments = []
            for item in comments_response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comment_text = comment['textDisplay']
                # Clean up the comment text
                comment_text = comment_text.replace('\n', ' ').strip()
                if comment_text and len(comment_text) > 10:  # Filter out very short comments
                    comments.append(comment_text)
            
            logger.info(f"Fetched {len(comments)} comments for video {video_id}")
            return comments
            
        except Exception as e:
            logger.error(f"Error fetching comments for video {video_id}: {e}")
            return self._get_mock_comments()
    
    def _get_mock_comments(self) -> List[str]:
        """Return mock comments as fallback"""
        return [
            "This video is absolutely amazing! Thank you for the great content.",
            "Really helpful tutorial, learned so much from this.",
            "Not sure I agree with this approach, seems overly complicated.",
            "Love your videos! Keep up the excellent work.",
            "Could have been explained better in some parts.",
            "Excellent explanation, very clear and easy to follow.",
            "This helped me solve my exact problem, thank you so much!",
            "Good video overall but the audio quality could be improved.",
            "Amazing content as always! You're the best.",
            "Perfect timing, I was just looking for this information.",
            "I disagree with some points but overall good video.",
            "Fantastic tutorial! Very well structured and informative.",
            "This is exactly what I needed, thank you!",
            "Great job explaining complex concepts in simple terms.",
            "Not my favorite video but still useful information.",
            "Incredible work! This channel never disappoints.",
            "Very helpful, will definitely try this approach.",
            "Good content but could be more concise.",
            "Outstanding tutorial! Subscribed immediately.",
            "This video changed my perspective completely."
        ]

class YouTubeAnalyticsEngine:
    """Core analytics engine for YouTube data processing"""
    
    def __init__(self):
        self.base_data = self._initialize_base_data()
        self.current_channel_data = None
    
    def _initialize_base_data(self) -> Dict[str, Any]:
        """Initialize base YouTube data structure"""
        return {
            "currentVideo": {
                "id": "dQw4w9WgXcQ",
                "title": "How to Build Amazing React Applications - Complete Tutorial",
                "thumbnail": "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=450&fit=crop",
                "duration": "24:35",
                "publishedAt": "2024-07-15T10:30:00Z",
                "views": 156789,
                "likes": 12456,
                "dislikes": 234,
                "comments": 1876,
                "shares": 892,
                "subscribers": 45230,
                "watchTime": "2.1M hours",
                "avgViewDuration": "18:42",
                "clickThroughRate": 8.7,
                "impressions": 2.1e6
            }
        }
    
    def update_channel_data(self, channel_data: Dict[str, Any], videos: List[Dict[str, Any]]):
        """Update analytics engine with new channel data"""
        self.current_channel_data = channel_data
        
        if videos:
            # Use the most recent video as current video
            latest_video = videos[0]
            self.base_data["currentVideo"] = {
                "id": latest_video["videoId"],
                "title": latest_video["title"],
                "thumbnail": latest_video["thumbnail"],
                "duration": self._parse_iso_duration(latest_video["duration"]),
                "publishedAt": latest_video["publishedAt"],
                "views": latest_video["viewCount"],
                "likes": latest_video["likeCount"],
                "dislikes": 0,  # YouTube API doesn't provide dislikes anymore
                "comments": latest_video["commentCount"],
                "shares": latest_video["favoriteCount"],
                "subscribers": channel_data.get("subscriberCount", 0),
                "watchTime": f"{latest_video['viewCount'] * 0.015:.1f}K hours",  # Estimate
                "avgViewDuration": "18:42",  # Estimate
                "clickThroughRate": 8.7,  # Estimate
                "impressions": latest_video["viewCount"] * 10  # Estimate
            }
    
    def _parse_iso_duration(self, duration: str) -> str:
        """Parse ISO 8601 duration to readable format"""
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if match:
            hours, minutes, seconds = match.groups()
            hours = int(hours) if hours else 0
            minutes = int(minutes) if minutes else 0
            seconds = int(seconds) if seconds else 0
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes}:{seconds:02d}"
        return "0:00"
    
    def calculate_views_over_time(self, days: int = 7) -> List[Dict[str, Any]]:
        """Calculate views over time with realistic growth patterns"""
        base_views = 1000
        growth_rate = 1.15  # 15% daily growth
        views_data = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-1-i)
            # Add some randomness to make it more realistic
            daily_views = int(base_views * (growth_rate ** i) * random.uniform(0.8, 1.2))
            watch_time = daily_views * random.uniform(0.015, 0.025)  # 1.5-2.5% watch time ratio
            
            views_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "views": daily_views,
                "watchTime": round(watch_time, 1)
            })
        
        return views_data
    
    def calculate_engagement_metrics(self) -> Dict[str, Any]:
        """Calculate engagement metrics with advanced analytics"""
        current_video = self.base_data["currentVideo"]
        
        # Calculate engagement rate
        total_engagements = current_video["likes"] + current_video["comments"] + current_video["shares"]
        engagement_rate = (total_engagements / current_video["views"]) * 100
        
        # Calculate like to dislike ratio
        like_dislike_ratio = current_video["likes"] / current_video["dislikes"] if current_video["dislikes"] > 0 else 0
        
        # Calculate watch time percentage
        duration_seconds = self._parse_duration(current_video["duration"])
        avg_duration_seconds = self._parse_duration(current_video["avgViewDuration"])
        watch_time_percentage = (avg_duration_seconds / duration_seconds) * 100
        
        return {
            "engagementRate": round(engagement_rate, 2),
            "likeToDislikeRatio": round(like_dislike_ratio, 1),
            "watchTimePercentage": round(watch_time_percentage, 1),
            "totalEngagements": total_engagements,
            "avgViewDurationSeconds": avg_duration_seconds
        }
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to seconds"""
        parts = duration_str.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        return 0
    
    def calculate_performance_score(self) -> Dict[str, Any]:
        """Calculate overall performance score using advanced YouTube analytics algorithm"""
        current_video = self.base_data["currentVideo"]
        engagement_metrics = self.calculate_engagement_metrics()
        
        # Use channel data if available for more accurate scoring
        channel_views = self.current_channel_data.get("viewCount", 0) if self.current_channel_data else current_video["views"]
        channel_subscribers = self.current_channel_data.get("subscriberCount", 0) if self.current_channel_data else 45230
        video_count = self.current_channel_data.get("videoCount", 0) if self.current_channel_data else 150
        
        # Industry benchmarks based on YouTube Creator Playbook and analytics research
        benchmarks = {
            "excellent_ctr": 10.0,      # Top 10% of videos
            "good_ctr": 4.0,           # Above average
            "average_ctr": 2.0,        # YouTube average
            "excellent_engagement": 8.0, # Top tier engagement
            "good_engagement": 4.0,     # Good engagement
            "average_engagement": 2.0,  # Average engagement
            "excellent_retention": 70.0, # Excellent watch time %
            "good_retention": 50.0,     # Good watch time %
            "average_retention": 30.0,  # Average watch time %
            "viral_threshold": 0.05,    # 5% of subscribers for viral content
            "good_view_rate": 0.02,     # 2% of subscribers is good
            "average_view_rate": 0.01   # 1% of subscribers is average
        }
        
        # Calculate individual metric scores using percentile-based scoring
        
        # 1. Views Performance Score (0-100)
        if channel_subscribers > 0:
            view_rate = current_video["views"] / channel_subscribers
            if view_rate >= benchmarks["viral_threshold"]:
                views_score = 95 + min(5, (view_rate - benchmarks["viral_threshold"]) * 100)
            elif view_rate >= benchmarks["good_view_rate"]:
                views_score = 70 + ((view_rate - benchmarks["good_view_rate"]) / 
                                   (benchmarks["viral_threshold"] - benchmarks["good_view_rate"])) * 25
            elif view_rate >= benchmarks["average_view_rate"]:
                views_score = 40 + ((view_rate - benchmarks["average_view_rate"]) / 
                                   (benchmarks["good_view_rate"] - benchmarks["average_view_rate"])) * 30
            else:
                views_score = min(40, (view_rate / benchmarks["average_view_rate"]) * 40)
        else:
            # Fallback for channels without subscriber data
            views_score = min(100, (current_video["views"] / 100000) * 80)
        
        # 2. Click-Through Rate Score (0-100)
        ctr = current_video["clickThroughRate"]
        if ctr >= benchmarks["excellent_ctr"]:
            ctr_score = 95 + min(5, (ctr - benchmarks["excellent_ctr"]) / 2)
        elif ctr >= benchmarks["good_ctr"]:
            ctr_score = 75 + ((ctr - benchmarks["good_ctr"]) / 
                             (benchmarks["excellent_ctr"] - benchmarks["good_ctr"])) * 20
        elif ctr >= benchmarks["average_ctr"]:
            ctr_score = 50 + ((ctr - benchmarks["average_ctr"]) / 
                             (benchmarks["good_ctr"] - benchmarks["average_ctr"])) * 25
        else:
            ctr_score = (ctr / benchmarks["average_ctr"]) * 50
        
        # 3. Engagement Rate Score (0-100)
        engagement_rate = engagement_metrics["engagementRate"]
        if engagement_rate >= benchmarks["excellent_engagement"]:
            engagement_score = 95 + min(5, (engagement_rate - benchmarks["excellent_engagement"]) / 2)
        elif engagement_rate >= benchmarks["good_engagement"]:
            engagement_score = 75 + ((engagement_rate - benchmarks["good_engagement"]) / 
                                    (benchmarks["excellent_engagement"] - benchmarks["good_engagement"])) * 20
        elif engagement_rate >= benchmarks["average_engagement"]:
            engagement_score = 50 + ((engagement_rate - benchmarks["average_engagement"]) / 
                                    (benchmarks["good_engagement"] - benchmarks["average_engagement"])) * 25
        else:
            engagement_score = (engagement_rate / benchmarks["average_engagement"]) * 50
        
        # 4. Watch Time/Retention Score (0-100)
        retention_percentage = engagement_metrics["watchTimePercentage"]
        if retention_percentage >= benchmarks["excellent_retention"]:
            watch_time_score = 95 + min(5, (retention_percentage - benchmarks["excellent_retention"]) / 10)
        elif retention_percentage >= benchmarks["good_retention"]:
            watch_time_score = 75 + ((retention_percentage - benchmarks["good_retention"]) / 
                                    (benchmarks["excellent_retention"] - benchmarks["good_retention"])) * 20
        elif retention_percentage >= benchmarks["average_retention"]:
            watch_time_score = 50 + ((retention_percentage - benchmarks["average_retention"]) / 
                                    (benchmarks["good_retention"] - benchmarks["average_retention"])) * 25
        else:
            watch_time_score = (retention_percentage / benchmarks["average_retention"]) * 50
        
        # Advanced weighted scoring with dynamic weights based on content type and channel maturity
        channel_maturity_factor = min(1.0, video_count / 100)  # Mature channels have 100+ videos
        
        # Dynamic weights that adjust based on channel maturity
        if channel_maturity_factor > 0.8:  # Mature channel
            weights = {
                "views": 0.20,
                "engagement_rate": 0.35,  # More weight on engagement for mature channels
                "watch_time": 0.30,       # High importance on retention
                "click_through_rate": 0.15
            }
        elif channel_maturity_factor > 0.4:  # Growing channel
            weights = {
                "views": 0.25,
                "engagement_rate": 0.30,
                "watch_time": 0.25,
                "click_through_rate": 0.20
            }
        else:  # New channel
            weights = {
                "views": 0.30,           # More weight on views for new channels
                "engagement_rate": 0.25,
                "watch_time": 0.25,
                "click_through_rate": 0.20
            }
        
        # Calculate weighted performance score
        performance_score = (
            views_score * weights["views"] +
            engagement_score * weights["engagement_rate"] +
            watch_time_score * weights["watch_time"] +
            ctr_score * weights["click_through_rate"]
        )
        
        # Apply bonus/penalty factors
        
        # Consistency bonus (if channel has good historical performance)
        consistency_bonus = min(5, channel_maturity_factor * 5)
        
        # Viral content bonus (if views significantly exceed subscriber base)
        if channel_subscribers > 0:
            viral_ratio = current_video["views"] / channel_subscribers
            if viral_ratio > 0.1:  # 10% of subscribers is viral
                viral_bonus = min(10, (viral_ratio - 0.1) * 20)
            else:
                viral_bonus = 0
        else:
            viral_bonus = 0
        
        # Apply bonuses
        final_score = min(100, performance_score + consistency_bonus + viral_bonus)
        
        # Generate trend indicators
        trends = self._calculate_performance_trends({
            "views": views_score,
            "engagement": engagement_score,
            "watchTime": watch_time_score,
            "ctr": ctr_score
        })
        
        return {
            "overallScore": round(final_score, 1),
            "scores": {
                "views": round(views_score, 1),
                "engagement": round(engagement_score, 1),
                "watchTime": round(watch_time_score, 1),
                "ctr": round(ctr_score, 1)
            },
            "grade": self._get_performance_grade(final_score),
            "trends": trends,
            "benchmarks": {
                "viewRate": round((current_video["views"] / max(channel_subscribers, 1)) * 100, 3),
                "industry": {
                    "avgCTR": benchmarks["average_ctr"],
                    "avgEngagement": benchmarks["average_engagement"],
                    "avgRetention": benchmarks["average_retention"]
                }
            },
            "bonuses": {
                "consistency": round(consistency_bonus, 1),
                "viral": round(viral_bonus, 1)
            },
            "channelMaturity": round(channel_maturity_factor * 100, 1)
        }
    
    def _calculate_performance_trends(self, scores: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Calculate performance trends and changes for each metric"""
        # Simulate historical data for trend calculation
        # In a real implementation, this would compare against historical performance
        trends = {}
        
        for metric, current_score in scores.items():
            # Simulate previous period score (with some randomness for demo)
            # In production, this would come from historical data
            historical_variance = random.uniform(-10, 10)
            previous_score = max(0, min(100, current_score + historical_variance))
            
            change = current_score - previous_score
            change_percentage = (change / max(previous_score, 1)) * 100
            
            if abs(change) < 2:
                direction = "stable"
                trend_strength = "weak"
            elif change > 0:
                direction = "up"
                trend_strength = "strong" if change > 10 else "moderate"
            else:
                direction = "down"
                trend_strength = "strong" if change < -10 else "moderate"
            
            trends[metric] = {
                "change": round(change, 1),
                "changePercentage": round(change_percentage, 1),
                "direction": direction,
                "strength": trend_strength
            }
        
        return trends
    
    def _get_performance_grade(self, score: float) -> str:
        """Get performance grade based on score"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        elif score >= 40:
            return "D"
        else:
            return "F"
    
    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on advanced analytics"""
        current_video = self.base_data["currentVideo"]
        engagement_metrics = self.calculate_engagement_metrics()
        performance = self.calculate_performance_score()
        
        # Use channel data for more accurate recommendations
        channel_views = self.current_channel_data.get("viewCount", 0) if self.current_channel_data else current_video["views"]
        channel_subscribers = self.current_channel_data.get("subscriberCount", 0) if self.current_channel_data else 45230
        video_count = self.current_channel_data.get("videoCount", 0) if self.current_channel_data else 150
        
        recommendations = []
        scores = performance["scores"]
        trends = performance["trends"]
        
        # Priority-based recommendation system
        
        # 1. Critical Issues (Score < 40)
        if scores["views"] < 40:
            view_rate = current_video["views"] / max(channel_subscribers, 1)
            if view_rate < 0.005:  # Less than 0.5% of subscribers
                recommendations.append({
                    "id": 1,
                    "type": "warning",
                    "title": "Critical: Very Low View Performance",
                    "description": f"Only {view_rate*100:.2f}% of your subscribers viewed this content. Consider: 1) Better thumbnails, 2) More engaging titles, 3) Optimal posting times, 4) Community engagement.",
                    "priority": "high",
                    "impact": "high",
                    "category": "Views",
                    "actionItems": [
                        "A/B test thumbnail designs",
                        "Analyze competitor titles",
                        "Post when your audience is most active",
                        "Engage with comments within first hour"
                    ]
                })
        
        if scores["watchTime"] < 40:
            recommendations.append({
                "id": 2,
                "type": "warning",
                "title": "Critical: Poor Audience Retention",
                "description": f"Viewers are leaving after {engagement_metrics['watchTimePercentage']:.1f}% of your video. This severely impacts YouTube's algorithm ranking.",
                "priority": "high",
                "impact": "high",
                "category": "Retention",
                "actionItems": [
                    "Hook viewers in first 15 seconds",
                    "Remove slow/boring sections",
                    "Add pattern interrupts every 30 seconds",
                    "Use jump cuts and visual variety"
                ]
            })
        
        # 2. Improvement Opportunities (Score 40-70)
        if 40 <= scores["ctr"] < 70:
            ctr_value = current_video["clickThroughRate"]
            recommendations.append({
                "id": 3,
                "type": "info",
                "title": "Optimize Click-Through Rate",
                "description": f"Your CTR of {ctr_value:.1f}% is below optimal. Industry leaders achieve 8-12% CTR through strategic thumbnail and title optimization.",
                "priority": "medium",
                "impact": "high",
                "category": "CTR",
                "actionItems": [
                    "Use bright, contrasting colors in thumbnails",
                    "Include emotional expressions in thumbnails",
                    "Write curiosity-driven titles",
                    "Test different thumbnail styles"
                ]
            })
        
        if 40 <= scores["engagement"] < 70:
            recommendations.append({
                "id": 4,
                "type": "info",
                "title": "Boost Audience Engagement",
                "description": f"Engagement rate of {engagement_metrics['engagementRate']:.1f}% can be improved. Higher engagement signals quality content to YouTube's algorithm.",
                "priority": "medium",
                "impact": "medium",
                "category": "Engagement",
                "actionItems": [
                    "Ask specific questions to encourage comments",
                    "Create polls and community posts",
                    "Respond to comments quickly",
                    "End videos with clear call-to-action"
                ]
            })
        
        # 3. Excellent Performance Recognition (Score > 80)
        if scores["ctr"] > 80:
            recommendations.append({
                "id": 5,
                "type": "success",
                "title": "Excellent Click-Through Rate!",
                "description": f"Outstanding CTR of {current_video['clickThroughRate']:.1f}%! This is significantly above average. Document what worked for future videos.",
                "priority": "low",
                "impact": "high",
                "category": "CTR",
                "actionItems": [
                    "Document successful thumbnail elements",
                    "Analyze title structure for patterns",
                    "Create template based on this success",
                    "Share insights with team/community"
                ]
            })
        
        if scores["engagement"] > 80:
            recommendations.append({
                "id": 6,
                "type": "success",
                "title": "Exceptional Audience Engagement!",
                "description": f"Your engagement rate of {engagement_metrics['engagementRate']:.1f}% is excellent! This content resonates strongly with your audience.",
                "priority": "low",
                "impact": "medium",
                "category": "Engagement",
                "actionItems": [
                    "Create similar content themes",
                    "Analyze what topics drove engagement",
                    "Consider making this a series",
                    "Promote this video across platforms"
                ]
            })
        
        # 4. Trend-based Recommendations
        for metric, trend_data in trends.items():
            if trend_data["direction"] == "down" and trend_data["strength"] == "strong":
                metric_name = {
                    "views": "Views",
                    "engagement": "Engagement",
                    "watchTime": "Watch Time",
                    "ctr": "Click-Through Rate"
                }.get(metric, metric)
                
                recommendations.append({
                    "id": 7 + len(recommendations),
                    "type": "warning",
                    "title": f"Declining {metric_name} Trend",
                    "description": f"{metric_name} has dropped by {abs(trend_data['change']):.1f} points recently. This needs immediate attention to prevent further decline.",
                    "priority": "high",
                    "impact": "medium",
                    "category": "Trends",
                    "actionItems": [
                        f"Analyze recent {metric_name.lower()} performance",
                        "Compare with successful past content",
                        "Identify what changed in your approach",
                        "Test returning to previous successful strategies"
                    ]
                })
        
        # 5. Channel Maturity-based Recommendations
        channel_maturity = performance["channelMaturity"]
        if channel_maturity < 30:  # New channel
            recommendations.append({
                "id": 10,
                "type": "info",
                "title": "New Channel Growth Strategy",
                "description": f"As a newer channel ({video_count} videos), focus on consistency and finding your niche. Establish a regular posting schedule.",
                "priority": "medium",
                "impact": "high",
                "category": "Growth",
                "actionItems": [
                    "Post consistently (same days/times)",
                    "Focus on one main topic/niche",
                    "Engage actively with similar channels",
                    "Create eye-catching channel art"
                ]
            })
        elif channel_maturity > 80:  # Mature channel
            recommendations.append({
                "id": 11,
                "type": "info",
                "title": "Mature Channel Optimization",
                "description": f"With {video_count}+ videos, focus on optimizing your best content and exploring new formats to maintain growth.",
                "priority": "low",
                "impact": "medium",
                "category": "Optimization",
                "actionItems": [
                    "Update thumbnails on top-performing videos",
                    "Create playlists to increase session time",
                    "Experiment with new content formats",
                    "Consider collaborations with other creators"
                ]
            })
        
        # 6. Viral Potential Recognition
        if performance["bonuses"]["viral"] > 5:
            recommendations.append({
                "id": 12,
                "type": "success",
                "title": "Viral Content Detected!",
                "description": f"This content is performing exceptionally well beyond your subscriber base! Capitalize on this momentum.",
                "priority": "high",
                "impact": "high",
                "category": "Viral",
                "actionItems": [
                    "Promote heavily across all social platforms",
                    "Create follow-up content quickly",
                    "Engage with all comments to boost algorithm",
                    "Consider paid promotion to amplify reach"
                ]
            })
        
        # Sort recommendations by priority and impact
        priority_order = {"high": 3, "medium": 2, "low": 1}
        impact_order = {"high": 3, "medium": 2, "low": 1}
        
        recommendations.sort(
            key=lambda x: (priority_order.get(x["priority"], 0), impact_order.get(x["impact"], 0)),
            reverse=True
        )
        
        return recommendations[:6]  # Return top 6 recommendations
    
    def get_overview_data(self) -> Dict[str, Any]:
        """Get comprehensive overview data"""
        views_over_time = self.calculate_views_over_time()
        engagement_metrics = self.calculate_engagement_metrics()
        performance_score = self.calculate_performance_score()
        recommendations = self.generate_recommendations()
        
        # Get both last video views and channel total views
        last_video_views = self.base_data["currentVideo"]["views"]
        channel_total_views = self.current_channel_data.get("viewCount", 0) if self.current_channel_data else last_video_views
        
        # Create a modified currentVideo object with both values
        current_video_with_comparison = self.base_data["currentVideo"].copy()
        current_video_with_comparison["lastVideoViews"] = last_video_views
        current_video_with_comparison["channelTotalViews"] = channel_total_views
        
        return {
            "currentVideo": current_video_with_comparison,  # Contains both last video and channel total views
            "viewsOverTime": views_over_time,
            "engagementMetrics": engagement_metrics,
            "performanceScore": performance_score,
            "recommendations": recommendations,
            "channelData": self.current_channel_data,
            "lastUpdated": datetime.now().isoformat(),
            "analyticsVersion": "1.0.0"
        }

class SentimentAnalyzer:
    """Sentiment analysis engine for YouTube comments"""
    
    def __init__(self):
        self.analyzer = None
        if SENTIMENT_AVAILABLE:
            self.analyzer = SentimentIntensityAnalyzer()
            logger.info("Sentiment analyzer initialized successfully")
        else:
            logger.warning("Sentiment analyzer not available, using mock data")
    
    def preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""
        if not text:
            return ""
        
        # Remove extra whitespace and convert to lowercase
        text = re.sub(r'\s+', ' ', text.strip().lower())
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of a single text"""
        if not self.analyzer or not text:
            # Return mock sentiment if analyzer not available
            return {
                'pos': random.uniform(0.1, 0.9),
                'neu': random.uniform(0.1, 0.3),
                'neg': random.uniform(0.0, 0.2),
                'compound': random.uniform(-0.5, 0.8)
            }
        
        processed_text = self.preprocess_text(text)
        scores = self.analyzer.polarity_scores(processed_text)
        return scores
    
    def analyze_comments(self, comments: List[str]) -> Dict[str, Any]:
        """Analyze sentiment for a list of comments"""
        if not comments:
            return self._get_mock_sentiment_data()
        
        sentiments = []
        positive_count = 0
        neutral_count = 0
        negative_count = 0
        total_compound = 0
        
        for comment in comments:
            if not comment or len(comment.strip()) < 3:
                continue
                
            sentiment = self.analyze_sentiment(comment)
            sentiments.append({
                'text': comment[:100] + '...' if len(comment) > 100 else comment,
                'sentiment': sentiment,
                'classification': self._classify_sentiment(sentiment['compound'])
            })
            
            # Count classifications
            if sentiment['compound'] >= 0.05:
                positive_count += 1
            elif sentiment['compound'] <= -0.05:
                negative_count += 1
            else:
                neutral_count += 1
            
            total_compound += sentiment['compound']
        
        total_comments = len(sentiments)
        if total_comments == 0:
            return self._get_mock_sentiment_data()
        
        # Calculate percentages
        positive_pct = (positive_count / total_comments) * 100
        neutral_pct = (neutral_count / total_comments) * 100
        negative_pct = (negative_count / total_comments) * 100
        
        # Calculate overall rating (1-5 scale)
        avg_compound = total_compound / total_comments
        overall_rating = max(1.0, min(5.0, 3.0 + (avg_compound * 2)))
        
        return {
            'overview': {
                'positive_percentage': round(positive_pct, 1),
                'neutral_percentage': round(neutral_pct, 1),
                'negative_percentage': round(negative_pct, 1),
                'overall_rating': round(overall_rating, 1),
                'total_comments': total_comments,
                'avg_compound_score': round(avg_compound, 3)
            },
            'detailed_sentiments': sentiments[:50],  # Limit to first 50 for performance
            'summary': {
                'most_positive': max(sentiments, key=lambda x: x['sentiment']['compound']) if sentiments else None,
                'most_negative': min(sentiments, key=lambda x: x['sentiment']['compound']) if sentiments else None,
                'dominant_sentiment': 'positive' if positive_pct > max(neutral_pct, negative_pct) else 
                                    'negative' if negative_pct > neutral_pct else 'neutral'
            },
            'last_updated': datetime.now().isoformat()
        }
    
    def _classify_sentiment(self, compound_score: float) -> str:
        """Classify sentiment based on compound score"""
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_mock_sentiment_data(self) -> Dict[str, Any]:
        """Generate mock sentiment data when analyzer is not available"""
        mock_comments = [
            "This video is amazing! Great content as always.",
            "Really helpful tutorial, thanks for sharing.",
            "Not sure about this approach, seems complicated.",
            "Love your videos! Keep up the great work.",
            "Could be better explained in some parts.",
            "Excellent explanation, very clear and concise.",
            "This helped me solve my problem, thank you!",
            "Good video but audio quality could be improved."
        ]
        
        return {
            'overview': {
                'positive_percentage': 72.3,
                'neutral_percentage': 18.7,
                'negative_percentage': 9.0,
                'overall_rating': 4.2,
                'total_comments': len(mock_comments),
                'avg_compound_score': 0.342
            },
            'detailed_sentiments': [
                {
                    'text': comment,
                    'sentiment': {
                        'pos': random.uniform(0.2, 0.8),
                        'neu': random.uniform(0.1, 0.4),
                        'neg': random.uniform(0.0, 0.3),
                        'compound': random.uniform(-0.2, 0.8)
                    },
                    'classification': random.choice(['positive', 'neutral', 'negative'])
                } for comment in mock_comments
            ],
            'summary': {
                'dominant_sentiment': 'positive',
                'most_positive': {'text': mock_comments[0], 'sentiment': {'compound': 0.8}},
                'most_negative': {'text': mock_comments[2], 'sentiment': {'compound': -0.2}}
            },
            'last_updated': datetime.now().isoformat()
        }

# Initialize sentiment analyzer
sentiment_analyzer = SentimentAnalyzer()

# Add the missing endpoint
@app.route('/api/fetch-youtube-data', methods=['POST'])
def fetch_youtube_data():
    """Fetch YouTube channel data from URL"""
    try:
        data = request.get_json()
        channel_url = data.get('channelUrl')
        
        if not channel_url:
            return jsonify({"error": "Channel URL is required"}), 400
        
        logger.info(f"Fetching YouTube data for URL: {channel_url}")
        
        # Get channel information
        channel_data = youtube_api.get_channel_info(channel_url)
        if "error" in channel_data:
            return jsonify(channel_data), 400
        
        # Get channel videos
        videos = youtube_api.get_channel_videos(channel_data["channelId"])
        
        # Update analytics engine with new data
        analytics_engine.update_channel_data(channel_data, videos)
        
        # Get updated overview data
        overview_data = analytics_engine.get_overview_data()
        
        return jsonify({
            "success": True,
            "channelData": channel_data,
            "videos": videos,
            "analytics": overview_data,
            "message": "YouTube data fetched successfully"
        })
        
    except Exception as e:
        logger.error(f"Error fetching YouTube data: {str(e)}")
        return jsonify({"error": "Failed to fetch YouTube data"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "YouTube Analytics API"
    })

@app.route('/api/overview', methods=['GET'])
def get_overview():
    """Get overview tab data"""
    try:
        overview_data = analytics_engine.get_overview_data()
        logger.info("Overview data requested successfully")
        return jsonify(overview_data)
    except Exception as e:
        logger.error(f"Error getting overview data: {str(e)}")
        return jsonify({"error": "Failed to get overview data"}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Get key metrics for overview tab"""
    try:
        current_video = analytics_engine.base_data["currentVideo"]
        engagement_metrics = analytics_engine.calculate_engagement_metrics()
        
        # Use channel's total view count instead of just the last video's views
        channel_total_views = analytics_engine.current_channel_data.get("viewCount", 0) if analytics_engine.current_channel_data else current_video["views"]
        
        metrics = {
            "totalViews": channel_total_views,  # Use channel's total views
            "watchTime": current_video["watchTime"],
            "engagementRate": engagement_metrics["engagementRate"],
            "clickThroughRate": current_video["clickThroughRate"],
            "totalLikes": current_video["likes"],
            "totalComments": current_video["comments"],
            "avgViewDuration": current_video["avgViewDuration"]
        }
        
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({"error": "Failed to get metrics"}), 500

@app.route('/api/views-trend', methods=['GET'])
def get_views_trend():
    """Get views trend data"""
    try:
        days = request.args.get('days', 7, type=int)
        views_data = analytics_engine.calculate_views_over_time(days)
        return jsonify(views_data)
    except Exception as e:
        logger.error(f"Error getting views trend: {str(e)}")
        return jsonify({"error": "Failed to get views trend"}), 500

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get Gemini AI-powered performance analysis"""
    try:
        # Get current video and channel data
        current_video = analytics_engine.base_data["currentVideo"]
        channel_data = analytics_engine.current_channel_data
        
        logger.info("Starting Gemini AI performance analysis")
        
        # Use Gemini AI for enhanced performance analysis
        gemini_analysis = gemini_performance_analyzer.analyze_performance_with_gemini(
            current_video, 
            channel_data
        )
        
        # Also get traditional performance data for comparison
        traditional_performance = analytics_engine.calculate_performance_score()
        
        # Combine both analyses
        enhanced_performance_data = {
            'gemini_analysis': gemini_analysis,
            'traditional_analysis': traditional_performance,
            'video_info': {
                'video_id': current_video['id'],
                'video_title': current_video['title'],
                'analysis_timestamp': datetime.now().isoformat()
            },
            'analysis_method': gemini_analysis.get('analysis_method', 'gemini_ai')
        }
        
        logger.info(f"Performance analysis completed using {gemini_analysis.get('analysis_method', 'gemini_ai')}")
        return jsonify(enhanced_performance_data)
        
    except Exception as e:
        logger.error(f"Error getting performance data: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Fallback to traditional analysis
        try:
            fallback_performance = analytics_engine.calculate_performance_score()
            return jsonify({
                'gemini_analysis': {
                    'overall_score': fallback_performance.get('overallScore', 75),
                    'grade': fallback_performance.get('grade', 'B'),
                    'analysis_method': 'fallback',
                    'error': str(e)
                },
                'traditional_analysis': fallback_performance,
                'video_info': {
                    'video_id': 'fallback',
                    'video_title': 'Fallback Analysis',
                    'analysis_timestamp': datetime.now().isoformat()
                }
            })
        except Exception as fallback_error:
            logger.error(f"Fallback performance analysis also failed: {str(fallback_error)}")
            return jsonify({"error": "Failed to get performance data"}), 500

@app.route('/api/engagement-rate', methods=['GET'])
def get_engagement_rate():
    """Get real-time engagement rate for the latest video"""
    try:
        current_video = analytics_engine.base_data["currentVideo"]
        
        # Calculate engagement rate: (likes + comments) / views * 100
        likes = current_video["likes"]
        comments = current_video["comments"]
        views = current_video["views"]
        
        if views > 0:
            engagement_rate = ((likes + comments) / views) * 100
        else:
            engagement_rate = 0
        
        # Calculate trend (mock for now - could be enhanced with historical data)
        trend_change = round(random.uniform(-1, 3), 1)  # Random trend between -1% to +3%
        trend_direction = "up" if trend_change > 0 else "down" if trend_change < 0 else "stable"
        
        return jsonify({
            "engagementRate": round(engagement_rate, 2),
            "likes": likes,
            "comments": comments,
            "views": views,
            "totalEngagements": likes + comments,
            "trend": {
                "change": abs(trend_change),
                "direction": trend_direction
            },
            "calculation": f"({likes:,} likes + {comments:,} comments) / {views:,} views × 100",
            "lastUpdated": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting engagement rate: {str(e)}")
        return jsonify({"error": "Failed to get engagement rate"}), 500

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get actionable recommendations"""
    try:
        recommendations = analytics_engine.generate_recommendations()
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({"error": "Failed to get recommendations"}), 500

@app.route('/api/sentiment-analysis', methods=['GET'])
def get_sentiment_analysis():
    """Get LLM-based sentiment analysis of video comments from the latest video"""
    try:
        # Get the current video ID from analytics engine
        current_video_id = analytics_engine.base_data["currentVideo"]["id"]
        
        logger.info(f"Fetching comments for LLM sentiment analysis from video: {current_video_id}")
        
        # Initialize YouTube API if not already done
        if not hasattr(get_sentiment_analysis, 'youtube_api'):
            get_sentiment_analysis.youtube_api = YouTubeAPI()
        
        # Fetch real comments from the latest video
        comments = get_sentiment_analysis.youtube_api.get_video_comments(current_video_id, max_results=50)
        
        if not comments:
            logger.warning("No comments found, using fallback mock data")
            comments = get_sentiment_analysis.youtube_api._get_mock_comments()
        
        logger.info(f"Analyzing sentiment for {len(comments)} comments using LLM")
        
        # Create CSV of comments for LLM processing
        comments_csv = llm_sentiment_analyzer.create_comments_csv(comments)
        logger.info(f"Created CSV with {len(comments)} comments for LLM analysis")
        
        # Analyze sentiment using LLM (Gemini API)
        sentiment_data = llm_sentiment_analyzer.analyze_with_gemini(comments)
        
        # Add metadata about the video and processing
        sentiment_data['video_info'] = {
            'video_id': current_video_id,
            'video_title': analytics_engine.base_data["currentVideo"]["title"],
            'comments_analyzed': len(comments),
            'data_source': 'youtube_api' if hasattr(get_sentiment_analysis.youtube_api, 'youtube') and get_sentiment_analysis.youtube_api.youtube else 'mock_data',
            'analysis_method': 'gemini_llm',
            'model_used': 'gemini-2.0-flash'
        }
        
        # Add CSV data for download/inspection
        sentiment_data['input_csv'] = comments_csv
        
        logger.info(f"LLM sentiment analysis completed successfully for video {current_video_id}")
        return jsonify(sentiment_data)
        
    except Exception as e:
        logger.error(f"Error getting LLM sentiment analysis: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Fallback to VADER sentiment analysis in case of LLM failure
        try:
            logger.info("Falling back to VADER sentiment analysis")
            fallback_comments = [
                "This video is absolutely amazing! Thank you for the great content.",
                "Really helpful tutorial, learned so much from this.",
                "Not sure I agree with this approach, seems overly complicated.",
                "Love your videos! Keep up the excellent work.",
                "Could have been explained better in some parts.",
                "Excellent explanation, very clear and easy to follow.",
                "This helped me solve my exact problem, thank you so much!",
                "Good video overall but the audio quality could be improved.",
                "Amazing content as always! You're the best.",
                "Perfect timing, I was just looking for this information."
            ]
            
            # Use LLM analyzer's fallback method which uses VADER
            fallback_results = []
            for i, comment in enumerate(fallback_comments):
                fallback_results.append(llm_sentiment_analyzer._fallback_sentiment(comment, i+1))
            
            sentiment_data = llm_sentiment_analyzer._process_llm_results(fallback_results)
            sentiment_data['video_info'] = {
                'video_id': 'fallback',
                'video_title': 'Fallback Data',
                'comments_analyzed': len(fallback_comments),
                'data_source': 'fallback_mock_data',
                'analysis_method': 'vader_fallback',
                'error': str(e)
            }
            
            return jsonify(sentiment_data)
        except Exception as fallback_error:
            logger.error(f"Fallback sentiment analysis also failed: {str(fallback_error)}")
            return jsonify({"error": "Failed to get sentiment analysis"}), 500

@app.route('/api/likes-dislikes', methods=['GET'])
def get_likes_dislikes():
    """Get likes vs dislikes data for the current video"""
    try:
        current_video = analytics_engine.base_data["currentVideo"]
        likes = current_video["likes"]
        dislikes = current_video.get("dislikes", max(1, int(likes * 0.02)))  # Estimate dislikes if not available
        
        total_reactions = likes + dislikes
        like_percentage = (likes / total_reactions) * 100 if total_reactions > 0 else 0
        dislike_percentage = (dislikes / total_reactions) * 100 if total_reactions > 0 else 0
        
        ratio = likes / dislikes if dislikes > 0 else likes
        
        likes_dislikes_data = {
            "likes": likes,
            "dislikes": dislikes,
            "total_reactions": total_reactions,
            "like_percentage": round(like_percentage, 1),
            "dislike_percentage": round(dislike_percentage, 1),
            "ratio": round(ratio, 1),
            "ratio_text": f"{round(ratio, 1)}:1",
            "chart_data": [
                {"name": "Likes", "value": likes, "color": "#10b981"},
                {"name": "Dislikes", "value": dislikes, "color": "#ef4444"}
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        logger.info("Likes vs dislikes data requested successfully")
        return jsonify(likes_dislikes_data)
    except Exception as e:
        logger.error(f"Error getting likes vs dislikes data: {str(e)}")
        return jsonify({"error": "Failed to get likes vs dislikes data"}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Refresh analytics data"""
    try:
        # In a real implementation, this would fetch fresh data from YouTube API
        logger.info("Data refresh requested")
        return jsonify({
            "message": "Data refreshed successfully",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error refreshing data: {str(e)}")
        return jsonify({"error": "Failed to refresh data"}), 500

class LLMSentimentAnalyzer:
    """Enhanced sentiment analysis using Google Gemini API"""
    
    def __init__(self):
        # Google Gemini API (free tier)
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.gemini_headers = {
            "Content-Type": "application/json"
        }
        logger.info("LLM Sentiment Analyzer initialized with Gemini API")
    
    def create_comments_csv(self, comments: List[str]) -> str:
        """Create CSV string from comments list"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['comment_id', 'comment_text'])
        
        # Write comments
        for i, comment in enumerate(comments, 1):
            # Clean comment text for CSV
            clean_comment = comment.replace('\n', ' ').replace('\r', ' ').strip()
            writer.writerow([f'comment_{i}', clean_comment])
        
        csv_content = output.getvalue()
        output.close()
        return csv_content
    
    def analyze_with_gemini(self, comments: List[str]) -> Dict[str, Any]:
        """Analyze sentiment using Google Gemini API"""
        results = []
        
        # Process comments in batches for efficiency
        batch_size = 10
        for batch_start in range(0, len(comments), batch_size):
            batch_comments = comments[batch_start:batch_start + batch_size]
            
            try:
                # Create prompt for batch sentiment analysis
                prompt = self._create_gemini_prompt(batch_comments, batch_start)
                
                # Make API request to Gemini
                response = requests.post(
                    f"{self.gemini_api_url}?key={self.gemini_api_key}",
                    headers=self.gemini_headers,
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.1,
                            "maxOutputTokens": 2048
                        }
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    gemini_result = response.json()
                    if 'candidates' in gemini_result and len(gemini_result['candidates']) > 0:
                        response_text = gemini_result['candidates'][0]['content']['parts'][0]['text']
                        batch_results = self._parse_gemini_response(response_text, batch_comments, batch_start)
                        results.extend(batch_results)
                    else:
                        logger.warning(f"Unexpected Gemini response format for batch starting at {batch_start}")
                        # Fallback for this batch
                        for i, comment in enumerate(batch_comments):
                            results.append(self._fallback_sentiment(comment, batch_start + i + 1))
                else:
                    logger.warning(f"Gemini API error for batch starting at {batch_start}: {response.status_code}")
                    if response.status_code == 429:
                        logger.info("Rate limit hit, waiting before retry...")
                        time.sleep(2)
                    
                    # Fallback to VADER for this batch
                    for i, comment in enumerate(batch_comments):
                        results.append(self._fallback_sentiment(comment, batch_start + i + 1))
                        
                # Rate limiting - delay between batches
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error analyzing batch starting at {batch_start} with Gemini: {str(e)}")
                # Fallback for this batch
                for i, comment in enumerate(batch_comments):
                    results.append(self._fallback_sentiment(comment, batch_start + i + 1))
        
        return self._process_llm_results(results)
    
    def _create_gemini_prompt(self, comments: List[str], batch_start: int) -> str:
        """Create a structured prompt for Gemini sentiment analysis"""
        prompt = """Analyze the sentiment of the following YouTube comments. For each comment, provide:
1. Sentiment: positive, negative, or neutral
2. Confidence: a decimal between 0 and 1

Respond in this exact JSON format:
[
  {"comment_id": "comment_X", "sentiment": "positive/negative/neutral", "confidence": 0.XX},
  ...
]

Comments to analyze:
"""
        
        for i, comment in enumerate(comments):
            comment_id = batch_start + i + 1
            clean_comment = comment.replace('"', '\"').replace('\n', ' ').strip()
            prompt += f"\ncomment_{comment_id}: \"{clean_comment}\""
        
        prompt += "\n\nProvide only the JSON array response, no additional text."
        return prompt
    
    def _parse_gemini_response(self, response_text: str, comments: List[str], batch_start: int) -> List[Dict[str, Any]]:
        """Parse Gemini's JSON response into our format"""
        results = []
        
        try:
            # Extract JSON from response (sometimes Gemini adds extra text)
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                gemini_results = json.loads(json_str)
                
                for i, comment in enumerate(comments):
                    comment_id = batch_start + i + 1
                    
                    # Find matching result from Gemini
                    gemini_result = None
                    for result in gemini_results:
                        if result.get('comment_id') == f'comment_{comment_id}':
                            gemini_result = result
                            break
                    
                    if gemini_result:
                        sentiment = gemini_result.get('sentiment', 'neutral').lower()
                        confidence = float(gemini_result.get('confidence', 0.5))
                        
                        # Validate sentiment
                        if sentiment not in ['positive', 'negative', 'neutral']:
                            sentiment = 'neutral'
                        
                        # Validate confidence
                        if not (0 <= confidence <= 1):
                            confidence = 0.5
                        
                        results.append({
                            'comment_id': f'comment_{comment_id}',
                            'comment_text': comment,
                            'sentiment': sentiment,
                            'confidence': round(confidence, 3),
                            'source': 'gemini_api'
                        })
                    else:
                        # Fallback if no matching result found
                        results.append(self._fallback_sentiment(comment, comment_id))
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            
            # Fallback for all comments in this batch
            for i, comment in enumerate(comments):
                results.append(self._fallback_sentiment(comment, batch_start + i + 1))
        
        return results
    
    def _fallback_sentiment(self, comment: str, comment_id: int) -> Dict[str, Any]:
        """Fallback sentiment analysis using VADER"""
        if SENTIMENT_AVAILABLE:
            analyzer = SentimentIntensityAnalyzer()
            scores = analyzer.polarity_scores(comment)
            
            # Convert VADER compound score to sentiment
            if scores['compound'] >= 0.05:
                sentiment = 'positive'
            elif scores['compound'] <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'comment_id': f'comment_{comment_id}',
                'comment_text': comment,
                'sentiment': sentiment,
                'confidence': abs(scores['compound']),
                'source': 'vader_fallback'
            }
        else:
            return {
                'comment_id': f'comment_{comment_id}',
                'comment_text': comment,
                'sentiment': 'neutral',
                'confidence': 0.5,
                'source': 'mock_fallback'
            }
    
    def _process_llm_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process LLM results and create comprehensive analysis"""
        if not results:
            return {"error": "No results to process"}
        
        # Count sentiments
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        total_confidence = 0
        
        for result in results:
            sentiment_counts[result['sentiment']] += 1
            total_confidence += result['confidence']
        
        total_comments = len(results)
        avg_confidence = total_confidence / total_comments if total_comments > 0 else 0
        
        # Calculate percentages
        positive_pct = (sentiment_counts['positive'] / total_comments) * 100
        neutral_pct = (sentiment_counts['neutral'] / total_comments) * 100
        negative_pct = (sentiment_counts['negative'] / total_comments) * 100
        
        # Calculate overall rating (1-5 scale)
        overall_rating = 1 + (positive_pct * 0.04) + (neutral_pct * 0.02)
        
        # Find most confident predictions
        sorted_results = sorted(results, key=lambda x: x['confidence'], reverse=True)
        
        return {
            'overview': {
                'positive_percentage': round(positive_pct, 1),
                'neutral_percentage': round(neutral_pct, 1),
                'negative_percentage': round(negative_pct, 1),
                'overall_rating': round(overall_rating, 1),
                'total_comments': total_comments,
                'average_confidence': round(avg_confidence, 3)
            },
            'detailed_sentiments': results[:20],  # Show top 20 for frontend
            'summary': {
                'most_positive': max([r for r in results if r['sentiment'] == 'positive'], 
                                   key=lambda x: x['confidence'], default=None),
                'most_negative': max([r for r in results if r['sentiment'] == 'negative'], 
                                   key=lambda x: x['confidence'], default=None),
                'dominant_sentiment': max(sentiment_counts.items(), key=lambda x: x[1])[0],
                'confidence_distribution': {
                    'high_confidence': len([r for r in results if r['confidence'] > 0.8]),
                    'medium_confidence': len([r for r in results if 0.5 <= r['confidence'] <= 0.8]),
                    'low_confidence': len([r for r in results if r['confidence'] < 0.5])
                }
            },
            'csv_results': self.create_results_csv(results),
            'last_updated': datetime.now().isoformat()
        }
    
    def create_results_csv(self, results: List[Dict[str, Any]]) -> str:
        """Create CSV string with sentiment analysis results"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['comment_id', 'comment_text', 'sentiment', 'confidence', 'source'])
        
        # Write results
        for result in results:
            writer.writerow([
                result['comment_id'],
                result['comment_text'][:100] + '...' if len(result['comment_text']) > 100 else result['comment_text'],
                result['sentiment'],
                result['confidence'],
                result['source']
            ])
        
        csv_content = output.getvalue()
        output.close()
        return csv_content

class GeminiPerformanceAnalyzer:
    """AI-powered performance analysis using Google Gemini API"""
    
    def __init__(self):
        # Use the same Gemini API configuration as sentiment analyzer
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
        self.gemini_api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.gemini_headers = {
            "Content-Type": "application/json"
        }
        logger.info("Gemini Performance Analyzer initialized")
    
    def analyze_performance_with_gemini(self, video_data: Dict[str, Any], channel_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze video performance using Gemini AI"""
        try:
            # Check if Gemini API key is configured
            if not self.gemini_api_key or self.gemini_api_key.strip() == '':
                logger.warning("Gemini API key not configured, falling back to traditional analysis")
                return self._fallback_performance_analysis(video_data)
            
            logger.info("Starting Gemini AI performance analysis with configured API key")
            
            # Create comprehensive performance analysis prompt
            prompt = self._create_performance_analysis_prompt(video_data, channel_data)
            
            # Make API request to Gemini
            response = requests.post(
                f"{self.gemini_api_url}?key={self.gemini_api_key}",
                headers=self.gemini_headers,
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 3000
                    }
                },
                timeout=30
            )
            
            logger.info(f"Gemini API response status: {response.status_code}")
            
            if response.status_code == 200:
                gemini_result = response.json()
                if 'candidates' in gemini_result and len(gemini_result['candidates']) > 0:
                    response_text = gemini_result['candidates'][0]['content']['parts'][0]['text']
                    logger.info("Successfully received Gemini AI analysis response")
                    return self._parse_performance_analysis(response_text, video_data)
                else:
                    logger.warning("Unexpected Gemini response format for performance analysis")
                    return self._fallback_performance_analysis(video_data)
            else:
                logger.warning(f"Gemini API error for performance analysis: {response.status_code} - {response.text}")
                return self._fallback_performance_analysis(video_data)
                
        except Exception as e:
            logger.error(f"Error analyzing performance with Gemini: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._fallback_performance_analysis(video_data)
    
    def _create_performance_analysis_prompt(self, video_data: Dict[str, Any], channel_data: Dict[str, Any] = None) -> str:
        """Create a comprehensive prompt for Gemini performance analysis"""
        
        # Extract key metrics
        views = video_data.get('views', 0)
        likes = video_data.get('likes', 0)
        comments = video_data.get('comments', 0)
        watch_time = video_data.get('watchTime', '0h')
        ctr = video_data.get('clickThroughRate', 0)
        avg_view_duration = video_data.get('avgViewDuration', '0:00')
        subscribers = channel_data.get('subscriberCount', 0) if channel_data else video_data.get('subscribers', 0)
        
        # Calculate engagement rate
        engagement_rate = ((likes + comments) / max(views, 1)) * 100 if views > 0 else 0
        
        prompt = f"""As a YouTube analytics expert, analyze the performance of this video and provide detailed insights and recommendations.

**VIDEO METRICS:**
- Views: {views:,}
- Likes: {likes:,}
- Comments: {comments:,}
- Watch Time: {watch_time}
- Click-Through Rate (CTR): {ctr}%
- Average View Duration: {avg_view_duration}
- Channel Subscribers: {subscribers:,}
- Engagement Rate: {engagement_rate:.2f}%

**ANALYSIS REQUIRED:**
1. Overall Performance Score (0-100)
2. Individual metric scores for: Views, Engagement, Watch Time, CTR
3. Performance grade (A+ to F)
4. Key strengths and weaknesses
5. Specific actionable recommendations
6. Comparison to YouTube benchmarks
7. Growth potential assessment

**RESPONSE FORMAT (JSON):**
{{
  "overall_score": 85,
  "grade": "A-",
  "scores": {{
    "views": 78,
    "engagement": 92,
    "watch_time": 85,
    "ctr": 88
  }},
  "analysis": {{
    "strengths": ["High engagement rate", "Strong CTR performance"],
    "weaknesses": ["Below average watch time", "Low view count relative to subscribers"],
    "benchmark_comparison": "Above average in engagement, below average in retention"
  }},
  "recommendations": [
    {{
      "type": "critical",
      "title": "Improve Content Retention",
      "description": "Focus on hook creation and pacing to increase watch time",
      "priority": "high",
      "expected_impact": "15-25% improvement in watch time"
    }}
  ],
  "growth_potential": "high",
  "key_insights": [
    "Strong audience engagement indicates quality content",
    "CTR suggests effective thumbnail and title optimization"
  ]
}}

Provide only the JSON response, no additional text."""
        
        return prompt
    
    def _parse_performance_analysis(self, response_text: str, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gemini's performance analysis response"""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                gemini_analysis = json.loads(json_str)
                
                # Validate and structure the response
                analysis_result = {
                    'overall_score': gemini_analysis.get('overall_score', 75),
                    'grade': gemini_analysis.get('grade', 'B'),
                    'scores': {
                        'views': gemini_analysis.get('scores', {}).get('views', 70),
                        'engagement': gemini_analysis.get('scores', {}).get('engagement', 75),
                        'watch_time': gemini_analysis.get('scores', {}).get('watch_time', 70),
                        'ctr': gemini_analysis.get('scores', {}).get('ctr', 75)
                    },
                    'analysis': {
                        'strengths': gemini_analysis.get('analysis', {}).get('strengths', []),
                        'weaknesses': gemini_analysis.get('analysis', {}).get('weaknesses', []),
                        'benchmark_comparison': gemini_analysis.get('analysis', {}).get('benchmark_comparison', 'Analysis pending')
                    },
                    'recommendations': gemini_analysis.get('recommendations', []),
                    'growth_potential': gemini_analysis.get('growth_potential', 'medium'),
                    'key_insights': gemini_analysis.get('key_insights', []),
                    'analysis_method': 'gemini_ai',
                    'last_updated': datetime.now().isoformat()
                }
                
                return analysis_result
            else:
                raise ValueError("No valid JSON found in Gemini response")
                
        except Exception as e:
            logger.error(f"Error parsing Gemini performance analysis: {str(e)}")
            logger.debug(f"Response text: {response_text}")
            return self._fallback_performance_analysis(video_data)
    
    def _fallback_performance_analysis(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback performance analysis when Gemini is unavailable"""
        views = video_data.get('views', 0)
        likes = video_data.get('likes', 0)
        comments = video_data.get('comments', 0)
        
        # Simple scoring algorithm as fallback
        engagement_rate = ((likes + comments) / max(views, 1)) * 100 if views > 0 else 0
        
        # Basic scoring
        view_score = min(100, (views / 100000) * 100) if views > 0 else 0
        engagement_score = min(100, engagement_rate * 20)
        overall_score = (view_score + engagement_score) / 2
        
        # Determine grade
        if overall_score >= 90:
            grade = "A+"
        elif overall_score >= 85:
            grade = "A"
        elif overall_score >= 80:
            grade = "A-"
        elif overall_score >= 75:
            grade = "B+"
        elif overall_score >= 70:
            grade = "B"
        else:
            grade = "C"
        
        return {
            'overall_score': round(overall_score, 1),
            'grade': grade,
            'scores': {
                'views': round(view_score, 1),
                'engagement': round(engagement_score, 1),
                'watch_time': 70,
                'ctr': 75
            },
            'analysis': {
                'strengths': ['Baseline performance analysis'],
                'weaknesses': ['Limited analysis without AI'],
                'benchmark_comparison': 'Fallback analysis mode'
            },
            'recommendations': [{
                'type': 'info',
                'title': 'Enable AI Analysis',
                'description': 'Configure Gemini API for detailed performance insights',
                'priority': 'medium',
                'expected_impact': 'Enhanced analysis capabilities'
            }],
            'growth_potential': 'medium',
            'key_insights': ['Basic performance metrics calculated'],
            'analysis_method': 'fallback',
            'last_updated': datetime.now().isoformat()
        }

# Initialize YouTube API and Analytics Engine instances AFTER all classes are defined
youtube_api = YouTubeAPI()
analytics_engine = YouTubeAnalyticsEngine()
llm_sentiment_analyzer = LLMSentimentAnalyzer()
gemini_performance_analyzer = GeminiPerformanceAnalyzer()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 