# Samudra Sachet Mobile App

A React Native mobile application for ocean hazard reporting, built with Expo.

## Features

- **Citizen Dashboard**: View recent hazard reports and social media updates
- **Report Submission**: Submit hazard reports with location, photos, and details
- **Social Media Integration**: View relevant social media posts about ocean hazards
- **User Profile**: Manage account information and settings
- **Real-time Updates**: Pull-to-refresh functionality for latest data

## Tech Stack

- **React Native** with Expo
- **React Navigation** for navigation
- **Expo Location** for GPS functionality
- **Expo Image Picker** for photo capture
- **Axios** for API communication
- **AsyncStorage** for local data persistence

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Expo CLI (`npm install -g @expo/cli`)
- Expo Go app on your mobile device

### Installation

1. Navigate to the mobile directory:
   ```bash
   cd mobile
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Scan the QR code with Expo Go app on your mobile device

### Available Scripts

- `npm start` - Start the Expo development server
- `npm run android` - Run on Android device/emulator
- `npm run ios` - Run on iOS device/simulator (macOS only)
- `npm run web` - Run in web browser

## Project Structure

```
mobile/
├── src/
│   ├── components/          # Reusable UI components
│   ├── context/            # React Context providers
│   ├── screens/            # Screen components
│   └── services/           # API services
├── App.js                  # Main app component
└── package.json           # Dependencies and scripts
```

## API Integration

The app connects to the Samudra Sachet backend API at `http://localhost:8000/api/v1` for:

- User authentication
- Report submission and retrieval
- Social media post fetching
- User profile management

## Demo Credentials

Use these credentials to test the app:

- **Citizen**: `citizen@samudra-sachet.com` / `citizen123`
- **Citizen 2**: `citizen2@samudra-sachet.com` / `citizen123`
- **Citizen 3**: `citizen3@samudra-sachet.com` / `citizen123`

## Features Overview

### Dashboard
- Recent hazard reports summary
- Social media updates
- Quick statistics
- Pull-to-refresh functionality

### Report Submission
- Hazard type selection (High Waves, Storm Surge, Tsunami, Flooding, Erosion)
- Severity level (1-5)
- GPS location capture
- Photo attachment
- Detailed description

### Social Media
- Platform-specific icons (Twitter, Facebook, Instagram, YouTube, TikTok)
- Relevance scoring
- Sentiment analysis
- Direct links to original posts

### Profile
- User information display
- Account status
- App version and settings
- Logout functionality

## Development Notes

- The app is designed specifically for citizen users
- All API calls include proper error handling
- Location permissions are requested when needed
- Camera and photo library permissions are handled gracefully
- The app follows Material Design principles for Android and iOS design guidelines

## Troubleshooting

### Common Issues

1. **Metro bundler issues**: Clear cache with `npx expo start --clear`
2. **Permission errors**: Ensure location and camera permissions are granted
3. **API connection issues**: Verify backend is running on `http://localhost:8000`
4. **Build errors**: Try deleting `node_modules` and reinstalling dependencies

### Debug Mode

Enable debug mode by shaking the device or pressing `Cmd+D` (iOS) / `Cmd+M` (Android) to access developer tools.

## Contributing

1. Follow the existing code style and structure
2. Test on both iOS and Android devices
3. Ensure proper error handling for all API calls
4. Update documentation for new features

## License

This project is part of the Samudra Sachet ocean hazard reporting system.
