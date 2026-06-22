import { useAuthStore } from "@/store/authStore";
import { cn } from "@/utils/cn";
import { downloadElectricityId } from "@/utils/downloadFile";
import { AlertCircle, CheckCircle, Download, Zap } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";



export default function Signup() {
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    nic_number: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ electricity_id: string } | null>(null);
  const { register, isLoading, clearError } = useAuthStore();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setError(null);

    // Basic validation
    if (formData.name.trim().length < 2) {
      setError('Name must be at least 2 characters');
      return;
    }
    if (!/^\+?[0-9\s\-]{7,15}$/.test(formData.phone_number)) {
      setError('Please enter a valid phone number');
      return;
    }
    if (formData.nic_number.trim().length < 5) {
      setError('NIC number must be at least 5 characters');
      return;
    }

    try {
      const electricity_id = await register(formData);
      setSuccess({ electricity_id });
      
      // Auto-download the ID file
      downloadElectricityId(electricity_id, `${electricity_id}.txt`);
      
      // Show success message, then redirect to login after delay
      setTimeout(() => {
        navigate('/login', { 
          state: { electricity_id },
          replace: true 
        });
      }, 3000);
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.');
    }
  };

  // Success state: show download confirmation
  if (success) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4">
        <div className="w-full max-w-md text-center space-y-6">
          <div className="mx-auto w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          
          <div>
            <h2 className="text-2xl font-bold">Registration Successful!</h2>
            <p className="mt-2 text-muted-foreground">
              Your Electricity ID has been generated and downloaded.
            </p>
          </div>

          <div className="bg-muted p-4 rounded-md">
            <p className="text-sm font-mono font-bold text-primary">
              {success.electricity_id}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Save this ID securely. You'll need it to log in.
            </p>
          </div>

          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <Download className="w-4 h-4" />
            <span>File downloaded: <code className="bg-muted px-1 rounded">{success.electricity_id}.txt</code></span>
          </div>

          <p className="text-sm">
            Redirecting to login in 3 seconds...{' '}
            <Link to="/login" className="text-primary hover:underline">
              Go now
            </Link>
          </p>
        </div>
      </div>
    );
  }

  // Form state
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
            <Zap className="w-6 h-6 text-primary" />
          </div>
          <h2 className="mt-6 text-3xl font-bold tracking-tight">Create your account</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Enter your details to get your unique Electricity ID
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

          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-1">
                Full Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleChange}
                placeholder="John Doe"
                className={cn(
                  "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
                  "ring-offset-background placeholder:text-muted-foreground",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                )}
              />
            </div>

            <div>
              <label htmlFor="phone_number" className="block text-sm font-medium mb-1">
                Phone Number
              </label>
              <input
                id="phone_number"
                name="phone_number"
                type="tel"
                required
                value={formData.phone_number}
                onChange={handleChange}
                placeholder="+1 234 567 8900"
                className={cn(
                  "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
                  "ring-offset-background placeholder:text-muted-foreground",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                )}
              />
            </div>

            <div>
              <label htmlFor="nic_number" className="block text-sm font-medium mb-1">
                NIC / ID Number
              </label>
              <input
                id="nic_number"
                name="nic_number"
                type="text"
                required
                value={formData.nic_number}
                onChange={handleChange}
                placeholder="123456789V"
                className={cn(
                  "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
                  "ring-offset-background placeholder:text-muted-foreground",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                )}
              />
              <p className="mt-1 text-xs text-muted-foreground">
                Used to verify your identity (stored securely)
              </p>
            </div>
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
                Creating account...
              </span>
            ) : (
              'Get My Electricity ID'
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            Already have an ID?{' '}
            <Link to="/login" className="font-medium text-primary hover:text-primary/90">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}