"""
Script de prueba para el WebSocket de DomoVida.

Se conecta al endpoint ws://localhost:8000/api/ws/alertas
y muestra los mensajes recibidos en tiempo real.

Escucha indefinidamente hasta que se presione Ctrl+C.
"""

import asyncio
import websockets
import json
from datetime import datetime


async def probar_websocket():
    """Prueba la conexión al WebSocket de DomoVida."""
    
    uri = "ws://localhost:8000/api/ws/alertas"
    
    print("=" * 60)
    print("🧪 PRUEBA DE WEBSOCKET - DOMOVIDA")
    print("=" * 60)
    print(f"📡 Conectando a: {uri}")
    print()
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Conectado al WebSocket")
            print()
            
            # Recibir mensaje de bienvenida
            mensaje_bienvenida = await websocket.recv()
            print(f"📩 Mensaje de bienvenida:")
            print(f"   {mensaje_bienvenida}")
            print()
            
            # Enviar ping
            print("📤 Enviando 'ping'...")
            await websocket.send("ping")
            
            # Recibir pong
            respuesta = await websocket.recv()
            print(f"📩 Respuesta:")
            print(f"   {respuesta}")
            print()
            
            # Escuchar mensajes INDEFINIDAMENTE
            print("⏳ Escuchando alertas en tiempo real...")
            print("   (Presiona Ctrl+C para detener)")
            print("=" * 60)
            print()
            
            contador = 0
            while True:
                try:
                    # Esperar mensaje (sin timeout)
                    mensaje = await websocket.recv()
                    contador += 1
                    
                    hora_actual = datetime.now().strftime("%H:%M:%S")
                    
                    # Parsear el mensaje
                    try:
                        data = json.loads(mensaje)
                        tipo = data.get("tipo", "desconocido")
                        
                        if tipo == "alerta":
                            print(f"\n🚨 [{hora_actual}] ALERTA #{contador} RECIBIDA:")
                            print(f"   {json.dumps(data, indent=2, ensure_ascii=False)}")
                            print()
                        elif tipo == "pong":
                            print(f"🏓 [{hora_actual}] Pong recibido")
                        else:
                            print(f"📩 [{hora_actual}] Mensaje ({tipo}): {mensaje[:100]}")
                    
                    except json.JSONDecodeError:
                        print(f"📩 [{hora_actual}] Mensaje (texto plano): {mensaje[:100]}")

                except websockets.exceptions.ConnectionClosed:
                    print("❌ Conexión cerrada por el servidor")
                    break

    except KeyboardInterrupt:
        print("\n\n🛑 Prueba detenida por el usuario (Ctrl+C)")
        print("✅ Prueba completada exitosamente")
    except ConnectionRefusedError:
        print("❌ Error: No se pudo conectar al WebSocket")
        print("   ¿Está corriendo el backend en http://localhost:8000?")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(probar_websocket())
    except KeyboardInterrupt:
        print("\n\n🛑 Programa terminado")