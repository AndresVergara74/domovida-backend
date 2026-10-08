// src/MapaHogar.tsx
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import { divIcon } from "leaflet";
import "leaflet/dist/leaflet.css";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { iconoTipo, nombreTipo, nombreHabitacion, haceCuanto } from "./etiquetas";

interface Sensor {
  sensor_id: string;
  tipo: string;
  habitacion: string;
  online: boolean;
  ultima_lectura: string;
}

interface MapaHogarProps {
  sensores: Sensor[];
}

// Coordenadas del hogar (Santiago, Chile - ejemplo)
const HOGAR_CENTRO: [number, number] = [-33.4489, -70.6693];

// Coordenadas por habitación (offset desde el centro)
const COORDENADAS_HABITACIONES: Record<string, [number, number]> = {
  dormitorio: [-33.4485, -70.6695],
  living: [-33.4489, -70.6690],
  cocina: [-33.4492, -70.6693],
  entrada: [-33.4495, -70.6695],
  sala: [-33.4487, -70.6688],
  baño: [-33.4483, -70.6692],
  pasillo: [-33.4490, -70.6691],
  wearable: [-33.4489, -70.6693],
};

// Marcador: círculo con el ícono del tipo de sensor (petróleo = activo, ámbar = sin datos recientes)
function crearIcono(sensor: Sensor) {
  const color = sensor.online ? "#0E5566" : "#9A5B06";
  const svg = renderToStaticMarkup(createElement(iconoTipo(sensor.tipo), { size: 18, color: "#ffffff", strokeWidth: 2.2 }));
  return divIcon({
    html: `<div style="background:${color};width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:2px solid #fff;box-shadow:0 1px 4px rgba(16,38,45,.35)">${svg}</div>`,
    className: "sensor-marker",
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  });
}

export default function MapaHogar({ sensores }: MapaHogarProps) {
  return (
    <div className="mapa-hogar-container">
      <div className="mapa-header">
        <h2>Mapa del hogar</h2>
        <p className="mapa-descripcion">
          Ubicación aproximada de cada sensor. Toque un sensor para ver su última lectura.
        </p>
      </div>

      <div className="mapa-wrapper">
        <MapContainer
          center={HOGAR_CENTRO}
          zoom={19}
          scrollWheelZoom={true}
          style={{ height: "480px", width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Círculo que representa el área del hogar */}
          <Circle
            center={HOGAR_CENTRO}
            radius={30}
            pathOptions={{
              color: "#0E5566",
              fillColor: "#0E5566",
              fillOpacity: 0.1,
              weight: 2,
              dashArray: "5, 5",
            }}
          />

          {/* Marcadores de sensores */}
          {sensores.map((sensor) => {
            const coords =
              COORDENADAS_HABITACIONES[sensor.habitacion] || HOGAR_CENTRO;

            return (
              <Marker
                key={sensor.sensor_id}
                position={coords}
                icon={crearIcono(sensor)}
              >
                <Popup>
                  <div className="popup-sensor">
                    <strong>{nombreTipo(sensor.tipo)}</strong>
                    <p>{nombreHabitacion(sensor.habitacion)}</p>
                    <p>{sensor.online ? "Activo" : "Sin datos recientes"}, última lectura {haceCuanto(sensor.ultima_lectura)}</p>
                    <p className="tenue">{sensor.sensor_id}</p>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>

      {/* Leyenda */}
      <div className="mapa-leyenda">
        <div className="leyenda-item">
          <span className="leyenda-punto online"></span>
          <span>Activo (lectura en la última hora)</span>
        </div>
        <div className="leyenda-item">
          <span className="leyenda-punto offline"></span>
          <span>Sin datos recientes</span>
        </div>
        <div className="leyenda-item">
          <span className="leyenda-circulo"></span>
          <span>Área del hogar</span>
        </div>
      </div>
    </div>
  );
}