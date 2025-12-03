import React from 'react';
import './PlayerCard.css';

function PlayerCard({ player, onSelect, isSelected }) {
  const getColorByPoints = (points) => {
    if (points >= 6) return '#00ff87';
    if (points >= 4) return '#ffc107';
    return '#ff5252';
  };

  const positionColors = {
    'GKP': '#ebff00',
    'DEF': '#00ff87',
    'MID': '#05f0ff',
    'FWD': '#e90052'
  };

  const predictedPoints = player.predicted_points ?? 0;
  const hasPrediction = player.predicted_points != null;

  return (
    <div 
      className={`player-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect && onSelect(player)}
    >
      <div 
        className="position-badge"
        style={{ backgroundColor: positionColors[player.position] || '#888' }}
      >
        {player.position}
      </div>
      
      <div className="player-info">
        <div className="player-name">{player.web_name || player.second_name}</div>
        <div className="player-team">{player.team_name}</div>
      </div>
      
      <div className="player-stats">
        <div className="stat">
          <span className="stat-label">Price</span>
          <span className="stat-value">£{player.price?.toFixed(1) || '?'}m</span>
        </div>
        <div className="stat">
          <span className="stat-label">Points</span>
          <span className="stat-value">{player.total_points || 0}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Form</span>
          <span className="stat-value">{player.form || '-'}</span>
        </div>
      </div>
      
      <div 
        className={`predicted-points ${hasPrediction ? '' : 'no-prediction'}`}
        style={{ color: hasPrediction ? getColorByPoints(predictedPoints) : '#666' }}
        title={hasPrediction ? 'ML-predicted points for next gameweek' : 'No prediction available'}
      >
        {predictedPoints.toFixed(1)} xPts
      </div>
    </div>
  );
}

export default PlayerCard;
