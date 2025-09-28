import React from 'react';
import { useSelector } from 'react-redux';
import { useDispatch } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { logout } from '../state/slices/authSlice';
import {
  LayoutDashboard,
  FileText,
  MapPin,
  CheckCircle,
  Shield,
  User,
  LogOut
} from 'lucide-react';

const Sidebar = () => {
  const dispatch = useDispatch();
  const { user, userRole } = useSelector((state) => state.auth);

  const base = 'flex items-center gap-3 px-4 py-3 rounded-md transition-colors';
  const active = 'bg-primary-600 text-white';
  const inactive = 'text-gray-700 hover:bg-gray-100';

  const handleLogout = () => {
    dispatch(logout());
  };

  const getNavigationLinks = () => {
    const baseLinks = [
      { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', roles: ['analyst', 'authority', 'admin'] },
      { to: '/reports', icon: FileText, label: 'Reports', roles: ['analyst', 'authority', 'admin'] },
      { to: '/hotspots', icon: MapPin, label: 'Hotspots', roles: ['analyst', 'authority', 'admin'] },
    ];

    if (userRole === 'analyst' || userRole === 'authority') {
      baseLinks.push({ to: '/verification', icon: CheckCircle, label: 'Verification', roles: ['analyst', 'authority'] });
    }

    if (userRole === 'admin') {
      baseLinks.push({ to: '/admin', icon: Shield, label: 'Admin Panel', roles: ['admin'] });
    }

    baseLinks.push({ to: '/profile', icon: User, label: 'Profile', roles: ['analyst', 'authority', 'admin'] });

    return baseLinks.filter(link => link.roles.includes(userRole));
  };

  return (
    <aside className="w-64 bg-white min-h-screen text-gray-900 flex-shrink-0 border-r border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center">
          <div className="text-2xl mr-2">🌊</div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">Samudra Sachet</h1>
            <p className="text-xs text-gray-500">Coastal Monitoring</p>
          </div>
        </div>
      </div>

      <nav className="pt-6">
        <ul className="space-y-1 px-4">
          {getNavigationLinks().map(({ to, icon: Icon, label }) => (
            <li key={to}>
              <NavLink
                to={to}
                className={({ isActive }) => `${base} ${isActive ? active : inactive}`}
              >
                <Icon size={20} />
                <span className="font-medium">{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="absolute bottom-0 w-64 p-4 border-t border-gray-200">
        <div className="flex items-center mb-3">
          <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
            {user?.full_name?.charAt(0)?.toUpperCase()}
          </div>
          <div className="ml-3">
            <p className="text-sm font-medium text-gray-900">{user?.full_name}</p>
            <p className="text-xs text-gray-500 capitalize">{userRole}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-4 py-2 w-full text-red-600 hover:bg-red-50 rounded-md transition-colors"
        >
          <LogOut size={16} />
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
