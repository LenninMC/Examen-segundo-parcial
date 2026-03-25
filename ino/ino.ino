// ============================================
// EXAMEN INTEGRADOR - PUENTE H + MOTOR + SENSOR DE TEMPERATURA
// ============================================

// Pines para el puente H (L298N)
const int PIN_IN1 = 9;
const int PIN_IN2 = 10;
const int PIN_ENA = 5;  // PWM para velocidad

// Pin para el sensor de temperatura (LM35)
const int PIN_TEMPERATURA = A0;

// Rangos definidos según temperatura (°C)
// Zona 1: Temperatura BAJA (< 20°C) -> Motor apagado
// Zona 2: Temperatura MEDIA (20°C - 35°C) -> Motor velocidad media
// Zona 3: Temperatura ALTA (> 35°C) -> Motor velocidad máxima

const float ZONA_1_MAX = 20.0;      // Menos de 20°C -> apagado
const float ZONA_2_MAX = 35.0;      // 20°C a 35°C -> velocidad media
const float ZONA_3_MAX = 100.0;     // Más de 35°C -> velocidad máxima

// Velocidades PWM (0-255)
const int VELOCIDAD_APAGADO = 0;
const int VELOCIDAD_MEDIA = 170;     // 66% aprox
const int VELOCIDAD_ALTA = 255;      // 100%

float temperatura = 0;
int velocidadActual = 0;
int zonaActual = 1;
unsigned long lastSend = 0;
const unsigned long INTERVALO = 500;  // ms entre lecturas

// Nombres de las zonas para mostrar
const char* nombresZonas[] = {"Temperatura Baja", "Temperatura Media", "Temperatura Alta"};

void setup() {
  // Configurar pines del puente H
  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_ENA, OUTPUT);
  
  // Configurar dirección del motor (IN1=HIGH, IN2=LOW)
  digitalWrite(PIN_IN1, HIGH);
  digitalWrite(PIN_IN2, LOW);
  
  // Iniciar motor apagado
  analogWrite(PIN_ENA, VELOCIDAD_APAGADO);
  
  Serial.begin(115200);
  Serial.println("Sistema iniciado - Sensor de temperatura LM35");
}

void loop() {
  if (millis() - lastSend >= INTERVALO) {
    lastSend = millis();
    
    // Leer sensor de temperatura LM35
    // Fórmula: Temperatura (°C) = (voltaje * 100)
    // Voltaje = (analogRead * 5.0) / 1023.0
    int lectura = analogRead(PIN_TEMPERATURA);
    temperatura = (lectura * 5.0 / 1023.0) * 100.0;
    
    // Determinar zona y velocidad según temperatura
    if (temperatura <= ZONA_1_MAX) {
      // Temperatura baja -> motor apagado
      zonaActual = 1;
      velocidadActual = VELOCIDAD_APAGADO;
    }
    else if (temperatura <= ZONA_2_MAX) {
      // Temperatura media -> motor velocidad media
      zonaActual = 2;
      velocidadActual = VELOCIDAD_MEDIA;
    }
    else {
      // Temperatura alta -> motor velocidad máxima
      zonaActual = 3;
      velocidadActual = VELOCIDAD_ALTA;
    }
    
    // Aplicar velocidad al motor
    analogWrite(PIN_ENA, velocidadActual);
    
    // Enviar datos por serial (formato: TEMP:25.5,ZONA:2,VEL:170)
    Serial.print("TEMP:");
    Serial.print(temperatura);
    Serial.print(",ZONA:");
    Serial.print(zonaActual);
    Serial.print(",VEL:");
    Serial.println(velocidadActual);
    
    // Debug por serial (opcional)
    Serial.print("  -> Temperatura: ");
    Serial.print(temperatura);
    Serial.print("°C | Estado: ");
    Serial.print(nombresZonas[zonaActual-1]);
    Serial.print(" | Velocidad: ");
    Serial.println(velocidadActual);
  }
  
  // Procesar comandos entrantes
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd == "GET_STATE") {
      Serial.print("TEMP:");
      Serial.print(temperatura);
      Serial.print(",ZONA:");
      Serial.print(zonaActual);
      Serial.print(",VEL:");
      Serial.println(velocidadActual);
    }
    else {
      Serial.println("ERR:CMD");
    }
  }
}
