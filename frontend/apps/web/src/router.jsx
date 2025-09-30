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
  CitizenPage,
} from './pages';
import { NotFound } from './components';

export default createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<MainLayout />}>
      <Route index element={<Navigate to="/login" replace />} />

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
          <AuthLayout authentication={true} roles={['coastal_volunteer', 'coastal_guard', 'disaster_manager', 'admin']}>
            <DashboardPage />
          </AuthLayout>
        }
      />

      <Route
        path="reports"
        element={
          <AuthLayout authentication={true} roles={['coastal_volunteer', 'coastal_guard', 'disaster_manager', 'admin']}>
            <ReportsPage />
          </AuthLayout>
        }
      />

      <Route
        path="verification"
        element={
          <AuthLayout authentication={true} roles={['coastal_volunteer', 'coastal_guard', 'disaster_manager']}>
            <VerificationPage />
          </AuthLayout>
        }
      />

      <Route
        path="hotspots"
        element={
          <AuthLayout authentication={true} roles={['coastal_volunteer', 'coastal_guard', 'disaster_manager', 'admin']}>
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
          <AuthLayout authentication={true} roles={['citizen', 'coastal_volunteer', 'coastal_guard', 'disaster_manager', 'admin']}>
            <ProfilePage />
          </AuthLayout>
        }
      />

      <Route
        path="citizen"
        element={
          <AuthLayout authentication={true} roles={['citizen']}>
            <CitizenPage />
          </AuthLayout>
        }
      />

      <Route path="*" element={<NotFound />} />
    </Route>
  )
);
