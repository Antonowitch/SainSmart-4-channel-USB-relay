import customtkinter as ctk
import ftd2xx

# FTDI initialisieren
dev = ftd2xx.open(0)
dev.setBitMode(0xFF, 1)
current_state = 0b0000  # alle Relais aus

def schalteRelais(relaisNr, onOff):
    global current_state
    bit_position = relaisNr - 1
    if onOff:
        current_state |= (1 << bit_position)
    else:
        current_state &= ~(1 << bit_position)
    dev.write(bytes([current_state]))

def toggle_relais(idx):
    zustand = relais_states[idx]
    relais_states[idx] = not zustand
    schalteRelais(idx+1, not zustand)
    update_light(idx)

def update_light(idx):
    # LED-Farbe
    color = "#FFFF00" if relais_states[idx] else "#7f8c8d"
    leds[idx].configure(fg_color=color)
    # Button-Farbe je nach Zustand
    if relais_states[idx]:
        buttons[idx].configure(
            fg_color=button_styles[idx]["fg_color"],
            hover_color=button_styles[idx]["hover_color"],
            border_color=button_styles[idx]["border_color"]
        )
    else:
        buttons[idx].configure(
            fg_color="#7f8c8d",
            hover_color="#b0b0b0",
            border_color="#7f8c8d"
        )

def alles_aus():
    global current_state
    current_state = 0b0000
    dev.write(bytes([current_state]))
    for i in range(4):
        relais_states[i] = False
        update_light(i)

# Modernes Design aktivieren
ctk.set_appearance_mode("dark")  # "light" oder "dark"
ctk.set_default_color_theme("green")  # Alternativen: "blue", "green", "dark-blue"

root = ctk.CTk()
root.title("SainSmart 4-Kanal Relais GUI")
root.geometry("650x200")
root.resizable(False, False)

relais_states = [False] * 4
leds = []
buttons = []

frame = ctk.CTkFrame(root)
frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

# Spaltengewichte setzen, damit alle gleich breit werden
for col in range(4):
    frame.grid_columnconfigure(col, weight=1, uniform="a")

button_styles = [
    {"fg_color": "#16a085", "hover_color": "#1abc9c", "border_color": "#27ae60"},
    {"fg_color": "#2980b9", "hover_color": "#3498db", "border_color": "#2980b9"},
    {"fg_color": "#8e44ad", "hover_color": "#9b59b6", "border_color": "#8e44ad"},
    {"fg_color": "#e67e22", "hover_color": "#f39c12", "border_color": "#e67e22"},
]

button_labels = ["Staubsauger", "Luftkuehlung", "MMS", "Beleuchtung"]

for i in range(4):
    col_frame = ctk.CTkFrame(frame, fg_color="transparent")
    col_frame.grid(row=0, column=i, padx=10, pady=0, sticky="nsew")
    # Kleine Punkt-LED als Statusanzeige
    led = ctk.CTkLabel(
        col_frame,
        text="",
        width=18,
        height=18,
        corner_radius=9,
        fg_color="#7f8c8d",
        bg_color="transparent"
    )
    led.pack(pady=(0, 7))
    leds.append(led)
    # Moderner, breiter Button mit individueller Beschriftung
    btn = ctk.CTkButton(
        col_frame,
        text=button_labels[i],
        width=150,
        height=40,
        corner_radius=20,
        font=("Helvetica Neue", 14, "bold"),
        text_color="white",
        border_width=3,
        fg_color="#7f8c8d",      # Start: grau (inaktiv)
        hover_color="#b0b0b0",   # Start: hellgrau beim Hover
        border_color="#7f8c8d",  # Start: grau
        command=lambda i=i: toggle_relais(i)
    )
    btn.pack()
    buttons.append(btn)

# Button zum Ausschalten aller Relais mit mittlerem Abstand und schmaler Breite
aus_btn = ctk.CTkButton(
    root,
    text="Alle Relais AUS",
    width=220,
    height=36,
    font=("Helvetica Neue", 15, "bold"),
    corner_radius=18,
    fg_color="#c0392b",
    hover_color="#e74c3c",
    text_color="white",
    border_width=2,
    border_color="#e74c3c",
    command=alles_aus
)
aus_btn.grid(row=1, column=0, pady=(30, 10), sticky="n")

root.grid_columnconfigure(0, weight=1)

def on_close():
    alles_aus()
    dev.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
