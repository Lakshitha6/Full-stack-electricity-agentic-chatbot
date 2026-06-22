import { AlertCircle, Zap } from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuthStore } from "@/store/authStore";
import { cn } from "@/utils/cn";
import { toast } from "@/components/ui/Toast";


export default function Login() {
  const [electricity_id, setElectricityId] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { login, isLoading, clearError } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();

  // Pre-fill ID if passed from signup
  const fromSignup = location.state?.electricity_id;
  if (fromSignup && !electricity_id) {
    setElectricityId(fromSignup);
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setError(null);

    // Basic validation
    if (!/^(ELEC-)?\d{6}$/.test(electricity_id.trim().toUpperCase())) {
      setError('Please enter a valid Electricity ID (e.g., ELEC-123456)');
      return;
    }

    try {
      await login(electricity_id.trim().toUpperCase());
      toast.success('Welcome back! 👋');
      // Redirect to where user tried to go, or home
      const from = (location.state as any)?.from?.pathname || '/';
      navigate(from, { replace: true });
    } catch (err: any) {
      toast.error(err.message || 'Login failed. Please check your ID.');
      setError(err.message || 'Login failed. Please check your ID.');
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Zap className="w-6 h-6 text-primary" />
          </div>
          <h2 className="mt-6 text-3xl font-bold tracking-tight">Welcome back</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Enter your Electricity ID to access your account
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {error && (
            <div className="rounded-md bg-destructive/10 p-4 border border-destructive/20">
              <div className="flex items-center gap-2 text-destructive text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>{error}</span>
              </div>
            </div>
          )}

          <div>
            <label htmlFor="electricity_id" className="block text-sm font-medium mb-2">
              Electricity ID
            </label>
            <input
              id="electricity_id"
              name="electricity_id"
              type="text"
              required
              value={electricity_id}
              onChange={(e) => setElectricityId(e.target.value)}
              placeholder="ELEC-123456"
              className={cn(
                "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
                "ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium",
                "placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                "disabled:cursor-not-allowed disabled:opacity-50"
              )}
            />
            <p className="mt-1 text-xs text-muted-foreground">
              Format: <code className="bg-muted px-1 py-0.5 rounded">ELEC-123456</code>
            </p>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className={cn(
              "w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white",
              "bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                Signing in...
              </span>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            Don't have an ID?{' '}
            <Link to="/signup" className="font-medium text-primary hover:text-primary/90">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}