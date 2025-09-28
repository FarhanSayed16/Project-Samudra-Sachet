import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getCurrentUser } from './state/slices/authSlice';
import Loader from './components/Loader';

export default function AuthInitializer({ children }) {
  const dispatch = useDispatch();
  const { token, user, isLoading } = useSelector(state => state.auth);

  useEffect(() => {
    if (token && !user) {
      dispatch(getCurrentUser());
    }
  }, [dispatch, token, user]);

  if (token && isLoading) {
    return <Loader fullScreen />;
  }

  return <>{children}</>;
}
