import json
from datetime import datetime
import random
import string
from faker import Faker  
fake = Faker()
class PowerCARDGenerator :
    def __init__(self, record_length=215):
        self.record_length = record_length
        self.field_template = [
            ['record_type','M', 1, 2, 2, 'AN', 'DT'],
            ['sequence','M', 3, 5, 19, 'N', None],
            ['action','O', 22, 1, 2, 'AN', ["NI","MO"]],
            ['language','O', 24, 5, 5, 'AN', ["FRfra", "ANang", "ESesp"]],
            ['bank_code','M', 29, 2, 6, 'AN', None],
            ['branch_code','M', 35, 4, 6, 'AN', None],
            ['app_date','M', 41, 8, 8, 'DATE', None],
            ['delivery_branch','O', 49, 2, 6, 'AN', None],
            ['client_host_id','O', 55, 13, 24, 'AN', None],
            ['file_number','O', 77, 10, 20, 'AN', None],
            ['client_code','O', 97, 15, 24, 'AN', None],
            ['card_product','O', 121, 1, 3, 'AN', None],
            ['plastic_type','O', 124, 2, 3, 'AN', None],
            ['card_fees','O', 127, 2, 3, 'AN', None],
            ['family_status','M', 130, 1, 1, 'AN', ["M","D","C"]],
            ['gender','M', 131, 1, 1, 'AN', ["M","F"]],
            ['document_code','M', 132, 1, 2, 'AN', None],
            ['legal_id','O', 134, 9, 30, 'AN', None],
            ['title_code','O', 164, 1, 2, 'AN', None],
            ['client_name','O', 166, 10, 50, 'AN', None],
        ]
   
    def update_field_template(self,template):
        self.field_template = template
        self.record_length =  template[-1][3] + template[-1][4]

    def charger_template_depuis_fichier(self, chemin_fichier):
        with open(chemin_fichier, "r", encoding="utf-8") as f:
            self.field_template = json.load(f)
        print("Template chargé :", self.field_template)

    def format_date(self, date_str):
        try:
            if '/' in date_str:
                return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y%m%d")
            elif len(date_str) == 8 and date_str.isdigit():
                return date_str
            else:
                return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y%m%d")
        except ValueError:
            return datetime.now().strftime("%Y%m%d")

    def validate_required_fields(self, data):
        required_fields = [field[0] for field in self.field_template if field[1] == 'M']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValueError(f"Champs obligatoires manquants: {missing_fields}")
        return True

    def create_record(self, data, sequence_num):
        try:
            self.validate_required_fields(data)
        except ValueError as e:
            print(f"Erreur: {e}")
            return None

        record = [' '] * self.record_length

        for field_spec in self.field_template:
            field_name, required, pos, min_length, max_length, field_type, default_value = field_spec
            value = data.get(field_name, "").strip()
            if not value:
                if required == "M" and default_value is None:
                    raise ValueError(f"Valeur manquante pour le champ obligatoire: {field_name}")
                if isinstance(default_value, list):
                    value = random.choice(default_value)
                elif  field_name == "client_name":
                    value = fake.name() 
                elif default_value is not None:
                    value = default_value
                else:
                    max_num = 10**max_length - 1
                    value = str(random.randint(0, max_num)).zfill(max_length)
            try:
                if field_type == 'DATE':
                    value = self.format_date(value)
                elif field_type == 'N':
                    value = str(value).zfill(max_length)[:max_length]
                elif field_type == 'AN':
                    value = str(value).ljust(max_length)[:max_length]
            except Exception as e:
                raise ValueError(f"Formatting error for field {field_name}: {str(e)}")
            start = pos - 1
            end = start + max_length
            if len(value) != max_length:
                raise ValueError(f"Formatted value for {field_name} has incorrect length (got {len(value)}, expected {max_length})")
        
            record[start:end] = list(value)

        return ''.join(record)
    
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
            return True
        except Exception as e:
            print(f"Erreur lors de l'écriture: {e}")
            return False

    def validate_file(self, filename):
        try:
            with open(filename, 'r') as f:
                for i, line in enumerate(f, 1):
                    line = line.rstrip('\n\r')
                    if line[0:2] != 'DT':
                        print(f"Ligne {i}: Type d'enregistrement incorrect")
                        return False
            return True
        except Exception as e:
            print(f"Erreur lors de la validation: {e}")
            return False