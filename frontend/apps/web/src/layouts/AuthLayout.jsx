import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { logout } from '../state/slices/authSlice';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import Loader from '../components/Loader';

export default function AuthLayout({ children, authentication = true, roles = [] }) {
  const dispatch = useDispatch();
  const { user, isAuthenticated, token, isLoading } = useSelector((state) => state.auth);
  const navigate = useNavigate();
  const location = useLocation();

  if (authentication) {
    if (isLoading) {
      return <Loader fullScreen />;
    }

    if (!token || !isAuthenticated) {
      return (
        <Navigate
          to="/login"
          state={{ from: location.pathname }}
          replace
        />
      );
    }

    if (roles.length > 0 && user && !roles.includes(user.user_role)) {
      return <Navigate to="/dashboard" replace />;
    }

    return <>{children}</>;
  }

  if (!authentication && !isLoading && isAuthenticated) {
    const from = location.state?.from || "/dashboard";
    return <Navigate to={from} replace />;
  }

  return <>{children}</>;
}
