"use client";

import React, { useEffect } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useMap } from 'react-leaflet';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

const Map = ({ data, type }) => {
  useEffect(() => {
    // Fix Leaflet's default icon path issues
    delete L.Icon.Default.prototype._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    });
  }, []);

  // Custom icons for different types
  const icons = {
    Emergency: L.icon({
      iconUrl: '/emergency-icon.png',
      iconSize: [25, 25],
    }),
    assistance: L.icon({
      iconUrl: '/assistance-icon.png',
      iconSize: [25, 25],
    }),
    events: L.icon({
      iconUrl: '/events-icon.png',
      iconSize: [25, 25],
    }),
  };

  // Center map on New York City coordinates
  const center = [40.7128, -74.0060];

  return (
    <div className="h-[400px] w-full rounded-lg overflow-hidden">
      <MapContainer
        center={center}
        zoom={12}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {data?.map((item) => (
          <Marker
            key={item.id}
            position={[item.coordinates?.lat || 0, item.coordinates?.lng || 0]}
            icon={icons[type] || L.Icon.Default}
          >
            <Popup>
              <div className="p-2">
                <h3 className="font-semibold">{item.title}</h3>
                <p className="text-sm">{item.description}</p>
                <p className="text-sm mt-1">{item.location}</p>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default Map;