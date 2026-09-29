import machine
from morse_code import MorseCode
from empfanger import Empfanger

"""
Main der Leuchten Interaktion. 

Beachte bei Datenübermittlung: 

Rythmus empfänger x:wach , y:schlafen

|----     |
|    ----|

Sender einmaliges Senden muss mindestens (x+y+c) sein 
|       -----------
|-------           ---------|

Eingestellte Werte:
x = 1.8 sek. (Empfänger)
y = 0.15 sek.

x+y+c = 2.2 sek. (Sender)
"""

# ---- Kommunikations Konfiguration Empfänger----
EMPFANGS_ZEITRAUM = 150  # [ms]
EMPFANGS_PAUSE = 1800  # [ms]


def main() -> None:
    print("ESP32 Wake-Up Routine gestartet ---")

    try:
        empfänger = Empfanger()
        morse_code = MorseCode()

    except OSError as e:
        print(f"Fehler bei der Initialisierung des Empfängers: {e}")
        print("Gehe in 5 Minuten Sicherheits-Schlaf...")
        machine.deepsleep(300000)  # 5 Minuten interner Schlaf als Notfall-Lösung

    # Prüfen, ob wir uns gerade innerhalb des Fensters befinden (Kaltstrat durch Zeitlimitierung des Schlafmoduses)
    """
    Anforderung soll sein, dass sdas System mehrfach von einer Gruppe wieder aufgefahren werden soll (Mehrfachinteraktion).
    Das Zeitfenster der Interaktion soll sogegeben sein, dass die Interaktion nach einem gegebenen Zeitintervall (automatisch abgebrochen) werden. 
    Die Interaktion muss auch von (verschiedenen Gruppen über den Tag) verwendet werden könne ohne das der MIkrokontroller vom Strom genommen wird.
    """
    print(">>> ESP im Aktivmodus. Warte auf Signale...")
    # Starte Empfangen von Signalen
    empfänger.aktiviere_empfänger()
    morse_code = MorseCode

    # Empfänger wartet auf Signal spezifisch an ihn addressiert von einem beliebigen Addressat.
    while True:
        msg = empfänger.lauschen()

        if msg:
            # Starte die Ansteuerung des Linearaktuators
            morse_code.play_morse_code()

        # Gehe in Stromsparenden Modus
        machine.lightsleep(EMPFANGS_PAUSE)

    # Momentan noch unsauberes killen des Mikrokontrollers über die Zeitschaltuhr.
    # empfänger.deinit_empfänger()
    """
    Falls das zu Problemen führen sollte gäbe es folgende weiter Vorgänge: 
    -wechsel zum Zeitmodul

    -parallelschalten eines Kondensators, der den 
    Deinitialisierungsprozess einleitet über RTC-Pin Signal und die 
    Bestromung des ESP für den Vorgang ermöglicht.
    (Kondensator musst genügend Groß sein, um den Strombedarf für dieses Zeitintervall zu decken. )  
    """
    # enter_deep_sleep()

if __name__ == "__main__":
    main()