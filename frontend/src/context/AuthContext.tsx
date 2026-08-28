import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

export interface UserProfile {
  id: string;
  email: string;
  display_name: string;
  role: string;
  status: string;
  organization_id: string;
  organization_name: string;
}

interface AuthContextType {
  user: UserProfile | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  setDemoUser: (roleEmail: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Restore authenticated session from HttpOnly cookie on initialization
  useEffect(() => {
    api.getMe()
      .then(profile => {
        setUser(profile);
        setLoading(false);
      })
      .catch(() => {
        // Unauthenticated or expired session cookie
        setUser(null);
        setLoading(false);
      });
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.login(email, password);
    setUser({
      id: res.user_id,
      email: res.email,
      display_name: res.display_name,
      role: res.role,
      status: 'ACTIVE',
      organization_id: res.organization_id,
      organization_name: res.organization_name,
    });
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch (err) {
      console.error('Logout error:', err);
    }
    setUser(null);
  };

  const setDemoUser = async (roleEmail: string) => {
    await login(roleEmail, 'DemoPass123!');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, setDemoUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
