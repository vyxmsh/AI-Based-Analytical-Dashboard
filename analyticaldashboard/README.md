# YouTube Analytics Dashboard

A comprehensive YouTube analytics dashboard built with React frontend and Python Flask backend. This project provides real-time analytics, performance scoring, and actionable recommendations for YouTube content creators.

## Features

### Frontend (React)
- **Modern UI**: Beautiful, responsive design with Tailwind CSS
- **Real-time Data**: Live updates from Python backend
- **Interactive Charts**: Advanced visualizations with Recharts
- **Multiple Tabs**: Overview, Sentiment, Engagement, Transcription, Performance, Audience, Revenue
- **API Integration**: Seamless connection to Python backend
- **Error Handling**: Graceful fallback to mock data when API is unavailable

### Backend (Python Flask)
- **Analytics Engine**: Advanced algorithms for YouTube data processing
- **Performance Scoring**: Weighted scoring system (0-100 scale)
- **Recommendations Engine**: AI-powered content improvement suggestions
- **RESTful API**: Clean endpoints for frontend integration
- **Real-time Calculations**: Dynamic metrics and trend analysis
- **CORS Support**: Cross-origin resource sharing enabled

## Project Structure

```
AnalyticalDashboard/
├── analyticaldashboard/          # React Frontend
│   ├── src/
│   │   ├── App.jsx              # Main dashboard component
│   │   ├── App.css              # Styles
│   │   └── main.jsx             # Entry point
│   ├── package.json             # Frontend dependencies
│   └── README.md                # Frontend documentation
├── backend/                     # Python Backend
│   ├── app.py                   # Main Flask application
│   ├── config.py                # Configuration settings
│   ├── requirements.txt         # Python dependencies
│   └── README.md                # Backend documentation
├── start.bat                    # Windows startup script
├── start.sh                     # Unix startup script
└── README.md                    # This file
```

## Quick Start

### Option 1: Automated Startup (Recommended)

#### Windows
```bash
# Double-click start.bat or run:
start.bat
```

#### macOS/Linux
```bash
# Make script executable and run:
chmod +x start.sh
./start.sh
```

### Option 2: Manual Startup

#### 1. Start the Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python app.py
```

#### 2. Start the Frontend
```bash
cd analyticaldashboard
npm install
npm run dev
```

## API Endpoints

The backend provides the following RESTful endpoints:

- `GET /api/health` - Health check
- `GET /api/overview` - Comprehensive overview data
- `GET /api/metrics` - Key performance metrics
- `GET /api/views-trend?days=7` - Views trend data
- `GET /api/performance` - Performance analysis
- `GET /api/recommendations` - Actionable recommendations
- `POST /api/refresh` - Refresh analytics data

## Analytics Features

### Performance Scoring System
The backend implements a sophisticated scoring system that evaluates:

- **Views Score** (25% weight): Based on view count relative to benchmarks
- **Engagement Score** (30% weight): Likes, comments, and shares ratio
- **Watch Time Score** (25% weight): Average view duration percentage
- **CTR Score** (20% weight): Click-through rate performance

### Smart Recommendations
The system generates actionable recommendations based on:

- Low engagement rates → Suggest calls-to-action
- Poor retention → Review content structure
- Low CTR → Optimize thumbnails and titles
- Below-average views → Improve SEO and promotion

### Real-time Analytics
- Dynamic views trend calculation with realistic growth patterns
- Engagement rate calculations with advanced metrics
- Performance comparisons and benchmarking
- Trend analysis and forecasting

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
YOUTUBE_API_KEY=your-youtube-api-key
YOUTUBE_CHANNEL_ID=your-channel-id
```

### API Configuration
The frontend connects to the backend at `http://localhost:5000/api` by default. You can modify this in `src/App.jsx`:

```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

## Development

### Frontend Development
```bash
cd analyticaldashboard
npm install
npm run dev
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Adding New Features
1. **Backend**: Add new endpoints in `app.py` and corresponding methods in `YouTubeAnalyticsEngine`
2. **Frontend**: Create new components and integrate with existing API endpoints
3. **Charts**: Use Recharts library for new visualizations

## Troubleshooting

### Common Issues

1. **Backend not starting**
   - Check if Python 3.7+ is installed
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check if port 5000 is available

2. **Frontend not connecting to backend**
   - Ensure backend is running on `http://localhost:5000`
   - Check CORS configuration in backend
   - Verify API_BASE_URL in frontend

3. **Charts not displaying**
   - Check browser console for errors
   - Verify data format matches expected structure
   - Ensure Recharts is properly installed

### Error Handling
- The frontend gracefully falls back to mock data when the API is unavailable
- Error notifications are displayed to users
- API connection status is shown in the header

## Future Enhancements

### Planned Features
1. **YouTube API Integration**: Real data from YouTube Data API
2. **Database Integration**: Persistent data storage with PostgreSQL
3. **Authentication**: User authentication and multi-channel support
4. **Real-time Updates**: WebSocket support for live data
5. **Advanced Analytics**: Machine learning for predictions
6. **Export Features**: PDF/Excel report generation
7. **Mobile App**: React Native mobile application

### Technical Improvements
1. **Caching**: Redis integration for performance
2. **Rate Limiting**: API rate limiting and throttling
3. **Testing**: Comprehensive unit and integration tests
4. **CI/CD**: Automated deployment pipeline
5. **Monitoring**: Application performance monitoring
6. **Security**: Enhanced security measures

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit your changes: `git commit -m 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the backend and frontend README files
- Review the troubleshooting section above

## Acknowledgments

- **React**: Frontend framework
- **Tailwind CSS**: Styling framework
- **Recharts**: Chart library
- **Flask**: Backend framework
- **Lucide React**: Icon library
