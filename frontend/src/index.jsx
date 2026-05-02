import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
// 경로를 파일 확장자까지 명시하거나 index 파일을 활용하도록 수정
import MainPage from "./screens/MainPage/MainPage.jsx"; 
import MemoPage from "./screens/MemoPage/Memo.jsx";

const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Failed to find the root element");

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/memo" element={<MemoPage />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);