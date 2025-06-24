import csv
import json
import sqlite3
from datetime import datetime
import uuid


class PowerCARDGenerator:
        
    def __init__(self, record_length=215):
        self.record_length = record_length
        self.field_template = [
            # Champ, Position, Longueur, Type, Valeur par défaut
            ('record_type','M', 1, 2, 'AN', 'DT'),
            ('sequence','M', 3, 19, 'N', '0'),
            ('action','M', 22, 2, 'AN', 'IN'),
            ('language','M', 24, 5, 'AN', 'fr_FR'),
            ('bank_code','M', 29, 6, 'AN', None),
            ('branch_code','M', 35, 6, 'AN', None),
            ('app_date','M', 41, 8, 'DATE', None),
            ('delivery_branch','O', 49, 6, 'AN', ' ' * 6),
            ('client_host_id','O', 55, 24, 'AN', ' ' * 24),
            ('file_number','M', 77, 20, 'AN', None),
            ('client_code','O', 97, 24, 'AN', ' ' * 24),
            ('card_product','M', 121, 3, 'AN', None),
            ('plastic_type','M', 124, 3, 'AN', ' ' * 3),
            ('card_fees','O', 127, 3, 'AN', None),
            ('family_status','M', 130, 1, 'AN', None),
            ('gender','M', 131, 1, 'AN', None),
            ('document_code','M', 132, 2, 'AN', None),
            ('legal_id','O', 134, 30, 'AN', ' ' * 30),
            ('title_code','M', 164, 2, 'AN', None),
            ("client_name","M", 166, 50, 'AN', ' ' * 50)
        ]

    def insert(self, json_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier JSON: {e}")
            return False
        for item in data:
            if item.get("action") == "NI":
                con = sqlite3.connect('ma_base.db')
                cursor =con.cursor()
                if all(k in item for k in ("client_name", "bank_code", "branch_code")):
                    cursor.execute(
                        "INSERT INTO clients (client_name, bank_code, branch_code) VALUES (?, ?, ?)",
                        (item["client_name"], item["bank_code"], item["branch_code"])
                    )
                    print(f"[INSERT] client_name {item['client_name']} added to clients.")
                con.commit()
                con.close()

    def format_date(self, date_str):
        if not date_str:
            return datetime.now().strftime("%Y%m%d")
        try:
            if '/' in date_str:
                return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y%m%d")
            elif len(date_str) == 8 and date_str.isdigit():
                return date_str
            else:
                return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%d")
        except ValueError:
            print(f"Format de date invalide: {date_str}. Utilisation de la date actuelle.")
            return datetime.now().strftime("%Y%m%d")

    def validate_required_fields(self, data):

        required_fields = [field[0] for field in self.field_template if field[1] == 'M']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f"Champs obligatoires manquants: {missing_fields}")
        return True
    
    def update_field_template(self, new_template):
        self.field_template = new_template
        max_position = 0
        for field in self.field_template:
            field_end = field[1] + field[2] 
            if field_end > max_position:
                    max_position = field_end
        self.record_length = max_position - 1

    def create_record(self, data, sequence_num): 
        try:
            self.validate_required_fields(data)
        except ValueError as e:
            print(f"Erreur: {e}")
            return None

        record = [' '] * self.record_length
        
        for field_name, required, pos, length, field_type, default_value in self.field_template:
            value = data.get(field_name, default_value)
            
            if value is None:
                raise ValueError(f"Valeur manquante pour le champ obligatoire: {field_name}")
                
            if field_type == 'DATE':
                value = self.format_date(value)
            elif field_type == 'N':
                value = str(value).rjust(length)[-length:]
            elif field_type == 'AN':
                value = str(value).ljust(length)[:length]
            
            start = pos - 1
            end = start + length
            record[start:end] = list(value)
        
        return ''.join(record)

        records = []
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    record = self.create_record(row, i)
                    if record:
                        records.append(record)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier CSV: {e}")
            return False
        
        return self._write_output_file(output_file, records)

    def generate_from_json(self, json_file, output_file):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier JSON: {e}")
            return False

        records = []
        if isinstance(data, list):
            for i, row in enumerate(data, 1):
                record = self.create_record(row, i)
                if record:
                    records.append(record)
        elif isinstance(data, dict):
            record = self.create_record(data, 1)
            if record:
                records.append(record)
        
        return self._write_output_file(output_file, records)

    def _write_output_file(self, output_file, records):
        try:
            with open(output_file, 'w') as f:
                for record in records:
                    f.write(record + '\n')
            print(f"Fichier généré avec succès: {output_file}")
            return True
        except Exception as e:
            print(f"Erreur lors de l'écriture: {e}")
            return False

    def validate_file(self, filename):
        try:
            with open(filename, 'r') as f:
                for i, line in enumerate(f, 1):
                    line = line.rstrip('\n\r')
                    if len(line) != self.record_length:
                        print(f"Ligne {i}: Longueur incorrecte ({len(line)} au lieu de {self.record_length})")
                        return False
                    if line[0:2] != 'DT':
                        print(f"Ligne {i}: Type d'enregistrement incorrect")
                        return False
            return True
        except Exception as e:
            print(f"Erreur lors de la validation: {e}")
            return False
