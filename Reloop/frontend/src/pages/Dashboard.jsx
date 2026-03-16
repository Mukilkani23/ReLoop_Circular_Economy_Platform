/**
 * Dashboard Page — Overview of listings, impact analytics, and AI recommendations.
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { listingsAPI, analyticsAPI, recommendationsAPI, requestsAPI, notificationsAPI } from '../services/api';
import ImpactScore from '../components/ImpactScore';

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [listings, setListings] = useState([]);
  const [impact, setImpact] = useState(null);
  const [recommendations, setRecs] = useState([]);
  const [buyerRequests, setBuyerRequests] = useState([]); // Requests RECEIVED by this user (as seller)
  const [mySentRequests, setMySentRequests] = useState([]); // Requests SENT by this user (as buyer)
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [listingsRes, impactRes, requestsRes, myRequestsRes, notifsRes] = await Promise.all([
        listingsAPI.getAll(0, 5),
        analyticsAPI.getImpact(),
        requestsAPI.getSellerRequests(),
        requestsAPI.getBuyerRequests(),
        notificationsAPI.getAll(),
      ]);
      setListings(listingsRes.data);
      setImpact(impactRes.data);
      setBuyerRequests(requestsRes.data);
      setMySentRequests(myRequestsRes.data);
      setNotifications(notifsRes.data);

      // Get recommendations for the first listing if available
      if (listingsRes.data.length > 0) {
        try {
          const recsRes = await recommendationsAPI.getForListing(listingsRes.data[0].id);
          setRecs(recsRes.data);
        } catch {
          // AI recs may not be available
        }
      }
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="main-content page-enter">
        <div className="spinner"></div>
        <div className="loading-text">Loading your dashboard...</div>
      </div>
    );
  }

  const handleAccept = async (id) => {
    try {
      await requestsAPI.accept(id);
      loadDashboard();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to accept request');
    }
  };

  const handleReject = async (id) => {
    try {
      await requestsAPI.reject(id);
      loadDashboard();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to reject request');
    }
  };

  const handleComplete = async (id) => {
    try {
      await requestsAPI.complete(id);
      loadDashboard();
      alert("🎉 Transaction completed! Waste successfully diverted from landfill.");
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to complete transaction');
    }
  };

  const handleContactBuyer = (requestId) => {
    window.dispatchEvent(new CustomEvent('open-chat', { detail: { roomId: `chat_${requestId}` } }));
  };

  const platformMetrics = impact?.platform_metrics || {};
  const envImpact = impact?.environmental_impact || {};

  return (
    <div className="main-content page-enter">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.username}! 👋</h1>
        <p>Here's your circular economy overview</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card glass-card">
          <div className="stat-icon green">📦</div>
          <div className="stat-content">
            <h3>{platformMetrics.total_listings || 0}</h3>
            <p>Total Listings</p>
          </div>
        </div>
        <div className="stat-card glass-card">
          <div className="stat-icon blue">✅</div>
          <div className="stat-content">
            <h3>{platformMetrics.available_listings || 0}</h3>
            <p>Available Listings</p>
          </div>
        </div>
        <div className="stat-card glass-card">
          <div className="stat-icon amber">🤝</div>
          <div className="stat-content">
            <h3>{platformMetrics.total_transactions || 0}</h3>
            <p>Transactions</p>
          </div>
        </div>
        <div className="stat-card glass-card">
          <div className="stat-icon emerald">🌿</div>
          <div className="stat-content">
            <h3>{envImpact.co2_saved_kg?.toLocaleString() || 0} kg</h3>
            <p>CO₂ Saved</p>
          </div>
        </div>
      </div>

      {/* Dashboard Grid */}
      <div className="dashboard-grid">
        {/* Environmental Impact */}
        <div className="section-card glass-card">
          <h2>🌍 Environmental Impact</h2>
          <ImpactScore impact={envImpact} />
        </div>

        {/* AI Recommendations */}
        <div className="section-card glass-card">
          <h2>🤖 AI Industry Recommendations</h2>
          {recommendations.length > 0 ? (
            recommendations.map((rec, i) => (
              <div key={i} className="rec-card glass-card" style={{ marginBottom: '0.5rem' }}>
                <div className="rec-info">
                  <h4>{rec.industry}</h4>
                  <p>{rec.description}</p>
                </div>
                <div className="rec-score">
                  <span className="rec-score-value">{(rec.match_score * 100).toFixed(0)}%</span>
                  <span className="rec-score-label">Match</span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">
              <div className="icon">🔍</div>
              <h3>No Recommendations Yet</h3>
              <p>Create a listing to get AI-powered industry matches</p>
            </div>
          )}
        </div>

        {/* Recent Listings */}
        <div className="section-card glass-card" style={{ gridColumn: '1 / -1' }}>
          <h2>📋 Recent Listings</h2>
          {listings.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border)' }}>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Title</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Material</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Quantity</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Location</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Price</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {listings.map((l) => (
                    <tr
                      key={l.id}
                      onClick={() => navigate(`/listing/${l.id}`)}
                      style={{ borderBottom: '1px solid var(--border-light)', cursor: 'pointer', transition: 'var(--transition-fast)' }}
                      onMouseOver={(e) => (e.currentTarget.style.background = 'var(--bg-hover)')}
                      onMouseOut={(e) => (e.currentTarget.style.background = 'transparent')}
                    >
                      <td style={{ padding: '0.75rem', fontWeight: 600 }}>{l.title}</td>
                      <td style={{ padding: '0.75rem' }}>{l.material_type}</td>
                      <td style={{ padding: '0.75rem' }}>{l.quantity} {l.unit}</td>
                      <td style={{ padding: '0.75rem' }}>{l.location}</td>
                      <td style={{ padding: '0.75rem', color: 'var(--primary)', fontWeight: 700 }}>₹{l.price?.toLocaleString()}</td>
                      <td style={{ padding: '0.75rem' }}>
                        <span className={`listing-badge ${l.status?.toLowerCase()}`}>{l.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <div className="icon">📭</div>
              <h3>No Listings Yet</h3>
              <p>Be the first to list waste materials on the marketplace!</p>
              <button className="btn btn-primary" onClick={() => navigate('/marketplace')} style={{ marginTop: '1rem' }}>
                Go to Marketplace
              </button>
            </div>
          )}
        </div>

        {/* Buyer Requests */}
        <div className="section-card glass-card" style={{ gridColumn: '1 / -1' }}>
          <h2>📥 Buyer Requests</h2>
          {buyerRequests.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border)' }}>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Listing</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Buyer Email</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Quantity</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Status</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {buyerRequests.map((req) => (
                    <tr
                      key={req.id}
                      style={{ borderBottom: '1px solid var(--border-light)', transition: 'var(--transition-fast)' }}
                      onMouseOver={(e) => (e.currentTarget.style.background = 'var(--bg-hover)')}
                      onMouseOut={(e) => (e.currentTarget.style.background = 'transparent')}
                    >
                      <td style={{ padding: '0.75rem', fontWeight: 600 }}>{req.listing_title}</td>
                      <td style={{ padding: '0.75rem' }}>{req.buyer_email}</td>
                      <td style={{ padding: '0.75rem' }}>{req.quantity} {req.unit}</td>
                      <td style={{ padding: '0.75rem' }}>
                        <span className={`listing-badge ${req.status?.toLowerCase()}`}>{req.status}</span>
                      </td>
                      <td style={{ padding: '0.75rem' }}>
                        {req.status === 'PENDING' && (
                          <>
                            <button className="btn btn-primary btn-sm" onClick={() => handleAccept(req.id)} style={{ marginRight: '0.5rem', padding: '0.2rem 0.5rem' }}>Accept</button>
                            <button className="btn btn-secondary btn-sm" onClick={() => handleReject(req.id)} style={{ marginRight: '0.5rem', padding: '0.2rem 0.5rem' }}>Reject</button>
                          </>
                        )}
                        <button className="btn btn-secondary btn-sm" onClick={() => handleContactBuyer(req.id)} style={{ padding: '0.2rem 0.5rem' }}>💬 Chat</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <div className="icon">📬</div>
              <h3>No Requests Yet</h3>
              <p>You haven't received any buy requests for your listings.</p>
            </div>
          )}
        </div>

        {/* My Sent Requests (Buyer View) */}
        <div className="section-card glass-card" style={{ gridColumn: '1 / -1' }}>
          <h2>📤 My Sent Requests</h2>
          {mySentRequests.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border)' }}>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Listing</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Seller Email</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Status</th>
                    <th style={{ textAlign: 'left', padding: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {mySentRequests.map((req) => (
                    <tr key={req.id} style={{ borderBottom: '1px solid var(--border-light)' }}>
                      <td style={{ padding: '0.75rem', fontWeight: 600 }}>{req.listing_title}</td>
                      <td style={{ padding: '0.75rem' }}>{req.seller_email}</td>
                      <td style={{ padding: '0.75rem' }}>
                        <span className={`listing-badge ${req.status?.toLowerCase()}`}>{req.status}</span>
                      </td>
                      <td style={{ padding: '0.75rem', display: 'flex', gap: '0.5rem' }}>
                        <button className="btn btn-secondary btn-sm" onClick={() => handleContactBuyer(req.id)} style={{ padding: '0.2rem 0.5rem' }}>💬 Chat</button>
                        {req.status === 'ACCEPTED' && (
                          <button className="btn btn-primary btn-sm" onClick={() => handleComplete(req.id)} style={{ padding: '0.2rem 0.5rem', background: 'var(--success)' }}>✅ Mark Received</button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <div className="icon">🛒</div>
              <h3>No Requests Sent</h3>
              <p>Go to the Marketplace to request materials from other industries.</p>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
