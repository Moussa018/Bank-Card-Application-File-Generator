import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from PowerCARDGenerator import PowerCARDGenerator
import os


generator = PowerCARDGenerator()
json_data = []  

def traiter_fichier():
    global json_data
    if not json_data:
        messagebox.showwarning("Attention", "Veuillez d'abord charger et modifier un fichier JSON.")
        return
    fichier_sortie = "output_code.txt"
    try:
        # Générer depuis les données JSON modifiées (en mémoire)
        with open("temp_modified.json", "w") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        success = generator.generate_from_json("temp_modified.json", fichier_sortie)
        if success:
            if generator.validate_file(fichier_sortie):
                generator.insert("temp_modified.json")
                chemin_sortie_var.set(fichier_sortie)
                messagebox.showinfo("Succès", "Fichier généré et validé avec succès.")
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

        zone_texte = tk.Text(fenetre_txt, wrap="word", font=("Consolas", 11))
        zone_texte.insert("1.0", contenu)
        zone_texte.configure(state="disabled", bg="#f9f9f9")
        zone_texte.pack(expand=True, fill="both", padx=10, pady=10)

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

def afficher_modifier_template():
    fenetre_template = tk.Toplevel(fenetre)
    fenetre_template.title("📐 Modifier le Template")
    fenetre_template.geometry("1000x400")

    colonnes = ['Nom', 'Obligatoire', 'Position', 'Longueur', 'Type', 'Valeur par défaut']
    tree = ttk.Treeview(fenetre_template, columns=colonnes, show="headings", selectmode="browse")
    for col in colonnes:
        tree.heading(col, text=col)
        tree.column(col, width=140, anchor="center")
    tree.pack(expand=True, fill="both", padx=10, pady=10)

    for champ in generator.field_template:
        tree.insert("", "end", values=champ)

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
                    str(values[0]),
                    str(values[1]),
                    int(values[2]),
                    int(values[3]),
                    str(values[4]),
                    values[5] if values[5] != 'None' else None
                )
                nouveau_template.append(champ)
            generator.update_field_template(nouveau_template)
            messagebox.showinfo("Succès", "Template mis à jour avec succès.")
            fenetre_template.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la mise à jour du template : {e}")

    btn_save = ttk.Button(fenetre_template, text="💾 Sauvegarder les modifications", command=sauvegarder_template)
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

            # Met à jour json_data
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

    btn_save_json = ttk.Button(fenetre_json, text="💾 Sauvegarder JSON modifié", command=sauvegarder_json)
    btn_save_json.pack(pady=10)


    fen_chatbot = tk.Toplevel(fenetre)
    fen_chatbot.title("🤖 Mini Chatbot")
    fen_chatbot.geometry("400x400")

    frame_chat = ttk.Frame(fen_chatbot, padding=10)
    frame_chat.pack(expand=True, fill="both")

    zone_discussion = tk.Text(frame_chat, state="disabled", wrap="word", height=15)
    zone_discussion.pack(expand=True, fill="both")

    entry_question = ttk.Entry(frame_chat)
    entry_question.pack(fill="x", pady=5)
    
    def repondre():
        question = entry_question.get().strip()
        if not question:
            return
        zone_discussion.configure(state="normal")
        zone_discussion.insert("end", f"Toi : {question}\n")
        zone_discussion.configure(state="disabled")
        zone_discussion.see("end")
        entry_question.delete(0, "end")

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Tu es un assistant utile et poli."},
                    {"role": "user", "content": question}
                ],
                max_tokens=150,
                temperature=0.7,
            )
            reponse = response.choices[0].message.content.strip()
        except Exception as e:
            reponse = f"Erreur API : {e}"

        zone_discussion.configure(state="normal")
        zone_discussion.insert("end", f"Bot : {reponse}\n\n")
        zone_discussion.configure(state="disabled")
        zone_discussion.see("end")

    bouton_envoyer = ttk.Button(frame_chat, text="Envoyer", command=repondre)
    bouton_envoyer.pack(pady=5)  

# --- Interface principale ---
fenetre = tk.Tk()
fenetre.title("🧾 Générateur PowerCARD")
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

titre = ttk.Label(frame, text="Bienvenue dans le Générateur PowerCARD", font=("Segoe UI", 16, "bold"))
titre.pack(pady=(0, 25))

btn_generer = ttk.Button(frame, text="📄 Générer le fichier texte", command=traiter_fichier)
btn_generer.pack(pady=12, ipadx=12)

btn_template = ttk.Button(frame, text="📐 Afficher / Modifier le template", command=afficher_modifier_template)
btn_template.pack(pady=12, ipadx=12)

btn_json = ttk.Button(frame, text="📊 Afficher / Modifier JSON", command=afficher_modifier_json)
btn_json.pack(pady=12, ipadx=12)

champ_fichier_label = ttk.Label(frame, text="Fichier généré : (cliquez pour l'ouvrir)")
champ_fichier_label.pack(pady=(25, 8))

champ_fichier = ttk.Entry(frame, textvariable=chemin_sortie_var, width=55, state="readonly", cursor="hand2")
champ_fichier.pack()
champ_fichier.bind("<Button-1>", afficher_contenu_txt)

fenetre.mainloop()
