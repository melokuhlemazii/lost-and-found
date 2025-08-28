#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import sqlite3

# Direct database approach
db_path = 'instance/site.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if not cursor.fetchone():
        print("Users table doesn't exist. Creating it...")
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(80) UNIQUE NOT NULL,
                email VARCHAR(120) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'student',
                is_verified BOOLEAN DEFAULT 0,
                is_banned BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
    
    # Check if student user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", ('22211013',))
    if cursor.fetchone():
        print("Student user '22211013' already exists")
    else:
        # Create student user
        password_hash = generate_password_hash('password123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, is_verified)
            VALUES (?, ?, ?, ?, ?)
        ''', ('22211013', 'student@example.com', password_hash, 'student', 1))
        print("Student user created: username='22211013', password='password123'")
    
    # Check if admin user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", ('admin',))
    if cursor.fetchone():
        print("Admin user 'admin' already exists")
    else:
        # Create admin user
        password_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, is_verified)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@example.com', password_hash, 'admin', 1))
        print("Admin user created: username='admin', password='admin123'")
    
    conn.commit()
    print("Database operations completed successfully!")
    
    # Show all users
    cursor.execute("SELECT username, email, role FROM users")
    users = cursor.fetchall()
    print("\nCurrent users in database:")
    for user in users:
        print(f"  - {user[0]} ({user[1]}) - Role: {user[2]}")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
