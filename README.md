# Lost & Found Portal

A modern Flask web application for managing lost and found items, featuring a fully redesigned Tailwind CSS user interface and robust admin controls.

## Features
- User registration, login, and profile management
- Report lost and found items with photo uploads
- Browse, search, and claim items
- Admin dashboard for managing users, items, claims, categories, locations, and system settings
- Analytics/statistics dashboard for operational insights
- Responsive, accessible UI built with Tailwind CSS

## Tech Stack
- Python 3.13
- Flask & Flask extensions (Flask-Login, Flask-WTF, Flask-SQLAlchemy)
- Tailwind CSS (CDN, plugins)
- SQLite (default, can be swapped)

## Setup
1. **Clone the repository**
   ```sh
   git clone https://github.com/melokuhlemazii/lost-and-found.git
   cd lost-and-found
   ```
2. **Create and activate a virtual environment**
   ```sh
   python -m venv lostandfound
   lostandfound\Scripts\activate
   ```
3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```
4. **Initialize the database**
   ```sh
   python recreate_db.py
   ```
5. **Run the application**
   ```sh
   python app.py
   ```
6. **Access the app**
   - Open [http://localhost:5000](http://localhost:5000) in your browser.

## Folder Structure
```
├── app.py
├── models.py
├── forms.py
├── config.py
├── requirements.txt
├── templates/
│   ├── *.html
├── static/
│   ├── css/
│   ├── images/
│   └── uploads/
├── instance/
│   └── site.db
├── lostandfound/
│   └── ... (venv)
```

## Customization
- **Styling:** All templates use Tailwind CSS. You can further customize colors and layouts in `static/css/` or by editing the HTML templates.
- **Database:** Default is SQLite. To use another DB, update `config.py` and reinitialize.
- **Email:** Email notifications use Flask-Mail. Configure SMTP in `config.py`.

## Contributing
Pull requests and suggestions are welcome! Please open an issue for major changes.

## License
MIT

---
For questions or support, contact the repository owner.
