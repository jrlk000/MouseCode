"""
Plannung: Mouse Code


Mouse Code auf Mastleuchte Rahmenbedingungen:

-230V Spannungsversorgung (Batterie überhaupt möglich?)

Fragen:
-Technologie für die Aktivierung (ESP-now, Anrufen?), gewünschte mindest Entfernung für die Aktivierung
-Stromversorgung (Batterie, Strom in der Nähe)
-Solid State Relay (SSR / MOSFET-Basis) (Informieren über Funktionsweise Modellen etc.)


Ideen:
-Sender(Schlüssel) Empfänger(an Mastleuchte plaziert) Idee per ESP Kommunikation (integrieren mit Anruf?)
-Direkte Ansteuerung der Lampe per Relais oder Mosfet Transistor um Mouse Code über den Empfänger laufen zu lassen

Komponenten:
Solid State Relay (SSR / MOSFET-Basis) (Halbleiterrelais)

Zu beachten im Mikro-Python Code:
1. Non-Blocking Code (Nicht-blockierendes Programmieren)

    Was es ist: Der Verzicht auf time.sleep(). Wenn dein Programm "schläft", ist es taub für die Außenwelt (z.B. für einen Not-Aus-Taster).

    Was du stattdessen nutzt: time.ticks_ms() und time.ticks_diff(). Du baust eine Schleife, die ständig läuft und nur prüft: "Ist schon genug Zeit vergangen, um die nächste Aktion auszuführen?"

2. State Machines (Zustandsautomaten)

    Was es ist: Eine Art, dein Programm zu strukturieren. Anstatt Code stur von oben nach unten ablaufen zu lassen, definierst du "Zustände" (z.B. ZUSTAND_AUS, ZUSTAND_PULS_AN, ZUSTAND_FEHLER).

    Warum es hilft: Dein Code weiß immer genau, in welcher Phase er sich befindet und was als Nächstes zu tun ist, ohne dass er an einer Stelle stehen bleiben muss.

3. Hardware-Timer (machine.Timer)

    Was es ist: Ein Baustein im Mikrocontroller, der unabhängig vom Python-Code die Zeit misst und in exakten Abständen Funktionen (Callbacks) aufrufen kann.

    Warum es wichtig ist: Wenn du z.B. exakt alle 100 Millisekunden ein Signal brauchst, macht der Hardware-Timer das viel präziser als eine normale Python-Schleife.

4. Interrupts / IRQs (Hardware-Unterbrechungen)

    Was es ist: Ein Pin (z.B. für einen Taster) überwacht selbstständig, ob er gedrückt wird. Wenn ja, unterbricht er das laufende Programm sofort und führt eine Notfall-Funktion aus (die "Interrupt Service Routine" oder ISR).

    Wichtige Regel: In einer ISR darf man keine langen Berechnungen machen und (in MicroPython) am besten kein print() verwenden. Man setzt dort meistens nur eine Variable (ein "Flag"), z.B. not_aus_gedrueckt = True.

5. Garbage Collection (Die automatische Müllabfuhr)

    Was es ist: MicroPython räumt im Hintergrund immer wieder den Arbeitsspeicher auf. Das dauert ein paar Millisekunden.

    Die Gefahr: Wenn die Müllabfuhr genau in dem Moment anspringt, in dem du einen zeitkritischen Impuls senden willst, ruckelt dein Signal.

    Die Lösung: Man kann die Garbage Collection manuell zu Zeitpunkten anstoßen, wo es gerade nicht stört (mit import gc und gc.collect()).

6. Watchdog Timer (WDT)

    Was es ist: Ein elektronischer Wachhund im Chip. Du musst ihm im Code regelmäßig sagen: "Alles okay, ich laufe noch!" (das nennt man den Watchdog füttern).

    Warum du ihn brauchst: Wenn dein Programm sich in einer Endlosschleife aufhängt und den Hund nicht mehr füttert, löst dieser nach z.B. 2 Sekunden einen harten Hardware-Neustart aus. So bleibt ein Relais nie aus Versehen dauerhaft an.

7. Exception Handling (Fehler abfangen)

    Was es ist: Die Benutzung von try... except... finally Blöcken.

    Warum es wichtig ist: Wenn du in Python z.B. versehentlich durch Null teilst, stürzt das Programm ab. Mit einem finally-Block am Ende deines Codes stellst du sicher, dass – egal welcher Fehler passiert – als allerletzte Amtshandlung immer der Befehl relais.value(0) (Ausschalten) gesendet wird.

1. Der "Industrie-Block": Fotek SSR-25 DA (oder SSR-40 DA)

Das ist der absolute Klassiker für Maker, wenn es um 230V geht. Es sieht aus wie ein kleiner Plastikblock mit 4 Schraubanschlüssen.

    Warum es perfekt ist: * Eingang (Input): Auf dem Label steht meistens "3-32V DC". Das bedeutet, deine 3.3V vom Mikrocontroller reichen völlig aus, um es direkt zu schalten!

        Sicherheit: Es hat Schraubterminals, die oft mit einer kleinen Plastikklappe abgedeckt sind. Keine offenen Lötstellen auf einer Platine.

        Leistung: Ein "25 DA" kann theoretisch bis zu 25 Ampere schalten (für eine Lampe brauchst du nur einen Bruchteil davon).

    BastelBody-Tipp: Wenn du dicke Lasten (wie Heizlüfter) schaltest, brauchen diese Blöcke einen Kühlkörper. Für dein "MouseCode"-Projekt mit einer normalen Lampe werden sie aber nicht mal warm. Achtung: Es gibt viele billige Fälschungen auf dem Markt (Fake-Foteks). Kauf sie am besten bei einem seriösen Elektronik-Händler und nicht das billigste 2-Euro-Paket aus Fernost.

2. Das Maker-Breakout-Board: Omron G3MB-202P Modul

Diese kleinen Module findest du oft unter dem Namen "1-Kanal SSR Relais Modul" für Arduino. Auf der Platine sitzt ein schwarzer, flacher Chip (meist von Omron).

    Warum es perfekt ist:

        Es ist winzig und sehr günstig.

        Es ist für kleine Lasten gebaut (meist 2 Ampere, also ca. 460 Watt bei 230V). Für Signallampen mehr als genug.

    Die große Falle (Achtung!): Viele dieser Module sind für 5V ausgelegt (weil der Arduino Uno 5V nutzt). Ein 3.3V Mikrocontroller schafft es oft nicht, sie einzuschalten. Achte beim Kauf zwingend darauf, dass "High Level Trigger 3.3V" oder "3V SSR Modul" in der Beschreibung steht! Alternativ musst du einen kleinen Transistor als Pegelwandler (Level Shifter) dazwischenschalten.

🧠 Wichtiges Konzept für dein MouseCode-Projekt: "Zero-Cross"

Fast alle günstigen SSRs, die du kaufen kannst, sind sogenannte Zero-Cross-SSRs (Nulldurchgangsschaltend).
Was bedeutet das? Unser 230V-Stromnetz ist Wechselstrom (AC), der 50 Mal pro Sekunde in einer Welle hoch und runter schwingt. Ein Zero-Cross-SSR schaltet die Lampe nicht exakt in der Mikrosekunde ein, in der dein Python-Code den Pin auf HIGH setzt, sondern wartet auf den nächsten Moment, in dem die Stromwelle genau bei Null Volt ist (der Nulldurchgang).

    Der Vorteil: Es gibt keine Spannungsspitzen, keine Funken und dein Hausnetz wird nicht gestört (kein Knacken im Radio).

    Der Nachteil für dich: Es gibt eine winzige Verzögerung von maximal 10 Millisekunden, bis die Lampe wirklich angeht. Für deinen MouseCode ist das völlig in Ordnung (ein 100ms Puls ist dann vielleicht mal 95ms oder 105ms lang), das Auge sieht das kaum. Du solltest dich nur nicht wundern, falls du das Signal mal mit einem Oszilloskop messen solltest und das Timing minimal schwankt.

⚠️ BastelBody Sicherheits-Predigt:

Da du Anfänger bist: 230V verzeihen keine Fehler!

    Stecker raus! Arbeite an der 230V-Seite IMMER nur, wenn der Stecker komplett aus der Steckdose gezogen ist.

    Zugentlastung: 230V Kabel müssen fest sitzen und dürfen nicht bei einem kleinen Ruck herausreißen.

    Aderendhülsen: Wenn du flexible Kabel (Litzen) in die Schraubklemmen des Relais schraubst, MUSST du vorher Aderendhülsen auf die Kabel quetschen. Lötzinn auf den Kabelenden ist bei 230V streng verboten (das Zinn fließt unter Druck weg, das Kabel wird locker, es fängt an zu brennen).

    Gehäuse: Sobald die Kabel dran sind, pack das Relais in ein Plastikgehäuse (Berührungsschutz).
"""