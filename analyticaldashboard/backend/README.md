# YouTube Analytics Backend API

A Flask-based backend API that provides comprehensive analytics logic for the YouTube Analytics Dashboard. This backend processes YouTube data and provides insights, metrics, and recommendations.

## Features

- **Real-time Analytics**: Calculate views, engagement, and performance metrics
- **Data Processing**: Advanced algorithms for YouTube analytics
- **Performance Scoring**: Weighted scoring system for video performance
- **Recommendations Engine**: AI-powered recommendations for content improvement
- **RESTful API**: Clean API endpoints for frontend integration
- **CORS Support**: Cross-origin resource sharing enabled
- **Configuration Management**: Environment-based configuration

## Installation

1. **Clone the repository and navigate to backend directory:**
   ```bash
   cd analyticaldashboard/backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables (optional):**
   Create a `.env` file in the backend directory:
   ```env
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-secret-key-here
   YOUTUBE_API_KEY=your-youtube-api-key
   YOUTUBE_CHANNEL_ID=your-channel-id
   ```

## Running the Application

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Health Check
- **GET** `/api/health`
- Returns API health status

### Overview Data
- **GET** `/api/overview`
- Returns comprehensive overview data including:
  - Current video information
  - Views over time
  - Engagement metrics
  - Performance score
  - Recommendations

### Key Metrics
- **GET** `/api/metrics`
- Returns key performance metrics:
  - Total views
  - Watch time
  - Engagement rate
  - Click-through rate
  - Total likes and comments
  - Average view duration

### Views Trend
- **GET** `/api/views-trend?days=7`
- Returns views trend data for specified number of days (default: 7)

### Performance Analysis
- **GET** `/api/performance`
- Returns detailed performance analysis with scoring breakdown

### Recommendations
- **GET** `/api/recommendations`
- Returns actionable recommendations for content improvement

### Data Refresh
- **POST** `/api/refresh`
- Triggers data refresh (placeholder for YouTube API integration)

## API Response Examples

### Overview Data Response
```json
{
  "currentVideo": {
    "id": "dQw4w9WgXcQ",
    "title": "How to Build Amazing React Applications - Complete Tutorial",
    "views": 156789,
    "likes": 12456,
    "comments": 1876,
    "watchTime": "2.1M hours",
    "avgViewDuration": "18:42",
    "clickThroughRate": 8.7
  },
  "viewsOverTime": [
    {
      "date": "2024-07-15",
      "views": 1234,
      "watchTime": 25.4
    }
  ],
  "engagementMetrics": {
    "engagementRate": 9.2,
    "likeToDislikeRatio": 53.2,
    "watchTimePercentage": 76.8,
    "totalEngagements": 14566
  },
  "performanceScore": {
    "overallScore": 78.5,
    "grade": "B+",
    "breakdown": {
      "viewsScore": 75.6,
      "engagementScore": 82.3,
      "watchTimeScore": 76.8,
      "ctrScore": 87.0
    }
  },
  "recommendations": [
    {
      "category": "Engagement",
      "title": "Boost Audience Interaction",
      "description": "Add calls-to-action and encourage comments.",
      "priority": "high",
      "impact": "high"
    }
  ],
  "lastUpdated": "2024-07-21T10:30:00Z",
  "analyticsVersion": "1.0.0"
}
```

## Analytics Engine Features

### YouTubeAnalyticsEngine Class

The core analytics engine provides:

1. **Views Calculation**: Realistic growth patterns with randomization
2. **Engagement Metrics**: Advanced engagement rate calculations
3. **Performance Scoring**: Weighted scoring system (0-100 scale)
4. **Recommendations**: AI-powered content improvement suggestions
5. **Data Processing**: Duration parsing and metric normalization

### Key Methods

- `calculate_views_over_time(days)`: Generate views trend data
- `calculate_engagement_metrics()`: Calculate engagement rates and ratios
- `calculate_performance_score()`: Generate overall performance score
- `generate_recommendations()`: Create actionable recommendations
- `get_overview_data()`: Comprehensive data aggregation

## Configuration

The application uses environment-based configuration:

- **Development**: Debug mode, detailed logging
- **Production**: Optimized for performance
- **Testing**: Test-specific settings

### Environment Variables

- `FLASK_ENV`: Environment mode (development/production/testing)
- `FLASK_DEBUG`: Enable debug mode
- `SECRET_KEY`: Application secret key
- `YOUTUBE_API_KEY`: YouTube Data API key (for future integration)
- `YOUTUBE_CHANNEL_ID`: YouTube channel ID (for future integration)

## Future Enhancements

1. **YouTube API Integration**: Real data from YouTube Data API
2. **Database Integration**: Persistent data storage
3. **Authentication**: User authentication and authorization
4. **Real-time Updates**: WebSocket support for live updates
5. **Advanced Analytics**: Machine learning for predictions
6. **Caching**: Redis integration for performance
7. **Rate Limiting**: API rate limiting and throttling

## Error Handling

The API includes comprehensive error handling:

- HTTP status codes for different error types
- Detailed error messages for debugging
- Logging for monitoring and troubleshooting
- Graceful degradation for missing data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 