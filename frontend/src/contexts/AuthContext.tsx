import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import {
  fetchCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
  updateProfile,
  type AuthUser,
} from "@/services/api";

const TOKEN_KEY = "ats_auth_token";

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<string>;
  register: (fullName: string, email: string, password: string, phone?: string) => Promise<string>;
  logout: () => Promise<void>;
  updateUserProfile: (fullName: string, phone: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = sessionStorage.getItem(TOKEN_KEY);
    if (!token) {
      setIsLoading(false);
      return;
    }
    fetchCurrentUser(token)
      .then((currentUser) => setUser(currentUser))
      .catch(() => sessionStorage.removeItem(TOKEN_KEY))
      .finally(() => setIsLoading(false));
  }, []);

  const login = async (email: string, password: string) => {
    const { token, user: loggedInUser } = await loginUser(email, password);
    sessionStorage.setItem(TOKEN_KEY, token);
    setUser(loggedInUser);
    return token;
  };

  const register = async (fullName: string, email: string, password: string, phone = "") => {
    const message = await registerUser(fullName, email, password, phone);
    return message;
  };

  const logout = async () => {
    const token = sessionStorage.getItem(TOKEN_KEY);
    if (token) {
      try {
        await logoutUser(token);
      } catch {
        /* clear local session even if API call fails */
      }
    }
    sessionStorage.removeItem(TOKEN_KEY);
    setUser(null);
  };

  const updateUserProfile = async (fullName: string, phone: string) => {
    const token = sessionStorage.getItem(TOKEN_KEY);
    if (!token) throw new Error("Not authenticated");
    const updated = await updateProfile(token, fullName, phone);
    setUser(updated);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        updateUserProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function getAuthToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}
