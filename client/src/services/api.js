const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8080/api';

export const getHealth = async () => {
  try {
    const response = await fetch(`${API_BASE}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error calling health endpoint:', error);
    throw error;
  }
};

export const getPlayers = async () => {
  try {
    const response = await fetch(`${API_BASE}/players`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching players:', error);
    throw error;
  }
};

export const optimizeSquad = async (budget) => {
  try {
    const response = await fetch(`${API_BASE}/squads/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ budget }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error optimizing squad:', error);
    throw error;
  }
};

export const saveSquad = async (squad) => {
  try {
    const response = await fetch(`${API_BASE}/squads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(squad),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error saving squad:', error);
    throw error;
  }
};

export const getSavedSquads = async () => {
  try {
    const response = await fetch(`${API_BASE}/squads`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching saved squads:', error);
    throw error;
  }
};
