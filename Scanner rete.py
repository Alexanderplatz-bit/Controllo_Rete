import socket
import concurrent.futures
import threading
import tkinter as tk
from tkinter import ttk, messagebox

def esegui_scansione_thread(target):
    risultati = []

    def controlla_porta(porta):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        risultato = s.connect_ex((target, porta))
        
        if risultato == 0:
            try:
                servizio = socket.getservbyport(porta)
            except:
                servizio = "Sconosciuto"
            
            riga = f"[+] Porta {porta} aperta! -> Servizio: {servizio}"
            risultati.append(riga)
            
            # Aggiorna la finestra in modo sicuro
            text_output.insert(tk.END, riga + "\n")
            text_output.see(tk.END)
            
        s.close()

    # Esecuzione multithread
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(controlla_porta, range(1, 1025))

    text_output.insert(tk.END, "\n--- Scansione completata! ---\n")
    
    # Salvataggio automatico su file
    with open("risultati_scansione.txt", "w") as file:
        file.write(f"Report scansione per IP: {target}\n")
        file.write("=" * 40 + "\n")
        if risultati:
            for r in risultati:
                file.write(r + "\n")
        else:
            file.write("Nessuna porta aperta trovata.\n")

    messagebox.showinfo("Fatto", "Scansione terminata e salvata in 'risultati_scansione.txt'!")
    btn_scansiona.config(state=tk.NORMAL)

def avvia_scansione():
    target_input = entry_ip.get().strip()
    if not target_input:
        messagebox.showwarning("Attenzione", "Inserisci un IP o un dominio valido!")
        return

    try:
        target = socket.gethostbyname(target_input)
    except socket.gaierror:
        messagebox.showerror("Errore", "Impossibile risolvere l'indirizzo IP.")
        return

    # Pulizia finestra di output
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, f"--- Avvio scansione su {target} (Porte 1-1024) ---\n\n")
    btn_scansiona.config(state=tk.DISABLED)

    # Avviamo il lavoro di rete in un thread separato così la finestra non si blocca
    threading.Thread(target=esegui_scansione_thread, args=(target,), daemon=True).start()

# --- Creazione Finestra Grafica ---
root = tk.Tk()
root.title("Port Scanner Pro")
root.geometry("480x420")
root.resizable(False, False)

label_ip = tk.Label(root, text="Indirizzo IP / Dominio:", font=("Arial", 11))
label_ip.pack(pady=(15, 5))

entry_ip = tk.Entry(root, font=("Arial", 11), width=30, justify="center")
entry_ip.insert(0, "127.0.0.1")
entry_ip.pack(pady=5)

btn_scansiona = tk.Button(root, text="Avvia Scansione", font=("Arial", 11, "bold"), bg="#28a745", fg="white", command=avvia_scansione)
btn_scansiona.pack(pady=10)

frame_output = tk.Frame(root)
frame_output.pack(padx=15, pady=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame_output)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_output = tk.Text(frame_output, font=("Consolas", 9), yscrollcommand=scrollbar.set)
text_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=text_output.yview)

root.mainloop()
