import React, { useState, useEffect } from 'react';
import { getPlayers } from '../services/api';
import PlayerCard from '../components/PlayerCard';
import './PlayersPage.css';

function PlayersPage() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    position: 'ALL',
    team: 'ALL',
    search: '',
    sortBy: 'total_points'
  });

  useEffect(() => {
    loadPlayers();
  }, []);

  const loadPlayers = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getPlayers();
      setPlayers(data);
    } catch (err) {
      setError('Failed to load players. Is the backend running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getUniqueTeams = () => {
    const teams = [...new Set(players.map(p => p.team_name))];
    return teams.sort();
  };

  const filteredPlayers = players
    .filter(p => {
      if (filters.position !== 'ALL' && p.position !== filters.position) return false;
      if (filters.team !== 'ALL' && p.team_name !== filters.team) return false;
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        const fullName = (p.full_name || '').toLowerCase();
        const webName = (p.web_name || '').toLowerCase();
        if (!fullName.includes(searchLower) && !webName.includes(searchLower)) {
          return false;
        }
      }
      return true;
    })
    .sort((a, b) => {
      switch (filters.sortBy) {
        case 'price':
          return b.price - a.price;
        case 'form':
          return parseFloat(b.form) - parseFloat(a.form);
        case 'predicted_points':
          return b.predicted_points - a.predicted_points;
        case 'total_points':
        default:
          return b.total_points - a.total_points;
      }
    });

  if (loading) {
    return (
      <div className="players-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading players...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="players-page">
        <div className="error-container">
          <p>❌ {error}</p>
          <button onClick={loadPlayers}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="players-page">
      <header className="page-header">
        <h1>Players</h1>
        <p className="player-count">{filteredPlayers.length} players</p>
      </header>

      <div className="filters-bar">
        <input
          type="text"
          placeholder="Search players..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          className="search-input"
        />

        <select
          value={filters.position}
          onChange={(e) => setFilters({ ...filters, position: e.target.value })}
          className="filter-select"
        >
          <option value="ALL">All Positions</option>
          <option value="GKP">Goalkeepers</option>
          <option value="DEF">Defenders</option>
          <option value="MID">Midfielders</option>
          <option value="FWD">Forwards</option>
        </select>

        <select
          value={filters.team}
          onChange={(e) => setFilters({ ...filters, team: e.target.value })}
          className="filter-select"
        >
          <option value="ALL">All Teams</option>
          {getUniqueTeams().map(team => (
            <option key={team} value={team}>{team}</option>
          ))}
        </select>

        <select
          value={filters.sortBy}
          onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
          className="filter-select"
        >
          <option value="total_points">Sort by Points</option>
          <option value="price">Sort by Price</option>
          <option value="form">Sort by Form</option>
          <option value="predicted_points">Sort by xPts</option>
        </select>
      </div>

      <div className="players-list">
        {filteredPlayers.slice(0, 100).map(player => (
          <PlayerCard 
            key={player.id} 
            player={player}
          />
        ))}
        {filteredPlayers.length > 100 && (
          <p className="more-players">
            Showing first 100 of {filteredPlayers.length} players
          </p>
        )}
      </div>
    </div>
  );
}

export default PlayersPage;

