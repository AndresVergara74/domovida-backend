// src/LoginCuidador.tsx
// Ventana de inicio de sesión del cuidador (PS-01, parte 2).
import { useState } from "react";
import { LogIn, X } from "lucide-react";
import { iniciarSesion, type Sesion } from "./auth";

interface Props {
  onExito: (sesion: Sesion) => void;
  onCancelar: () => void;
}

export default function LoginCuidador({ onExito, onCancelar }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  async function enviar(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setEnviando(true);
    try {
      const sesion = await iniciarSesion(email.trim(), password);
      setPassword("");
      onExito(sesion);
    } catch (err) {
      setError(err instanceof Error ? err.message : "No se pudo iniciar sesión");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="login-overlay" role="dialog" aria-modal="true" aria-labelledby="login-titulo">
      <form className="login-caja" onSubmit={enviar}>
        <button type="button" className="login-cerrar" onClick={onCancelar} aria-label="Cerrar">
          <X size={18} />
        </button>
        <h2 id="login-titulo">Acceso del cuidador</h2>
        <p className="login-ayuda">Inicie sesión para ver el estado del hogar y atender alertas.</p>

        <label htmlFor="login-email">Correo</label>
        <input
          id="login-email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoFocus
        />

        <label htmlFor="login-password">Contraseña</label>
        <input
          id="login-password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && <p className="login-error" role="alert">{error}</p>}

        <button type="submit" className="login-enviar" disabled={enviando}>
          <LogIn size={18} />
          {enviando ? "Ingresando..." : "Ingresar"}
        </button>
      </form>
    </div>
  );
}
