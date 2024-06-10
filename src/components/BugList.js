// src/components/BugList.js
import React from 'react';
import './BugList.css'; // Import the CSS file

function BugList() {
  return (
    <section className="bugs">
      <div className="bug">
        <img src="/bug-icon-1.png" alt="Bug 1" />
        <h2>Bug 1</h2>
        <p>Description of bug 1...</p>
      </div>
      {/* Repeat similar bug blocks for other bugs */}
    </section>
  );
}

export default BugList;
