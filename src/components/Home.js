// src/components/Home.js
import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="container">
      <style>{`
        .container {
          display: flex;
          justify-content: space-between;
        }

        .content {
          flex: 1;
          padding-right: 20px;
          text-align: left; /* Align text to the left */
        }

        .title {
          font-size: 36px;
          font-weight: bold;
          color: #6B8E23; /* Olive Drab */
        }

        .subtitle {
          font-size: 18px;
          color:brown;
        }

        .description {
          margin-top: 20px;
          color: brown; /* Set text color to cyan */
        }

        .signup {
          flex: 0 0 auto;
          display: flex;
          align-items: flex-start;
          justify-content: flex-start;
        }

        .signup-button {
          padding: 10px 20px;
          background-color: #28a745; /* Green */
          color: #fff;
          border: none;
          border-radius: 5px;
          text-decoration: none;
          font-size: 16px;
        }

        .signup-button:hover {
          background-color: #218838; /* Darker green */
        }
      `}</style>
      <div className="content">
        <h1 className="title" style={{color: "#6B8E23"}}>Welcome to Bug Finder</h1>
        <p className="subtitle">Find and fix bugs with ease!</p>
        <div className="feature">
          {/* Your existing content */}
        </div>
        <div className="description">
          <p>Our website is a bug finder tool designed specifically for Python programmers.</p>
          <p>Similar to ChatGPT, users can input their code, and our tool will identify bugs within the code.</p>
          <p>Not only does it identify bugs, but it also provides suggestions and solutions to resolve them.</p>
          <p>Whether you're a beginner or an experienced programmer, our bug finder
             tool is here to help streamline your coding process and improve the quality of your Python projects.</p>
        </div>
      </div>
      <div className="signup">
        <Link to="/signup" className="signup-button">Sign Up to Use Our Service</Link>
      </div>
    </div>
  );
}

export default Home;
