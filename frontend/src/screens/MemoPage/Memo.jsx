import React, { useState } from "react";
import NavBar from "../../components/FixedNavBar";

const Memo = () => {
  const [inputText, setInputText] = useState("");
  const [schedules, setSchedules] = useState([]); // 파싱된 결과(배열)를 관리
  const [isLoading, setIsLoading] = useState(false);

  // 1. 일정 분석 (NLP 파싱 요청)
  const handleParse = async () => {
    if (!inputText.trim()) return alert("분석할 일정을 입력해주세요.");
    setIsLoading(true);
    try {
      const response = await fetch("/parse-multi-schedule/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: inputText }),
      });
      const data = await response.json();
      setSchedules(data.schedules); // 배열 형태로 저장하여 각각 수정 가능하게 함
    } catch (error) {
      console.error("Parsing failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // 2. 수정 핸들러: 특정 인덱스의 필드 값을 업데이트
  const handleSaveToCalendar = async () => {
    if (schedules.length === 0) return alert("저장할 일정이 없습니다.");

    try {
      // 1. 중복 확인 먼저 요청
      const checkRes = await fetch("/check_duplicates/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(schedules),
      });
      const checkData = await checkRes.json();

      // 2. 중복이 있다면 사용자에게 확인
      if (checkData.has_duplicates) {
        const confirmMsg = checkData.duplicates.map(d => 
          `"${d.existing_event.summary}" (시간: ${d.existing_event.start.dateTime})`
        ).join("\n");
        
        const proceed = window.confirm(`다음 일정이 캘린더에 이미 존재하거나 시간이 겹칩니다:\n\n${confirmMsg}\n\n그래도 저장하시겠습니까 (중복인 경우 덮어쓰기)?`);
        if (!proceed) return; // 취소하면 중단
      }

      // 3. 캘린더 저장 요청
      const saveRes = await fetch("/register-google-calendar/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(schedules),
      });

      if (saveRes.ok) {
        alert("일정이 구글 캘린더에 저장되었습니다! 🎉");
      } else {
        const err = await saveRes.json();
        alert("저장 실패: " + err.detail);
      }
    } catch (error) {
      console.error(error);
      alert("오류가 발생했습니다.");
    }
  };

  return (
    <div className="bg-[#F1F1F1] min-h-screen flex flex-col items-center font-pretendard">
      <NavBar />
      <div className="pt-[180px] w-full max-w-7xl mx-auto px-6">
        <h2 className="text-4xl font-black text-gray-900 text-center mb-10">Smart Editor</h2>

        <div className="flex flex-col md:flex-row justify-center gap-10 items-start">
          {/* 왼쪽: 입력 영역 */}
          <div className="bg-white shadow-xl rounded-3xl w-full md:w-[450px] p-8">
            <label className="text-xl font-bold text-indigo-700 mb-3 block">1. 일정 입력</label>
            <textarea
              className="w-full border-2 border-gray-100 rounded-xl p-4 min-h-[200px] text-gray-800 focus:border-indigo-300 outline-none"
              placeholder="내일 오후 2시 강남역 미팅..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
            <button onClick={handleParse} className="w-full mt-6 py-3 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700">
              {isLoading ? "분석 중..." : "일정 분석하기"}
            </button>
          </div>

          {/* 오른쪽: 수정 및 확인 영역 */}
          <div className="bg-white shadow-xl rounded-3xl w-full md:w-[600px] p-8">
            <label className="text-xl font-bold text-green-700 mb-3 block">2. 결과 확인 및 수정</label>
            
            <div className="space-y-6 max-h-[500px] overflow-y-auto pr-2">
              {schedules.length === 0 && <p className="text-gray-400 text-center py-10">분석 결과가 여기에 표시됩니다.</p>}
              
              {schedules.map((item, index) => (
                <div key={index} className="p-5 border-2 border-gray-50 rounded-2xl bg-gray-50 space-y-3">
                  <div>
                    <span className="text-xs font-bold text-gray-400 ml-1">TIME</span>
                    <input 
                      className="w-full p-2 bg-white border border-gray-200 rounded-lg text-sm"
                      value={item.time?.value || ""} 
                      onChange={(e) => handleEdit(index, "time", e.target.value)}
                    />
                  </div>
                  <div className="flex gap-3">
                    <div className="flex-1">
                      <span className="text-xs font-bold text-gray-400 ml-1">LOCATION</span>
                      <input 
                        className="w-full p-2 bg-white border border-gray-200 rounded-lg text-sm"
                        value={item.location || ""} 
                        onChange={(e) => handleEdit(index, "location", e.target.value)}
                      />
                    </div>
                    <div className="flex-1">
                      <span className="text-xs font-bold text-gray-400 ml-1">EVENT</span>
                      <input 
                        className="w-full p-2 bg-white border border-gray-200 rounded-lg text-sm"
                        value={item.event || ""} 
                        onChange={(e) => handleEdit(index, "event", e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {schedules.length > 0 && (
              <button onClick={handleSaveToCalendar} className="w-full mt-8 py-4 bg-green-600 text-white font-bold rounded-xl hover:bg-green-700 shadow-lg">
                최종 결과 구글 캘린더에 저장
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Memo;