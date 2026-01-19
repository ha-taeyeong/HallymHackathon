// src/components/FixedNavBar.jsx
import React, { useState } from 'react';
import { HashLink } from 'react-router-hash-link';

const NAV_HEIGHT = 100;   // 네비게이터 높이(px)
const EXTRA_GAP = 24;

const scrollWithOffset = (el) => {
  if (!el) return;
  const yCoordinate = el.getBoundingClientRect().top + window.pageYOffset;
  const yOffset = -NAV_HEIGHT - EXTRA_GAP;
  window.scrollTo({ top: yCoordinate + yOffset, behavior: 'smooth' });
};

const FixedNavBar = () => {
  // 모바일 메뉴 열림/닫힘 상태 관리
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // 메뉴 닫기 핸들러
  const closeMenu = () => setIsMenuOpen(false);

  // 링크 정보 배열 (중복 제거 및 관리 용이성)
  const navItems = [
    { to: "#about", label: "About" },
    { to: "#memo", label: "Memo", isSpecial: true }, 
    { to: "#skills", label: "Skills" },
    { to: "#contact", label: "Contact" },
  ];

  // 데스크탑용 공통 호버 애니메이션 스타일
  const desktopLinkStyle = `
    text-xl font-extrabold cursor-pointer
    transition-all duration-200
    hover:scale-110
    relative
    after:content-['']
    after:block
    after:w-0 hover:after:w-full
    after:h-[3px]
    after:bg-blue-600
    after:transition-all after:duration-300
    after:rounded-full
    after:absolute
    after:left-0 after:bottom-[-6px]
    px-2
  `;

  return (
    <nav className="fixed top-0 left-0 w-full h-[100px] bg-white shadow z-50 flex items-center justify-between px-6 md:px-10 bg-white/90 backdrop-blur-sm">
      {/* 로고 */}
      <img
        src="https://c.animaapp.com/kPFgkC5m/img/image-21@2x.png"
        alt="로고"
        className="w-[100px] h-[50px] md:w-[130px] md:h-[65px] cursor-pointer object-contain"
        onClick={() => window.location.href = "/"}
      />

      {/* === 데스크탑 메뉴 (md 이상에서만 보임) === */}
      <div className="hidden md:flex items-center gap-8 ml-auto">
        {navItems.map((item) => (
          <HashLink
            key={item.to}
            to={item.to}
            scroll={scrollWithOffset}
            className={`${desktopLinkStyle} ${item.isSpecial ? 'text-blue-700' : 'text-gray-800 hover:text-blue-700'}`}
          >
            {item.label}
          </HashLink>
        ))}
      </div>

      {/* === 모바일 햄버거 버튼 (md 미만에서만 보임) === */}
      <div className="md:hidden flex items-center">
        <button onClick={() => setIsMenuOpen(!isMenuOpen)} aria-label="메뉴 열기/닫기">
          {isMenuOpen ? (
            // 닫기 아이콘 (X)
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            // 햄버거 아이콘
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16m-7 6h7" />
            </svg>
          )}
        </button>
      </div>

      {/* === 모바일 드롭다운 메뉴 === */}
      {/* isMenuOpen 상태에 따라 보이거나 숨겨짐 */}
      <div className={`absolute top-[100px] left-0 w-full bg-white shadow-lg md:hidden transition-all duration-300 ease-in-out overflow-hidden ${isMenuOpen ? 'max-h-screen opacity-100' : 'max-h-0 opacity-0'}`}>
        <div className="flex flex-col items-center py-8 space-y-6">
          {navItems.map((item) => (
            <HashLink
              key={item.to}
              to={item.to}
              scroll={scrollWithOffset}
              onClick={closeMenu} // 클릭 시 메뉴 닫기
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