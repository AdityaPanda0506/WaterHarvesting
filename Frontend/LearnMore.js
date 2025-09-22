import React from 'react';
import FeatureCarousel from '../components/FeatureCarousel';

const LearnMore = () => {
  return (
    <div className="learn-more-page">
      {/* Hero Section */}
      <section className="hero" style={{ padding: '120px 0 60px' }}>
        <div className="container">
          <div className="hero-content">
            <h1>What is Rainwater Harvesting?</h1>
            <p style={{ maxWidth: '900px', marginTop: '1rem' }}>
              Rainwater harvesting is the simple process of collecting and storing rainwater that
              falls on your rooftop, instead of letting it go to waste through drains. The collected
              water can be used for daily needs like gardening, washing, flushing, and even for
              drinking (after proper filtration).
            </p>
          </div>
        </div>
      </section>

      {/* Features Carousel Section */}
      <section className="section" style={{ background: 'white' }}>
        <div className="container">
          <h2 className="section-title" style={{ textAlign: 'center' }}>Explore Our Key Features</h2>
          <p className="section-subtitle" style={{ textAlign: 'center', maxWidth: '900px', margin: '0 auto 2rem' }}>
            Discover insights, savings, and tools designed to make rainwater harvesting simple and effective.
          </p>
          <FeatureCarousel
            items={[
              {
                icon: '🌧',
                title: 'Rainwater Analysis',
                text:
                  "Every rooftop is a potential water reservoir. Discover how much rainwater you can harvest in a year using rooftop dimensions and local rainfall data. We also provide soil analysis to estimate recharge efficiency so you make the most of every drop.",
              },
              {
                icon: '💰',
                title: 'Cost Analysis and Financial Returns',
                text:
                  "See setup costs, payback period, and long-term savings. We calculate return on investment and project financial gains over the years—saving water truly means saving money.",
              },
              {
                icon: '🏠',
                title: '3D Visualization',
                text:
                  "View a detailed 3D model of your rainwater harvesting setup—pipes, filters, and storage tanks—so you can visualize the system before installation.",
              },
              {
                icon: '🌍',
                title: 'Community and Services',
                text:
                  "Connect with neighbors, find trusted local installers, and receive reminders for filter changes and routine maintenance to keep your system at peak performance.",
              },
            ]}
          />
        </div>
      </section>

      {/* Explanation Section */}
      <section className="section" style={{ background: '#f8f9fa' }}>
        <div className="container">
          <div className="about-content" style={{ alignItems: 'stretch' }}>
            <div className="about-text">
              <h2 className="section-title">How it works</h2>
              <ol style={{ paddingLeft: '1.25rem', lineHeight: 1.8 }}>
                <li>Rain falls on your roof (the catchment area).</li>
                <li>Pipes and gutters carry it down.</li>
                <li>The first flush system removes dirty water (dust, leaves).</li>
                <li>The clean water then passes through filters.</li>
                <li>Finally, it is stored in a tank or directed to the ground to recharge groundwater.</li>
              </ol>
              <div style={{ marginTop: '1rem', fontSize: '1.1rem' }}>💡 The bigger your roof and the more it rains in your area, the more water you can save.</div>
            </div>
            <div className="about-image" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div
                style={{
                  position: 'relative',
                  width: '100%',
                  maxWidth: '520px',
                  perspective: '1000px'
                }}
              >
                <div
                  style={{
                    transformStyle: 'preserve-3d',
                    transition: 'transform 300ms ease, box-shadow 300ms ease',
                    borderRadius: '16px',
                    overflow: 'hidden',
                    boxShadow: '0 12px 30px rgba(0,0,0,0.15)'
                  }}
                  className="hover-tilt"
                >
                  <a href="https://imgbb.com/" target="_blank" rel="noreferrer">
                    <img
                      src="https://i.ibb.co/bMx4f18V/Screenshot-2025-09-22-205520.png"
                      alt="Rainwater harvesting system diagram"
                      style={{ display: 'block', width: '100%', height: 'auto' }}
                    />
                  </a>
                </div>
                <div
                  style={{
                    content: '""',
                    position: 'absolute',
                    inset: '-8px',
                    borderRadius: '20px',
                    background: 'linear-gradient(135deg, rgba(44,90,160,0.35), rgba(30,63,115,0.35))',
                    zIndex: -1,
                    filter: 'blur(16px)'
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LearnMore;



