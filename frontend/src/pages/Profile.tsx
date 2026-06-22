import { useState } from 'react';
import { useNavigate, Navigate } from 'react-router-dom';
import { User, LogOut, Trash2, AlertTriangle } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/utils/cn';

export default function Profile() {
  const { user, logout, deleteAccount, isLoading, error, clearError, isAuthenticated, isInitialized } = useAuthStore();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteText, setDeleteText] = useState('');
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/', { replace: true });
  };

  const handleDeleteAccount = async () => {
    if (deleteText.trim().toUpperCase() !== 'DELETE') {
      return;
    }
    
    try {
      await deleteAccount();
      navigate('/', { replace: true });
    } catch (err) {
      // Error already set in store
    }
  };

  if (!isInitialized) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Redirect if not authenticated (after initialization)
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (!user) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <p className="text-muted-foreground">Unable to load profile. Please try logging in again.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto py-12 px-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">My Profile</h1>
          <p className="text-muted-foreground">Manage your account settings</p>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Logout
        </button>
      </div>

      {/* User Info Card */}
      <div className="bg-card border rounded-lg p-6 space-y-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
            <User className="w-6 h-6 text-primary" />
          </div>
          <div>
            <p className="font-medium">{user.name || 'User'}</p>
            <p className="text-sm text-muted-foreground font-mono">{user.electricity_id}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t">
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase">Phone</p>
            <p className="mt-1">{user.phone_number || 'Not provided'}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase">Member Since</p>
            <p className="mt-1">2024</p>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold mb-4">Danger Zone</h2>
        
        {!showDeleteConfirm ? (
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="flex items-center gap-2 px-4 py-2 border border-destructive text-destructive rounded-md hover:bg-destructive/10 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            Delete Account
          </button>
        ) : (
          <div className="border border-destructive rounded-lg p-4 space-y-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-destructive mt-0.5" />
              <div>
                <p className="font-medium text-destructive">Delete Account?</p>
                <p className="text-sm text-muted-foreground mt-1">
                  This action cannot be undone. All your data, chat history, and preferences will be permanently deleted.
                </p>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">
                Type <code className="bg-muted px-1 rounded">DELETE</code> to confirm:
              </label>
              <input
                type="text"
                value={deleteText}
                onChange={(e) => setDeleteText(e.target.value)}
                placeholder="Type DELETE"
                className={cn(
                  "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                )}
              />
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={handleDeleteAccount}
                disabled={deleteText.trim().toUpperCase() !== 'DELETE' || isLoading}
                className={cn(
                  "px-4 py-2 bg-destructive text-white rounded-md text-sm font-medium",
                  "hover:bg-destructive/90 disabled:opacity-50 disabled:cursor-not-allowed"
                )}
              >
                {isLoading ? 'Deleting...' : 'Confirm Delete'}
              </button>
              <button
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setDeleteText('');
                  clearError();
                }}
                className="px-4 py-2 border rounded-md text-sm font-medium hover:bg-muted"
              >
                Cancel
              </button>
            </div>
            
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}