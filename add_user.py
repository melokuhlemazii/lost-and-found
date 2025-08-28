from __init__ import create_app, db
from models import User

print("Starting user creation script...")

app = create_app()

with app.app_context():
    print("App context created")
    
    # Create admin user
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', email='admin@example.com', role='admin', is_verified=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created: username='admin', password='admin123'")
    else:
        print("Admin user already exists")
    
    # Create default student user
    student_user = User.query.filter_by(username='22211013').first()
    if not student_user:
        student_user = User(username='22211013', email='student@example.com', role='student', is_verified=True)
        student_user.set_password('password123')
        db.session.add(student_user)
        db.session.commit()
        print("Student user created: username='22211013', password='password123'")
    else:
        print("Student user '22211013' already exists")
    
    # List all users
    all_users = User.query.all()
    print(f"\nTotal users in database: {len(all_users)}")
    for user in all_users:
        print(f"  - {user.username} ({user.email}) - Role: {user.role}")

print("Script completed!")
