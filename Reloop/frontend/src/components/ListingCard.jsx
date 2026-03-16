/**
 * ListingCard Component — Displays a single waste listing in the marketplace grid.
 */
import { useNavigate } from 'react-router-dom';

export default function ListingCard({ listing }) {
  const navigate = useNavigate();

  const statusClass = listing.status?.toLowerCase() || 'available';

  return (
    <div className="listing-card glass-card" onClick={() => navigate(`/listing/${listing.id}`)}>
      <div className="listing-card-header">
        <h3>{listing.title}</h3>
        <span className={`listing-badge ${statusClass}`}>{listing.status}</span>
      </div>

      <div className="listing-card-meta">
        <span>🏷️ {listing.material_type}</span>
        <span>📦 {listing.quantity} {listing.unit}</span>
        <span>📍 {listing.location}</span>
      </div>

      {listing.description && (
        <p className="listing-card-desc">{listing.description}</p>
      )}

      <div className="listing-card-footer">
        <span className="listing-price">₹{listing.price?.toLocaleString()}</span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          by {listing.owner_name || 'Anonymous'}
        </span>
      </div>
    </div>
  );
}
