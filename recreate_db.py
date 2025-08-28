import os
from __init__ import create_app, db
from models import User, LostItemModel, FoundItemModel, ClaimModel, Category, Location, SystemSetting
from datetime import datetime, timedelta

# Remove the old database file
db_path = 'instance/site.db'
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print("Old database removed successfully")
    except PermissionError:
        print("Could not remove database file. Please stop the Flask app and try again.")
        exit(1)

# Create the app and database
app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database created successfully with new schema")
    
    # Create default admin user
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', email='admin@example.com', role='admin', is_verified=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: username='admin', password='admin123'")
    else:
        print("Admin user already exists")
    
    # Create default student user
    student_user = User.query.filter_by(username='22211013').first()
    if not student_user:
        student_user = User(username='22211013', email='student@example.com', role='student', is_verified=True)
        student_user.set_password('password123')
        db.session.add(student_user)
        db.session.commit()
        print("Default student user created: username='22211013', password='password123'")
    else:
        print("Student user already exists")
    
    # Create default categories
    default_categories = [
        'Electronics', 'Bags', 'Books', 'Personal Items', 'Clothing', 'Jewelry', 'Sports', 'Other'
    ]
    for cat_name in default_categories:
        if not Category.query.filter_by(name=cat_name).first():
            category = Category(name=cat_name, description=f'Default category for {cat_name.lower()}')
            db.session.add(category)
    db.session.commit()
    print("Default categories created")
    
    # Create default locations
    default_locations = [
        'Library(Steve Biko)', 'Library(M.L. Sultan)', 'IT Labs(Ritson)', 
        'Department Office', 'Library Information Desk'
    ]
    for loc_name in default_locations:
        if not Location.query.filter_by(name=loc_name).first():
            location = Location(name=loc_name, description=f'Default location: {loc_name}')
            db.session.add(location)
    db.session.commit()
    print("Default locations created")
    
    # Create default system settings
    default_settings = [
        ('item_expiry_days', '30', 'Number of days before items expire'),
        ('max_photo_size', '5242880', 'Maximum photo file size in bytes'),
        ('allowed_photo_types', 'jpg,jpeg,png,gif', 'Allowed photo file types'),
        ('site_name', 'Lost and Found Portal', 'Site display name'),
        ('contact_email', 'admin@example.com', 'Contact email for support')
    ]
    for key, value, description in default_settings:
        if not SystemSetting.query.filter_by(key=key).first():
            setting = SystemSetting(key=key, value=value, description=description)
            db.session.add(setting)
    db.session.commit()
    print("Default system settings created")

print("Database recreation completed!") 