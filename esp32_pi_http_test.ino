/**
 * ESP32 HTTP Test - Find and connect to Raspberry Pi Command Server
 * 
 * This sketch:
 * 1. Connects to WiFi
 * 2. Tries to reach the Pi at 172.19.135.159:5000
 * 3. Sends an HTTP POST command
 * 4. Shows the exact HTTP response code
 * 
 * Arduino IDE Board: ESP32 Dev Module
 * Upload Speed: 115200
 */

#include <WiFi.h>
#include <HTTPClient.h>

// WiFi credentials - CHANGE THESE
const char* ssid = "YOUR_SSID";           // Your WiFi network name
const char* password = "YOUR_PASSWORD";   // Your WiFi password

// Pi settings - Try these IPs in order
const char* pi_ips[] = {
  "172.19.135.159",    // The correct one (from your photo)
  "192.168.1.1",       // Fallback
  "10.0.0.1"           // Fallback
};
const int pi_port = 5000;
const char* pi_path = "/command";

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n╔════════════════════════════════════╗");
  Serial.println("║  ESP32 → Pi HTTP Connection Test  ║");
  Serial.println("╚════════════════════════════════════╝\n");
  
  // Connect to WiFi
  connectToWiFi();
  
  // Try to reach Pi
  testPiConnection();
  
  Serial.println("\n✓ Test complete. Check results above.");
}

void loop() {
  // Optional: Send a test command every 10 seconds
  delay(10000);
  sendTestCommand();
}

void connectToWiFi() {
  Serial.print("[WiFi] Connecting to: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("   IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("   RSSI: ");
    Serial.println(WiFi.RSSI());
  } else {
    Serial.println("\n❌ WiFi connection failed!");
    return;
  }
}

void testPiConnection() {
  Serial.println("\n[Attempting to reach Pi...]\n");
  
  for (int i = 0; i < 3; i++) {
    const char* pi_ip = pi_ips[i];
    
    Serial.print("Try ");
    Serial.print(i + 1);
    Serial.print("/3: ");
    Serial.print(pi_ip);
    Serial.print(":");
    Serial.print(pi_port);
    Serial.println(pi_path);
    
    String url = String("http://") + pi_ip + ":" + pi_port + pi_path;
    
    HTTPClient http;
    http.setConnectTimeout(3000);  // 3 second timeout
    http.setTimeout(3000);
    
    int httpCode = -1;
    
    if (http.begin(url)) {
      Serial.print("  Sending POST... ");
      httpCode = http.POST("hold");  // Send test command
      
      if (httpCode > 0) {
        Serial.print("HTTP ");
        Serial.println(httpCode);
        
        if (httpCode == 200 || httpCode == 201) {
          Serial.println("  ✅ SUCCESS! Pi is reachable!");
          Serial.print("  Response: ");
          Serial.println(http.getString());
          http.end();
          return;  // Success, stop trying
        } else {
          Serial.print("  Response: ");
          Serial.println(http.getString());
        }
      } else {
        Serial.print("HTTP ");
        Serial.println(httpCode);
        Serial.print("  ❌ Error: ");
        Serial.println(http.errorToString(httpCode));
      }
      
      http.end();
    } else {
      Serial.println("  ❌ Could not begin HTTP connection");
    }
    
    Serial.println();
    delay(1000);
  }
  
  Serial.println("❌ Pi not reachable at any IP!");
  Serial.println("\nTroubleshooting:");
  Serial.println("  1. Verify WiFi SSID/password above");
  Serial.println("  2. Check Pi is on same WiFi network");
  Serial.println("  3. Verify Pi IP: 172.19.135.159 (from your photo)");
  Serial.println("  4. Verify Pi command server running: python3 pi_command_server.py");
  Serial.println("  5. Check firewall not blocking port 5000");
}

void sendTestCommand() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected!");
    return;
  }
  
  const char* pi_ip = "172.19.135.159";  // Use correct IP from your photo
  String url = String("http://") + pi_ip + ":" + pi_port + pi_path;
  
  HTTPClient http;
  http.setConnectTimeout(3000);
  http.setTimeout(3000);
  
  if (http.begin(url)) {
    int httpCode = http.POST("test command");
    
    Serial.print("[");
    Serial.print(millis() / 1000);
    Serial.print("s] POST to ");
    Serial.print(pi_ip);
    Serial.print(" → HTTP ");
    Serial.println(httpCode);
    
    if (httpCode > 0) {
      String response = http.getString();
      if (response.length() > 0) {
        Serial.print("    Response: ");
        Serial.println(response);
      }
    }
    
    http.end();
  }
}
