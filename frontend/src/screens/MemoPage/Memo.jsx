import React from "react";
import { HashLink } from 'react-router-hash-link';
import { Rectangle } from "../../components/Rectangle";


const Memo = () => {
  return (
    <div
      className="bg-white flex flex-row justify-center w-full"
      data-model-id="1:777"
    >
      <div className="bg-white w-[1442px] h-[1308px] relative">
        <div className="absolute w-[1440px] h-[164px] top-0 left-0">
          <div className="relative h-[164px]">
            <div className="left-[970px] inline-flex items-center justify-end gap-[var(--variable-collection-spacing-m)] absolute top-14">
              <div className="relative w-fit text-[length:var(--body-text-font-size)] leading-[var(--body-text-line-height)] font-body-text font-[number:var(--body-text-font-weight)] text-white tracking-[var(--body-text-letter-spacing)] whitespace-nowrap [font-style:var(--body-text-font-style)]">
                페이지
              </div>

              <div className="relative w-fit text-[length:var(--body-text-font-size)] leading-[var(--body-text-line-height)] font-body-text font-[number:var(--body-text-font-weight)] text-white tracking-[var(--body-text-letter-spacing)] whitespace-nowrap [font-style:var(--body-text-font-style)]">
                페이지
              </div>

              <div className="relative w-fit text-[length:var(--body-text-font-size)] leading-[var(--body-text-line-height)] font-body-text font-[number:var(--body-text-font-weight)] text-white tracking-[var(--body-text-letter-spacing)] whitespace-nowrap [font-style:var(--body-text-font-style)]">
                페이지
              </div>

              <button className="all-[unset] box-border justify-center px-6 py-3.5 relative flex-[0_0_auto] border-2 border-solid border-white inline-flex items-center gap-2 rounded-lg shadow-button-shadow">
                <div className="relative w-fit mt-[-2.00px] text-[length:var(--small-text-font-size)] leading-[var(--small-text-line-height)] font-small-text font-[number:var(--small-text-font-weight)] text-white tracking-[var(--small-text-letter-spacing)] whitespace-nowrap [font-style:var(--small-text-font-style)]">
                  버튼
                </div>
              </button>
            </div>

            <div className="absolute h-[30px] top-[66px] left-20 text-[length:var(--body-text-font-size)] leading-[var(--body-text-line-height)] font-body-text font-[number:var(--body-text-font-weight)] text-white tracking-[var(--body-text-letter-spacing)] whitespace-nowrap [font-style:var(--body-text-font-style)]">
              사이트 이름
            </div>

            <div className="bg-white absolute w-[1440px] h-[164px] top-0 left-0">
              <div className="left-[935px] inline-flex items-center justify-end gap-[var(--variable-collection-spacing-m)] absolute top-14">
             <HashLink
                to="/#about-us"
                smooth
                className="relative w-fit font-body-text font-[number:var(--body-text-font-weight)] text-black text-[length:var(--body-text-font-size)] tracking-[var(--body-text-letter-spacing)] leading-[var(--body-text-line-height)] whitespace-nowrap [font-style:var(--body-text-font-style)] cursor-pointer"
              >
                About
              </HashLink>


              <HashLink
                to="/#skills-section"
                smooth
                className="relative w-fit font-body-text font-[number:var(--body-text-font-weight)] text-black text-[length:var(--body-text-font-size)] tracking-[var(--body-text-letter-spacing)] leading-[var(--body-text-line-height)] whitespace-nowrap [font-style:var(--body-text-font-style)] cursor-pointer"
              >
                Skills
              </HashLink>

                <button className="all-[unset] box-border justify-center px-6 py-3.5 relative flex-[0_0_auto] bg-black inline-flex items-center gap-2 rounded-lg shadow-button-shadow">
                  <div className="relative w-fit mt-[-1.00px] font-[number:var(--small-text-font-weight)] text-white text-[length:var(--small-text-font-size)] leading-[var(--small-text-line-height)] whitespace-nowrap font-small-text tracking-[var(--small-text-letter-spacing)] [font-style:var(--small-text-font-style)]">
                    Memo
                  </div>
                </button>

               <HashLink
                to="/#contact-section"
                smooth
                className="relative w-fit font-body-text font-[number:var(--body-text-font-weight)] text-black text-[length:var(--body-text-font-size)] tracking-[var(--body-text-letter-spacing)] leading-[var(--body-text-line-height)] whitespace-nowrap [font-style:var(--body-text-font-style)] cursor-pointer"
                >
                Contact
              </HashLink>
                </div>

              <img
                className="absolute w-[184px] h-[88px] top-[38px] left-[59px] object-cover"
                alt="Image"
                src="https://c.animaapp.com/V2AgVb95/img/image-22@2x.png"
              />
            </div>
          </div>
        </div>

        <div className="absolute w-[665px] h-[298px] top-[220px] left-[660px]">
          <div className="absolute w-[145px] top-0 left-0 font-semibold text-black text-[40px] leading-[48.0px] [font-family:'Inter',Helvetica] tracking-[0]">
            Memo
          </div>

          <Rectangle className="!absolute !left-[97px] !top-[17px]" />
        </div>

        <Rectangle className="!absolute !left-16 !top-[234px]" />
        <button className="all-[unset] box-border px-6 py-3 absolute top-[791px] left-[1127px] bg-black inline-flex items-center gap-2 rounded-lg shadow-button-shadow">
          <div className="relative w-fit mt-[-1.00px] text-2xl leading-9 [font-family:'Inter',Helvetica] font-medium text-white tracking-[0] whitespace-nowrap">
            구글 캘린더에 저장
          </div>
        </button>

        <div className="absolute w-[143px] h-[60px] top-[791px] left-[529px]">
          <button className="all-[unset] box-border px-6 py-3 relative bg-black inline-flex items-center gap-2 rounded-lg shadow-button-shadow">
            <div className="relative w-fit mt-[-1.00px] text-2xl leading-9 [font-family:'Inter',Helvetica] font-medium text-white tracking-[0] whitespace-nowrap">
              일정 확인
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};
export default Memo;