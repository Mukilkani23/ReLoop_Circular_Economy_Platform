/**
 * Marketplace Page — Browse, search, and create waste listings.
 */
import { useState, useEffect } from 'react';
import { listingsAPI } from '../services/api';
import ListingCard from '../components/ListingCard';

export default function Marketplace() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchMaterial, setSearchMaterial] = useState('');
  const [searchLocation, setSearchLocation] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [newListing, setNewListing] = useState({
    title: '',
    material_type: '',
    description: '',
    quantity: '',
    unit: 'kg',
    price: '',
    location: '',
  });

  useEffect(() => {
    loadListings();
  }, []);

  const loadListings = async () => {
    try {
      const res = await listingsAPI.getAll();
      setListings(res.data);
    } catch (err) {
      console.error('Failed to load listings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      if (!searchMaterial && !searchLocation) {
        await loadListings();
        return;
      }
      const params = {};
      if (searchMaterial) params.material = searchMaterial;
      if (searchLocation) params.location = searchLocation;
      const res = await listingsAPI.search(params);
      setListings(res.data);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    setError('');

    try {
      await listingsAPI.create({
        ...newListing,
        quantity: parseFloat(newListing.quantity),
        price: parseFloat(newListing.price),
      });
      setSuccess('Listing created successfully! 🎉');
      setShowModal(false);
      setNewListing({ title: '', material_type: '', description: '', quantity: '', unit: 'kg', price: '', location: '' });
      await loadListings();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create listing');
    } finally {
      setCreating(false);
    }
  };

  const handleInputChange = (e) => {
    setNewListing({ ...newListing, [e.target.name]: e.target.value });
  };

  return (
    <div className="main-content page-enter">
      {/* Header */}
      <div className="marketplace-header">
        <div>
          <h1>🏪 Marketplace</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Browse and list waste materials for the circular economy
          </p>
        </div>
        <button id="create-listing-btn" className="btn btn-primary" onClick={() => setShowModal(true)}>
          ➕ Create Listing
        </button>
      </div>

      {/* Search Bar */}
      <div className="search-bar" style={{ marginBottom: '1.5rem' }}>
        <input
          type="text"
          className="form-input"
          placeholder="🔍 Search by material..."
          value={searchMaterial}
          onChange={(e) => setSearchMaterial(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <input
          type="text"
          className="form-input"
          placeholder="📍 Filter by location..."
          value={searchLocation}
          onChange={(e) => setSearchLocation(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button className="btn btn-secondary" onClick={handleSearch}>
          Search
        </button>
      </div>

      {/* Messages */}
      {success && <div className="alert alert-success">{success}</div>}
      {error && <div className="alert alert-error">{error}</div>}

      {/* Listings Grid */}
      {loading ? (
        <div>
          <div className="spinner"></div>
          <div className="loading-text">Loading listings...</div>
        </div>
      ) : listings.length > 0 ? (
        <div className="listings-grid">
          {listings.map((listing) => (
            <ListingCard key={listing.id} listing={listing} />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <div className="icon">📭</div>
          <h3>No Listings Found</h3>
          <p>Be the first to create a waste listing!</p>
        </div>
      )}

      {/* Create Listing Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowModal(false)}>
          <div className="modal-content">
            <h2>📦 Create New Listing</h2>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label className="form-label">Title</label>
                <input
                  type="text"
                  name="title"
                  className="form-input"
                  value={newListing.title}
                  onChange={handleInputChange}
                  placeholder="e.g., Scrap Steel from Factory"
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Material Type</label>
                <select
                  name="material_type"
                  className="form-select"
                  value={newListing.material_type}
                  onChange={handleInputChange}
                  required
                >
                  <option value="">Select material type</option>
                  <option value="Steel">Steel</option>
                  <option value="Plastic">Plastic</option>
                  <option value="Wood">Wood</option>
                  <option value="Paper">Paper</option>
                  <option value="Glass">Glass</option>
                  <option value="Textile">Textile</option>
                  <option value="Food/Organic">Food/Organic</option>
                  <option value="Electronic">Electronic</option>
                  <option value="Rubber">Rubber</option>
                  <option value="Chemical">Chemical</option>
                  <option value="Metal">Metal</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  name="description"
                  className="form-textarea"
                  value={newListing.description}
                  onChange={handleInputChange}
                  placeholder="Describe the waste material, condition, and any special handling requirements..."
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Quantity</label>
                  <input
                    type="number"
                    name="quantity"
                    className="form-input"
                    value={newListing.quantity}
                    onChange={handleInputChange}
                    placeholder="500"
                    min="0"
                    step="0.01"
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Unit</label>
                  <select name="unit" className="form-select" value={newListing.unit} onChange={handleInputChange}>
                    <option value="kg">Kilograms (kg)</option>
                    <option value="tons">Tons</option>
                    <option value="liters">Liters</option>
                    <option value="pieces">Pieces</option>
                  </select>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Price (₹)</label>
                  <input
                    type="number"
                    name="price"
                    className="form-input"
                    value={newListing.price}
                    onChange={handleInputChange}
                    placeholder="10000"
                    min="0"
                    step="0.01"
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Location</label>
                  <input
                    type="text"
                    name="location"
                    className="form-input"
                    value={newListing.location}
                    onChange={handleInputChange}
                    placeholder="e.g., Chennai, India"
                    required
                  />
                </div>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? 'Creating...' : '✅ Create Listing'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
