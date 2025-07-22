import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import api from './api';

// Types
export type UserRole = 'teacher' | 'ta' | 'student';

interface User {
  id: string;
  username: string;
  email: string;
  role: UserRole;
  fullName?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  userRole: UserRole | null;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
}

interface RegisterData {
  username: string;
  email: string;
  password: string;
  fullName?: string;
  role: UserRole;
}

interface AuthProviderProps {
  children: ReactNode;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!token);
  const [userRole, setUserRole] = useState<UserRole | null>(null);

  // Check if token exists on mount
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        try {
          // Set auth header for all requests
          api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
          
          // Get user info
          const response = await api.get('/api/v1/auth/me');
          setUser(response.data);
          setUserRole(response.data.role);
          setIsAuthenticated(true);
        } catch (error) {
          console.error('Authentication failed:', error);
          logout();
        }
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (username: string, password: string) => {
    try {
      const response = await api.post('/api/v1/auth/login', {
        username,
        password,
      });

      const { access_token, user_role } = response.data;
      
      // Save token to localStorage
      localStorage.setItem('token', access_token);
      
      // Set auth header for all requests
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Get user info
      const userResponse = await api.get('/api/v1/auth/me');
      
      // Update state
      setToken(access_token);
      setUser(userResponse.data);
      setUserRole(user_role);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  // Register function
  const register = async (userData: RegisterData) => {
    try {
      await api.post('/api/v1/auth/register', userData);
      // After registration, log in automatically
      await login(userData.username, userData.password);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  // Logout function
  const logout = () => {
    // Remove token from localStorage
    localStorage.removeItem('token');
    
    // Remove auth header
    delete api.defaults.headers.common['Authorization'];
    
    // Update state
    setToken(null);
    setUser(null);
    setUserRole(null);
    setIsAuthenticated(false);
  };

  // Context value
  const value = {
    user,
    token,
    isAuthenticated,
    userRole,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 