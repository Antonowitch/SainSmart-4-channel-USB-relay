import ftd2xx
import time

# Öffne das erste FTDI-Gerät (ggf. Index anpassen)
dev = ftd2xx.open(0)
dev.setBitMode(0xFF, 1)  # Setze alle 8 Pins auf Output, aktiviere Bit-Bang-Modus

# Definierten Startzustand setzen, z.B. alle Relais aus (0b0000)
START_STATE = 0b0000
dev.write(bytes([START_STATE]))
print(f"Relais beim Start auf Zustand {bin(START_STATE)} gesetzt.")
time.sleep(0.1)


def set_relays(mask):
    """
    Steuert die 4 Relais.
    mask: 4 Bit (D0-D3), 1 = an, 0 = aus
    """
    dev.write(bytes([mask]))
    print(f"Relais-Maske gesendet: {bin(mask)}")
    time.sleep(0.1)

# Beispiel: Nur Relais 1 an (D0)
set_relays(0b0001)
time.sleep(1)

# Beispiel: Nur Relais 2 an (D1)
set_relays(0b0010)
time.sleep(1)

# Beispiel: Relais 3 an (D2)  
set_relays(0b0100)
time.sleep(1)     

# Beispiel: Relais 4 an (D3)
set_relays(0b1000)      
time.sleep(1)

# Beispiel: Alle Relais aus
set_relays(0b0000)
time.sleep(1)

# Schließe das Gerät
dev.close()
print("Fertig.")
