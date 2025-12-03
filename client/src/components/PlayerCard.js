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
          <span className="stat-value">£{player.price}m</span>
        </div>
        <div className="stat">
          <span className="stat-label">Points</span>
          <span className="stat-value">{player.total_points}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Form</span>
          <span className="stat-value">{player.form}</span>
        </div>
      </div>
      
      <div 
        className="predicted-points"
        style={{ color: getColorByPoints(player.predicted_points) }}
      >
        {player.predicted_points.toFixed(1)} xPts
      </div>
    </div>
  );
}

export default PlayerCard;

