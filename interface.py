import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from PowerCARDGenerator import PowerCARDGenerator
from faker import Faker 
import glob
generator = PowerCARDGenerator()
json_data = []

def traiter_fichier():
    global json_data
    if not json_data:
        fichier = filedialog.askopenfilename(
            title="Sélectionner un fichier JSON",
            filetypes=[("Fichiers JSON", "*.json")]
        )
        if not fichier:
            return
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                messagebox.showerror("Erreur", "Le fichier JSON doit contenir une liste d'objets.")
                return
            json_data = data
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier JSON : {e}")
            return

    if not verifier_longueurs():
        return 

    try:
        with open("temp_modified.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        generator.generate_from_json("temp_modified.json", None)
        # Chercher tous les fichiers output_*.txt générés
        fichiers_generes = sorted(glob.glob("output_*.txt"))
        if fichiers_generes:
            chemin_sortie_var.set(", ".join(fichiers_generes))
            afficher_labels_fichiers(fichiers_generes)
            messagebox.showinfo("Succès", f"Fichiers générés et validés avec succès :\n" + "\n".join(fichiers_generes))
        else:
            messagebox.showerror("Erreur", "Aucun fichier n'a été généré.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur inattendue : {e}")

def charger_template():
    chemin = filedialog.askopenfilename(
        title="Sélectionner un fichier template JSON",
        filetypes=[("Fichiers JSON", "*.json")]
    )
    if chemin:
        try:
            generator.charger_template_depuis_fichier(chemin)
            messagebox.showinfo("Succès", f"Template chargé depuis:\n{chemin}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le template:\n{e}")

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

        zone_texte = tk.Text(fenetre_txt, wrap="word", font=("Consolas", 11))
        zone_texte.insert("1.0", contenu)
        zone_texte.configure(state="disabled", bg="#f9f9f9")
        zone_texte.pack(expand=True, fill="both", padx=10, pady=10)

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

def afficher_modifier_template():
    fenetre_template = tk.Toplevel(fenetre)
    fenetre_template.title(" Modifier le Template")
    fenetre_template.geometry("1000x400")

    colonnes = ['Nom', 'Obligatoire', 'Position','Min_Longueur', 'Max_Longueur', 'Type', 'Valeur par défaut']
    tree = ttk.Treeview(fenetre_template, columns=colonnes, show="headings", selectmode="browse")
    for col in colonnes:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor="center")
    tree.pack(expand=True, fill="both", padx=10, pady=10)
    for champ in generator.field_template:
        if len(champ) == 7:
            nom, obligatoire, position, min_longueur, max_longueur, type_champ, valeur_defaut = champ
            tree.insert("", "end", values=(nom, obligatoire, position, min_longueur, max_longueur, type_champ, valeur_defaut))
        else:
            messagebox.showerror("Erreur", f"Template invalide : {champ} (attendu 7 champs, trouvé {len(champ)})")

    def modifier_cellule(event):
        item = tree.identify_row(event.y)
        col = tree.identify_column(event.x)
        if not item or not col:
            return
        col_index = int(col.replace("#", "")) - 1
        x, y, width, height = tree.bbox(item, column=col)
        old_value = tree.item(item, "values")[col_index]
        entry = ttk.Entry(tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, old_value)
        entry.focus()

        def save_edit(event=None):
            new_value = entry.get()
            values = list(tree.item(item, "values"))
            values[col_index] = new_value
            tree.item(item, values=values)
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    tree.bind("<Double-1>", modifier_cellule)

    def sauvegarder_template():
        try:
            nouveau_template = []
            for item_id in tree.get_children():
                values = list(tree.item(item_id, "values"))
                champ = (
                    str(values[0]),                    # nom
                    str(values[1]),                    # obligatoire
                    int(values[2]),                    # position
                    int(values[3]),                    # minlongueur
                    int(values[4]),                    # maxlongueur
                    str(values[5]),                    # typechamp
                    values[6] if values[6] != 'None' else None  # valeur
                )
                nouveau_template.append(champ)
            generator.update_field_template(nouveau_template)
            messagebox.showinfo("Succès", "Template mis à jour avec succès.")
            fenetre_template.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la mise à jour du template : {e}")

    btn_save = ttk.Button(fenetre_template, text=" Sauvegarder les modifications", command=sauvegarder_template)
    btn_save.pack(pady=10)

def afficher_modifier_json():
    global json_data
    fichier = filedialog.askopenfilename(
        title="Sélectionner un fichier JSON",
        filetypes=[("Fichiers JSON", "*.json")]
    )
    if not fichier:
        return

    try:
        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            messagebox.showerror("Erreur", "Le fichier JSON doit contenir une liste d'objets.")
            return
        json_data = data
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de charger le fichier JSON : {e}")
        return

    fenetre_json = tk.Toplevel(fenetre)
    fenetre_json.title("Modifier fichier JSON")
    fenetre_json.geometry("900x500")

    colonnes = list(json_data[0].keys())
    tree = ttk.Treeview(fenetre_json, columns=colonnes, show="headings", selectmode="browse")
    for col in colonnes:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    for item in json_data:
        values = [item.get(col, "") for col in colonnes]
        tree.insert("", "end", values=values)

    def modifier_cellule(event):
        item = tree.identify_row(event.y)
        col = tree.identify_column(event.x)
        if not item or not col:
            return
        col_index = int(col.replace("#", "")) - 1
        x, y, width, height = tree.bbox(item, column=col)
        old_value = tree.item(item, "values")[col_index]
        entry = ttk.Entry(tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, old_value)
        entry.focus()

        def save_edit(event=None):
            new_value = entry.get()
            values = list(tree.item(item, "values"))
            values[col_index] = new_value
            tree.item(item, values=values)
            entry.destroy()

            item_index = tree.index(item)
            json_data[item_index][colonnes[col_index]] = new_value

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    tree.bind("<Double-1>", modifier_cellule)

    def sauvegarder_json():
        save_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json")],
            title="Enregistrer le fichier JSON modifié"
        )
        if not save_path:
            return
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Succès", f"Fichier JSON sauvegardé sous : {save_path}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {e}")

    btn_save_json = ttk.Button(fenetre_json, text="Sauvegarder JSON modifié", command=sauvegarder_json)
    btn_save_json.pack(pady=10)

def verifier_longueurs():
    if not json_data:
        messagebox.showwarning("Attention", "Aucune donnée JSON chargée.")
        return False 
    erreurs = []
    for i, obj in enumerate(json_data, start=1):
        for champ in generator.field_template:
            nom, obligatoire, position, min_longueur, max_longueur, type_champ, valeur_defaut = champ
            valeur = str(obj.get(nom, ""))
            if len(valeur) > max_longueur  :
                erreurs.append(f"Ligne {i} : '{nom}' dépasse {max_longueur} caractères (actuel : {len(valeur)})")
            elif len(valeur) < min_longueur and obligatoire == "M" :
                erreurs.append(f"Ligne {i} : '{nom}' ne dépasse pas {min_longueur} caractères (actuel : {len(valeur)})")
              
    if erreurs:
        message = "\n".join(erreurs)
        messagebox.showerror("Erreurs de longueur", message)
        return False
    else:
        messagebox.showinfo("Succès", "Tous les champs respectent les longueurs du template.")
        return True

def afficher_labels_fichiers(fichiers):
    for lbl in labels_fichiers:
        lbl.destroy()
    labels_fichiers.clear()
    for chemin in fichiers:
        lbl = ttk.Label(frame_fichiers, text=chemin, foreground="blue", cursor="hand2")
        lbl.pack(anchor="center", pady=2)
        lbl.bind("<Button-1>", lambda e, c=chemin: afficher_contenu_fichier(c))
        labels_fichiers.append(lbl)

def afficher_contenu_fichier(chemin):
    try:
        with open(chemin, "r", encoding="utf-8") as f:
            contenu = f.read()
        fenetre_txt = tk.Toplevel(fenetre)
        fenetre_txt.title(f"Contenu de {chemin}")
        fenetre_txt.geometry("700x500")
        zone_texte = tk.Text(fenetre_txt, wrap="word", font=("Consolas", 11))
        zone_texte.insert("1.0", contenu)
        zone_texte.configure(state="disabled", bg="#f9f9f9")
        zone_texte.pack(expand=True, fill="both", padx=10, pady=10)
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

fenetre = tk.Tk()
fenetre.title("Générateur de fichier de demande de carte banquaire")
fenetre.geometry("600x480")
fenetre.configure(bg="#f0f0f5")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 11), padding=8)
style.configure("TLabel", background="#f0f0f5", font=("Segoe UI", 12))
style.configure("TEntry", font=("Segoe UI", 11))

chemin_sortie_var = tk.StringVar()

frame = ttk.Frame(fenetre, padding=25)
frame.pack(expand=True, fill="both")

titre = ttk.Label(frame, text="Bienvenue", font=("Segoe UI", 16, "bold"))
titre.pack(pady=(0, 25))

btn_generer = ttk.Button(frame, text="Générer le fichier texte", command=traiter_fichier)
btn_generer.pack(pady=12, ipadx=12)

btn_template = ttk.Button(frame, text="Modifier le template ", command=afficher_modifier_template)
btn_template.pack(pady=12, ipadx=12)

btn_charger = ttk.Button(frame, text="Charger un nouveau template ", command=charger_template)
btn_charger.pack(pady=12 , ipadx=12)

btn_json = ttk.Button(frame, text="Modifier JSON", command=afficher_modifier_json)
btn_json.pack(pady=12, ipadx=12)

champ_fichier_label = ttk.Label(frame, text="Fichier généré : (cliquez pour l'ouvrir)")
champ_fichier_label.pack(pady=(25, 8), anchor="center")

frame_fichiers = ttk.Frame(frame)
frame_fichiers.pack(pady=(10, 0))
labels_fichiers = []

fenetre.mainloop()