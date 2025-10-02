# Samudra Sachet Mobile App

A comprehensive Flutter mobile application for citizens to report ocean hazards and stay informed about coastal safety.

## Features

### 🏠 Home Screen
- Welcome dashboard with ocean safety alerts
- Quick action buttons for reporting hazards
- Recent reports feed
- Social media updates from coastal authorities

### 📝 Report Hazard
- GPS location detection
- Multiple hazard types (High Waves, Storm, Tsunami, Flooding, Oil Spill, Marine Debris, Water Pollution)
- Severity level selection (1-5 scale)
- Photo evidence capture
- Detailed description input
- Real-time address lookup

### 📱 Social Media Updates
- View posts from Twitter, Facebook, Instagram, YouTube
- Relevance scoring for ocean-related content
- Real-time updates from coastal authorities

### 📋 My Reports
- View all submitted reports
- Track report status (Pending, Verified, Rejected)
- Report history and details

### 👤 Profile
- User information display
- Role-based access (Citizen, Coastal Volunteer, Coastal Guard, etc.)
- Settings and preferences
- Logout functionality

## Technical Stack

- **Framework**: Flutter 3.6+
- **State Management**: Built-in Flutter state management
- **Networking**: Dio HTTP client
- **Storage**: Flutter Secure Storage + SharedPreferences
- **Location**: Geolocator + Geocoding
- **Camera**: Image Picker + Camera
- **UI**: Material Design 3 + Custom Ocean Theme
- **Icons**: Lucide Flutter
- **Fonts**: Google Fonts (Inter)

## Setup Instructions

### Prerequisites
- Flutter SDK 3.6.0 or higher
- Android Studio / VS Code
- Android device or emulator
- iOS device or simulator (for iOS development)

### Installation

1. **Navigate to mobile directory**
   ```bash
   cd frontend/apps/mobile
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Run the app**
   ```bash
   flutter run
   ```

### Backend Setup
Ensure the backend server is running on `http://localhost:8000` before using the mobile app.

## Demo Credentials

The app includes demo credentials for testing:

- **Citizen**: `citizen@samudra-sachet.com` / `citizen123`
- **Volunteer**: `volunteer@samudra-sachet.com` / `volunteer123`
- **Coastal Guard**: `guard@samudra-sachet.com` / `guard123`
- **Disaster Manager**: `manager@samudra-sachet.com` / `manager123`

## App Structure

```
lib/
├── core/
│   ├── api/
│   │   └── api_client.dart          # HTTP client and API calls
│   ├── services/
│   │   └── storage_service.dart     # Local storage management
│   └── theme/
│       ├── app_colors.dart          # Color scheme
│       └── app_theme.dart           # Theme configuration
├── features/
│   ├── auth/
│   │   └── presentation/
│   │       └── login_screen.dart    # Authentication
│   ├── home/
│   │   └── presentation/
│   │       └── home_screen.dart     # Main dashboard
│   ├── reports/
│   │   └── presentation/
│   │       └── report_issue_screen.dart # Hazard reporting
│   ├── social_media/
│   │   └── presentation/
│   │       └── social_media_screen.dart # Social updates
│   ├── my_reports/
│   │   └── presentation/
│   │       └── my_reports_screen.dart # Report history
│   ├── profile/
│   │   └── presentation/
│   │       └── profile_screen.dart   # User profile
│   └── notifications/
│       └── presentation/
│           └── notification_screen.dart # Notifications
└── main.dart                         # App entry point
```

## Key Features Implementation

### Location Services
- Automatic GPS location detection
- Reverse geocoding for readable addresses
- Permission handling for location access

### Camera Integration
- Photo capture for hazard evidence
- Image compression and optimization
- File upload to backend

### Real-time Updates
- Pull-to-refresh functionality
- Background data loading
- Error handling and retry mechanisms

### Security
- JWT token authentication
- Secure token storage
- Automatic token refresh

## API Integration

The app integrates with the Samudra Sachet backend API:

- **Authentication**: `/api/v1/auth/login`
- **Reports**: `/api/v1/reports/` (POST), `/api/v1/reports/public` (GET)
- **Social Media**: `/api/v1/social-media/public` (GET)
- **User Profile**: `/api/v1/users/me` (GET)

## Development Notes

- Uses Material Design 3 with custom ocean-themed colors
- Responsive design for different screen sizes
- Comprehensive error handling and user feedback
- Offline-first approach with local storage
- Clean architecture with separation of concerns

## Future Enhancements

- Push notifications for hazard alerts
- Offline report submission
- Map integration for hazard visualization
- Multi-language support
- Dark mode theme
- Report sharing functionality
- Emergency contact integration

## Troubleshooting

### Common Issues

1. **Location not working**: Ensure location permissions are granted
2. **Camera not working**: Check camera permissions
3. **API connection failed**: Verify backend server is running
4. **Build errors**: Run `flutter clean` and `flutter pub get`

### Debug Mode
The app includes comprehensive logging for debugging:
- API request/response logging
- Location service debugging
- Authentication flow tracking
- Error handling with detailed messages

## Contributing

1. Follow Flutter best practices
2. Use meaningful variable and function names
3. Add comments for complex logic
4. Test on both Android and iOS
5. Ensure accessibility compliance

## License

This project is part of the Samudra Sachet ocean safety initiative.