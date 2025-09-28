import React from 'react';
import { createBrowserRouter, createRoutesFromElements, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import AuthLayout from './layouts/AuthLayout';
import {
  DashboardPage,
  LoginPage,
  ProfilePage,
  ReportsPage,
  HotspotsPage,
  AdminPage,
  VerificationPage,
} from './pages';
import { NotFound } from './components';

export default createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<MainLayout />}>
      <Route index element={<Navigate to="/dashboard" replace />} />

      <Route
        path="login"
        element={
          <AuthLayout authentication={false}>
            <LoginPage />
          </AuthLayout>
        }
      />

      <Route
        path="dashboard"
        element={
          <AuthLayout authentication={true} roles={['analyst', 'authority', 'admin']}>
            <DashboardPage />
          </AuthLayout>
        }
      />

      <Route
        path="reports"
        element={
          <AuthLayout authentication={true} roles={['analyst', 'authority', 'admin']}>
            <ReportsPage />
          </AuthLayout>
        }
      />

      <Route
        path="verification"
        element={
          <AuthLayout authentication={true} roles={['analyst', 'authority']}>
            <VerificationPage />
          </AuthLayout>
        }
      />

      <Route
        path="hotspots"
        element={
          <AuthLayout authentication={true} roles={['analyst', 'authority', 'admin']}>
            <HotspotsPage />
          </AuthLayout>
        }
      />

      <Route
        path="admin"
        element={
          <AuthLayout authentication={true} roles={['admin']}>
            <AdminPage />
          </AuthLayout>
        }
      />

      <Route
        path="profile"
        element={
          <AuthLayout authentication={true}>
            <ProfilePage />
          </AuthLayout>
        }
      />

      <Route path="*" element={<NotFound />} />
    </Route>
  )
);
