import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from PowerCARDGenerator import PowerCARDGenerator

def traiter_fichier():
    fichier = filedialog.askopenfilename(
        title="Sélectionner un fichier CSV ou JSON",
        filetypes=[("Fichiers JSON ou CSV", "*.json *.csv")]
    )

    if not fichier:
        return

    generator = PowerCARDGenerator()
    fichier_sortie = "output_code.txt"

    try:
        if fichier.endswith(".json"):
            success = generator.generate_from_json(fichier, fichier_sortie)
        else:
            messagebox.showerror("Erreur", "Format de fichier non pris en charge.")
            return

        if success:
            if generator.validate_file(fichier_sortie):
                generator.insert(fichier)
                chemin_sortie_var.set(fichier_sortie)
                messagebox.showinfo("Succès", f"Fichier généré et validé avec succès.")
            else:
                messagebox.showerror("Erreur", "Le fichier généré est invalide.")
        else:
            messagebox.showerror("Erreur", "Échec de la génération du fichier.")

    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def afficher_contenu_txt(event=None):
    chemin = chemin_sortie_var.get()
    if not chemin:
        return

    try:
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()

        fenetre_txt = tk.Toplevel(fenetre)
        fenetre_txt.title(f"Contenu de {chemin}")
        fenetre_txt.geometry("700x500")

        zone_texte = tk.Text(fenetre_txt, wrap="word")
        zone_texte.insert("1.0", contenu)
        zone_texte.configure(state="disabled")  # lecture seule
        zone_texte.pack(expand=True, fill="both", padx=10, pady=10)

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d’ouvrir le fichier : {e}")


def afficher_json():
    fichier = filedialog.askopenfilename(
        title="Sélectionner un fichier JSON",
        filetypes=[("Fichiers JSON", "*.json")]
    )

    if not fichier:
        return

    try:
        with open(fichier, 'r') as f:
            data = json.load(f)

        if not isinstance(data, list):
            messagebox.showerror("Erreur", "Le fichier JSON doit contenir une liste d’objets.")
            return

        table_fenetre = tk.Toplevel(fenetre)
        table_fenetre.title("Contenu du fichier JSON")
        table_fenetre.geometry("900x500")

        frame_table = ttk.Frame(table_fenetre)
        frame_table.pack(fill="both", expand=True, padx=10, pady=10)

        colonnes = list(data[0].keys())
        tree = ttk.Treeview(frame_table, columns=colonnes, show="headings")

        vsb = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        for col in colonnes:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')

        for item in data:
            values = [item.get(col, "") for col in colonnes]
            tree.insert("", "end", values=values)

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d’afficher le fichier JSON : {e}")


# Interface principale
fenetre = tk.Tk()
fenetre.title("🧾 Générateur PowerCARD")
fenetre.geometry("500x360")
fenetre.configure(bg="#f0f0f5")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("TLabel", background="#f0f0f5", font=("Segoe UI", 11))

chemin_sortie_var = tk.StringVar()

frame = ttk.Frame(fenetre, padding=20)
frame.pack(expand=True)

titre = ttk.Label(frame, text="Bienvenue dans le Générateur PowerCARD", font=("Segoe UI", 14, "bold"))
titre.pack(pady=(0, 15))

btn_generer = ttk.Button(frame, text="📄 Générer le fichier texte", command=traiter_fichier)
btn_generer.pack(pady=10, ipadx=10)

btn_afficher = ttk.Button(frame, text="📊 Afficher le fichier JSON", command=afficher_json)
btn_afficher.pack(pady=10, ipadx=10)

champ_fichier_label = ttk.Label(frame, text="Fichier généré : (cliquez pour l’ouvrir)")
champ_fichier_label.pack(pady=(20, 5))

champ_fichier = ttk.Entry(frame, textvariable=chemin_sortie_var, width=50, state="readonly", cursor="hand2")
champ_fichier.pack()
champ_fichier.bind("<Button-1>", afficher_contenu_txt)

fenetre.mainloop()
