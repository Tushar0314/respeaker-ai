/**
 * LoRa32 Bidirectional Communication with Raspberry Pi 5
 * 
 * Hardware: TTGO LoRa32, Heltec LoRa32, or similar ESP32+LoRa board
 * 
 * Features:
 * - Receive GPS coordinates from Pi5
 * - Send text commands to Pi5 (which will be spoken via TTS)
 * - Display received coordinates on Serial/OLED
 * 
 * Board Settings (Arduino IDE):
 * - Board: "ESP32 Dev Module" or "TTGO LoRa32"
 * - Upload Speed: 115200
 * - CPU Frequency: 240MHz
 */

#include <SPI.h>
#include <LoRa.h>

// LoRa Pin Configuration (adjust based on your board)
// For TTGO LoRa32 V2.1:
#define SCK     5
#define MISO    19
#define MOSI    27
#define SS      18
#define RST     14
#define DIO0    26

// LoRa Frequency (choose one based on your region)
#define LORA_FREQ   915E6  // 915 MHz for North America
// #define LORA_FREQ   868E6  // 868 MHz for Europe
// #define LORA_FREQ   433E6  // 433 MHz for Asia

// Button pins (optional - for sending commands)
#define BUTTON_HOLD     0   // Boot button on most ESP32 boards
#define BUTTON_STOP     12  // Add external button if needed

// Variables
String lastCoordinates = "";
unsigned long lastTransmit = 0;
const unsigned long transmitInterval = 5000; // Send command every 5 seconds

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("╔═══════════════════════════════════════╗");
  Serial.println("║  LoRa32 ↔ Raspberry Pi 5              ║");
  Serial.println("║  Bidirectional Communication          ║");
  Serial.println("╚═══════════════════════════════════════╝");
  Serial.println();
  
  // Initialize button pins
  pinMode(BUTTON_HOLD, INPUT_PULLUP);
  // pinMode(BUTTON_STOP, INPUT_PULLUP);
  
  // Initialize LoRa
  Serial.print("Initializing LoRa...");
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DIO0);
  
  if (!LoRa.begin(LORA_FREQ)) {
    Serial.println(" FAILED!");
    Serial.println("Check wiring and antenna!");
    while (1) {
      delay(1000);
    }
  }
  
  Serial.println(" OK!");
  
  // Configure LoRa parameters for better range
  LoRa.setSpreadingFactor(7);     // 7-12, higher = longer range but slower
  LoRa.setSignalBandwidth(125E3); // 125 kHz
  LoRa.setCodingRate4(5);         // 4/5
  LoRa.setTxPower(20);            // 20 dBm (max power)
  
  Serial.println();
  Serial.println("Configuration:");
  Serial.print("  Frequency: ");
  Serial.print(LORA_FREQ / 1E6);
  Serial.println(" MHz");
  Serial.println("  Spreading Factor: 7");
  Serial.println("  Bandwidth: 125 kHz");
  Serial.println("  TX Power: 20 dBm");
  Serial.println();
  Serial.println("Ready to communicate with Pi5!");
  Serial.println("─────────────────────────────────────");
  Serial.println();
}

void loop() {
  // Check for incoming LoRa packets (GPS coordinates from Pi5)
  receiveCoordinates();
  
  // Check buttons and send commands
  checkButtonsAndSendCommands();
  
  // Auto-send periodic status (optional)
  // sendPeriodicStatus();
  
  delay(10);
}

/**
 * Receive GPS coordinates from Raspberry Pi 5
 */
void receiveCoordinates() {
  int packetSize = LoRa.parsePacket();
  
  if (packetSize) {
    String received = "";
    
    // Read packet
    while (LoRa.available()) {
      received += (char)LoRa.read();
    }
    
    // Get RSSI (signal strength)
    int rssi = LoRa.packetRssi();
    float snr = LoRa.packetSnr();
    
    Serial.println("┌─────────────────────────────────────┐");
    Serial.println("│  RECEIVED FROM PI5                  │");
    Serial.println("└─────────────────────────────────────┘");
    Serial.print("Data: ");
    Serial.println(received);
    Serial.print("RSSI: ");
    Serial.print(rssi);
    Serial.print(" dBm, SNR: ");
    Serial.print(snr);
    Serial.println(" dB");
    
    // Parse coordinates
    parseAndDisplay(received);
    
    Serial.println("─────────────────────────────────────");
    Serial.println();
    
    lastCoordinates = received;
  }
}

/**
 * Parse and display GPS coordinates
 * Formats supported:
 * - CURRENT:37.788250,-122.432400
 * - WP1:37.788250,-122.432400;WP2:37.789,-122.433
 */
void parseAndDisplay(String data) {
  // Check if it's a single coordinate or multiple waypoints
  if (data.indexOf(';') > 0) {
    // Multiple waypoints
    Serial.println("Waypoints received:");
    
    int start = 0;
    int end = 0;
    int wpCount = 0;
    
    while (end != -1) {
      end = data.indexOf(';', start);
      String wp;
      
      if (end == -1) {
        wp = data.substring(start);
      } else {
        wp = data.substring(start, end);
      }
      
      if (wp.length() > 0) {
        wpCount++;
        parseCoordinate(wp, wpCount);
      }
      
      start = end + 1;
    }
    
    Serial.print("Total waypoints: ");
    Serial.println(wpCount);
  } 
  else {
    // Single coordinate
    parseCoordinate(data, 0);
  }
}

/**
 * Parse a single coordinate
 * Format: NAME:lat,lon
 */
void parseCoordinate(String coord, int index) {
  int colonPos = coord.indexOf(':');
  int commaPos = coord.indexOf(',');
  
  if (colonPos > 0 && commaPos > colonPos) {
    String name = coord.substring(0, colonPos);
    String latStr = coord.substring(colonPos + 1, commaPos);
    String lonStr = coord.substring(commaPos + 1);
    
    float lat = latStr.toFloat();
    float lon = lonStr.toFloat();
    
    if (index > 0) {
      Serial.print("  [");
      Serial.print(index);
      Serial.print("] ");
    } else {
      Serial.print("  ");
    }
    
    Serial.print(name);
    Serial.print(": ");
    Serial.print(lat, 6);
    Serial.print(", ");
    Serial.println(lon, 6);
    
    // Here you could:
    // - Display on OLED screen
    // - Store in array for navigation
    // - Calculate distance/bearing
    // - Update map display
  }
}

/**
 * Check button presses and send commands to Pi5
 */
void checkButtonsAndSendCommands() {
  // Check HOLD button (Boot button)
  if (digitalRead(BUTTON_HOLD) == LOW) {
    delay(50); // Debounce
    if (digitalRead(BUTTON_HOLD) == LOW) {
      sendCommand("hold");
      while (digitalRead(BUTTON_HOLD) == LOW) {
        delay(10); // Wait for release
      }
    }
  }
  
  // Add more buttons for other commands
  // if (digitalRead(BUTTON_STOP) == LOW) {
  //   sendCommand("stop");
  //   delay(500);
  // }
}

/**
 * Send a command to Raspberry Pi 5
 * Pi5 will speak this command via text-to-speech
 */
void sendCommand(String command) {
  Serial.println("┌─────────────────────────────────────┐");
  Serial.println("│  SENDING TO PI5                     │");
  Serial.println("└─────────────────────────────────────┘");
  Serial.print("Command: ");
  Serial.println(command);
  
  LoRa.beginPacket();
  LoRa.print(command);
  LoRa.endPacket();
  
  Serial.println("✓ Sent!");
  Serial.println("─────────────────────────────────────");
  Serial.println();
}

/**
 * Send a command with speed control
 */
void sendCommandWithSpeed(String speed, String message) {
  String cmd = "SPEED:" + speed + ":" + message;
  
  Serial.println("┌─────────────────────────────────────┐");
  Serial.println("│  SENDING TO PI5 (with speed)        │");
  Serial.println("└─────────────────────────────────────┘");
  Serial.print("Speed: ");
  Serial.println(speed);
  Serial.print("Message: ");
  Serial.println(message);
  
  LoRa.beginPacket();
  LoRa.print(cmd);
  LoRa.endPacket();
  
  Serial.println("✓ Sent!");
  Serial.println("─────────────────────────────────────");
  Serial.println();
}

/**
 * Send an alert to Pi5
 */
void sendAlert(String alertType, String message) {
  String cmd = "ALERT:" + alertType + ":" + message;
  
  Serial.println("┌─────────────────────────────────────┐");
  Serial.println("│  SENDING ALERT TO PI5               │");
  Serial.println("└─────────────────────────────────────┘");
  Serial.print("Type: ");
  Serial.println(alertType);
  Serial.print("Message: ");
  Serial.println(message);
  
  LoRa.beginPacket();
  LoRa.print(cmd);
  LoRa.endPacket();
  
  Serial.println("✓ Alert sent!");
  Serial.println("─────────────────────────────────────");
  Serial.println();
}

/**
 * Send periodic status updates (optional)
 */
void sendPeriodicStatus() {
  unsigned long now = millis();
  
  if (now - lastTransmit > transmitInterval) {
    lastTransmit = now;
    
    // Example: Send battery status
    // float voltage = readBatteryVoltage();
    // String status = "Battery: " + String(voltage, 2) + "V";
    // sendCommand(status);
    
    // Or send a simple heartbeat
    sendCommand("System OK");
  }
}

/**
 * Example: Read battery voltage (if available on your board)
 */
float readBatteryVoltage() {
  // TTGO LoRa32 has battery voltage on pin 35
  int raw = analogRead(35);
  float voltage = (raw / 4095.0) * 2.0 * 3.3 * 1.1; // Adjust for your board
  return voltage;
}

/**
 * Example command menu via Serial (for testing)
 * Type commands in Serial Monitor to send to Pi5
 */
void serialCommandMenu() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd.length() > 0) {
      if (cmd.startsWith("ALERT:")) {
        // Parse: ALERT:Warning:Message
        int firstColon = cmd.indexOf(':');
        int secondColon = cmd.indexOf(':', firstColon + 1);
        
        if (secondColon > 0) {
          String type = cmd.substring(firstColon + 1, secondColon);
          String msg = cmd.substring(secondColon + 1);
          sendAlert(type, msg);
        }
      }
      else if (cmd.startsWith("SPEED:")) {
        // Parse: SPEED:slow:Message
        int firstColon = cmd.indexOf(':');
        int secondColon = cmd.indexOf(':', firstColon + 1);
        
        if (secondColon > 0) {
          String speed = cmd.substring(firstColon + 1, secondColon);
          String msg = cmd.substring(secondColon + 1);
          sendCommandWithSpeed(speed, msg);
        }
      }
      else {
        // Simple command
        sendCommand(cmd);
      }
    }
  }
}

/**
 * Uncomment this in loop() for Serial command testing:
 * serialCommandMenu();
 */
