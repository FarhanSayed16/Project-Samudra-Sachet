# Project Samudra Sachet - Frontend Dashboard

A modern React dashboard for coastal hazard monitoring and management, built for authorities, analysts, and administrators.

## 🌊 Features

- **Dashboard Overview**: Real-time statistics and recent activity
- **Report Management**: View, filter, and manage coastal hazard reports
- **Hotspot Monitoring**: Track active hazard hotspots
- **Verification System**: Review and verify reports (Analyst/Authority roles)
- **Admin Panel**: User management and system administration
- **Profile Management**: Update user profile and change password
- **Role-based Access**: Different views based on user roles (Admin, Authority, Analyst)

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd frontend/apps/web

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Demo Credentials

- **Admin**: `admin@samudra-sachet.com` / `admin123`
- **Analyst**: `analyst@samudra-sachet.com` / `analyst123`
- **Authority**: `authority@samudra-sachet.com` / `authority123`

## 🏗️ Architecture

### Tech Stack

- **React 19** - UI framework
- **Redux Toolkit** - State management
- **React Router** - Navigation
- **Axios** - API communication
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Vite** - Build tool

### Project Structure

```
src/
├── api/                 # API service layer
│   └── apiService.js
├── components/          # Reusable UI components
│   ├── ui/             # Basic UI components
│   ├── Header.jsx      # App header
│   ├── Sidebar.jsx     # Navigation sidebar
│   └── ...
├── layouts/            # Page layouts
│   ├── MainLayout.jsx  # Main app layout
│   └── AuthLayout.jsx  # Authentication layout
├── pages/              # Page components
│   ├── DashboardPage.jsx
│   ├── ReportsPage.jsx
│   ├── HotspotsPage.jsx
│   └── ...
├── state/              # Redux store and slices
│   ├── slices/
│   │   ├── authSlice.js
│   │   ├── reportsSlice.js
│   │   └── ...
│   └── store.js
├── utils/              # Utility functions
├── App.jsx             # Main app component
└── main.jsx           # Entry point
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

### API Integration

The frontend connects to the Project Samudra Sachet backend API. Make sure the backend is running on the configured URL.

## 📱 Pages & Features

### Dashboard
- Overview statistics
- Recent reports and hotspots
- Quick access to key metrics

### Reports
- List all coastal hazard reports
- Filter by status, hazard type, severity
- Search functionality
- Detailed report information

### Hotspots
- Monitor active hazard hotspots
- Filter by status and event type
- Location-based filtering
- Intensity tracking

### Verification (Analyst/Authority)
- Review pending reports
- Verify or reject reports
- Add verification notes
- Confidence scoring

### Admin Panel (Admin only)
- User management
- Role assignment
- System administration
- User statistics

### Profile
- Update personal information
- Change password
- View account status

## 🔐 Authentication & Authorization

- JWT-based authentication
- Role-based access control
- Automatic token refresh
- Persistent login state

### User Roles

- **Admin**: Full system access, user management
- **Authority**: Report verification, hotspot monitoring
- **Analyst**: Report verification, data analysis
- **Citizen**: Report submission (not in this dashboard)

## 🎨 UI Components

Built with reusable components:

- **Button**: Various styles and sizes
- **Input**: Form inputs with validation
- **Card**: Content containers
- **Badge**: Status indicators
- **Loader**: Loading states
- **Modal**: Overlay dialogs

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure backend is running on `http://localhost:8000`
   - Check CORS settings in backend

2. **Authentication Issues**
   - Clear browser storage
   - Check JWT token validity

3. **Build Errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility

## 📄 License

© 2024 Project Samudra Sachet. All rights reserved.

## 🤝 Contributing

This is part of the Project Samudra Sachet coastal hazard monitoring system. For contributions, please contact the development team.
