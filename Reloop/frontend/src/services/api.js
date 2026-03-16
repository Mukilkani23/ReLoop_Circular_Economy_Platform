/**
 * API Service — Centralized HTTP client for all backend requests.
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('reloop_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses (expired token)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('reloop_token');
      localStorage.removeItem('reloop_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// === Auth API ===
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
};

// === Listings API ===
export const listingsAPI = {
  getAll: (skip = 0, limit = 50) => api.get(`/listings?skip=${skip}&limit=${limit}`),
  getById: (id) => api.get(`/listings/${id}`),
  create: (data) => api.post('/listings', data),
  update: (id, data) => api.put(`/listings/${id}`, data),
  delete: (id) => api.delete(`/listings/${id}`),
  buy: (id) => api.post(`/listings/${id}/buy`),
  search: (params) => api.get('/listings/search', { params }),
};

// === Recommendations API ===
export const recommendationsAPI = {
  getForListing: (listingId) => api.get(`/recommendations/${listingId}`),
  getForMaterial: (materialType) => api.get(`/recommendations/material/${materialType}`),
  getImpact: (listingId) => api.get(`/recommendations/impact/${listingId}`),
};

// === Analytics API ===
export const analyticsAPI = {
  getImpact: () => api.get('/analytics/impact'),
};

// === Requests API ===
export const requestsAPI = {
  create: (data) => api.post('/requests/', data),
  getSellerRequests: () => api.get('/requests/seller'),
  getBuyerRequests: () => api.get('/requests/buyer'),
  accept: (requestId) => api.post(`/requests/${requestId}/accept`),
  reject: (requestId) => api.post(`/requests/${requestId}/reject`),
  complete: (requestId) => api.post(`/requests/${requestId}/complete`),
};

// === Notifications API ===
export const notificationsAPI = {
  getAll: () => api.get('/notifications/'),
  getUnreadCount: () => api.get('/notifications/unread-count'),
  markAsRead: (id) => api.put(`/notifications/${id}/read`),
};

// === Chat API ===
export const chatAPI = {
  uploadPublicKey: (publicKey) => api.post('/chat/keys', { public_key: publicKey }),
  getPublicKey: (userId) => api.get(`/chat/keys/${userId}`),
  getRoomInfo: (requestId) => api.get(`/chat/room/${requestId}`),
  getMessages: (roomId) => api.get(`/chat/messages/${roomId}`),
};

// === WebSocket URL ===
export const WS_URL = 'ws://localhost:8000/ws/chat';

export default api;
