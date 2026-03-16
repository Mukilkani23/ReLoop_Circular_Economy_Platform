/**
 * Auth Context — Global authentication state management.
 * Stores JWT token and user info, provides login/logout/register functions.
 */
import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI, chatAPI } from '../services/api';
import CryptoService from '../services/cryptoService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('reloop_token'));
  const [loading, setLoading] = useState(true);

  // Load user on mount if token exists
  useEffect(() => {
    if (token) {
      authAPI.getMe()
        .then(async (res) => {
          setUser(res.data);
          
          // --- E2EE Key Management for Existing Session ---
          let publicKey = localStorage.getItem(`reloop_pub_${res.data.id}`);
          let secretKey = localStorage.getItem(`reloop_sec_${res.data.id}`);

          if (!publicKey || !secretKey) {
            const keyPair = CryptoService.generateKeyPair();
            publicKey = CryptoService.keyToBase64(keyPair.publicKey);
            secretKey = CryptoService.keyToBase64(keyPair.secretKey);
            localStorage.setItem(`reloop_pub_${res.data.id}`, publicKey);
            localStorage.setItem(`reloop_sec_${res.data.id}`, secretKey);
          }

          try {
            await chatAPI.uploadPublicKey(publicKey);
          } catch (err) {
            console.error("Failed to sync E2EE public key on mount:", err);
          }
        })
        .catch(() => {
          localStorage.removeItem('reloop_token');
          localStorage.removeItem('reloop_user');
          setToken(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (username, password) => {
    const res = await authAPI.login({ username, password });
    const accessToken = res.data.access_token;
    localStorage.setItem('reloop_token', accessToken);
    setToken(accessToken);

    const userRes = await authAPI.getMe();
    setUser(userRes.data);
    localStorage.setItem('reloop_user', JSON.stringify(userRes.data));

    // --- E2EE Key Management ---
    let publicKey = localStorage.getItem(`reloop_pub_${userRes.data.id}`);
    let secretKey = localStorage.getItem(`reloop_sec_${userRes.data.id}`);

    if (!publicKey || !secretKey) {
      const keyPair = CryptoService.generateKeyPair();
      publicKey = CryptoService.keyToBase64(keyPair.publicKey);
      secretKey = CryptoService.keyToBase64(keyPair.secretKey);
      localStorage.setItem(`reloop_pub_${userRes.data.id}`, publicKey);
      localStorage.setItem(`reloop_sec_${userRes.data.id}`, secretKey);
    }

    // Always ensure the backend has the latest public key
    try {
      await chatAPI.uploadPublicKey(publicKey);
    } catch (err) {
      console.error("Failed to upload E2EE public key:", err);
    }

    return userRes.data;
  };

  const register = async (userData) => {
    const res = await authAPI.register(userData);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem('reloop_token');
    localStorage.removeItem('reloop_user');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
