import React from 'react';
import { HashLink } from 'react-router-hash-link';

const NAV_HEIGHT = 100;   // 네비게이터 높이(px)
const EXTRA_GAP = 24;

const scrollWithOffset = (el) => {
  if (!el) return;
  const yCoordinate = el.getBoundingClientRect().top + window.pageYOffset;
  const yOffset = -NAV_HEIGHT - EXTRA_GAP;
  window.scrollTo({ top: yCoordinate + yOffset, behavior: 'smooth' });
};

const FixedNavBar = () => (
  <nav className="fixed top-0 left-0 w-full h-[100px] bg-white shadow z-50 flex items-center px-10">
    <img
      src="https://c.animaapp.com/kPFgkC5m/img/image-21@2x.png"
      alt="로고"
      className="w-[130px] h-[65px] cursor-pointer"
      onClick={() => window.location.href = "/"}
    />
    <div className="ml-auto flex gap-8">
      {/* 공통 Tailwind 클래스 반환 함수 활용도 가능 */}
      <HashLink
        to="#about"
        scroll={scrollWithOffset}
        className="
          text-xl font-extrabold cursor-pointer
          transition-all duration-200
          hover:text-blue-700
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
        "
      >
        About
      </HashLink>
      <HashLink
        to="#skills"
        scroll={scrollWithOffset}
        className="
          text-xl font-extrabold cursor-pointer
          transition-all duration-200
          hover:text-blue-700
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
        "
      >
        Skills
      </HashLink>
      <HashLink
        to="#contact"
        scroll={scrollWithOffset}
        className="
          text-xl font-extrabold cursor-pointer
          transition-all duration-200
          hover:text-blue-700
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
        "
      >
        Contact
      </HashLink>
      <a
        href="http://3.104.198.251:8001/home"
        target="_blank"
        rel="noopener noreferrer"
        className="
          text-xl font-extrabold text-blue-700 cursor-pointer
          transition-all duration-200
          hover:text-blue-900
          hover:scale-110
          relative
          after:content-['']
          after:block
          after:w-0 hover:after:w-full
          after:h-[3px]
          after:bg-blue-700
          after:transition-all after:duration-300
          after:rounded-full
          after:absolute
          after:left-0 after:bottom-[-6px]
          px-2
        "
      >
        Memo
      </a>
    </div>
  </nav>
);



export default FixedNavBar;
