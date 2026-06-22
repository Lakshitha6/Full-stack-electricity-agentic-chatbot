import { authService } from '@/services/auth';
import { create } from 'zustand';

export interface User {
    electricity_id: string;
    name?: string;
    phone_number?: string;
}

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
    isInitialized: boolean;

    // Actions
    login: (electricity_id: string) => Promise<void>;
    register: (data: { name: string; phone_number: string; nic_number: string }) => Promise<string>;
    logout: () => Promise<void>;
    deleteAccount: () => Promise<void>;
    clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  isInitialized: false,

  login: async (electricity_id: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authService.login(electricity_id);
      
      if (response.token) {
        localStorage.setItem('jwt_token', response.token);

        const userData = response.user || { 
        electricity_id: response.electricity_id || electricity_id 
        };

        set({
          token: response.token,
          user: { 
            electricity_id: userData.electricity_id,
            name: userData.name,
            phone_number: userData.phone_number
          },
          isAuthenticated: true,
          isLoading: false,
        });
      } else {
        throw new Error('No token received from server');
      }
    } catch (err: any) {
      set({ 
        error: err.response?.data?.detail || 'Login failed. Please check your ID.',
        isLoading: false 
      });
      throw err;
    }
  },

  register: async (data: { name: string; phone_number: string; nic_number: string }) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authService.register(data);
      set({ isLoading: false });
      return response.electricity_id; // Return ID for download
    } catch (err: any) {
      set({ 
        error: err.response?.data?.detail || 'Registration failed. Please try again.',
        isLoading: false 
      });
      throw err;
    }
  },

  logout: async () => {
    try {
      const { api } = await import('@/services/api');
      await api.post('/api/v1/auth/logout');
    } catch (err) {
      console.warn('Backend logout call failed (continuing with local cleanup):', err);
    }
    
    localStorage.removeItem('jwt_token');
    set({ 
      token: null, 
      user: null, 
      isAuthenticated: false,
      error: null 
    });
  },

  deleteAccount: async () => {
    set({ isLoading: true, error: null });
    try {
      await authService.deleteAccount();
      get().logout(); // Clear auth state after deletion
    } catch (err: any) {
      set({ 
        error: err.response?.data?.detail || 'Failed to delete account.',
        isLoading: false 
      });
      throw err;
    }
  },

  clearError: () => set({ error: null }),

  setInitialized: () => set({ isInitialized: true }),
}));

// Initialize auth from localStorage on app load
export const initAuth = async () => {
  const token = localStorage.getItem('jwt_token');
  if (token) {
    try {
      //  Fetch fresh user data from backend (validates token + gets latest profile)
      const { authService } = await import('@/services/auth');
      const profile = await authService.getProfile();
      
      useAuthStore.setState({
        token,
        user: {
          electricity_id: profile.electricity_id,
          name: profile.name,
          phone_number: profile.phone_number,
        },
        isAuthenticated: true,
        isInitialized: true,  // ← Mark as ready
      });
    } catch (err) {
      // Token invalid/expired → clear auth state
      console.warn('Auth init failed (invalid token?):', err);
      localStorage.removeItem('jwt_token');
      useAuthStore.setState({
        token: null,
        user: null,
        isAuthenticated: false, 
        isInitialized: true 
      });
    }
  } else {
    // No token → mark initialized as guest
    useAuthStore.setState({ 
      token: null,
      user: null,
      isAuthenticated: false,
      isInitialized: true
     });
  }
};