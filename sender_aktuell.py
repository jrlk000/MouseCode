class Sender:

    #def __init__(self, start_pin)->None:
    def __init__(self) -> None:
        #self.start_pin = Pin(start_pin, Pin.IN, Pin.PULL_DOWN)
        #pin würd zum aufwachen aus deep-sleep verwendet also beachte RTC
        #priorisiert sind GPIO 32, 33

        #self.ziel_mac_leuchte = b'\xb0\xa6\x04\x07R8' # (string)b0:a6:04:07:52:38 ; (bytes)b'\xb0\xa6\x04\x07R8'(Morse-Code Xiao)
        #self.ziel_mac_kiste = b'\x08\xb6\x1fo.\xe4' # (alte vom WROVER)


        # ---- Antene / ESPNOW ----

        try:
            # 1. AP-Modus sicherheitshalber ausschalten
            wlan_ap = network.WLAN(network.AP_IF)
            wlan_ap.active(False)

            # 2. Station-Modus aktivieren
            wlan_sta = network.WLAN(network.STA_IF)
            wlan_sta.active(True)
            wlan_sta.disconnect()  # Trennen von evtl. alten Router-Verbindungen

            # 3. ESP-NOW starten
            self.esp_now = espnow.ESPNow()
            self.esp_now.active(True)

        except OSError as e:
            print(f"Fehler bei Initialisiereung des Senders {e}.")
            self.deinit_sender()

    def deinit_sender(self):
        try:
            #Deaktivierung

            # ----Wlan----
            wlan_sta = network.WLAN(network.STA_IF)
            wlan_sta.active(False)

            wlan_ap = network.WLAN(network.AP_IF)
            wlan_ap.active(False)

            # ----Esp-now----
            self.esp_now.active(False)

            print("Sender heruntergefahren...")

        except Exception as e:
            print(f"Fehler beim Deinitialisieren des Senders: {e}")



    def _verpacke_nachricht(self, nachricht: str)->str|None:
        """
        Verschlüssele Nachricht in byte-code.
        """
        daten = {"nachricht" : nachricht}
        msg_bytes = json.dumps(daten).encode('utf-8')

        if len(msg_bytes) > espnow.MAX_DATA_LEN:
            print(f"Fehler: Daten zu groß ({len(msg_bytes)} Bytes).")
            return None

        return msg_bytes

    def kontaktiere_empfänger(self, ziel_mac: bytes, msg: str):
        """
        Sendet Daten. Falls der Peer fehlt, wird er automatisch hinzugefügt.
        Fängt Längen- und Existenz-Fehler hardwarenah ab.
        """
        msg_bytes = self._verpacke_nachricht(msg)

        try:
            # 1. Sendeversuch
            self.esp_now.send(ziel_mac, msg_bytes, True)
            print("Erfolg: Nachricht wurde gesendet!")
            return True

        except OSError as err:
            # err.args ist ein Tuple: (Fehlercode, Fehlermeldung)
            if len(err.args) > 1 and err.args[1] == 'ESP_ERR_ESPNOW_NOT_FOUND':
                print("Warnung: Peer war nicht registriert. Füge ihn jetzt hinzu...")

                try:
                    # Peer nachregistrieren
                    self.esp_now.add_peer(ziel_mac)

                    # 2. Sendeversuch
                    self.esp_now.send(ziel_mac, msg_bytes, True)
                    print("Erfolg: Nachricht im zweiten Anlauf gesendet!")
                    return True

                except OSError as add_err:
                    print(f"Kritischer Fehler beim Nachregistrieren: {add_err}")
                    #self.deinit_sender() #DEinitialisieren 2 sek. Dauerfeuer Fehlermeldungen harmlos, lediglich nicht reagieren  des empfängers.
                    return False
            else:
                # Ein ganz anderer Hardware-Fehler (z.B. WLAN aus)
                print(f"Allgemeiner Sende-Fehler: {err}")
                #self.deinit_sender()
                return False