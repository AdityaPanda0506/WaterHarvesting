import React from 'react';

const About = () => {
  return (
    <div className="about-page">
      {/* Hero Section */}
      <section className="hero" style={{ padding: '120px 0 80px' }}>
        <div className="container">
          <div className="hero-content">
            <h1>About RainWater Harvest</h1>
            <p>
              Leading the way in sustainable water management and rainwater harvesting solutions across India
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="section" style={{ background: 'white' }}>
        <div className="container">
          <div className="about-content">
            <div className="about-text">
              <h2 className="section-title">Our Mission</h2>
              <p>
                At RainWater Harvest, we believe that every drop of rainwater is precious. 
                Our mission is to empower individuals, communities, and organizations 
                across India to implement effective rainwater harvesting and artificial 
                recharge systems that contribute to water security and environmental sustainability.
              </p>
              <p>
                We provide comprehensive resources, expert guidance, and innovative 
                technology solutions to make water conservation accessible and effective 
                for everyone, from urban households to rural communities.
              </p>
            </div>
            <div className="about-image">
              <a href="https://imgbb.com/" target="_blank" rel="noreferrer" style={{ display: 'block', width: '100%', height: '100%' }}>
                <img 
                  src="https://i.ibb.co/6RrXHQhD/World-Water-Day-image.jpg" 
                  alt="World Water Day - Rainwater and sustainability"
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Vision Section */}
      <section className="section" style={{ background: '#f8f9fa' }}>
        <div className="container">
          <div className="about-content">
            <div className="about-image">
              <a href="https://ibb.co/DPpb4cwD" target="_blank" rel="noreferrer" style={{ display: 'block', width: '100%', height: '100%' }}>
                <img
                  src="https://i.ibb.co/cKLvJf2c/Humanity-Artwork.jpg"
                  alt="Humanity and sustainability artwork"
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </a>
            </div>
            <div className="about-text">
              <h2 className="section-title">Our Vision</h2>
              <p>
                We envision a future where every building, community, and region in India 
                has implemented sustainable water management practices. A future where 
                rainwater is not wasted but collected, stored, and used efficiently to 
                meet water needs while replenishing groundwater resources.
              </p>
              <p>
                Through education, technology, and community engagement, we aim to create 
                a water-secure India where future generations have access to clean, 
                sustainable water resources.
              </p>
            </div>
          </div>
        </div>
      </section>


      {/* Team Section */}
      <section className="section" style={{ background: 'white' }}>
        <div className="container">
          <h2 className="section-title">Our Team</h2>
          <p className="section-subtitle">
            Dedicated professionals working towards water sustainability
          </p>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '2rem',
            marginTop: '3rem'
          }}>
            <div className="feature-card">
              <div style={{ 
                width: '100px', 
                height: '100px', 
                background: 'linear-gradient(135deg, #2c5aa0, #1e3f73)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1.5rem',
                fontSize: '2rem',
                color: 'white'
              }}>
                👨‍💼
              </div>
              <h3>Dr. Rajesh Kumar</h3>
              <p style={{ color: '#2c5aa0', fontWeight: '500', marginBottom: '1rem' }}>
                Chief Executive Officer
              </p>
              <p>
                Water resource management expert with over 20 years of experience 
                in sustainable water solutions and policy development.
              </p>
            </div>
            
            <div className="feature-card">
              <div style={{ 
                width: '100px', 
                height: '100px', 
                background: 'linear-gradient(135deg, #2c5aa0, #1e3f73)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1.5rem',
                fontSize: '2rem',
                color: 'white'
              }}>
                👩‍🔬
              </div>
              <h3>Dr. Priya Sharma</h3>
              <p style={{ color: '#2c5aa0', fontWeight: '500', marginBottom: '1rem' }}>
                Chief Technology Officer
              </p>
              <p>
                Environmental engineer specializing in water treatment technologies 
                and smart monitoring systems for water conservation.
              </p>
            </div>
            
            <div className="feature-card">
              <div style={{ 
                width: '100px', 
                height: '100px', 
                background: 'linear-gradient(135deg, #2c5aa0, #1e3f73)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1.5rem',
                fontSize: '2rem',
                color: 'white'
              }}>
                👨‍🏫
              </div>
              <h3>Prof. Amit Patel</h3>
              <p style={{ color: '#2c5aa0', fontWeight: '500', marginBottom: '1rem' }}>
                Director of Education
              </p>
              <p>
                Leading educator and researcher in water conservation with expertise 
                in community engagement and sustainable development practices.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="cta" style={{ 
        background: 'linear-gradient(135deg, #2c5aa0, #1e3f73)', 
        color: 'white', 
        padding: '80px 0', 
        textAlign: 'center' 
      }}>
        <div className="container">
          <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
            Ready to Make a Difference?
          </h2>
          <p style={{ fontSize: '1.2rem', marginBottom: '2rem', opacity: 0.9 }}>
            Join us in our mission to create a water-secure future for India.
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="/signup" className="btn" style={{ 
              background: 'white', 
              color: '#2c5aa0',
              padding: '15px 30px',
              fontSize: '1.1rem'
            }}>
              Get Involved
            </a>
            <a href="mailto:contact@rainwaterharvest.com" className="btn" style={{ 
              background: 'transparent', 
              color: 'white',
              border: '2px solid white',
              padding: '15px 30px',
              fontSize: '1.1rem'
            }}>
              Contact Us
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;
