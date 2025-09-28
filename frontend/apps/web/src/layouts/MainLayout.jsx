import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Sidebar from '../components/Sidebar';
import { Toaster } from "../components/ui/sonner";

const MainLayout = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster richColors />
      <div className="flex">
        <Sidebar />
        <div className="flex-1 flex flex-col min-h-screen">
          <Header />
          <main className="flex-1 p-6 bg-gray-50 pt-16">
            <Outlet/>
          </main>
          <Footer/>
        </div>
      </div>
    </div>
  );
};

export default MainLayout;
