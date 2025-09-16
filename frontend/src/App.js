import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import TimeAndMaterialForm from "./components/TimeAndMaterialForm";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<TimeAndMaterialForm />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;