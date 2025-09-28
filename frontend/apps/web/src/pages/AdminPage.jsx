import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchUsers, updateUserRole } from '../state/slices/adminSlice';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Badge from '../components/ui/Badge';
import { Search, Filter, Users, Shield, UserCheck, UserX } from 'lucide-react';

const AdminPage = () => {
  const dispatch = useDispatch();
  const { users, isLoading, pagination } = useSelector((state) => state.admin);
  
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState('');

  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);

  const handleSearch = () => {
    const filters = {
      search: searchTerm,
      role: selectedRole || null,
    };
    dispatch(fetchUsers(filters));
  };

  const handleRoleChange = async (userId, newRole) => {
    try {
      await dispatch(updateUserRole({ userId, roleData: { user_role: newRole } })).unwrap();
      dispatch(fetchUsers()); // Refresh the list
    } catch (error) {
      console.error('Failed to update user role:', error);
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'danger';
      case 'authority': return 'warning';
      case 'analyst': return 'secondary';
      case 'citizen': return 'default';
      default: return 'default';
    }
  };

  const getStatusColor = (isActive, isVerified) => {
    if (!isActive) return 'danger';
    if (!isVerified) return 'warning';
    return 'success';
  };

  const getStatusText = (isActive, isVerified) => {
    if (!isActive) return 'Inactive';
    if (!isVerified) return 'Unverified';
    return 'Active';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
          <p className="text-gray-600">Manage users and system settings</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="secondary">
            <Users className="h-3 w-3 mr-1" />
            {pagination.total || users.length} Users
          </Badge>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Filter className="h-5 w-5 mr-2" />
            User Management
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4 items-end">
            <div className="flex-1 min-w-64">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search Users
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search by name or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="min-w-32">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Role
              </label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">All Roles</option>
                <option value="admin">Admin</option>
                <option value="authority">Authority</option>
                <option value="analyst">Analyst</option>
                <option value="citizen">Citizen</option>
              </select>
            </div>

            <Button onClick={handleSearch}>
              Search
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Users List */}
      <Card>
        <CardHeader>
          <CardTitle>Users ({pagination.total || users.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading users...</p>
            </div>
          ) : users.length > 0 ? (
            <div className="space-y-4">
              {users.map((user) => (
                <div key={user.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-medium">
                        {user.full_name?.charAt(0)?.toUpperCase()}
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h3 className="font-medium text-gray-900">{user.full_name}</h3>
                          <Badge variant={getRoleColor(user.user_role)}>
                            {user.user_role}
                          </Badge>
                          <Badge variant={getStatusColor(user.is_active, user.is_verified)}>
                            {getStatusText(user.is_active, user.is_verified)}
                          </Badge>
                        </div>
                        
                        <p className="text-sm text-gray-600">{user.email}</p>
                        {user.organization && (
                          <p className="text-xs text-gray-500">{user.organization}</p>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <select
                        value={user.user_role}
                        onChange={(e) => handleRoleChange(user.id, e.target.value)}
                        className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      >
                        <option value="citizen">Citizen</option>
                        <option value="analyst">Analyst</option>
                        <option value="authority">Authority</option>
                        <option value="admin">Admin</option>
                      </select>
                      
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
              <p className="text-gray-600">Try adjusting your search criteria.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminPage;
