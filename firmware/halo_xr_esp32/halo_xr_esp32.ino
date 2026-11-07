/* HALO-XR · firmware ESP32 + PAJ7620U2
 * Mengirim nama gestur sebagai teks (diakhiri '\n') lewat BLE Nordic UART Service.
 * Aplikasi web (Web Bluetooth) memetakan: UP DOWN LEFT RIGHT FORWARD BACKWARD CW CCW WAVE.
 *
 * Library: "RevEng PAJ7620" (Library Manager). Board: ESP32 Dev Module (core arduino-esp32 ≥ 2.x).
 * Kabel I2C: PAJ7620 SDA→GPIO21, SCL→GPIO22, VCC→3V3, GND→GND.
 * Catatan: sketsa ini belum diuji pada perangkat fisik, jadi cek orientasi sensor dan sesuaikan peta arahnya.
 */
#include <Wire.h>
#include <RevEng_PAJ7620.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLE2902.h>

#define NUS_SERVICE "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
#define NUS_TX      "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

RevEng_PAJ7620 sensor;
BLECharacteristic *tx;
volatile bool connected = false;

class Cb : public BLEServerCallbacks {
  void onConnect(BLEServer *) override { connected = true; }
  void onDisconnect(BLEServer *s) override { connected = false; s->getAdvertising()->start(); }
};

void send(const char *g) {
  Serial.println(g);
  if (!connected) return;
  String msg = String(g) + "\n";
  tx->setValue((uint8_t *)msg.c_str(), msg.length());
  tx->notify();
}

void setup() {
  Serial.begin(115200);
  if (!sensor.begin()) { Serial.println("PAJ7620 tidak terdeteksi"); while (true) delay(1000); }
  sensor.setGestureEntryTime(0);   // respons secepat mungkin (target latensi < 150 ms)
  sensor.setGestureExitTime(100);

  BLEDevice::init("HALO-XR");
  BLEServer *srv = BLEDevice::createServer();
  srv->setCallbacks(new Cb());
  BLEService *svc = srv->createService(NUS_SERVICE);
  tx = svc->createCharacteristic(NUS_TX, BLECharacteristic::PROPERTY_NOTIFY);
  tx->addDescriptor(new BLE2902());
  svc->start();
  BLEAdvertising *adv = BLEDevice::getAdvertising();
  adv->addServiceUUID(NUS_SERVICE);
  adv->start();
  Serial.println("HALO-XR siap, menunggu koneksi BLE");
}

void loop() {
  switch (sensor.readGesture()) {
    case GES_UP:            send("UP"); break;
    case GES_DOWN:          send("DOWN"); break;
    case GES_LEFT:          send("LEFT"); break;
    case GES_RIGHT:         send("RIGHT"); break;
    case GES_FORWARD:       send("FORWARD"); break;
    case GES_BACKWARD:      send("BACKWARD"); break;
    case GES_CLOCKWISE:     send("CW"); break;
    case GES_ANTICLOCKWISE: send("CCW"); break;
    case GES_WAVE:          send("WAVE"); break;
    default: break;
  }
  delay(20);
}
