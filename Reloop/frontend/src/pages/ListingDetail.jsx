/**
 * ListingDetail Page — View a single listing with AI recommendations and impact score.
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { listingsAPI, recommendationsAPI, requestsAPI } from '../services/api';
import ImpactScore from '../components/ImpactScore';

export default function ListingDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [listing, setListing] = useState(null);
  const [recommendations, setRecs] = useState([]);
  const [impact, setImpact] = useState(null);
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    loadListing();
  }, [id]);

  const loadListing = async () => {
    try {
      const [listingRes, recsRes, impactRes] = await Promise.allSettled([
        listingsAPI.getById(id),
        recommendationsAPI.getForListing(id),
        recommendationsAPI.getImpact(id),
      ]);

      if (listingRes.status === 'fulfilled') setListing(listingRes.value.data);
      if (recsRes.status === 'fulfilled') setRecs(recsRes.value.data);
      if (impactRes.status === 'fulfilled') setImpact(impactRes.value.data);
    } catch (err) {
      console.error('Failed to load listing:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRequest = async () => {
    setBuying(true);
    try {
      await requestsAPI.create({ listing_id: parseInt(id) });
      setMessage({ type: 'success', text: 'Your request has been sent to the seller. They can contact you through chat.' });
      await loadListing();
    } catch (err) {
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Failed to send request' });
    } finally {
      setBuying(false);
    }
  };

  if (loading) {
    return (
      <div className="main-content page-enter">
        <div className="spinner"></div>
        <div className="loading-text">Loading listing details...</div>
      </div>
    );
  }

  if (!listing) {
    return (
      <div className="main-content page-enter">
        <div className="empty-state">
          <div className="icon">❌</div>
          <h3>Listing Not Found</h3>
          <button className="btn btn-primary" onClick={() => navigate('/marketplace')}>Back to Marketplace</button>
        </div>
      </div>
    );
  }

  return (
    <div className="main-content page-enter">
      <div className="listing-detail">
        {/* Back Button */}
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => navigate('/marketplace')}
          style={{ marginBottom: '1.5rem' }}
        >
          ← Back to Marketplace
        </button>

        {/* Messages */}
        {message.text && (
          <div className={`alert alert-${message.type}`}>{message.text}</div>
        )}

        {/* Listing Header */}
        <div className="listing-detail-header glass-card" style={{ padding: '2rem', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1>{listing.title}</h1>
              <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                Listed by <strong>{listing.owner_name}</strong> • {new Date(listing.created_at).toLocaleDateString()}
              </p>
            </div>
            <span className={`listing-badge ${listing.status?.toLowerCase()}`} style={{ fontSize: '0.85rem', padding: '0.4rem 1rem' }}>
              {listing.status}
            </span>
          </div>

          {listing.description && (
            <p style={{ marginTop: '1rem', color: 'var(--text-secondary)', lineHeight: 1.7 }}>
              {listing.description}
            </p>
          )}

          {/* Detail Grid */}
          <div className="listing-detail-info" style={{ marginTop: '1.5rem' }}>
            <div className="detail-item">
              <label>Material Type</label>
              <p>🏷️ {listing.material_type}</p>
            </div>
            <div className="detail-item">
              <label>Quantity</label>
              <p>📦 {listing.quantity} {listing.unit}</p>
            </div>
            <div className="detail-item">
              <label>Price</label>
              <p>💰 ₹{listing.price?.toLocaleString()}</p>
            </div>
            <div className="detail-item">
              <label>Location</label>
              <p>📍 {listing.location}</p>
            </div>
          </div>

          {/* Buy Button */}
          {listing.status === 'AVAILABLE' && listing.user_id !== user?.id && (
            <button
              id="buy-listing-btn"
              className="btn btn-primary btn-lg"
              onClick={handleRequest}
              disabled={buying}
              style={{ marginTop: '1rem' }}
            >
              {buying ? 'Processing...' : '🛒 Request Material'}
            </button>
          )}
        </div>

        {/* Environmental Impact */}
        {impact && (
          <div className="section-card glass-card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              🌍 Environmental Impact Score
            </h2>
            <ImpactScore impact={impact} />
          </div>
        )}

        {/* AI Recommendations */}
        <div className="recommendations-section">
          <div className="section-card glass-card" style={{ padding: '1.5rem' }}>
            <h2>🤖 AI-Recommended Industries</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1rem' }}>
              Industries best suited to reuse this waste material
            </p>
            {recommendations.length > 0 ? (
              recommendations.map((rec, i) => (
                <div key={i} className="rec-card glass-card">
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
                <h3>No Recommendations Available</h3>
                <p>AI recommendations will appear here when the engine is trained.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
