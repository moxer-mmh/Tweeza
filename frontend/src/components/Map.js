"use client";
import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";

const Map = ({ items, activeTab }) => {
  const [map, setMap] = useState(null);

  useEffect(() => {
    let L;
    if (typeof window !== "undefined") {
      L = require("leaflet");
    }
    const map = L.map("map").setView([40.7128, -74.006], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
    }).addTo(map);

    const markerColors = {
      Emergency: "#973535",
      assistance: "#3B82F6",
      events: "#059669",
    };
    map.eachLayer((layer) => {
      if (layer instanceof L.Marker) {
        map.removeLayer(layer);
      }
    });

    items.forEach((item) => {
      const lat = item.coordinates.lat;
      const lng = item.coordinates.lng;

      const markerIcon = L.divIcon({
        className: "custom-marker",
        html: `<div style="background-color: ${markerColors[activeTab]}; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });

      const marker = L.marker([lat, lng], { icon: markerIcon }).addTo(map)
        .bindPopup(`
          <div class="p-2">
            <h3 class="font-semibold">${item.title}</h3>
            <p class="text-sm text-gray-600">${item.location}</p>
          </div>
        `);
    });

    return () => {
      map.remove();
    };
  }, [items, activeTab]);

  return <div id="map" className="w-full h-full rounded-lg" />;
};

export default Map;
