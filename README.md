
```markdown
# 💳 Bank Card Application File Generator

A modern, full-stack web application for generating standardized bank card request files from user data and customizable templates.

This tool simplifies the process of creating correctly formatted `.txt` files (like `output_powercard.txt`) that follow specific rules for field length, type, and required values — commonly used in banking and enterprise systems.

---

## 🧩 Why Use This Tool?

Manually generating bank card application files is time-consuming and error-prone. This app automates the process by:

- Allowing users to import data from `.csv` or `.json` files
- Validating all fields against a template (types, lengths, required)
- Applying default values when needed
- Saving all generated codes in a persistent database
- Exporting a clean, structured text file for submission

---

## 🚀 Features

- 📂 **Import Data**: Supports `.json` and `.csv` uploads
- 🧩 **Flexible Template**: Customize fields (name, length, type, required, default)
- ✅ **Validation Engine**: Enforces type and length rules with feedback
- 💾 **SQLite Database**: Stores all generated entries and their associated codes
- ⚙️ **Smart File Generation**: Outputs a bank-ready `output_powercard.txt`
- 🖥️ **Modern Frontend**: Built with React and Tailwind CSS for ease of use
- 🔁 **RESTful API**: Flask backend with organized endpoints and clean separation of logic

---

## 🧰 Tech Stack

### Frontend
- React (Hooks + functional components)
- Axios (for API communication)
- Tailwind CSS (for modern styling)

### Backend
- Python + Flask
- Flask-CORS (for cross-origin API requests)
- SQLAlchemy (ORM for SQLite database)
- Faker (for generating test data)

### Database
- SQLite (local development)

---

## 📂 Project Structure

```

Bank-Card-Application-File-Generator/
├── frontend/              # React app
│   ├── src/
│   │   ├── components/    # Upload UI, form generator, etc.
│   │   └── App.js
│   └── public/
├── backend/               # Flask app
│   ├── PowerCARDGenerator.py
│   ├── database.py
│   ├── models.py
│   └── app.py             # Main Flask app

````

---

## 📦 Installation

### Step 1: Clone the repository
```bash
git clone https://github.com/Moussa018/Bank-Card-Application-File-Generator.git
cd Bank-Card-Application-File-Generator
````

### Step 2: Set up the backend (Flask)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The API should now be running at `http://localhost:5000`.

### Step 3: Set up the frontend (React)

```bash
cd ../frontend
npm install
npm start
```

The React app will open in your browser at `http://localhost:3000`.

---

## 📝 How It Works

1. Upload a data file (`.json` or `.csv`)
2. Modify or confirm the field template
3. Click **Generate** to create your `output_powercard.txt`
4. All generated records are saved in the database with tracking codes
5. Download or inspect the final file

---

## 🧪 Example Template Field

Each field in the template has the following structure:

```json
{
  "name": "record_type",
  "required": true,
  "length": 2,
  "type": "AN",        // A: alpha, N: numeric, AN: alphanumeric
  "default": "DT"
}
```

This ensures the generator only outputs well-structured, valid lines.

---

## 🧠 Use Cases

* Banks needing to batch-submit card application files
* FinTech tools needing to pre-format data for legacy systems
* Training / simulation tools for developers working on financial data pipelines

---

## 💡 Future Improvements

* User authentication and roles
* Live preview of generated output
* Exporting to other formats (XML, Excel)
* Multi-language support (English, French...)

---

## 🙋‍♂️ Author

Created with ❤️ by **Moussa Mohammed Nour**
🔗 GitHub: [Moussa018](https://github.com/Moussa018)

---


