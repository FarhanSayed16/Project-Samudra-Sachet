import React, { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { updateProfile, changePassword, clearError } from "../state/slices/authSlice";
import Badge from "../components/ui/Badge";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/Card";
import Separator from "../components/ui/Separator";
import Label from "../components/ui/Label";
import { User, Phone, ShieldCheck, Calendar, Edit2, Save, X, Lock, AlertCircle } from 'lucide-react';

const InfoItem = ({ icon, label, value }) => (
  <div className="flex items-center space-x-4">
    <div className="flex-shrink-0 w-12 h-12 flex items-center justify-center bg-slate-100 rounded-lg">
      {icon}
    </div>
    <div>
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="text-lg font-semibold text-slate-800">{value}</p>
    </div>
  </div>
);

export default function ProfilePage() {
  const dispatch = useDispatch();
  const { user, isLoading, error } = useSelector((state) => state.auth);

  const [isEditing, setIsEditing] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [form, setForm] = useState({
    full_name: "",
    phone_number: "",
    organization: ""
  });
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: ""
  });

  useEffect(() => {
    if (user) {
      setForm({
        full_name: user.full_name || "",
        phone_number: user.phone_number || "",
        organization: user.organization || "",
      });
    }
  }, [user]);

  const onSave = async () => {
    try {
      await dispatch(updateProfile(form)).unwrap();
      setIsEditing(false);
    } catch (e) {
      console.error("Failed to update profile:", e);
    }
  };

  const onPasswordChange = async () => {
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      alert("New passwords don't match");
      return;
    }

    try {
      await dispatch(changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password
      })).unwrap();
      setIsChangingPassword(false);
      setPasswordForm({
        current_password: "",
        new_password: "",
        confirm_password: ""
      });
    } catch (e) {
      console.error("Failed to change password:", e);
    }
  };

  const getInitials = (name) => {
    if (!name) return "?";
    const names = name.split(' ');
    if (names.length > 1) {
      return `${names[0][0]}${names[names.length - 1][0]}`;
    }
    return names[0].slice(0, 2);
  };

  const formattedJoinDate = user?.created_at
    ? new Date(user.created_at).toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric',
      })
    : 'N/A';

  if (isLoading || !user) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <p className="text-slate-600">Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-6xl mx-auto">
        <Card className="overflow-hidden shadow-xl rounded-2xl border-slate-200">
          <div className="grid grid-cols-1 md:grid-cols-3">
            <div className="md:col-span-1 bg-slate-100 p-8 flex flex-col items-center text-center">
              <div className="relative w-32 h-32 mb-4">
                <div className="w-full h-full rounded-full bg-primary-600 flex items-center justify-center text-white text-4xl font-bold ring-4 ring-white">
                  {getInitials(user.full_name)}
                </div>
              </div>
              <h1 className="text-3xl font-bold text-slate-900">{user.full_name}</h1>
              <Badge variant="secondary" className="mt-2 capitalize bg-primary-200 text-primary-800">
                {user.user_role}
              </Badge>
              <Separator className="my-6" />
              <div className="flex items-center space-x-3 text-slate-600">
                <Calendar size={20} />
                <span>Member since {formattedJoinDate}</span>
              </div>
            </div>

            <div className="md:col-span-2 p-8">
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-center mb-6">
                  <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                  <span className="text-sm text-red-700">{error}</span>
                </div>
              )}

              {!isEditing && !isChangingPassword ? (
                <>
                  <CardHeader className="p-0 mb-6 flex-row justify-between items-center">
                    <CardTitle className="text-2xl font-bold text-slate-800">Account Details</CardTitle>
                    <div className="flex space-x-2">
                      <Button variant="outline" onClick={() => setIsEditing(true)}>
                        <Edit2 size={16} className="mr-2" />
                        Edit Profile
                      </Button>
                      <Button variant="outline" onClick={() => setIsChangingPassword(true)}>
                        <Lock size={16} className="mr-2" />
                        Change Password
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="p-0 space-y-8">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                      <InfoItem icon={<User size={24} className="text-primary-600" />} label="Email" value={user.email} />
                      <InfoItem icon={<Phone size={24} className="text-primary-600" />} label="Phone Number" value={user.phone_number || "Not provided"} />
                      <InfoItem icon={<ShieldCheck size={24} className="text-primary-600" />} label="Organization" value={user.organization || "Not provided"} />
                      <InfoItem icon={<User size={24} className="text-primary-600" />} label="User ID" value={user.id} />
                    </div>
                    <div className="flex justify-center pt-4">
                      <div className="text-center">
                        <div className="text-4xl font-bold text-primary-600">
                          {user.is_verified ? "✓" : "⚠"}
                        </div>
                        <p className="text-sm font-medium text-slate-500">
                          {user.is_verified ? "Verified Account" : "Unverified Account"}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </>
              ) : isEditing ? (
                <>
                  <CardHeader className="p-0 mb-6">
                    <CardTitle className="text-2xl font-bold text-slate-800">Edit Profile</CardTitle>
                  </CardHeader>
                  <CardContent className="p-0 space-y-6">
                    <div>
                      <Label htmlFor="full_name" className="block text-sm font-medium text-slate-700 mb-1">Full Name</Label>
                      <Input id="full_name" value={form.full_name} onChange={(e) => setForm(f => ({ ...f, full_name: e.target.value }))} />
                    </div>
                    <div>
                      <Label htmlFor="phone_number" className="block text-sm font-medium text-slate-700 mb-1">Phone Number</Label>
                      <Input id="phone_number" value={form.phone_number} onChange={(e) => setForm(f => ({ ...f, phone_number: e.target.value }))} />
                    </div>
                    <div>
                      <Label htmlFor="organization" className="block text-sm font-medium text-slate-700 mb-1">Organization</Label>
                      <Input id="organization" value={form.organization} onChange={(e) => setForm(f => ({ ...f, organization: e.target.value }))} />
                    </div>
                    <div className="flex justify-end space-x-3 pt-4">
                      <Button variant="ghost" onClick={() => setIsEditing(false)}>
                        <X size={16} className="mr-2" />
                        Cancel
                      </Button>
                      <Button onClick={onSave} disabled={isLoading}>
                        <Save size={16} className="mr-2" />
                        {isLoading ? "Saving..." : "Save Changes"}
                      </Button>
                    </div>
                  </CardContent>
                </>
              ) : (
                <>
                  <CardHeader className="p-0 mb-6">
                    <CardTitle className="text-2xl font-bold text-slate-800">Change Password</CardTitle>
                  </CardHeader>
                  <CardContent className="p-0 space-y-6">
                    <div>
                      <Label htmlFor="current_password" className="block text-sm font-medium text-slate-700 mb-1">Current Password</Label>
                      <Input
                        id="current_password"
                        type="password"
                        value={passwordForm.current_password}
                        onChange={(e) => setPasswordForm(f => ({ ...f, current_password: e.target.value }))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="new_password" className="block text-sm font-medium text-slate-700 mb-1">New Password</Label>
                      <Input
                        id="new_password"
                        type="password"
                        value={passwordForm.new_password}
                        onChange={(e) => setPasswordForm(f => ({ ...f, new_password: e.target.value }))}
                      />
                    </div>
                    <div>
                      <Label htmlFor="confirm_password" className="block text-sm font-medium text-slate-700 mb-1">Confirm New Password</Label>
                      <Input
                        id="confirm_password"
                        type="password"
                        value={passwordForm.confirm_password}
                        onChange={(e) => setPasswordForm(f => ({ ...f, confirm_password: e.target.value }))}
                      />
                    </div>
                    <div className="flex justify-end space-x-3 pt-4">
                      <Button variant="ghost" onClick={() => setIsChangingPassword(false)}>
                        <X size={16} className="mr-2" />
                        Cancel
                      </Button>
                      <Button onClick={onPasswordChange} disabled={isLoading}>
                        <Save size={16} className="mr-2" />
                        {isLoading ? "Changing..." : "Change Password"}
                      </Button>
                    </div>
                  </CardContent>
                </>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
