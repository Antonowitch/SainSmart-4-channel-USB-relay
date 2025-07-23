import tkinter as tk
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
    zustand = relais_vars[idx].get()
    schalteRelais(idx+1, zustand)
    update_light(idx)

def update_light(idx):
    color = "green" if relais_vars[idx].get() else "gray"
    canvas_lights[idx].itemconfig(light_circles[idx], fill=color)

def alles_aus():
    global current_state
    current_state = 0b0000
    dev.write(bytes([current_state]))
    for i in range(4):
        relais_vars[i].set(False)
        update_light(i)

# GUI aufbauen
root = tk.Tk()
root.title("SainSmart 4-Kanal Relais GUI")

relais_vars = [tk.BooleanVar(value=False) for _ in range(4)]
canvas_lights = []
light_circles = []

for i in range(4):
    frame = tk.Frame(root)
    frame.grid(row=0, column=i, padx=10, pady=10)
    # Lichtanzeige (Kreis)
    canvas = tk.Canvas(frame, width=40, height=40, highlightthickness=0)
    circle = canvas.create_oval(5, 5, 35, 35, fill="gray")
    canvas.pack()
    canvas_lights.append(canvas)
    light_circles.append(circle)
    # Toggle-Button
    btn = tk.Checkbutton(
        frame,
        text=f"Relais {i+1}",
        variable=relais_vars[i],
        indicatoron=True,
        font=("Arial", 11),
        command=lambda i=i: toggle_relais(i)
    )
    btn.pack()

# Button zum Ausschalten aller Relais
aus_btn = tk.Button(root, text="Alle Relais AUS", font=("Arial", 11), command=alles_aus)
aus_btn.grid(row=1, column=0, columnspan=4, pady=10)

def on_close():
    alles_aus()
    dev.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
