// src/MapaHogar.tsx
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import { divIcon } from "leaflet";
import "leaflet/dist/leaflet.css";

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

// Icono personalizado según estado del sensor
function crearIcono(sensor: Sensor) {
  const color = sensor.online ? "#10b981" : "#ef4444";
  const icono = obtenerEmojiPorTipo(sensor.tipo);

  return divIcon({
    html: `
      <div style="
        background: ${color};
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 3px solid white;
      ">
        ${icono}
      </div>
    `,
    className: "sensor-marker",
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });
}

function obtenerEmojiPorTipo(tipo: string): string {
  const emojis: Record<string, string> = {
    pir: "🚶",
    acelerometro: "📳",
    gas: "💨",
    humo: "🔥",
    apertura: "🚪",
    cardiovascular: "❤️",
    boton_panico: "🚨",
  };
  return emojis[tipo] || "📡";
}

export default function MapaHogar({ sensores }: MapaHogarProps) {
  return (
    <div className="mapa-hogar-container">
      <div className="mapa-header">
        <h3>📍 Ubicación de sensores en el hogar</h3>
        <p className="mapa-descripcion">
          Vista satelital del hogar con la ubicación de cada sensor IoT.
          Los sensores <span className="punto-verde">● verdes</span> están online
          y los <span className="punto-rojo">● rojos</span> offline.
        </p>
      </div>

      <div className="mapa-wrapper">
        <MapContainer
          center={HOGAR_CENTRO}
          zoom={19}
          scrollWheelZoom={true}
          style={{ height: "500px", width: "100%", borderRadius: "16px" }}
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
              color: "#10b981",
              fillColor: "#10b981",
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
                    <h4>{sensor.sensor_id}</h4>
                    <p>
                      <strong>Tipo:</strong> {sensor.tipo}
                    </p>
                    <p>
                      <strong>Habitación:</strong> {sensor.habitacion}
                    </p>
                    <p>
                      <strong>Estado:</strong>{" "}
                      {sensor.online ? "✅ Online" : "⚠️ Inactivo"}
                    </p>
                    <p>
                      <strong>Última lectura:</strong>{" "}
                      {new Date(sensor.ultima_lectura).toLocaleTimeString("es-CL")}
                    </p>
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
          <span>Sensor online</span>
        </div>
        <div className="leyenda-item">
          <span className="leyenda-punto offline"></span>
          <span>Sensor offline</span>
        </div>
        <div className="leyenda-item">
          <span className="leyenda-circulo"></span>
          <span>Área del hogar</span>
        </div>
      </div>
    </div>
  );
}