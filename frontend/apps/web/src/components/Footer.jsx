import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 py-4">
      <div className="px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-sm text-gray-500">
              © 2024 Project Samudra Sachet. All rights reserved.
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">Version 1.0.0</span>
            <div className="flex items-center text-sm text-gray-500">
              <span className="mr-1">🌊</span>
              Coastal Hazard Monitoring System
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
