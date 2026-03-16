/**
 * ImpactScore Component — Displays environmental impact metrics for a listing.
 */
export default function ImpactScore({ impact }) {
  if (!impact) return null;

  return (
    <div className="impact-grid">
      <div className="impact-item">
        <div className="impact-icon">🌿</div>
        <div className="impact-value">{impact.co2_saved_kg?.toLocaleString() || 0}</div>
        <div className="impact-label">kg CO₂ Saved</div>
      </div>
      <div className="impact-item">
        <div className="impact-icon">⚡</div>
        <div className="impact-value">{impact.energy_saved_kwh?.toLocaleString() || 0}</div>
        <div className="impact-label">kWh Energy Saved</div>
      </div>
      <div className="impact-item">
        <div className="impact-icon">🗑️</div>
        <div className="impact-value">{impact.landfill_avoided_tons?.toLocaleString() || 0}</div>
        <div className="impact-label">Tons Landfill Avoided</div>
      </div>
    </div>
  );
}
