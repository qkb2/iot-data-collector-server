import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import Devices from "./pages/Devices";
import DeviceDetail from "./pages/DeviceDetail";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />}>
          <Route index element={<Devices />} />
          <Route path="device/:id" element={<DeviceDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
