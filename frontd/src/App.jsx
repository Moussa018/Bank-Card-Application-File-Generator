import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';
axios.defaults.baseURL = API_BASE_URL;

function Header() {
  return (
    <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-svg" aria-label="logo" style={{display: 'flex', alignItems: 'center'}}>
              <svg width="44" height="32" viewBox="0 0 44 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3.5" result="coloredBlur"/>
                    <feMerge>
                      <feMergeNode in="coloredBlur"/>
                      <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                  </filter>
                </defs>
                <rect x="3" y="5" width="38" height="22" rx="8" fill="#17e6ff" fillOpacity="0.13" filter="url(#glow)"/>
                <rect x="7" y="9" width="30" height="14" rx="6" fill="#fff"/>
                <ellipse cx="15" cy="16" rx="3.5" ry="3.5" fill="#17e6ff" fillOpacity="0.7"/>
                <ellipse cx="29" cy="16" rx="3.5" ry="3.5" fill="#17e6ff" fillOpacity="0.7"/>
                <ellipse cx="15" cy="16" rx="1.2" ry="1.2" fill="#fff"/>
                <ellipse cx="29" cy="16" rx="1.2" ry="1.2" fill="#fff"/>
                <rect x="13" y="12.5" width="18" height="7" rx="3.5" fill="#17e6ff" fillOpacity="0.18"/>
                <rect x="18" y="15" width="8" height="2.5" rx="1.2" fill="#17e6ff" fillOpacity="0.45"/>
              </svg>
            </span>
            <span style={{color: '#fff', fontWeight: 700, fontSize: '2.1rem', letterSpacing: 1, textShadow: '0 0 12px #17e6ff99, 0 2px 8px #0002'}}>Power</span><span className="logo-accent" style={{color: '#17e6ff', fontWeight: 700, fontSize: '2.1rem', marginLeft: 6, letterSpacing: 0.5}}>CARD</span>
          </div>
          <nav className="header-nav">
            <a href="https://github.com/Moussa018/Bank-Card-Application-File-Generator/tree/mainly" className="header-doc-link" target="_blank" rel="noopener noreferrer">
              Documentation
            </a>
            <a href="https://github.com/Moussa018" className="header-user-link" target="_blank" rel="noopener noreferrer">
              <span className="header-user-svg" aria-label="user">
                <svg width="18" height="18" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="7" r="4" fill="#fff" fillOpacity="0.7"/><ellipse cx="10" cy="15" rx="6" ry="3" fill="#fff" fillOpacity="0.4"/></svg>
              </span>
              Profil GitHub
            </a>
          </nav>
        </div>
      </header>
  );
}

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [template, setTemplate] = useState([]);
  const [jsonData, setJsonData] = useState([]);
  const [generatedFiles, setGeneratedFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadTemplate();
    loadGeneratedFiles();
  }, []);

  const loadTemplate = async () => {
    try {
      const response = await axios.get('/template');
      setTemplate(response.data.template);
    } catch (err) {
      setError('Erreur lors du chargement du template');
      console.error(err);
    }
  };

  const loadGeneratedFiles = async () => {
    try {
      const response = await axios.get('/files');
      setGeneratedFiles(response.data.files);
    } catch (err) {
      console.error('Erreur lors du chargement des fichiers:', err);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/upload-json', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setJsonData(response.data.json_data);
      setSuccess(`Fichier ${response.data.filename} chargé avec succès`);
      setCurrentView('json-editor');
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du chargement du fichier');
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError('');
    setSuccess('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/template/load', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      setSuccess(response.data.message);
      loadTemplate();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du chargement du template');
    } finally {
      setLoading(false);
    }
  };

  const validateAndGenerate = async () => {
    if (!jsonData || jsonData.length === 0) {
      setError('Aucune donnée JSON à traiter');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const validateResponse = await axios.post('/validate', {
        json_data: jsonData
      });

      if (validateResponse.data.valid) {
          const generateResponse = await axios.post('/generate', {
          json_data: jsonData,
          original_filename: 'uploaded_data.json'
        });

        setSuccess(`Fichiers générés avec succès: ${generateResponse.data.files.length} fichier(s)`);
        loadGeneratedFiles();
        setCurrentView('files');
      }
    } catch (err) {
      if (err.response?.data?.errors) {
        setError(err.response.data.errors.join('\n'));
      } else {
        setError(err.response?.data?.error || 'Erreur lors de la génération');
      }
    } finally {
      setLoading(false);
    }
  };

  const updateTemplate = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await axios.put('/template', { template });
      setSuccess('Template mis à jour avec succès');
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la mise à jour');
    } finally {
      setLoading(false);
    }
  };

  const deleteFile = async (fileId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce fichier?')) return;

    try {
      await axios.delete(`/files/${fileId}`);
      setSuccess('Fichier supprimé avec succès');
      loadGeneratedFiles();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la suppression');
    }
  };

  const downloadFile = (fileId) => {
    window.open(`${API_BASE_URL}/files/${fileId}/download`, '_blank');
  };

  const AlertMessage = ({ type, message, onClose }) => {
    if (!message) return null;

    // Choix de l'icône et du style selon le type
    const icon = type === 'success' ? (
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" style={{marginRight: 8}}><circle cx="11" cy="11" r="11" fill="#2ecc40" fillOpacity="0.18"/><path d="M6.5 11.5l3 3 6-6" stroke="#2ecc40" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/></svg>
    ) : (
      <svg width="22" height="22" viewBox="0 0 22 22" fill="none" style={{marginRight: 8}}><circle cx="11" cy="11" r="11" fill="#e74c3c" fillOpacity="0.18"/><path d="M7.5 7.5l7 7M14.5 7.5l-7 7" stroke="#e74c3c" strokeWidth="2.2" strokeLinecap="round"/></svg>
    );

    return (
      <div
        className={`alert alert-${type}`}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '16px 28px 16px 18px',
          borderRadius: 14,
          background: type === 'success'
            ? 'linear-gradient(90deg, #eafff3 0%, #d2fbe7 100%)'
            : 'linear-gradient(90deg, #ffeaea 0%, #fbe2e2 100%)',
          color: type === 'success' ? '#218c5a' : '#b03a2e',
          fontWeight: 600,
          fontSize: 17,
          boxShadow: '0 2px 16px 0 rgba(0,0,0,0.08)',
          position: 'relative',
          margin: '0 auto 18px',
          maxWidth: 520,
          border: '1.5px solid ' + (type === 'success' ? '#2ecc40' : '#e74c3c'),
          animation: 'fadeInAlert 0.7s cubic-bezier(.4,1.6,.6,1)'
        }}
      >
        {icon}
        <span style={{flex: 1, whiteSpace: 'pre-line'}}>{message}</span>
        <button
          onClick={onClose}
          className="alert-close"
          style={{
            background: 'none',
            border: 'none',
            color: '#888',
            fontSize: 22,
            fontWeight: 700,
            cursor: 'pointer',
            marginLeft: 10,
            transition: 'color 0.2s',
            lineHeight: 1
          }}
          aria-label="Fermer"
        >
          ×
        </button>
      </div>
    );
  };

  const HomeView = () => (
    <div className="home-view" style={{ maxWidth: 600, margin: '40px auto', background: '#fff', borderRadius: 18, boxShadow: '0 4px 24px rgba(0,0,0,0.08)', padding: 32 }}>
      <h1 style={{ textAlign: 'center', fontWeight: 600, fontSize: 38, marginBottom: 18, color: '#2a3b4c', letterSpacing: 1 }}>CardReq Maker</h1>
      <div className="action-buttons" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16, marginBottom: 18 }}>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 14, width: '100%' }}>
          <button onClick={() => setCurrentView('json-editor')} className="btn btn-primary home-btn-blue" style={{ minWidth: 180, fontWeight: 600, fontSize: 18 }}>
            Modifier JSON
          </button>
          <button onClick={() => setCurrentView('template')} className="btn btn-primary home-btn-green" style={{ minWidth: 180, fontWeight: 600, fontSize: 18 }}>
            Modifier Template
          </button>
        </div>
        <div style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
          <button onClick={() => setCurrentView('files')} className="btn btn-primary home-btn-purple" style={{ minWidth: 360, fontWeight: 600, fontSize: 18 }}>
            Fichiers Générés
          </button>
        </div>
      </div>
      <div className="upload-section" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, marginTop: 8 }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, width: '100%' }}>
          <h3 style={{ fontSize: 17, margin: 0, color: '#2a3b4c', fontWeight: 600 }}>Charger un fichier JSON</h3>
          <label className="btn home-btn-blue" style={{ cursor: 'pointer', marginBottom: 0, minWidth: 220, textAlign: 'center', fontWeight: 600, fontSize: 16 }}>
            Choisir un fichier JSON
            <input
              type="file"
              accept=".json"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </label>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, width: '100%' }}>
          <h3 style={{ fontSize: 17, margin: 0, color: '#2a3b4c', fontWeight: 600 }}>Charger un nouveau template</h3>
          <label className="btn home-btn-green" style={{ cursor: 'pointer', marginBottom: 0, minWidth: 220, textAlign: 'center', fontWeight: 600, fontSize: 16 }}>
            Choisir un template
            <input
              type="file"
              accept=".json"
              onChange={handleTemplateUpload}
              style={{ display: 'none' }}
            />
          </label>
        </div>
      </div>
    </div>
  );

  const addJsonRow = () => {
    let keys = [];
    if (jsonData.length > 0) {
      keys = Object.keys(jsonData[0]);
    } else if (template.length > 0) {
      keys = template.map(f => f.nom);
    }
    if (keys.length === 0) return;
    const emptyRow = {};
    keys.forEach(key => { emptyRow[key] = ''; });
    setJsonData([...jsonData, emptyRow]);
  };

  const removeJsonRow = (index) => {
    const newData = [...jsonData];
    newData.splice(index, 1);
    setJsonData(newData);
  };

  const JsonEditorView = () => (
    <div className="json-editor-view">
      <h2>Éditeur JSON</h2>
      <div className="json-editor-controls" style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
        <button onClick={() => setCurrentView('home')} className="btn btn-secondary">
          Retour
        </button>
        <button onClick={addJsonRow} className="btn btn-info" disabled={jsonData.length === 0}>
          + Ajouter une ligne
        </button>
        <button onClick={validateAndGenerate} className="btn btn-primary" disabled={loading}>
          {loading ? 'Traitement...' : 'Valider et Générer'}
        </button>
      </div>
      <div className="json-table-container" style={{ overflowX: 'auto', width: '100%', minWidth: 0 }}>
        {jsonData.length > 0 && (
          <div style={{ width: '100%' }}>
            <table className="json-table" style={{ minWidth: 900 }}>
              <thead>
                <tr>
                  {Object.keys(jsonData[0]).map(key => {
                    let type = '';
                    if (template && template.length > 0) {
                      const found = template.find(f => f.nom === key);
                      if (found) type = found.obligatoire;
                    }
                    return (
                      <th key={key} style={{ position: 'relative' }}>
                        <span style={{ marginRight: 6 }}>{key}</span>
                        {type && (
                          <span style={{
                            display: 'inline-block',
                            fontWeight: 700,
                            fontSize: 13,
                            color: type === 'M' ? '#e74c3c' : '#17a2b8',
                            background: type === 'M' ? 'rgba(231,76,60,0.08)' : 'rgba(23,162,184,0.08)',
                            borderRadius: 8,
                            padding: '2px 7px',
                            marginLeft: 2,
                            letterSpacing: 1
                          }} title={type === 'M' ? 'Obligatoire' : 'Optionnel (O)'}>
                            {type === 'M' ? 'Obligatoire' : 'Optionnel'}
                          </span>
                        )}
                      </th>
                    );
                  })}
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {jsonData.map((item, index) => (
                  <tr key={index}>
                    {Object.keys(jsonData[0]).map(key => (
                      <td key={key}>
                        <input
                          type="text"
                          value={item[key] ?? ''}
                          onChange={e => {
                            setJsonData(prev => prev.map((row, i) =>
                              i === index ? { ...row, [key]: e.target.value } : row
                            ));
                          }}
                          className="table-input"
                          style={{ minWidth: 120 }}
                        />
                      </td>
                    ))}
                    <td>
                      <button onClick={() => removeJsonRow(index)} className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 15 }}>Supprimer</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );

  const TemplateView = () => (
    <div className="template-view">
      <h2>Configuration du Template</h2>
      <div className="template-controls">
        <button onClick={() => setCurrentView('home')} className="btn btn-secondary">
          Retour
        </button>
        <button onClick={updateTemplate} className="btn btn-primary" disabled={loading}>
          {loading ? 'Sauvegarde...' : 'Sauvegarder'}
        </button>
        <button
          onClick={() => {
            setTemplate([
              ...template,
              {
                nom: '',
                obligatoire: 'O',
                position: template.length + 1,
                min_longueur: 0,
                max_longueur: 255,
                type: '',
                valeur_defaut: ''
              }
            ]);
          }}
          className="btn btn-info"
          style={{ marginLeft: 10 }}
        >
          + Ajouter un champ
        </button>
      </div>

      <div className="template-table-container" style={{ overflowX: 'auto', width: '100%', minWidth: 0 }}>
        <table className="template-table" style={{ minWidth: 900 }}>
          <thead>
            <tr>
              <th>Nom</th>
              <th>Obligatoire</th>
              <th>Position</th>
              <th>Min Longueur</th>
              <th>Max Longueur</th>
              <th>Type</th>
              <th>Valeur par défaut</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {template.map((field, index) => (
              <tr key={index}>
                <td>
                  <input
                    type="text"
                    value={field.nom}
                    onChange={(e) => {
                      const newTemplate = [...template];
                      newTemplate[index].nom = e.target.value;
                      setTemplate(newTemplate);
                    }}
                    className="table-input"
                  />
                </td>
                <td>
                  <select
                    value={field.obligatoire}
                    onChange={(e) => {
                      const newTemplate = [...template];
                      newTemplate[index].obligatoire = e.target.value;
                      setTemplate(newTemplate);
                    }}
                    className="table-select"
                  >
                    <option value="M">Obligatoire</option>
                    <option value="O">Optionnel</option>
                  </select>
                </td>
                <td>
                  <input
                    type="number"
                    value={field.position}
                    onChange={(e) => {
                      const newTemplate = [...template];
                      newTemplate[index].position = parseInt(e.target.value);
                      setTemplate(newTemplate);
                    }}
                    className="table-input"
                  />
                </td>
                <td>
                  <input
                    type="number"
                    value={field.min_longueur}
                    onChange={(e) => {
                      const newTemplate = [...template];
                      newTemplate[index].min_longueur = parseInt(e.target.value);
                      setTemplate(newTemplate);
                    }}
                    className="table-input"
                  />
                </td>
                <td>
                  <input
                    type="number"
                    value={field.max_longueur}
                    onChange={(e) => {
                      const newTemplate = [...template];
                      newTemplate[index].max_longueur = parseInt(e.target.value);
                      setTemplate(newTemplate);
                    }}
                    className="table-input"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={field.type}
                    onChange={(e) => {
                      const newTemplate = [...template];
                      newTemplate[index].type = e.target.value;
                      setTemplate(newTemplate);
                    }}
                    className="table-input"
                  />
                </td>
                <td>
                  <input
                    type="text"
                    value={field.valeur_defaut || ''}
                    onChange={(e) => {
                      const newTemplate = [...template];
                      newTemplate[index].valeur_defaut = e.target.value || null;
                      setTemplate(newTemplate);
                    }}
                    className="table-input"
                  />
                </td>
                <td>
                  <button
                    className="btn btn-danger"
                    style={{ padding: '4px 10px', fontSize: 15 }}
                    onClick={() => {
                      const newTemplate = template.filter((_, i) => i !== index);
                      setTemplate(newTemplate);
                    }}
                  >
                    Supprimer
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const FilesView = () => (
    <div className="files-view">
      <h2>Fichiers Générés</h2>
      <div className="files-controls">
        <button onClick={() => setCurrentView('home')} className="btn btn-secondary">
          Retour
        </button>
        <button onClick={loadGeneratedFiles} className="btn btn-info">
          Actualiser
        </button>
      </div>

      <div className="files-list">
        {generatedFiles.length === 0 ? (
          <p>Aucun fichier généré</p>
        ) : (
          <table className="files-table">
            <thead>
              <tr>
                <th>Nom du fichier</th>
                <th>Date de génération</th>
                <th>Fichier JSON original</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {generatedFiles.map(file => (
                <tr key={file.id}>
                  <td>{file.filename}</td>
                  <td>{new Date(file.generated_at).toLocaleString()}</td>
                  <td>{file.original_json_name}</td>
                  <td>
                    <button
                      onClick={() => downloadFile(file.id)}
                      className="btn btn-sm btn-info"
                    >
                      Télécharger
                    </button>
                    <button
                      onClick={() => deleteFile(file.id)}
                      className="btn btn-sm btn-danger"
                    >
                      Supprimer
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
   
  return (
    <div className="app">
      <Header />
      <div className="background-dots">
        <div className="dot dot1"></div>
        <div className="dot dot2"></div>
        <div className="dot dot3"></div>
        <div className="dot dot4"></div>
        <div className="dot dot5"></div>
      </div>
      <div className="container">
        {loading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
          </div>
        )}
        {currentView === 'home' && <HomeView />}
        {currentView === 'json-editor' && <JsonEditorView />}
        {currentView === 'template' && <TemplateView />}
        {currentView === 'files' && <FilesView />}
        <AlertMessage
          type="error"
          message={error}
          onClose={() => setError('')}
        />
        <AlertMessage
          type="success"
          message={success}
          onClose={() => setSuccess('')}
        />
      </div>
      <Footer />
    </div>
  );
}

function Footer() {
  return(<footer className="footer">
        <div className="footer-title">
          <span className="footer-brand">CardReq Maker</span>
          <span className="footer-sep">·</span>
          <span className="footer-version">v1.0</span>
        </div>
        <div className="footer-copyright">
          © {new Date().getFullYear()}CardReq Maker
        </div>
      </footer>
  );
}


export default App;