// src/Consentimiento.tsx
import { useState } from "react";
import { Shield, FileText, Lock, UserCheck, AlertTriangle, X } from "lucide-react";

interface ConsentimientoProps {
  onAceptar: () => void;
  onRechazar: () => void;
}

export default function Consentimiento({ onAceptar, onRechazar }: ConsentimientoProps) {
  const [nombre, setNombre] = useState("");
  const [rut, setRut] = useState("");
  const [checkLeido, setCheckLeido] = useState(false);
  const [checkAcepto, setCheckAcepto] = useState(false);

  const puedeAceptar =
    nombre.trim().length > 3 &&
    rut.trim().length > 7 &&
    checkLeido &&
    checkAcepto;

  function handleAceptar() {
    if (!puedeAceptar) return;

    // Guardar en localStorage (seudonimizado: solo iniciales + timestamp)
    const registro = {
      iniciales: nombre.trim().split(" ").map((p) => p[0]).join("").toUpperCase(),
      rutHash: btoa(rut.trim()).slice(0, 12), // hash simple (seudonimización)
      fecha: new Date().toISOString(),
      version: "1.0",
    };
    localStorage.setItem("domovida-consentimiento", JSON.stringify(registro));

    onAceptar();
  }

  return (
    <div className="modal-overlay">
      <div className="modal-consentimiento">
        {/* Header del modal */}
        <div className="modal-header">
          <div className="modal-header-titulo">
            <Shield size={28} />
            <div>
              <h2>Consentimiento Informado</h2>
              <p>Ley N° 21.719 · Protección de Datos Personales</p>
            </div>
          </div>
        </div>

        {/* Cuerpo del modal */}
        <div className="modal-body">
          <div className="consentimiento-intro">
            <FileText size={20} />
            <p>
              Antes de activar el monitoreo de <strong>DomoVida</strong>, necesitamos
              tu consentimiento explícito e informado. Lee con atención.
            </p>
          </div>

          {/* Secciones del consentimiento */}
          <div className="consentimiento-secciones">
            <div className="consentimiento-seccion">
              <h3>
                <Shield size={16} /> ¿Qué es DomoVida?
              </h3>
              <p>
                Sistema de monitoreo domiciliario <strong>no invasivo</strong> que usa
                sensores ambientales y biomédicos para detectar eventos críticos
                (caídas, fugas de gas, incendios, inactividad). <strong>NO usa cámaras
                de video</strong> ni captura imágenes.
              </p>
            </div>

            <div className="consentimiento-seccion">
              <h3>
                <Lock size={16} /> ¿Qué datos recolecta?
              </h3>
              <ul>
                <li>Movimiento (PIR) en habitaciones</li>
                <li>Apertura de puertas y ventanas</li>
                <li>Nivel de gas y humo (ppm)</li>
                <li>Aceleración (detección de caídas)</li>
                <li>Frecuencia cardíaca (solo con wearable)</li>
              </ul>
              <p className="nota">
                Los datos son <strong>seudonimizados</strong>: no se almacena nombre,
                RUT ni datos de identificación personal en la base operativa.
              </p>
            </div>

            <div className="consentimiento-seccion">
              <h3>
                <UserCheck size={16} /> Tus derechos
              </h3>
              <ul>
                <li>Acceder a tus datos en cualquier momento</li>
                <li>Rectificar datos incorrectos</li>
                <li>Eliminar tus datos (derecho al olvido)</li>
                <li>Revocar el consentimiento sin justificación</li>
                <li>Presentar reclamos ante la Agencia de Protección de Datos</li>
              </ul>
            </div>

            <div className="consentimiento-seccion advertencia">
              <h3>
                <AlertTriangle size={16} /> Importante
              </h3>
              <p>
                <strong>DomoVida NO reemplaza la atención médica profesional.</strong> Es
                una herramienta de apoyo y prevención. En caso de emergencia, llama
                siempre a los servicios de urgencia (131 SAMU, 132 Bomberos).
              </p>
            </div>
          </div>

          {/* Formulario */}
          <div className="consentimiento-formulario">
            <h3>Datos del usuario</h3>

            <div className="form-group">
              <label>Nombre completo *</label>
              <input
                type="text"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                placeholder="Ej: María González Pérez"
              />
            </div>

            <div className="form-group">
              <label>RUT *</label>
              <input
                type="text"
                value={rut}
                onChange={(e) => setRut(e.target.value)}
                placeholder="Ej: 12.345.678-9"
              />
              <span className="nota-campo">
                El RUT se almacena como hash (seudonimizado), nunca en texto plano.
              </span>
            </div>
          </div>

          {/* Checkboxes */}
          <div className="consentimiento-checks">
            <label className="check-item">
              <input
                type="checkbox"
                checked={checkLeido}
                onChange={(e) => setCheckLeido(e.target.checked)}
              />
              <span>
                He leído y comprendido el presente Consentimiento Informado.
              </span>
            </label>

            <label className="check-item">
              <input
                type="checkbox"
                checked={checkAcepto}
                onChange={(e) => setCheckAcepto(e.target.checked)}
              />
              <span>
                Acepto voluntariamente que DomoVida monitoree mi hogar y autorizo el
                tratamiento de mis datos según lo descrito.
              </span>
            </label>
          </div>
        </div>

        {/* Footer con botones */}
        <div className="modal-footer">
          <button className="btn-rechazar" onClick={onRechazar}>
            <X size={16} /> Rechazar
          </button>
          <button
            className="btn-aceptar"
            onClick={handleAceptar}
            disabled={!puedeAceptar}
          >
            <UserCheck size={16} /> Acepto y activo el monitoreo
          </button>
        </div>
      </div>
    </div>
  );
}