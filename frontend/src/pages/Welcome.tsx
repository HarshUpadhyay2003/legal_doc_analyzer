import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ICONS = [
  { className: 'icon-1', emoji: '⚖️' },
  { className: 'icon-2', emoji: '📄' },
  { className: 'icon-3', emoji: '🔍' },
  { className: 'icon-4', emoji: '💬' },
  { className: 'icon-5', emoji: '⛓' },
  { className: 'icon-6', emoji: '📋' },
  { className: 'icon-7', emoji: '📜' },
  { className: 'icon-8', emoji: '🗽' },
  { className: 'icon-9', emoji: '🤝' },
  { className: 'icon-10', emoji: '🧑‍⚖️' },
];

const PARTICLE_COUNT = 50;

export default function Welcome() {
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');
  const [particles, setParticles] = useState([]);
  const containerRef = useRef(null);
  const navigate = useNavigate();
  const iconsRef = useRef([]);
  const [showDetails, setShowDetails] = useState(false);
  const detailsRef = useRef(null);

  // Theme toggle
  useEffect(() => {
    document.body.classList.remove('light-mode', 'dark-mode');
    document.body.classList.add(theme === 'dark' ? 'dark-mode' : 'light-mode');
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Particles
  useEffect(() => {
    const arr = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      arr.push({
        left: Math.random() * 100,
        delay: Math.random() * 15,
        duration: Math.random() * 10 + 10,
        key: i,
      });
    }
    setParticles(arr);
  }, []);

  // Parallax effect for icons
  useEffect(() => {
    const handleMouseMove = (e) => {
      const x = e.clientX / window.innerWidth;
      const y = e.clientY / window.innerHeight;
      iconsRef.current.forEach((icon, index) => {
        if (icon) {
          const speed = (index + 1) * 0.5;
          const xPos = (x - 0.5) * speed * 50;
          const yPos = (y - 0.5) * speed * 50;
          icon.style.transform = `translate(${xPos}px, ${yPos}px)`;
        }
      });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Ripple effect
  const handleButtonClick = (e, path) => {
    e.preventDefault();
    const btn = e.currentTarget;
    const ripple = document.createElement('span');
    const rect = btn.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.style.position = 'absolute';
    ripple.style.borderRadius = '50%';
    ripple.style.background = 'rgba(255, 255, 255, 0.6)';
    ripple.style.transform = 'scale(0)';
    ripple.style.animation = 'ripple 0.6s linear';
    ripple.style.pointerEvents = 'none';
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
    setTimeout(() => navigate(path), 300);
  };

  // Scroll indicator
  const handleScrollIndicator = () => {
    setShowDetails(true);
    setTimeout(() => {
      if (detailsRef.current) {
        detailsRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }, 50);
  };

  // Show details on scroll
  useEffect(() => {
    const onScroll = () => {
      if (window.scrollY > 100) {
        setShowDetails(true);
      } else {
        setShowDetails(false);
      }
    };
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, [showDetails]);

  return (
    <>
      <style>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; overflow-x: hidden; transition: all 0.3s ease; }
        .light-mode { background: linear-gradient(135deg, #F9FAFB 0%, #E4E4E7 100%); color: #1F2937; }
        .dark-mode { background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); color: #F1F5F9; }
        .container { min-height: 100vh; display: flex; flex-direction: column; justify-content: flex-start; align-items: center; position: relative; perspective: 1000px; }
        .theme-toggle { position: absolute; top: 20px; right: 20px; background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); border-radius: 50px; padding: 8px 16px; cursor: pointer; transition: all 0.3s ease; z-index: 100; }
        .theme-toggle:hover { transform: scale(1.05); background: rgba(255,255,255,0.2); }
        .floating-icon { position: absolute; font-size: 2rem; opacity: 0.6; animation: float 6s ease-in-out infinite; transform-style: preserve-3d; }
        .icon-1 { top: 15%; left: 10%; animation-delay: 0s; color: #4F46E5; }
        .icon-2 { top: 25%; right: 15%; animation-delay: -2s; color: #7C3AED; }
        .icon-3 { bottom: 20%; left: 20%; animation-delay: -4s; color: #2563EB; }
        .icon-4 { bottom: 30%; right: 25%; animation-delay: -1s; color: #059669; }
        .icon-5 { top: 50%; left: 5%; animation-delay: -3s; color: #DC2626; }
        .icon-6 { top: 60%; right: 8%; animation-delay: -5s; color: #D97706; }
        @keyframes float { 0%,100%{transform:translateY(0px) rotateY(0deg) rotateX(0deg);} 25%{transform:translateY(-20px) rotateY(90deg) rotateX(10deg);} 50%{transform:translateY(-10px) rotateY(180deg) rotateX(-5deg);} 75%{transform:translateY(-25px) rotateY(270deg) rotateX(15deg);} }
        .main-content { text-align: center; z-index: 10; animation: fadeInUp 1.5s ease-out; }
        .logo { font-size: 3.5rem; font-weight: 800; margin-bottom: 1rem; background: linear-gradient(135deg, #4F46E5, #7C3AED, #2563EB); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; animation: shimmer 3s ease-in-out infinite; }
        @keyframes shimmer { 0%,100%{filter:hue-rotate(0deg);} 50%{filter:hue-rotate(20deg);} }
        .tagline { font-size: 2.2rem; font-weight: 600; margin-bottom: 2rem; max-width: 800px; line-height: 1.3; animation: fadeIn 2s ease-out 0.5s both; }
        .subtitle { font-size: 1.2rem; opacity: 0.8; margin-bottom: 3rem; animation: fadeIn 2s ease-out 1s both; }
        .button-container { display: flex; gap: 2rem; justify-content: center; margin-bottom: 4rem; animation: fadeInUp 2s ease-out 1.5s both; }
        .btn { padding: 1rem 2.5rem; font-size: 1.1rem; font-weight: 600; border: none; border-radius: 50px; cursor: pointer; transition: all 0.3s ease; text-decoration: none; display: inline-block; position: relative; overflow: hidden; background: none; }
        .btn-primary { background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; box-shadow: 0 10px 30px rgba(79,70,229,0.3); }
        .btn-secondary { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 2px solid rgba(79,70,229,0.3); color: inherit; }
        .dark-mode .btn-secondary { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.3); }
        .btn:hover { transform: translateY(-3px) scale(1.05); box-shadow: 0 15px 40px rgba(79,70,229,0.4); }
        .btn::before { content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent); transition: left 0.5s; }
        .btn:hover::before { left: 100%; }
        .scroll-indicator.hide {
          opacity: 0;
          pointer-events: none;
          transform: translateY(20px) scale(0.98);
          transition: opacity 0.5s cubic-bezier(0.4,0,0.2,1), transform 0.3s;
        }
        .scroll-arrow {
          width: 56px; height: 56px; border-right: 6px solid currentColor; border-bottom: 6px solid currentColor; transform: rotate(45deg); margin: 0 auto 18px; color: #4F46E5;
        }
        .scroll-indicator small {
          font-size: 1.45rem;
          font-weight: 700;
          letter-spacing: 0.02em;
          color: #4F46E5;
          text-shadow: none;
        }
        .dark-mode .scroll-indicator, .dark-mode .scroll-arrow, .dark-mode .scroll-indicator small {
          color: #fff;
        }
        @keyframes bounce { 0%,20%,50%,80%,100%{transform:translateX(-50%) translateY(0);} 40%{transform:translateX(-50%) translateY(-10px);} 60%{transform:translateX(-50%) translateY(-5px);} }
        @keyframes fadeInUp { from{opacity:0;transform:translateY(50px);} to{opacity:1;transform:translateY(0);} }
        @keyframes fadeIn { from{opacity:0;} to{opacity:1;} }
        .particles { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: 1; }
        .particle { position: absolute; width: 4px; height: 4px; background: rgba(79,70,229,0.3); border-radius: 50%; animation: particle-float 15s linear infinite; }
        @keyframes particle-float { 0%{transform:translateY(100vh) translateX(0);opacity:0;} 10%{opacity:1;} 90%{opacity:1;} 100%{transform:translateY(-100px) translateX(100px);opacity:0;} }
        @media (max-width: 768px) { .logo{font-size:2.5rem;} .tagline{font-size:1.6rem;padding:0 1rem;} .button-container{flex-direction:column;align-items:center;gap:1rem;} .btn{width:200px;} .floating-icon{font-size:1.5rem;} }
        .glass { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); border-radius: 20px; padding: 3rem; margin: 2rem; box-shadow: 0 25px 50px rgba(0,0,0,0.1); }
        .dark-mode .glass { background: rgba(59,130,246,0.1); border-color: rgba(59,130,246,0.2); }
        @keyframes ripple { to { transform: scale(4); opacity: 0; } }
        .welcome-details-fade {
          opacity: 0;
          transition: opacity 0.6s cubic-bezier(0.4,0,0.2,1);
          pointer-events: none;
        }
        .welcome-details-fade.show {
          opacity: 1;
          pointer-events: auto;
        }
      `}</style>
      <div className="container" ref={containerRef} style={{ minHeight: '120vh' }}>
        {/* Theme Toggle */}
        <div className="theme-toggle" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
          🌓 Theme
        </div>
        {/* Floating Particles */}
        <div className="particles">
          {particles.map((p) => (
            <div
              key={p.key}
              className="particle"
              style={{ left: `${p.left}%`, animationDelay: `${p.delay}s`, animationDuration: `${p.duration}s` }}
            />
          ))}
        </div>
        {/* Floating 3D Legal Icons */}
        {ICONS.map((icon, i) => (
          <div
            key={icon.className}
            className={`floating-icon ${icon.className}`}
            ref={el => iconsRef.current[i] = el}
          >
            {icon.emoji}
          </div>
        ))}
        {/* Main Content */}
        <div className="main-content glass" style={{ marginTop: '4.5rem' }}>
          <h1 className="logo">JuriSense</h1>
          <h2 className="tagline">Turn Legal Complexity Into Clarity – Instantly.</h2>
          <p className="subtitle">AI-Powered Legal Intelligence at Your Fingertips</p>
          <div className="button-container">
            <button className="btn btn-primary" onClick={e => handleButtonClick(e, '/login')}>Login</button>
            <button className="btn btn-secondary" onClick={e => handleButtonClick(e, '/register')}>Register</button>
          </div>
        </div>
        {/* Scroll Indicator (now below the card) */}
        <div className={`scroll-indicator${showDetails ? ' hide' : ''}`} onClick={handleScrollIndicator}>
          <div className="scroll-arrow"></div>
          <small>Scroll to explore</small>
        </div>
        {/* Warm Welcome Section (below the fold) */}
        <div
          ref={detailsRef}
          className={`glass welcome-details-fade${showDetails ? ' show' : ''}`}
          style={{ maxWidth: 700, margin: '8rem auto 2rem', textAlign: 'center', display: showDetails || window.scrollY > 100 ? 'block' : 'none' }}
        >
          <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '1rem' }}>Welcome to JuriSense!</h2>
          <p style={{ fontSize: '1.15rem', marginBottom: '1.5rem' }}>
            <strong>We're delighted to have you here.</strong>
          </p>
          <div style={{ fontSize: '1.05rem', lineHeight: 1.7, marginBottom: '1.5rem' }}>
            JuriSense is your AI-powered legal assistant, designed to make legal document analysis, question answering, and contract management effortless.<br/><br/>
            <ul style={{ textAlign: 'left', display: 'inline-block', margin: '0 auto 1.5rem', paddingLeft: 0 }}>
              <li>• Instantly upload and review legal documents</li>
              <li>• Get clear, AI-generated answers to your legal questions</li>
              <li>• Search and summarize complex contracts in seconds</li>
              <li>• Enjoy a secure, user-friendly experience</li>
            </ul>
            <br/>
            Whether you're a legal professional, business owner, or just someone who wants clarity, JuriSense is here to help you turn legal complexity into clarity—instantly.
          </div>
        </div>
      </div>
    </>
  );
} 