/**
 * Settings Page - Officer Dashboard
 */

'use client';

import { useState } from 'react';
import { useAuth } from '@/context/AuthContext';
import { 
  Card, CardContent, CardHeader, CardTitle, CardDescription 
} from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Switch } from '@/components/ui/Switch';
import { Shield, User, Bell, Key, Database, Cpu } from 'lucide-react';



export default function SettingsPage() {
  const { user } = useAuth();
  const [settings, setSettings] = useState({
    demoMode: true,
    emailNotifications: true,
    autoAssign: false,
    retentionDays: 90,
    confidenceThreshold: 0.5,
  });

  const handleChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-1">Configure system preferences and account settings</p>
      </div>

      {/* Demo Mode Toggle */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Cpu className="w-5 h-5" />System Mode</CardTitle>
          <CardDescription>Configure the operating mode of the AI analysis system</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Demo Mode</p>
              <p className="text-sm text-gray-500">Use synthetic data and simulated analysis results</p>
            </div>
            <Switch
              checked={settings.demoMode}
              onChange={(checked) => handleChange('demoMode', checked)}
              aria-label="Toggle demo mode"
            />
          </div>
          <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800">
            <strong>Note:</strong> Demo mode uses fictional/synthetic cases. No real victim data is processed.
          </div>
        </CardContent>
      </Card>

      {/* General Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Shield className="w-5 h-5" />General Settings</CardTitle>
          <CardDescription>System-wide configuration options</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Email Notifications</p>
              <p className="text-sm text-gray-500">Receive email alerts for high-priority cases</p>
            </div>
            <Switch
              checked={settings.emailNotifications}
              onChange={(checked) => handleChange('emailNotifications', checked)}
              aria-label="Toggle email notifications"
            />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Auto-assign Cases</p>
              <p className="text-sm text-gray-500">Automatically assign new cases to available officers</p>
            </div>
            <Switch
              checked={settings.autoAssign}
              onChange={(checked) => handleChange('autoAssign', checked)}
              aria-label="Toggle auto-assign"
            />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Data Retention (days)</label>
              <Input
                type="number"
                value={settings.retentionDays}
                onChange={(e) => handleChange('retentionDays', parseInt(e.target.value))}
                min={1}
                max={365}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confidence Threshold</label>
              <Input
                type="number"
                step="0.1"
                value={settings.confidenceThreshold}
                onChange={(e) => handleChange('confidenceThreshold', parseFloat(e.target.value))}
                min={0}
                max={1}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Account Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><User className="w-5 h-5" />Account Settings</CardTitle>
          <CardDescription>Manage your account preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input label="Name" value={user?.name || ''} disabled />
            <Input label="Identifier" value={user?.identifier || ''} disabled />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <p className="text-sm text-gray-600">{user?.role || 'AUTHORIZED_STAFF'}</p>
          </div>
          <Button variant="outline">Update Profile</Button>
        </CardContent>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Key className="w-5 h-5" />Security</CardTitle>
          <CardDescription>Security and authentication settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Two-Factor Authentication</p>
              <p className="text-sm text-gray-500">Add an extra layer of security to your account</p>
            </div>
            <Button variant="outline" size="sm">Enable 2FA</Button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Change Password</p>
              <p className="text-sm text-gray-500">Update your account password</p>
            </div>
            <Button variant="outline" size="sm">Change Password</Button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">API Keys</p>
              <p className="text-sm text-gray-500">Manage API keys for external integrations</p>
            </div>
            <Button variant="outline" size="sm">Manage Keys</Button>
          </div>
        </CardContent>
      </Card>

      {/* Database & System Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Database className="w-5 h-5" />System Information</CardTitle>
          <CardDescription>System status and version information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex justify-between"><span className="text-gray-500">Application Version</span><span className="font-mono">1.0.0-prototype</span></div>
          <div className="flex justify-between"><span className="text-gray-500">AI Services Mode</span><span className="font-mono">{settings.demoMode ? 'Demo (Rule-based)' : 'Real (ML models)'}</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Database</span><span className="font-mono">PostgreSQL</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Backend</span><span className="font-mono">FastAPI + Python</span></div>
          <div className="flex justify-between"><span className="text-gray-500">Frontend</span><span className="font-mono">Next.js + React + TypeScript</span></div>
        </CardContent>
      </Card>
    </div>
  );
}
