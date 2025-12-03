import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import PlayersPage from './pages/PlayersPage';
import './App.css';

function HomePage() {
  return (
    <div className="home-page">
      <h1>FPL ML Team Builder</h1>
      <p className="tagline">Build your optimal Fantasy Premier League team using machine learning predictions</p>
      
      <div className="feature-cards">
        <Link to="/players" className="feature-card">
          <h2>📊 Browse Players</h2>
          <p>View all 700+ Premier League players with stats, prices, and predicted points</p>
        </Link>
        
        <div className="feature-card disabled">
          <h2>⚽ Squad Builder</h2>
          <p>Build and optimize your dream team (coming soon)</p>
        </div>
        
        <div className="feature-card disabled">
          <h2>🤖 ML Predictions</h2>
          <p>AI-powered points predictions (coming soon)</p>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <Link to="/" className="nav-brand">FPL ML Builder</Link>
          <div className="nav-links">
            <Link to="/">Home</Link>
            <Link to="/players">Players</Link>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/players" element={<PlayersPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
