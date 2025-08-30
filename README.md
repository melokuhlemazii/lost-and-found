🎒 Campus Lost & Found System

A secure and user-friendly web application that helps students report, track, and claim lost and found items on campus. The system makes it easy for students to recover their belongings and for administrators to manage reports efficiently.

✨ Features

🔑 User Authentication – Secure student login and registration

📋 Report Lost Items – Students can submit details & photos of lost items

📋 Report Found Items – Submit details & location of found items

📦 Claim Items – Students can initiate claims by describing the item

📊 Student Dashboard – View lost/found items and claim status

📷 Image Uploads – Attach photos for better identification

🎨 Responsive UI – Clean design using Bootstrap & TailwindCSS

🛠️ Prerequisites

Python 3.8 or higher

pip (Python package installer)

Flask & SQLAlchemy

⚙️ Installation

Clone the repository:

git clone <repository-url>
cd lost-and-found


Create and activate a virtual environment:

python -m venv venv  

# On Windows
venv\Scripts\activate  

# On MacOS/Linux
source venv/bin/activate  


Install dependencies:

pip install -r requirements.txt


Initialize the database:

flask db init
flask db migrate -m "Initial migration"
flask db upgrade

🔧 Configuration

The application uses the following default settings:

Database: SQLite (lostandfound.db)

Admin credentials: configurable in config.py

Environment variables:

FLASK_APP=app.py

FLASK_ENV=development

For production deployment, update database and email settings in config.py.

🚀 Running the Application

Start the Flask development server:

flask run


Open your browser and navigate to:
👉 http://localhost:5000

📌 Usage
For Students

Register with your student email

Login with your credentials

Report lost or found items with details & images

Track the status of claims through your dashboard

For Administrators

Review and manage reported items

Verify and approve claims

Monitor system statistics

🔒 Security Features

Password hashing with Werkzeug

CSRF protection (Flask-WTF)

Email validation with email_validator

Secure session management

📸 Screenshots

(Add screenshots here to showcase the UI)

Student Dashboard

Report Lost Item Form

Claim Item Form

Admin View

📌 Roadmap / Future Enhancements

✅ Search & filter by category/location

🔔 Email notifications when items match

📊 Analytics dashboard with item statistics

📱 Mobile-first optimizations

🌍 Deployment to Heroku/Vercel for live use

🤝 Contributing

Fork the repository

Create a feature branch

Commit your changes

Push to your branch

Create a Pull Request

📜 License

This project is licensed under the MIT License – see the LICENSE file for details.
