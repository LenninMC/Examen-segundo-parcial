import socket
import serial
import threading
import time

# --- CONFIGURACIÓN ---
SERIAL_PORT = "/dev/ttyACM0"   # Ajusta según tu sistema (ej. COM3 en Windows)
BAUDRATE    = 115200
HOST = "0.0.0.0"
PORT = 5001
# ----------------------

ultima_temp = 0.0
ultima_zona = 1
ultima_velocidad = 0
lock = threading.Lock()

def leer_serial(ser):
    """Hilo que lee continuamente del serial y actualiza los valores."""
    global ultima_temp, ultima_zona, ultima_velocidad
    while True:
        try:
            linea = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Serial: {linea}")  # Debug
            
            if linea.startswith("TEMP:") and ",ZONA:" in linea:
                # Formato: "TEMP:25.5,ZONA:2,VEL:170"
                partes = linea.split(",")
                temp_parte = partes[0]  # "TEMP:25.5"
                zona_parte = partes[1]   # "ZONA:2"
                vel_parte = partes[2]    # "VEL:170"
                
                with lock:
                    ultima_temp = float(temp_parte[5:])
                    ultima_zona = int(zona_parte[5:])
                    ultima_velocidad = int(vel_parte[4:])
                    
                print(f"Actualizado - Temp: {ultima_temp}°C, Zona: {ultima_zona}, Vel: {ultima_velocidad}")
                    
        except Exception as e:
            print(f"Error serial: {e}")
            time.sleep(0.1)

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=0.5)
        print(f"Conectado a Arduino en {SERIAL_PORT} a {BAUDRATE} baudios")
    except Exception as e:
        print(f"Error al abrir puerto: {e}")
        return

    # Iniciar hilo de lectura serial
    hilo = threading.Thread(target=leer_serial, args=(ser,), daemon=True)
    hilo.start()

    # Crear socket TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"Servidor TCP escuchando en {HOST}:{PORT}...")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Conexión desde {addr}")
                data = conn.recv(1024)
                if not data:
                    continue

                cmd = data.decode("utf-8", errors="ignore").strip().upper()

                if cmd == "GET_STATE":
                    with lock:
                        respuesta = f"TEMP:{ultima_temp},ZONA:{ultima_zona},VEL:{ultima_velocidad}"
                    conn.sendall((respuesta + "\n").encode("utf-8"))
                else:
                    conn.sendall(b"ERR:CMD\n")

if __name__ == "__main__":
    main()
