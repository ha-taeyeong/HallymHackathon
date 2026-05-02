// src/components/FixedNavBar.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom'; // Link 추가
import { HashLink } from 'react-router-hash-link';

const NAV_HEIGHT = 100;
const EXTRA_GAP = 24;

const scrollWithOffset = (el) => {
  if (!el) return;
  const yCoordinate = el.getBoundingClientRect().top + window.pageYOffset;
  const yOffset = -NAV_HEIGHT - EXTRA_GAP;
  window.scrollTo({ top: yCoordinate + yOffset, behavior: 'smooth' });
};

const FixedNavBar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const closeMenu = () => setIsMenuOpen(false);

  const navItems = [
    { to: "/#about", label: "About" },
    { to: "/#memo-info", label: "Memo", isSpecial: true },
    { to: "/#skills", label: "Skills" },
    { to: "/#contact", label: "Contact" },
  ];

  const handleForcedJump = (e, to) => {
    if (window.location.pathname !== "/") {
      e.preventDefault(); 
      window.location.href = to; // SPA 라우팅을 깨고 루트(/)로 강제 이동
    }
  };

  const desktopLinkStyle = `
    text-xl font-extrabold cursor-pointer transition-all duration-200
    hover:scale-110 relative px-2
    after:content-[''] after:block after:w-0 hover:after:w-full after:h-[3px]
    after:bg-blue-600 after:transition-all after:duration-300 after:rounded-full
    after:absolute after:left-0 after:bottom-[-6px]
  `;

  return (
    <nav className="fixed top-0 left-0 w-full h-[100px] bg-white shadow z-50 flex items-center justify-between px-6 md:px-10 bg-white/90 backdrop-blur-sm">
      <Link to="/" onClick={closeMenu}>
        <img
          src="https://c.animaapp.com/kPFgkC5m/img/image-21@2x.png"
          alt="로고"
          className="w-[100px] h-[50px] md:w-[130px] md:h-[65px] cursor-pointer object-contain"
        />
      </Link>

      {/* 데스크탑 메뉴: 정상 적용됨 */}
      <div className="hidden md:flex items-center gap-8 ml-auto">
        {navItems.map((item) => (
          <HashLink
            key={item.label}
            to={item.to}
            scroll={scrollWithOffset}
            onClick={(e) => handleForcedJump(e, item.to)}
            className={`${desktopLinkStyle} ${item.isSpecial ? 'text-blue-700' : 'text-gray-800 hover:text-blue-700'}`}
          >
            {item.label}
          </HashLink>
        ))}
      </div>

      {/* 모바일 햄버거 버튼 */}
      <div className="md:hidden flex items-center">
        <button onClick={() => setIsMenuOpen(!isMenuOpen)}>
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            {isMenuOpen 
              ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
            }
          </svg>
        </button>
      </div>

      {/* 모바일 메뉴: [수정] handleForcedJump 추가 */}
      <div className={`absolute top-[100px] left-0 w-full bg-white shadow-lg md:hidden transition-all duration-300 ease-in-out overflow-hidden ${isMenuOpen ? 'max-h-screen opacity-100' : 'max-h-0 opacity-0'}`}>
        <div className="flex flex-col items-center py-8 space-y-6">
          {navItems.map((item) => (
            <HashLink
              key={item.label}
              to={item.to}
              scroll={scrollWithOffset}
              // [추가] 모바일에서도 메뉴를 닫고 강제 점프를 실행합니다.
              onClick={(e) => {
                closeMenu();
                handleForcedJump(e, item.to);
              }}
              className={`text-2xl font-bold transition-colors duration-200 ${item.isSpecial ? 'text-blue-600' : 'text-gray-700 hover:text-blue-600'}`}
            >
              {item.label}
            </HashLink>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default FixedNavBar;