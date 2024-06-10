// src/components/Login.js
import React, { useState } from 'react';
import './Login.css';

function Login() {
  const [isSignup, setIsSignup] = useState(false);

  const toggleForm = () => {
    setIsSignup(!isSignup);
  };

  return (
    <div className="login-container">
      <form className="login-form">
        <h2>{isSignup ? 'Sign Up' : 'Login'}</h2>
        {isSignup && <input type="text" placeholder="Username" required />}
        <input type="email" placeholder="Email" required />
        <input type="password" placeholder="Password" required />
        <button type="submit">{isSignup ? 'Sign Up' : 'Login'}</button>
        <p onClick={toggleForm}>
          {isSignup ? 'Already have an account? Login' : "Don't have an account? Sign Up"}
        </p>
      </form>
    </div>
  );
}

export default Login;
