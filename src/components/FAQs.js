// src/components/FAQs.js
import React from 'react';
import './FAQs.css'; // Ensure you have this CSS file for styling

function FAQs() {
  return (
    <div className="faqs">
      <h1>Frequently Asked Questions</h1>
      <div className="faq-item">
        <h2>Question 1?</h2>
        <p>Answer to question 1.</p>
      </div>
      <div className="faq-item">
        <h2>Question 2?</h2>
        <p>Answer to question 2.</p>
      </div>
      {/* Add more FAQs as needed */}
    </div>
  );
}

export default FAQs;
