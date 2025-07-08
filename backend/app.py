from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
import glob
from werkzeug.utils import secure_filename
from PowerCARDGenerator import PowerCARDGenerator

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///powercard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)
class GeneratedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(500), nullable=False)
    original_json_name = db.Column(db.String(255))
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'generated_at': self.generated_at.isoformat(),
            'original_json_name': self.original_json_name
        }

generator = PowerCARDGenerator()

with app.app_context():
    db.create_all()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'message': 'Server is running'})

@app.route('/api/template', methods=['GET'])
def get_template():
    try:
        template = []
        for field in generator.field_template:
            if len(field) == 7:
                nom, obligatoire, position, min_longueur, max_longueur, type_champ, valeur_defaut = field
                template.append({
                    'nom': nom,
                    'obligatoire': obligatoire,
                    'position': position,
                    'min_longueur': min_longueur,
                    'max_longueur': max_longueur,
                    'type': type_champ,
                    'valeur_defaut': valeur_defaut
                })
        return jsonify({'template': template})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/template', methods=['PUT'])
def update_template():
    """Mettre à jour le template"""
    try:
        data = request.get_json()
        template = data.get('template', [])
        new_template = []
        for field in template:
            champ = (
                str(field['nom']),
                str(field['obligatoire']),
                int(field['position']),
                int(field['min_longueur']),
                int(field['max_longueur']),
                str(field['type']),
                field['valeur_defaut'] if field['valeur_defaut'] != 'None' else None
            )
            new_template.append(champ)
        
        generator.update_field_template(new_template)
        return jsonify({'message': 'Template mis à jour avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/template/load', methods=['POST'])
def load_template():
    """Charger un template depuis un fichier"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if file and file.filename.endswith('.json'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            generator.charger_template_depuis_fichier(filepath)
            os.remove(filepath)  # Nettoyer le fichier temporaire
            
            return jsonify({'message': f'Template chargé depuis {filename}'})
        else:
            return jsonify({'error': 'Format de fichier non supporté'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def validate_json():
    """Valider un fichier JSON contre le template"""
    try:
        data = request.get_json()
        json_data = data.get('json_data', [])
        
        if not isinstance(json_data, list):
            return jsonify({'error': 'Le JSON doit contenir une liste d\'objets'}), 400
        
        erreurs = []
        for i, obj in enumerate(json_data, start=1):
            for champ in generator.field_template:
                nom, obligatoire, position, min_longueur, max_longueur, type_champ, valeur_defaut = champ
                valeur = str(obj.get(nom, ""))
                
                if len(valeur) > max_longueur:
                    erreurs.append(f"Ligne {i} : '{nom}' dépasse {max_longueur} caractères (actuel : {len(valeur)})")
                elif len(valeur) < min_longueur and obligatoire == "M":
                    erreurs.append(f"Ligne {i} : '{nom}' ne dépasse pas {min_longueur} caractères (actuel : {len(valeur)})")
        
        if erreurs:
            return jsonify({'valid': False, 'errors': erreurs}), 400
        else:
            return jsonify({'valid': True, 'message': 'Tous les champs respectent les longueurs du template'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_files():
    """Générer les fichiers de sortie"""
    try:
        data = request.get_json()
        json_data = data.get('json_data', [])
        original_filename = data.get('original_filename', 'unknown.json')
        
        if not isinstance(json_data, list):
            return jsonify({'error': 'Le JSON doit contenir une liste d\'objets'}), 400
        
        # Sauvegarder temporairement le JSON
        temp_json_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_data.json')
        with open(temp_json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        # Générer les fichiers
        generator.generate_from_json(temp_json_path, None)
        
        # Chercher les fichiers générés
        fichiers_generes = sorted(glob.glob("output_*.txt"))
        
        if not fichiers_generes:
            return jsonify({'error': 'Aucun fichier n\'a été généré'}), 500
        
        # Enregistrer dans la base de données
        generated_files = []
        for fichier in fichiers_generes:
            new_file = GeneratedFile(
                filename=os.path.basename(fichier),
                file_path=os.path.abspath(fichier),
                original_json_name=original_filename
            )
            db.session.add(new_file)
            generated_files.append(new_file)
        
        db.session.commit()
        
        # Nettoyer le fichier temporaire
        os.remove(temp_json_path)
        
        return jsonify({
            'message': 'Fichiers générés avec succès',
            'files': [f.to_dict() for f in generated_files]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files', methods=['GET'])
def get_generated_files():
    """Récupérer la liste des fichiers générés"""
    try:
        files = GeneratedFile.query.order_by(GeneratedFile.generated_at.desc()).all()
        return jsonify({'files': [f.to_dict() for f in files]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<int:file_id>', methods=['GET'])
def get_file_content(file_id):
    """Récupérer le contenu d'un fichier généré"""
    try:
        file_record = GeneratedFile.query.get_or_404(file_id)
        
        if not os.path.exists(file_record.file_path):
            return jsonify({'error': 'Fichier non trouvé sur le système'}), 404
        
        with open(file_record.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'content': content,
            'filename': file_record.filename,
            'generated_at': file_record.generated_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<int:file_id>/download', methods=['GET'])
def download_file(file_id):
    """Télécharger un fichier généré"""
    try:
        file_record = GeneratedFile.query.get_or_404(file_id)
        
        if not os.path.exists(file_record.file_path):
            return jsonify({'error': 'Fichier non trouvé sur le système'}), 404
        
        return send_file(
            file_record.file_path,
            as_attachment=True,
            download_name=file_record.filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Supprimer un fichier généré"""
    try:
        file_record = GeneratedFile.query.get_or_404(file_id)
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
        db.session.delete(file_record)
        db.session.commit()
        return jsonify({'message': 'Fichier supprimé avec succès'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-json', methods=['POST'])
def upload_json():
    """Uploader et parser un fichier JSON"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if file and file.filename.endswith('.json'):
            content = file.read().decode('utf-8')
            json_data = json.loads(content)
            if not isinstance(json_data, list):
                return jsonify({'error': 'Le fichier JSON doit contenir une liste d\'objets'}), 400
            return jsonify({
                'json_data': json_data,
                'filename': file.filename,
                'message': 'Fichier JSON chargé avec succès'
            })
        else:
            return jsonify({'error': 'Format de fichier non supporté'}), 400
    except json.JSONDecodeError:
        return jsonify({'error': 'Fichier JSON invalide'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)