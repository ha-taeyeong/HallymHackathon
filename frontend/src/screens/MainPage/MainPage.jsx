// src/pages/MainPage.jsx
import React, { useEffect, useState } from "react";
import FixedNavBar from "../../components/FixedNavBar";

const NAV_HEIGHT = 100; // FixedNavBar 높이(px)
const EXTRA_GAP = 24;   // 추가 여백(px)

const scrollHashWithOffset = () => {
  if (window.location.hash) {
    const id = window.location.hash.replace("#", "");
    const element = document.getElementById(id);
    if (element) {
      const yOffset = element.getBoundingClientRect().top + window.pageYOffset - NAV_HEIGHT - EXTRA_GAP;
      window.scrollTo({ top: yOffset, behavior: "smooth" });
    }
  }
};

// ★ 1. 스킬 정보 배열 통합(Frontend, Backend 별도)
const frontendSkills = [
  {
    name: "HTML5",
    logo: "/images/html5.png",
    description: "HTML5는 웹페이지의 구조를 정의하는 최신 마크업 언어로, 폼/미디어/인터랙션 향상 등 풍부한 웹 환경을 제공합니다.",
  },
  {
    name: "CSS3",
    logo: "/images/css3.png",
    description: "CSS3는 웹페이지의 디자인을 담당하며 레이아웃·애니메이션 등 다채로운 시각 효과를 구현할 수 있습니다.",
  },
  {
    name: "TailwindCSS",
    logo: "/images/tailwindcss.png",
    description: "TailwindCSS는 utility-first 기반의 모던 CSS 프레임워크로, 빠르게 반응형 UI 개발이 가능합니다.",
  },
  {
    name: "React",
    logo: "/images/react.png",
    description: "React는 페이스북에서 제작한 빠르고 확장가능한 프론트엔드 UI 라이브러리입니다.",
  },
  {
    name: "Node.js",
    logo: "/images/node.js.png",
    description: "Node.js는 JavaScript 런타임 환경으로, 서버 개발에 널리 쓰이며 비동기 프로그래밍이 강점입니다.",
  },
  {
    name: "Figma",
    logo: "/images/figma.png",
    description: "Figma는 협업 기반의 디자인 툴입니다. UI/UX 설계, 프토로타이핑, 팀 실시간 피드백에 최적화되어 있습니다.",
  },
  {
    name: "Anima",
    logo: "/images/anima.png",
    description: "Anima는 디자인(피그마/스케치) → 실동작 코드 변환을 지원하는 프로토타이핑 툴입니다.",
  },
];

const backendSkills = [
  {
    name: "Python",
    logo: "/images/python.jpeg",
    description: "Python은 간결한 문법과 강력한 라이브러리로 유명한 범용 프로그래밍 언어로, AI/데이터/백엔드에도 널리 쓰입니다.",
  },
  {
    name: "FastAPI",
    logo: "/images/fastapi.png",
    description: "FastAPI는 직관적이고 빠른 비동기 REST API 서버 개발을 위한 Python 프레임워크입니다.",
  },
  {
    name: "Google API",
    logo: "/images/googleapi.png",
    description: "Google API는 구글 서비스와 일정·인증 등 연동을 위한 다양한 개발용 API입니다.",
  },
  {
    name: "Duckling",
    logo: "/images/duckling.png",
    description: "Duckling은 자연어에서 시간·수량 등 정보를 추출하는 NLP 툴입니다.",
  },
  {
    name: "dateparser",
    logo: "/images/dateparser.png",
    description: "dateparser는 다양한 언어와 형식의 날짜 정보를 자동 해석해주는 라이브러리입니다.",
  },
  {
    name: "Stanza",
    logo: "/images/stanza.png",
    description: "Stanza는 스탠포드대에서 만든 고성능 자연어처리(NLP) Python 패키지입니다.",
  },
  {
    name: "Ubuntu",
    logo: "/images/ubuntu.png",
    description: "Ubuntu는 대표적인 리눅스 배포판으로 안정적인 서버 운영에 많이 쓰입니다.",
  },
  {
    name: "AWS EC2",
    logo: "/images/awsec2.png",
    description: "AWS EC2는 클라우드 기반의 가상 서버로, 대용량 서비스, 쉬운 확장성까지 제공하는 인프라입니다.",
  },
];

const MainPage = () => {
  useEffect(() => {
    setTimeout(scrollHashWithOffset, 300);
  }, []);

  const [selectedSkill, setSelectedSkill] = useState(null);

  useEffect(() => {
    document.title = "Plan Up";    
    if (!selectedSkill) return;
    const onKeyDown = (e) => {
      if (e.key === "Escape") setSelectedSkill(null);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [selectedSkill]);

  return (
    <div className="bg-white min-h-screen w-full font-pretendard">
      <FixedNavBar />
      <main className="pt-[calc(100px+1rem)] max-w-7xl mx-auto px-6">

        {/* 1. Why Make platform Section */}
        <section className="mb-40 pt-6">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-left">Why Make platform?</h1>
          <p className="text-lg md:text-xl text-gray-700 leading-relaxed max-w-4xl mb-10 text-left">
            저희는 평소 떠오른 일정이나 약속을 간단히 메모만 해도,<br />
            자동으로 날짜, 시간, 장소를 인식해 캘린더에 등록해주는 서비스를 만들었습니다.<br />
            매번 캘린더에 일정을 옮겨 적는 번거로움을 덜고,<br />
            생산성과 편의성을 높일 수 있는 솔루션이 될 것이라 믿습니다.
          </p>
          <img
            src="https://c.animaapp.com/kPFgkC5m/img/image-4.png"
            alt="대표 이미지"
            className="w-full max-h-[700px] object-cover rounded-2xl mx-auto shadow-lg"
          />
        </section>

        {/* 2. About us Section */}
        <section id="about" className="mb-40 scroll-mt-28">
          <h2 className="text-4xl md:text-5xl font-extrabold mb-14 text-left">About us</h2>
          <p className="text-xl text-gray-700 leading-relaxed max-w-4xl mx-auto mb-10 text-center">
            일상을 자동화하는 일정관리 웹서비스 <b>Plan UP</b> 팀입니다.
          </p>
          <div className="flex gap-12 flex-wrap justify-center items-center">
            {/* 하태영 */}
            <div className="w-80 md:w-96 bg-gray-50 rounded-2xl shadow-xl p-10 flex flex-col items-center">
              <img src="https://c.animaapp.com/kPFgkC5m/img/image-5-1.png" alt="하태영" className="w-48 h-48 md:w-56 md:h-56 rounded-full object-cover mb-6" />
              <h3 className="text-3xl font-black mb-2">하태영</h3>
              <p className="text-xl text-gray-700 mb-3">Backend 개발</p>
              <p className="text-gray-500 text-lg">스마트IoT</p>
            </div>
            {/* 이신우 */}
            <div className="w-80 md:w-96 bg-gray-50 rounded-2xl shadow-xl p-10 flex flex-col items-center">
              <img src="https://c.animaapp.com/kPFgkC5m/img/image-7@2x.png" alt="이신우" className="w-48 h-48 md:w-56 md:h-56 rounded-full object-cover mb-6" />
              <h3 className="text-3xl font-black mb-2">이신우</h3>
              <p className="text-xl text-gray-700 mb-3">Frontend 개발</p>
              <p className="text-gray-500 text-lg">빅데이터전공</p>
            </div>
          </div>
        </section>

        {/* ★ 3. Memo Section (새로 추가됨) ★ */}
        <section id="memo" className="mb-40 scroll-mt-28">
          <h2 className="text-4xl md:text-5xl font-extrabold mb-14 text-left text-blue-700">Memo</h2>
          <div className="bg-blue-50 rounded-3xl p-8 md:p-16 flex flex-col md:flex-row items-center gap-12 border border-blue-100 shadow-sm">
            <div className="flex-1 text-left">
              <h3 className="text-3xl font-bold mb-6">자연어 인식 메모</h3>
              <p className="text-xl text-gray-700 leading-relaxed mb-10">
                복잡한 클릭 없이 한 줄의 메모만 남기세요.<br />
                인공지능이 텍스트에서 <b>시간, 날짜, 장소</b>를 추출하여<br />
                당신의 캘린더에 자동으로 등록합니다.
              </p>
              <a 
                href="https://planup.p-e.kr/home" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-block bg-blue-600 text-white px-10 py-4 rounded-xl font-bold text-lg hover:bg-blue-700 transition-all shadow-md hover:-translate-y-1"
              >
                서비스 이용해보기
              </a>
            </div>
<<<<<<< HEAD
            <div className="flex-1 w-full max-w-md bg-white p-6 rounded-2xl shadow-2xl border borderd-blue-50 rotate-1 md:rotate-2">
=======
            <div className="flex-1 w-full max-w-md bg-white p-6 rounded-2xl shadow-2xl border border-blue-50 rotate-1 md:rotate-2">
>>>>>>> c242d9b63ce9b07ff6bd6220c8ebaeeb64c3b944
              <div className="flex gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                <div className="w-3 h-3 rounded-full bg-green-400"></div>
              </div>
              <p className="text-2xl font-medium text-gray-800 italic">"내일 오후 2시에 강남역에서 회의"</p>
              <div className="mt-6 pt-4 border-t border-dashed border-blue-200">
                <p className="text-blue-600 font-bold">✓ 2024-11-20 14:00 등록 완료</p>
              </div>
            </div>
          </div>
        </section>

        {/* 4. Skills Section */}
        <section id="skills" className="mb-40 scroll-mt-28">
          <h2 className="text-4xl md:text-5xl font-extrabold mb-16 text-left">Skills</h2>
          {/* Frontend */}
          <div className="mb-24">
            <h3 className="text-3xl font-semibold mb-12 text-left">Frontend</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-12 justify-items-center">
              {frontendSkills.map(skill => (
                <div key={skill.name} onClick={() => setSelectedSkill(skill)} className="flex flex-col items-center cursor-pointer hover:scale-110 transition-transform">
                  <img src={skill.logo} alt={skill.name} className="h-24 md:h-28 object-contain mb-3" />
                  <span className="text-lg text-gray-600 font-bold">{skill.name}</span>
                </div>
              ))}
            </div>
          </div>
          {/* Backend */}
          <div>
            <h3 className="text-3xl font-semibold mb-12 text-left">Backend & Infra</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-12 justify-items-center">
              {backendSkills.map(skill => (
                <div key={skill.name} onClick={() => setSelectedSkill(skill)} className="flex flex-col items-center cursor-pointer hover:scale-110 transition-transform">
                  <img src={skill.logo} alt={skill.name} className="h-24 md:h-36 object-contain mb-3" />
                  <span className="text-lg text-gray-600 font-bold">{skill.name}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* 5. Contact Section */}
        <section id="contact" className="mb-40 pb-32 scroll-mt-28">
          <h2 className="text-4xl md:text-5xl font-extrabold mb-8 text-center">Contact</h2>
          <div className="text-xl flex flex-col md:flex-row justify-center items-center gap-12 text-gray-700">
            <p>하태영: electro0218@gmail.com</p>
            <p>이신우: steven8602@naver.com</p>
          </div>
        </section>

        {/* 스킬 모달 (생략 없이 유지) */}
        {selectedSkill && (
          <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-[100] animate-fadeIn">
            <div className="bg-white rounded-2xl p-8 max-w-lg w-full mx-4 relative shadow-2xl">
              <button onClick={() => setSelectedSkill(null)} className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-full">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              <img src={selectedSkill.logo} alt={selectedSkill.name} className="h-24 object-contain mb-5 mx-auto" />
              <h3 className="text-2xl font-extrabold mb-3 text-center">{selectedSkill.name}</h3>
              <p className="text-gray-700 text-lg text-center">{selectedSkill.description}</p>
            </div>
          </div>
        )}
<<<<<<< HEAD
        <footer className="py-10 border-t border-gray-100 text-center">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-500">© 2025 Plan Up. All rights reserved.</p>
            <div className="flex gap-6">
              {/* 반드시 전체 HTTPS 경로를 입력하세요 */}
              <a 
                href="https://planup.p-e.kr/static/privacy.html" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-gray-600 font-bold hover:text-blue-600 transition-colors"
              >
                개인정보처리방침
              </a>
              <span className="text-gray-300">|</span>
              <span className="text-gray-500">Service: Plan Up</span>
            </div>
          </div>
        </footer>
=======
>>>>>>> c242d9b63ce9b07ff6bd6220c8ebaeeb64c3b944
      </main>
    </div>
  );
};

export default MainPage;