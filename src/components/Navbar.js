// src/components/Navbar.js
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';
import bugsLogo from '../assets/bugs.png'; // Updated path
import Login from './Login';

function Navbar() {
  const [showLogin, setShowLogin] = useState(false);

  const toggleLogin = () => {
    setShowLogin(!showLogin);
  };

  return (
    <>
      <nav className="navbar">
        <img src={bugsLogo} alt="Bugs Logo" className="navbar-logo" />
        <div className="navbar-links">
          <Link to="/">Home</Link>
          <Link to="/bugs">Bugs</Link>
          <Link to="/about">About</Link>
          <Link to="/contact">Contact</Link>
          <Link to="/customer-stories">Customer Stories</Link>
          <button className="login-button" onClick={toggleLogin}>Login</button>
        </div>
      </nav>
      {showLogin && <Login />}
    </>
  );
}

export default Navbar;
