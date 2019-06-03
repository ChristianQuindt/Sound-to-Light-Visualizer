#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <Hash.h>
#include <WiFiUdp.h>
#include <NeoPixelBus.h>

// number of LEDs
#define NUM_LEDS 150
#define BUFFER_LEN 1024

//NeoPixelBus settings
const uint8_t PixelPin = 9;  // make sure to set this to the correct pin

// Wifi and socket settings
const char* ssid     = "Schrödingers Wlan";
const char* password = "13572468";
unsigned int localPort = 7777;
char packetBuffer[BUFFER_LEN];

// LED strip
NeoPixelBus<NeoGrbFeature, Neo800KbpsMethod> ledstrip(NUM_LEDS, PixelPin);

WiFiUDP port;

// Network information
// IP must match the IP in config.py
IPAddress ip(192, 168, 0, 150);
// Set gateway
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

void setup() {
    Serial.begin(115200);
    WiFi.config(ip, gateway, subnet);
    WiFi.begin(ssid, password);
    Serial.println("");
    // Connect to wifi and print the IP address over serial
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");
    Serial.print("Connected to ");
    Serial.println(ssid);
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    
    port.begin(localPort);
    ledstrip.Begin();//Begin output
    ledstrip.Show();//Clear the strip for use
}

uint8_t N = 0;

void loop() {
    int packetSize = port.parsePacket();
    // If packets have been received, interpret the command
    if (packetSize) {
        int len = port.read(packetBuffer, BUFFER_LEN);
        for(int i = 0; i < len; i+=4) {
            packetBuffer[len] = 0;
            N = packetBuffer[i];
            RgbColor pixel((uint8_t)packetBuffer[i+1], (uint8_t)packetBuffer[i+2], (uint8_t)packetBuffer[i+3]);
            ledstrip.SetPixelColor(N, pixel);
        } 
        ledstrip.Show();
    }
}
