import React from 'react';

function Services() {
  return (
    <section className="services">
      <div className="service">
        <img src="service-icon-1.png" alt="Service 1" />
        <h2>Service 1</h2>
        <p>Our expert team provides...</p>
      </div>
      {/* Repeat similar service blocks for other services */}
    </section>
  );
}

export default Services;
