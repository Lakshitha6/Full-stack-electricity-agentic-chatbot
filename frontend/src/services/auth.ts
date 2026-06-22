import { api } from "./api";

export interface RegisterRequest {
    name: string;
    phone_number: string;
    nic_number: string;
}

export interface LoginRequest {
    electricity_id: string;
}

export interface AuthResponse {

    token: string;
    token_type: string;
    user: {                           // ← Nested user object
      electricity_id: string;
      name?: string;
      phone_number?: string;
    };
    
    electricity_id: string;
    name?: string;
    phone_number?: string;
}

export const authService = {
  /**
   * Register a new user
   * Returns: { electricity_id: "ELEC-XXXXXX" }
   */
  register: async (data: RegisterRequest): Promise<{ electricity_id: string }> => {
    const response = await api.post('/api/v1/auth/register', data);
    return response.data;
  },

    /**
   * Login with electricity ID
   * Returns: { token, user: { electricity_id, name, phone_number } }
   */
  login: async (electricity_id: string): Promise<AuthResponse> => {
    const response = await api.post('/api/v1/auth/login', { electricity_id });
    return response.data;
  },

  /**
   * Get current user profile (requires JWT)
   */
  getProfile: async (): Promise<AuthResponse> => {
    const response = await api.get('/api/v1/auth/profile');
    return response.data;
  },

  /**
   * Delete user account (requires JWT)
   */
  deleteAccount: async (): Promise<void> => {
    await api.delete('/api/v1/auth/account');
  },
};