import React, { useState, useEffect } from 'react';
import { getUserSquad, getPlayers, getGameweeks } from '../services/api';
import { supabase } from '../supabaseClient';
import './SquadBuilder.css';

const VALID_FORMATIONS = ['3-4-3', '3-5-2', '4-4-2', '4-3-3', '4-5-1', '5-3-2', '5-4-1', '5-2-3'];

function SquadBuilder() {
  const [fplId, setFplId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [teamData, setTeamData] = useState(null);
  const [allPlayers, setAllPlayers] = useState([]);
  
  // Gameweek State
  const [gameweeks, setGameweeks] = useState([]);
  const [currentGameweekId, setCurrentGameweekId] = useState(null);
  const [initialGameweekId, setInitialGameweekId] = useState(null);
  
  // Squad State per Gameweek
  // Structure: { [gwId]: { squad: [], transfers: [], bank: 0, freeTransfers: 1 } }
  const [gameweekData, setGameweekData] = useState({});
  
  // Derived state for current view
  const currentSquad = gameweekData[currentGameweekId]?.squad || [];
  const transfers = gameweekData[currentGameweekId]?.transfers || [];
  
  const [selectedOut, setSelectedOut] = useState(null);
  const [selectedForSwap, setSelectedForSwap] = useState(null);
  const [playerFilter, setPlayerFilter] = useState({ position: 'ALL', search: '', maxPrice: 20 });
  const [swapError, setSwapError] = useState(null);
  const [modalPlayer, setModalPlayer] = useState(null);
  const [adjustedPrices, setAdjustedPrices] = useState({});
  const [priceInputValue, setPriceInputValue] = useState('');
  const [showPriceModal, setShowPriceModal] = useState(false);
  const [transferPrices, setTransferPrices] = useState({});
  const [savedPlan, setSavedPlan] = useState(null);
  const [showSavedPlan, setShowSavedPlan] = useState(false);
  const [planName, setPlanName] = useState('');

  useEffect(() => {
    const fetchGameweeks = async () => {
      try {
        const gws = await getGameweeks();
        setGameweeks(gws);
        
        // Find the next active gameweek
        // Logic: Find first GW where is_next is true, or calculate based on deadline
        const nextGw = gws.find(gw => gw.is_next) || gws[0];
        if (nextGw) {
          setInitialGameweekId(nextGw.id);
          setCurrentGameweekId(nextGw.id);
        }
      } catch (err) {
        console.error("Failed to fetch gameweeks", err);
      }
    };
    fetchGameweeks();
  }, []);

  useEffect(() => {
    if (fplId) {
      const fetchSavedPlan = async () => {
        try {
          const { data, error } = await supabase
            .from('squads')
            .select('*')
            .eq('fpl_id', fplId)
            .order('created_at', { ascending: false })
            .limit(1);

          if (error) throw error;

          if (data && data.length > 0) {
            setSavedPlan(data[0]);
            setShowSavedPlan(true);
          } else {
            setSavedPlan(null);
            setShowSavedPlan(false);
          }
        } catch (err) {
          console.error('Error fetching saved plan:', err);
          setSavedPlan(null);
          setShowSavedPlan(false);
        }
      };

      fetchSavedPlan();
    }
  }, [fplId]);

  const savePlan = async () => {
    if (!fplId) return;
    
    try {
      const planData = {
        fpl_id: fplId,
        plan_name: planName || `Plan ${new Date().toLocaleDateString()}`,
        squad_data: gameweekData[initialGameweekId]?.squad || [], // Save base squad
        transfers_data: transfers, // This might need to be updated to save full multi-gw plan
        full_plan: gameweekData // Save the entire multi-gameweek state
      };

      const { error } = await supabase
        .from('squads')
        .insert([planData]);

      if (error) throw error;

      alert('Plan saved successfully!');
      setSavedPlan(planData);
      setShowSavedPlan(true);
    } catch (err) {
      console.error('Error saving plan:', err);
      alert('Failed to save plan');
    }
  };

  const loadSavedPlan = () => {
    if (savedPlan) {
      if (savedPlan.full_plan) {
        setGameweekData(savedPlan.full_plan);
      } else {
        // Legacy plan support
        setGameweekData({
          [initialGameweekId]: {
            squad: savedPlan.squad_data,
            transfers: savedPlan.transfers_data || [],
            bank: teamData?.bank || 0,
            freeTransfers: 1
          }
        });
      }
      alert('Plan loaded!');
    }
  };

  const handleLoadTeam = async () => {
    if (!fplId.trim()) {
      setError('Please enter a valid FPL Team ID');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      // Reset state
      setGameweekData({});
      setSelectedOut(null);

      const [userData, playersData] = await Promise.all([
        getUserSquad(fplId),
        getPlayers()
      ]);

      if (userData.status === 'error') {
        throw new Error(userData.message);
      }

      setTeamData(userData);
      setAllPlayers(playersData);
      
      // Initialize the first gameweek with fetched data
      if (initialGameweekId) {
        setGameweekData({
          [initialGameweekId]: {
            squad: userData.squad || [],
            transfers: [],
            bank: userData.bank || 0,
            freeTransfers: 1 // Default to 1 FT for next GW
          }
        });
        setCurrentGameweekId(initialGameweekId);
      }
      
    } catch (err) {
      setError(err.message || 'Failed to load team. Check your Team ID.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Helper to update state for a specific GW
  const updateGameweekState = (gwId, newState) => {
    setGameweekData(prev => {
      const updated = { ...prev, [gwId]: { ...prev[gwId], ...newState } };
      
      // Propagate changes to future gameweeks
      // If we change GW X, GW X+1 should inherit the resulting squad of GW X
      // But we must preserve transfers made in GW X+1 if possible
      
      let currentGw = gwId;
      let nextGw = getNextGameweekId(currentGw);
      
      let runningState = updated;
      
      while (nextGw && runningState[nextGw]) {
        // The starting squad for nextGw is the ending squad of currentGw
        const prevGwState = runningState[currentGw];
        const prevSquadAfterTransfers = applyTransfersToSquad(prevGwState.squad, prevGwState.transfers);
        
        // We need to re-apply nextGw's transfers to this new base squad
        // Note: This might fail if a player was transferred out in prevGw that is also transferred out in nextGw
        // For simplicity, we'll just update the base squad and keep transfers if valid
        
        runningState = {
          ...runningState,
          [nextGw]: {
            ...runningState[nextGw],
            squad: prevSquadAfterTransfers
          }
        };
        
        currentGw = nextGw;
        nextGw = getNextGameweekId(currentGw);
      }
      
      return runningState;
    });
  };

  const getNextGameweekId = (currentId) => {
    const idx = gameweeks.findIndex(gw => gw.id === currentId);
    if (idx !== -1 && idx < gameweeks.length - 1) {
      return gameweeks[idx + 1].id;
    }
    return null;
  };
  
  const getPrevGameweekId = (currentId) => {
    const idx = gameweeks.findIndex(gw => gw.id === currentId);
    if (idx > 0) {
      return gameweeks[idx - 1].id;
    }
    return null;
  };

  const handleGameweekChange = (direction) => {
    if (!currentGameweekId) return;
    
    let newId;
    if (direction === 'next') {
      newId = getNextGameweekId(currentGameweekId);
      
      // If moving to a new future GW that doesn't exist in state yet
      if (newId && !gameweekData[newId]) {
        const currentGwState = gameweekData[currentGameweekId];
        const squadAfterTransfers = applyTransfersToSquad(currentGwState.squad, currentGwState.transfers);
        
        // Calculate bank after transfers
        // This is a simplified calculation
        const bankAfterTransfers = calculateBankAfterTransfers(currentGwState);

        setGameweekData(prev => ({
          ...prev,
          [newId]: {
            squad: squadAfterTransfers,
            transfers: [],
            bank: bankAfterTransfers,
            freeTransfers: 1 // Accumulate logic could go here (max 5)
          }
        }));
      }
    } else {
      newId = getPrevGameweekId(currentGameweekId);
      // Prevent going before initial loaded GW
      if (newId < initialGameweekId) return;
    }
    
    if (newId) {
      setCurrentGameweekId(newId);
      setSelectedOut(null);
      setSelectedForSwap(null);
    }
  };

  const applyTransfersToSquad = (baseSquad, transfersList) => {
    let newSquad = [...baseSquad];
    transfersList.forEach(t => {
      newSquad = newSquad.map(p => 
        p.id === t.out.id ? { ...t.in, squad_position: p.squad_position, is_starter: p.is_starter } : p
      );
    });
    return newSquad;
  };
  
  const calculateBankAfterTransfers = (gwState) => {
    let bank = gwState.bank;
    gwState.transfers.forEach(t => {
      bank += (t.out.price || 0);
      bank -= (t.in.price || 0);
    });
    return bank;
  };

  const getPositionColor = (position) => {
    const colors = {
      'GKP': '#ebff00',
      'DEF': '#00ff87',
      'MID': '#05f0ff',
      'FWD': '#e90052'
    };
    return colors[position] || '#888';
  };

  const getFdrColor = (fdr) => {
    const colors = {
      1: '#257d5a',
      2: '#00ff87',
      3: '#e7e7e7',
      4: '#ff1751',
      5: '#80072d'
    };
    return colors[fdr] || '#666';
  };

  const getFdrTextColor = (fdr) => {
    return [1, 4, 5].includes(fdr) ? '#fff' : '#1a1a2e';
  };

  const getFormation = (squad) => {
    const starters = squad.filter(p => p.squad_position <= 11);
    const def = starters.filter(p => p.position === 'DEF').length;
    const mid = starters.filter(p => p.position === 'MID').length;
    const fwd = starters.filter(p => p.position === 'FWD').length;
    return `${def}-${mid}-${fwd}`;
  };

  const isValidFormation = (formation) => {
    return VALID_FORMATIONS.includes(formation);
  };

  const wouldBeValidSwap = (player1, player2) => {
    const isPlayer1Starter = player1.squad_position <= 11;
    const isPlayer2Starter = player2.squad_position <= 11;
    
    if (isPlayer1Starter === isPlayer2Starter) {
      return true;
    }
    
    const testSquad = currentSquad.map(p => {
      if (p.id === player1.id) {
        return { ...p, squad_position: player2.squad_position };
      }
      if (p.id === player2.id) {
        return { ...p, squad_position: player1.squad_position };
      }
      return p;
    });
    
    const newFormation = getFormation(testSquad);
    return isValidFormation(newFormation);
  };

  const handleSwap = (player1, player2) => {
    const pos1 = player1.squad_position;
    const pos2 = player2.squad_position;
    
    const newSquad = currentSquad.map(p => {
      if (p.id === player1.id) {
        return { ...p, squad_position: pos2 };
      }
      if (p.id === player2.id) {
        return { ...p, squad_position: pos1 };
      }
      return p;
    });
    
    updateGameweekState(currentGameweekId, { squad: newSquad });
  };

  const handlePlayerClick = (player) => {
    setSwapError(null);
    
    if (selectedForSwap) {
      if (selectedForSwap.id === player.id) {
        setSelectedForSwap(null);
        return;
      }
      
      const isSwapStarterToBench = 
        (selectedForSwap.squad_position <= 11 && player.squad_position > 11) ||
        (selectedForSwap.squad_position > 11 && player.squad_position <= 11);
      
      const isBothBench = selectedForSwap.squad_position > 11 && player.squad_position > 11;
      
      const isEitherGK = selectedForSwap.position === 'GKP' || player.position === 'GKP';
      const areBothGK = selectedForSwap.position === 'GKP' && player.position === 'GKP';
      
      if (isBothBench) {
        if (isEitherGK) {
          setSwapError('Goalkeeper bench position is fixed');
          setSelectedForSwap(null);
          return;
        }
        handleSwap(selectedForSwap, player);
        setSelectedForSwap(null);
        return;
      }
      
      if (isSwapStarterToBench) {
        if (isEitherGK && !areBothGK) {
          setSwapError('Goalkeepers can only swap with other goalkeepers');
          setSelectedForSwap(null);
          return;
        }
        
        if (wouldBeValidSwap(selectedForSwap, player)) {
          handleSwap(selectedForSwap, player);
          setSelectedForSwap(null);
        } else {
          const starter = selectedForSwap.squad_position <= 11 ? player : selectedForSwap;
          const benchPlayer = selectedForSwap.squad_position > 11 ? player : selectedForSwap;
          setSwapError(`Cannot sub ${benchPlayer.web_name} for ${starter.web_name} - invalid formation`);
          setSelectedForSwap(null);
        }
        return;
      }
      
      setSelectedForSwap(player);
      return;
    }
    
    if (selectedOut?.id === player.id) {
      setSelectedOut(null);
    } else {
      setSelectedForSwap(player);
    }
  };

  const handleTransferClick = (player) => {
    setSwapError(null);
    setSelectedForSwap(null);
    if (selectedOut?.id === player.id) {
      setSelectedOut(null);
    } else {
      setSelectedOut(player);
    }
  };

  const handleTransferIn = (playerIn) => {
    if (!selectedOut) return;

    const newTransfer = {
      out: selectedOut,
      in: playerIn
    };

    const newTransfers = [...transfers, newTransfer];
    
    const newSquad = currentSquad.map(p => 
      p.id === selectedOut.id ? { ...playerIn, squad_position: selectedOut.squad_position, is_starter: selectedOut.is_starter } : p
    );

    updateGameweekState(currentGameweekId, {
      squad: newSquad,
      transfers: newTransfers
    });

    setSelectedOut(null);
  };

  const undoTransfer = (index) => {
    const transfer = transfers[index];
    const newSquad = currentSquad.map(p => 
      p.id === transfer.in.id ? { ...transfer.out, squad_position: p.squad_position, is_starter: p.is_starter } : p
    );
    const newTransfers = transfers.filter((_, i) => i !== index);
    
    updateGameweekState(currentGameweekId, {
      squad: newSquad,
      transfers: newTransfers
    });
  };

  const resetAllTransfers = () => {
    if (teamData && initialGameweekId) {
      // Reset to initial state
      setGameweekData({
        [initialGameweekId]: {
          squad: teamData.squad || [],
          transfers: [],
          bank: teamData.bank || 0,
          freeTransfers: 1
        }
      });
      setCurrentGameweekId(initialGameweekId);
      setSelectedOut(null);
      setSelectedForSwap(null);
      setSwapError(null);
    }
  };
  
  const resetCurrentGameweek = () => {
    if (!currentGameweekId || currentGameweekId === initialGameweekId) return;
    
    const prevId = getPrevGameweekId(currentGameweekId);
    const prevGwState = gameweekData[prevId];
    
    // Re-initialize current GW from previous GW's end state
    const squadAfterTransfers = applyTransfersToSquad(prevGwState.squad, prevGwState.transfers);
    const bankAfterTransfers = calculateBankAfterTransfers(prevGwState);
    
    updateGameweekState(currentGameweekId, {
      squad: squadAfterTransfers,
      transfers: [],
      bank: bankAfterTransfers
    });
  };

  const makeCaptain = (player) => {
    setCurrentSquad(currentSquad.map(p => ({
      ...p,
      is_captain: p.id === player.id,
      is_vice_captain: p.id === player.id ? false : p.is_vice_captain
    })));
    setModalPlayer(prev => prev ? { ...prev, is_captain: true, is_vice_captain: false } : null);
  };

  const makeViceCaptain = (player) => {
    setCurrentSquad(currentSquad.map(p => ({
      ...p,
      is_vice_captain: p.id === player.id,
      is_captain: p.id === player.id ? false : p.is_captain
    })));
    setModalPlayer(prev => prev ? { ...prev, is_vice_captain: true, is_captain: false } : null);
  };

  const openPlayerModal = (player) => {
    const updatedPlayer = currentSquad.find(p => p.id === player.id) || player;
    setModalPlayer(updatedPlayer);
    setPriceInputValue(getPlayerPrice(updatedPlayer).toFixed(1));
  };

  const closeModal = () => {
    setModalPlayer(null);
    setPriceInputValue('');
  };

  const isTransferredIn = (playerId) => {
    return transfers.some(t => t.in.id === playerId);
  };

  const adjustPlayerPrice = (playerId, newPrice) => {
    setAdjustedPrices(prev => ({
      ...prev,
      [playerId]: parseFloat(newPrice)
    }));
  };

  const getPlayerPrice = (player) => {
    if (adjustedPrices[player.id] !== undefined) {
      return adjustedPrices[player.id];
    }
    return player.price || 0;
  };

  const handleSubstituteFromModal = () => {
    if (modalPlayer) {
      setSelectedForSwap(modalPlayer);
      closeModal();
    }
  };

  const handleTransferFromModal = () => {
    if (modalPlayer) {
      handleTransferClick(modalPlayer);
      closeModal();
    }
  };

  const currentFormation = currentSquad.length > 0 ? getFormation(currentSquad) : null;

  const freeTransfers = teamData?.free_transfers || 0;
  const transfersMade = transfers.length;
  const extraTransfers = Math.max(0, transfersMade - freeTransfers);
  const transferCost = extraTransfers * 4;

  const currentSquadIds = new Set(currentSquad.map(p => p.id));
  const availablePlayers = allPlayers
    .filter(p => !currentSquadIds.has(p.id))
    .filter(p => {
      if (selectedOut && p.position !== selectedOut.position) return false;
      if (playerFilter.position !== 'ALL' && p.position !== playerFilter.position) return false;
      if (playerFilter.search && !p.web_name?.toLowerCase().includes(playerFilter.search.toLowerCase())) return false;
      if (p.price > playerFilter.maxPrice) return false;
      return true;
    })
    .sort((a, b) => (b.predicted_points || 0) - (a.predicted_points || 0));

  const getTransferOutPrice = (transferIndex) => {
    const key = `out_${transferIndex}`;
    if (transferPrices[key] !== undefined) return transferPrices[key];
    return transfers[transferIndex]?.out?.price || 0;
  };

  const getTransferInPrice = (transferIndex) => {
    const key = `in_${transferIndex}`;
    if (transferPrices[key] !== undefined) return transferPrices[key];
    return transfers[transferIndex]?.in?.price || 0;
  };

  const calculateBudget = () => {
    const startingBudget = (teamData?.bank || 0) + (teamData?.squad_value || 0);
    
    // Calculate current squad value
    const currentSquadValue = currentSquad.reduce((sum, p) => sum + (p.price || 0), 0);
    
    return Math.round((startingBudget - currentSquadValue) * 10) / 10;
  };

  const calculateBudgetSimple = () => {
    // Use the bank tracked in state
    return gameweekData[currentGameweekId]?.bank || 0;
  };

  const renderPitchView = () => {
    if (!currentSquad.length) return null;

    const starters = currentSquad.filter(p => p.squad_position <= 11);
    const bench = currentSquad.filter(p => p.squad_position > 11).sort((a, b) => a.squad_position - b.squad_position);

    const gk = starters.filter(p => p.position === 'GKP');
    const def = starters.filter(p => p.position === 'DEF');
    const mid = starters.filter(p => p.position === 'MID');
    const fwd = starters.filter(p => p.position === 'FWD');

    const renderPlayer = (player, benchIndex = null) => {
      const isSelectedForTransfer = selectedOut?.id === player.id;
      const isSelectedForSwap = selectedForSwap?.id === player.id;
      const playerIsTransferredIn = transfers.some(t => t.in.id === player.id);
      const displayPrice = getPlayerPrice(player);
      
      const fixtures = player.fixtures || [];
      // Filter fixtures to start from the currentGameweekId
      const futureFixtures = fixtures.filter(f => f.gw >= currentGameweekId);
      const nextFixture = futureFixtures[0];
      const upcomingFixtures = futureFixtures.slice(1, 6);

      return (
        <div 
          key={player.id} 
          className={`pitch-player ${isSelectedForTransfer ? 'selected' : ''} ${isSelectedForSwap ? 'selected-swap' : ''} ${playerIsTransferredIn ? 'transferred-in' : ''}`}
          onClick={() => openPlayerModal(player)}
        >
          {benchIndex !== null && <div className="bench-order">#{benchIndex}</div>}
          <div 
            className="player-shirt"
            style={{ backgroundColor: getPositionColor(player.position) }}
          >
            {player.team_name || '???'}
          </div>
          <div className="player-name-pitch">
            {player.is_captain && <span className="captain-badge">C</span>}
            {player.is_vice_captain && <span className="vc-badge">V</span>}
            {player.web_name || player.second_name}
          </div>
          
          {nextFixture && (
            <div 
              className="next-fixture"
              style={{ 
                backgroundColor: getFdrColor(nextFixture.fdr),
                color: getFdrTextColor(nextFixture.fdr)
              }}
            >
              {nextFixture.is_home ? nextFixture.opponent.toUpperCase() : nextFixture.opponent.toLowerCase()}
            </div>
          )}
          
          {upcomingFixtures.length > 0 && (
            <div className="fixture-bar">
              {upcomingFixtures.map((fix, idx) => (
                <div 
                  key={idx}
                  className="fixture-chip"
                  style={{ 
                    backgroundColor: getFdrColor(fix.fdr),
                    color: getFdrTextColor(fix.fdr)
                  }}
                  title={`GW${fix.gw}: ${fix.is_home ? 'vs' : '@'} ${fix.opponent}`}
                >
                  {fix.is_home ? fix.opponent.substring(0, 3).toUpperCase() : fix.opponent.substring(0, 3).toLowerCase()}
                </div>
              ))}
            </div>
          )}
        </div>
      );
    };

    const renderRow = (players) => (
      <div className="pitch-row">
        {players.map(p => renderPlayer(p))}
      </div>
    );

    return (
      <div className="pitch-container">
        <div className="pitch">
          <div className="pitch-grass">
            {renderRow(fwd)}
            {renderRow(mid)}
            {renderRow(def)}
            {renderRow(gk)}
          </div>
        </div>
        <div className="bench-area">
          <h4>Bench <span className="bench-hint">(click two to swap order)</span></h4>
          <div className="bench-row">
            {bench.map((p, idx) => renderPlayer(p, idx + 1))}
          </div>
        </div>
      </div>
    );
  };

  const renderPlayerList = () => {
    if (!selectedOut) return null;

    return (
      <div className="player-list-panel">
        <div className="panel-header">
          <h3>Select Replacement for {selectedOut.web_name}</h3>
          <button className="cancel-btn" onClick={() => setSelectedOut(null)}>✕</button>
        </div>

        <div className="player-filters">
          <input
            type="text"
            placeholder="Search players..."
            value={playerFilter.search}
            onChange={(e) => setPlayerFilter({ ...playerFilter, search: e.target.value })}
            className="search-input"
          />
          <select
            value={playerFilter.maxPrice}
            onChange={(e) => setPlayerFilter({ ...playerFilter, maxPrice: parseFloat(e.target.value) })}
            className="filter-select"
          >
            <option value={20}>Max £20m</option>
            <option value={15}>Max £15m</option>
            <option value={10}>Max £10m</option>
            <option value={8}>Max £8m</option>
            <option value={6}>Max £6m</option>
            <option value={5}>Max £5m</option>
          </select>
        </div>

        <div className="player-list">
          {availablePlayers.slice(0, 50).map(player => (
            <div 
              key={player.id} 
              className="player-list-item"
              onClick={() => handleTransferIn(player)}
            >
              <div className="player-info">
                <span className="pos-badge" style={{ backgroundColor: getPositionColor(player.position) }}>
                  {player.position}
                </span>
                <span className="player-name">{player.web_name}</span>
                <span className="player-team">{player.team_name}</span>
              </div>
              <div className="player-stats">
                <span className="price">£{player.price?.toFixed(1)}m</span>
                <span className="xpts">{player.predicted_points?.toFixed(1)} xPts</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="squad-builder">
      <header className="page-header">
        <h1>Transfer Planner</h1>
        <p>Load your FPL team and plan transfers</p>
      </header>

      <div className="team-id-section">
        <div className="team-id-input">
          <input
            type="text"
            placeholder="Enter your FPL Team ID"
            value={fplId}
            onChange={(e) => setFplId(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleLoadTeam()}
          />
          <button onClick={handleLoadTeam} disabled={loading}>
            {loading ? 'Loading...' : 'Load Team'}
          </button>
        </div>
        <p className="help-text">
          Find your Team ID in the FPL website URL: fantasy.premierleague.com/entry/<strong>XXXXXX</strong>/event/...
        </p>
      </div>

      {error && (
        <div className="error-message">❌ {error}</div>
      )}

      {teamData && (
        <>
          <div className="gameweek-navigation">
            <button 
              className="nav-btn prev" 
              onClick={() => handleGameweekChange('prev')}
              disabled={!currentGameweekId || currentGameweekId <= initialGameweekId}
            >
              ← GW{currentGameweekId ? currentGameweekId - 1 : ''}
            </button>
            
            <div className="current-gameweek">
              <h2>Gameweek {currentGameweekId}</h2>
              <span className="deadline-label">
                {gameweeks.find(g => g.id === currentGameweekId)?.deadline_time 
                  ? new Date(gameweeks.find(g => g.id === currentGameweekId).deadline_time).toLocaleString()
                  : ''}
              </span>
            </div>
            
            <button 
              className="nav-btn next" 
              onClick={() => handleGameweekChange('next')}
              disabled={!currentGameweekId || currentGameweekId >= 38}
            >
              GW{currentGameweekId ? currentGameweekId + 1 : ''} →
            </button>
          </div>

          <div className="team-info-bar">
            <div className="info-item">
              <span className="label">Manager</span>
              <span className="value">{teamData.manager_name}</span>
            </div>
            <div className="info-item">
              <span className="label">Team</span>
              <span className="value">{teamData.team_name}</span>
            </div>
            <div className="info-item">
              <span className="label">Bank</span>
              <span className="value">£{calculateBudgetSimple().toFixed(1)}m</span>
            </div>
            <div className="info-item">
              <span className="label">Free Transfers</span>
              <span className="value">{gameweekData[currentGameweekId]?.freeTransfers || 1}</span>
            </div>
          </div>

          <div className="transfers-bar">
            <div className="transfer-stats">
              <span>Transfers: <strong>{transfers.length}</strong></span>
              <span>Budget: <strong>£{calculateBudgetSimple().toFixed(1)}m</strong></span>
            </div>
            <div className="plan-actions">
              <button className="save-btn" onClick={savePlan}>Save Plan</button>
              {showSavedPlan && (
                <button className="load-btn" onClick={loadSavedPlan}>
                  Load Saved Plan
                </button>
              )}
              {transfers.length > 0 && (
                <button className="reset-btn" onClick={resetCurrentGameweek}>Reset GW{currentGameweekId}</button>
              )}
              <button className="reset-all-btn" onClick={resetAllTransfers}>Reset All</button>
            </div>
          </div>

          {transfers.length > 0 && (
            <div className="transfers-list">
              <div className="transfers-header">
                <h4>Planned Transfers</h4>
                <button className="adjust-prices-btn" onClick={() => setShowPriceModal(true)}>
                  Adjust Transfer Prices
                </button>
              </div>
              {transfers.map((t, idx) => (
                <div key={idx} className="transfer-item">
                  <span className="out">{t.out.web_name} (£{getTransferOutPrice(idx).toFixed(1)}m)</span>
                  <span className="arrow">→</span>
                  <span className="in">{t.in.web_name} (£{getTransferInPrice(idx).toFixed(1)}m)</span>
                  <button className="undo-btn" onClick={() => undoTransfer(idx)}>Undo</button>
                </div>
              ))}
            </div>
          )}

          <div className="main-content-area">
            <div className="pitch-section">
              <p className="instruction">
                {selectedOut 
                  ? `Select a replacement for ${selectedOut.web_name}` 
                  : selectedForSwap
                    ? `Select a player to swap with ${selectedForSwap.web_name}`
                    : 'Click on a player to view details'}
              </p>
              {swapError && <p className="swap-error">⚠️ {swapError}</p>}
              {renderPitchView()}
            </div>
            {renderPlayerList()}
          </div>
        </>
      )}

      {modalPlayer && (
        <div className="player-modal-overlay" onClick={closeModal}>
          <div className="player-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={closeModal}>✕</button>
            
            <div className="modal-header" style={{ background: `linear-gradient(135deg, ${getPositionColor(modalPlayer.position)} 0%, #1a2744 100%)` }}>
              <div className="modal-player-info">
                <h2>{modalPlayer.web_name || modalPlayer.second_name}</h2>
                <div className="modal-player-meta">
                  <span className="modal-position">{modalPlayer.position}</span>
                  <span className="modal-team">{modalPlayer.team_name}</span>
                </div>
              </div>
            </div>

            <div className="modal-stats">
              <div className="modal-stat">
                <span className="stat-label">Price Now</span>
                <span className="stat-value">{getPlayerPrice(modalPlayer).toFixed(1)}</span>
              </div>
              <div className="modal-stat">
                <span className="stat-label">Owned</span>
                <span className="stat-value">{modalPlayer.selected_by_percent || '0'}%</span>
              </div>
              <div className="modal-stat">
                <span className="stat-label">Form</span>
                <span className="stat-value">{modalPlayer.form || '0.0'}</span>
              </div>
              <div className="modal-stat">
                <span className="stat-label">xPts</span>
                <span className="stat-value xpts">{modalPlayer.predicted_points?.toFixed(1) || '0.0'}</span>
              </div>
            </div>

            {modalPlayer.fixtures && modalPlayer.fixtures.length > 0 && (
              <div className="modal-fixtures">
                <h4>Upcoming Fixtures</h4>
                <div className="modal-fixture-list">
                  {modalPlayer.fixtures.slice(0, 6).map((fix, idx) => (
                    <div 
                      key={idx}
                      className="modal-fixture-item"
                      style={{ 
                        backgroundColor: getFdrColor(fix.fdr),
                        color: getFdrTextColor(fix.fdr)
                      }}
                    >
                      <span className="gw">GW{fix.gw}</span>
                      <span className="opponent">
                        {fix.is_home ? fix.opponent.toUpperCase() : fix.opponent.toLowerCase()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="modal-actions">
              {modalPlayer.squad_position <= 11 && (
                <div className="captain-actions">
                  <button 
                    className={`modal-btn captain-btn ${modalPlayer.is_captain ? 'active' : ''}`}
                    onClick={() => makeCaptain(modalPlayer)}
                    disabled={modalPlayer.is_captain}
                  >
                    <span className="btn-icon">C</span>
                    <span>{modalPlayer.is_captain ? 'Captain' : 'Make Captain'}</span>
                  </button>
                  <button 
                    className={`modal-btn vc-btn ${modalPlayer.is_vice_captain ? 'active' : ''}`}
                    onClick={() => makeViceCaptain(modalPlayer)}
                    disabled={modalPlayer.is_vice_captain}
                  >
                    <span className="btn-icon">VC</span>
                    <span>{modalPlayer.is_vice_captain ? 'Vice Captain' : 'Make Vice Captain'}</span>
                  </button>
                </div>
              )}

              <div className="squad-actions">
                <button className="modal-btn sub-btn" onClick={handleSubstituteFromModal}>
                  <span className="btn-icon">⇄</span>
                  <span>Substitute</span>
                </button>
                <button className="modal-btn transfer-btn-modal" onClick={handleTransferFromModal}>
                  <span className="btn-icon">↕</span>
                  <span>Transfer</span>
                </button>
              </div>

            </div>
          </div>
        </div>
      )}

      {showPriceModal && (
        <div className="player-modal-overlay" onClick={() => setShowPriceModal(false)}>
          <div className="player-modal price-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowPriceModal(false)}>✕</button>
            
            <div className="modal-header price-modal-header">
              <h2>Adjust Transfer</h2>
            </div>

            <div className="price-modal-content">
              <p className="price-modal-desc">
                Because we only use your publicly available team data sometimes you may need to adjust the transfer prices of players manually.
              </p>

              {transfers.map((t, idx) => (
                <div key={idx} className="transfer-price-row">
                  <div className="price-row-player">
                    <span className="price-direction out-direction">Set {t.out.web_name}'s Price</span>
                    <span className="direction-arrow out-arrow">←</span>
                  </div>
                  <div className="price-selects">
                    <select
                      value={Math.floor(getTransferOutPrice(idx))}
                      onChange={(e) => {
                        const decimal = getTransferOutPrice(idx) % 1;
                        setTransferPrices(prev => ({
                          ...prev,
                          [`out_${idx}`]: parseInt(e.target.value) + decimal
                        }));
                      }}
                    >
                      {[...Array(16)].map((_, i) => (
                        <option key={i} value={i + 4}>{i + 4}</option>
                      ))}
                    </select>
                    <select
                      value={Math.round((getTransferOutPrice(idx) % 1) * 10)}
                      onChange={(e) => {
                        const whole = Math.floor(getTransferOutPrice(idx));
                        setTransferPrices(prev => ({
                          ...prev,
                          [`out_${idx}`]: whole + parseInt(e.target.value) / 10
                        }));
                      }}
                    >
                      {[...Array(10)].map((_, i) => (
                        <option key={i} value={i}>{i}</option>
                      ))}
                    </select>
                  </div>

                  <div className="price-row-player">
                    <span className="price-direction in-direction">Set {t.in.web_name}'s Price</span>
                    <span className="direction-arrow in-arrow">→</span>
                  </div>
                  <div className="price-selects">
                    <select
                      value={Math.floor(getTransferInPrice(idx))}
                      onChange={(e) => {
                        const decimal = getTransferInPrice(idx) % 1;
                        setTransferPrices(prev => ({
                          ...prev,
                          [`in_${idx}`]: parseInt(e.target.value) + decimal
                        }));
                      }}
                    >
                      {[...Array(16)].map((_, i) => (
                        <option key={i} value={i + 4}>{i + 4}</option>
                      ))}
                    </select>
                    <select
                      value={Math.round((getTransferInPrice(idx) % 1) * 10)}
                      onChange={(e) => {
                        const whole = Math.floor(getTransferInPrice(idx));
                        setTransferPrices(prev => ({
                          ...prev,
                          [`in_${idx}`]: whole + parseInt(e.target.value) / 10
                        }));
                      }}
                    >
                      {[...Array(10)].map((_, i) => (
                        <option key={i} value={i}>{i}</option>
                      ))}
                    </select>
                  </div>
                </div>
              ))}

              <button className="confirm-prices-btn" onClick={() => setShowPriceModal(false)}>
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default SquadBuilder;
