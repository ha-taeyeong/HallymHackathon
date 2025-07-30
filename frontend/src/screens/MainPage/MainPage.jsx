import React,{useEffect} from "react";
import NavBar from "../../components/NavBar";

const MainPage = () => {
useEffect(() => {
  if (window.location.hash) {
    const id = window.location.hash.replace("#", "");
    const el = document.getElementById(id);
    if (el) {
      setTimeout(() => {
        el.scrollIntoView({ behavior: "smooth" });
      }, 300); // 50ms가 너무 짧을 수 있음
    }
  }
}, []);
  return (
    <div
      className="bg-white flex flex-row justify-center w-full"
      data-model-id="1:902">
         <NavBar /> 
      <div className="bg-white w-[1440px] h-[3603px] relative"
      style={{ paddingTop: "164px" }}
      >
       

        <img
          className="w-[1269px] h-[715px] top-[594px] left-[69px] absolute object-cover"
          alt="Image"
          src="https://c.animaapp.com/kPFgkC5m/img/image-4.png"
        />

        <div
        id="about-us" 
        className="absolute w-[624px] top-[1436px] left-[79px] [font-family:'Inter',Helvetica] font-semibold text-black text-5xl tracking-[-0.96px] leading-[normal]">
          About us
        </div>

        <div className="flex flex-col w-[405px] h-[541px] items-start gap-6 absolute top-[1543px] left-[79px]">
          <div className="relative self-stretch w-full h-[405px] rounded-lg overflow-hidden bg-[url(https://c.animaapp.com/kPFgkC5m/img/image-1@2x.png)] bg-cover bg-[50%_50%]">
            <img
              className="w-[405px] h-[405px] top-0 left-0 absolute object-cover"
              alt="Image"
              src="https://c.animaapp.com/kPFgkC5m/img/image-5-1.png"
            />
          </div>

          <div className="relative self-stretch [font-family:'Inter',Helvetica] font-medium text-black text-2xl tracking-[0] leading-9">
            하태영
            <br />
            Backend 개발
          </div>

          <div className="relative w-[381px] h-9 mb-[-20.00px]" />

          <div className="relative w-[381px] h-9 mb-[-80.00px]" />
        </div>

        <div className="inline-flex gap-24 absolute top-[1545px] left-[516px] flex-col items-start">
          <div className="flex w-[405px] h-[541px] gap-6 relative flex-col items-start">
            <div className="relative self-stretch w-full h-[405px] rounded-lg overflow-hidden bg-[url(https://c.animaapp.com/kPFgkC5m/img/image-1@2x.png)] bg-cover bg-[50%_50%]">
              <div className="relative w-[405px] h-[405px] bg-[url(https://c.animaapp.com/kPFgkC5m/img/image-5-1.png)] bg-cover bg-[50%_50%]">
                <img
                  className="w-[405px] h-[405px] top-0 left-0 absolute object-cover"
                  alt="Image"
                  src="https://c.animaapp.com/kPFgkC5m/img/image-7@2x.png"
                />
              </div>
            </div>

            <div className="relative self-stretch [font-family:'Inter',Helvetica] font-medium text-black text-2xl tracking-[0] leading-9">
              이신우
              <br />
              Frontend 개발
            </div>
          </div>

          <div className="relative w-[381px] h-9" />
        </div>

        <div 
        id="contact-section"
        className="absolute w-[624px] top-[3246px] left-[91px] [font-family:'Inter',Helvetica] font-semibold text-black text-5xl tracking-[-0.96px] leading-[normal]">
          Contact
        </div>

        <div className="flex w-[1280px] items-center gap-[31px] absolute top-[3353px] left-[91px]">
          <div className="flex gap-8 relative flex-1 grow flex-col items-start">
            <div className="flex flex-col w-[547.56px] items-start gap-[var(--variable-collection-spacing-XS)] relative flex-[0_0_auto]">
              <p className="relative w-[548px] mt-[-1.00px] mr-[-0.44px] [font-family:'Inter',Helvetica] font-medium text-black text-2xl tracking-[0] leading-9">
                하태영 hateyong@gmail.com / github
                <br />
                <br />
                이신우 steven8602@gamil.com / github
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-col w-[844px] items-start gap-10 absolute top-[212px] left-[79px]">
          <div className="flex flex-col items-start gap-6 relative self-stretch w-full flex-[0_0_auto]">
            <div className="relative self-stretch mt-[-1.00px] [font-family:'Inter',Helvetica] font-bold text-black text-[64px] tracking-[-1.28px] leading-[normal]">
              Why Make platform ?
            </div>

            <p className="relative self-stretch font-subheading font-[number:var(--subheading-font-weight)] text-[#000000bf] text-[length:var(--subheading-font-size)] tracking-[var(--subheading-letter-spacing)] leading-[var(--subheading-line-height)] [font-style:var(--subheading-font-style)]">
              일상속 떠오른 일정이나 정보를 메모하면 자동으로 날짜, 시간, 장소를
              추출해 <br />
              캘린더에 등록해주는 플랫폼입니다. 반복되는 수작업을 줄이고, 일정
              누락을 방지해 사용자 편의성과 생산성을 높이고자 개발하게
              되었습니다.
            </p>
          </div>

          <div
            className="flex w-[133px] h-14 items-center gap-2 px-8 py-5 relative bg-black rounded-lg shadow-button-shadow cursor-pointer"
            onClick={() => window.location.href = 'http://localhost:5173/memo'}
          >
            <div className="relative w-[68.25px] h-[17.72px] mt-[-0.86px] mb-[-0.86px]">
              <img
                className="absolute w-3 h-3.5 top-1 left-14"
                alt="Vector"
                src="https://c.animaapp.com/kPFgkC5m/img/vector.svg"
              />

              <img
                className="absolute w-[18px] h-[13px] top-1 left-[35px]"
                alt="Vector"
                src="https://c.animaapp.com/kPFgkC5m/img/vector-1.svg"
              />

              <img
                className="absolute w-3 h-3.5 top-1 left-[21px]"
                alt="Vector"
                src="https://c.animaapp.com/kPFgkC5m/img/vector-2.svg"
              />

              <img
                className="absolute w-[18px] h-[17px] top-0 left-0"
                alt="Vector"
                src="https://c.animaapp.com/kPFgkC5m/img/vector-3.svg"
              />
            </div>
          </div>
        </div>

        <div className="absolute w-[1070px] h-[607px] top-[2382px] left-[79px]">
          <div 
            id="skills-section"
            className="absolute w-[624px] top-0 left-[7px] [font-family:'Inter',Helvetica] font-semibold text-black text-5xl tracking-[-0.96px] leading-[normal]">
            Skills
          </div>

          <div className="absolute w-[1068px] h-[187px] top-[109px] left-0">
            <div className="absolute w-[624px] top-0 left-1.5 [font-family:'Inter',Helvetica] font-semibold text-black text-[32px] tracking-[-0.64px] leading-[normal]">
              Frontend
            </div>

            <div className="absolute w-[1066px] h-[124px] top-[63px] left-0">
              <img
                className="w-[88px] h-[120px] top-1 left-0 absolute object-cover"
                alt="Image"
                src="https://c.animaapp.com/kPFgkC5m/img/image-8@2x.png"
              />

              <img
                className="w-[82px] h-[124px] top-0 left-[118px] absolute object-cover"
                alt="Image"
                src="https://c.animaapp.com/kPFgkC5m/img/image-9@2x.png"
              />

              <img
                className="w-[175px] h-[108px] top-4 left-[234px] absolute object-cover"
                alt="Image"
                src="https://c.animaapp.com/kPFgkC5m/img/image-10@2x.png"
              />

              <img
                className="w-[220px] h-[84px] top-4 left-[437px] absolute object-cover"
                alt="Image"
                src="https://c.animaapp.com/kPFgkC5m/img/image-11@2x.png"
              />

              <img
                className="w-[79px] h-[103px] top-3 left-[708px] absolute object-cover"
                alt="Image"
                src="https://c.animaapp.com/kPFgkC5m/img/image-12@2x.png"
              />

              <img
                className="w-[228px] h-[83px] top-[17px] left-[838px] absolute object-cover"
                alt="Image"
                src="https://c.animaapp.com/kPFgkC5m/img/image-13@2x.png"
              />
            </div>
          </div>

          <div className="absolute w-[562px] top-[347px] left-3.5 [font-family:'Inter',Helvetica] font-semibold text-black text-[32px] tracking-[-0.64px] leading-[normal] whitespace-nowrap">
            Backend
          </div>

          <img
            className="w-[287px] h-[78px] top-[480px] left-[412px] absolute object-cover"
            alt="Image"
            src="https://c.animaapp.com/kPFgkC5m/img/image-16@2x.png"
          />

          <img
            className="w-[344px] h-[131px] top-[453px] left-[715px] absolute object-cover"
            alt="Image"
            src="https://c.animaapp.com/kPFgkC5m/img/image-17@2x.png"
          />

          <img
            className="w-[108px] h-[116px] top-[461px] left-[241px] absolute object-cover"
            alt="Image"
            src="https://c.animaapp.com/kPFgkC5m/img/image-19@2x.png"
          />

          <img
            className="w-[177px] h-[177px] top-[430px] left-0 absolute object-cover"
            alt="Image"
            src="https://c.animaapp.com/kPFgkC5m/img/image-20@2x.png"
          />
        </div>
      </div>
    </div>
  );
};

export default MainPage;