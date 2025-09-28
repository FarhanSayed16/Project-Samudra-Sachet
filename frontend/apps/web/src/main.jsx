import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";
import 'leaflet/dist/leaflet.css';

const container = document.getElementById("root");
createRoot(container).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
