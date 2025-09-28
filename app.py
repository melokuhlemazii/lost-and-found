from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from __init__ import create_app, db
from forms import (LostItem, FoundItem, Claim, LoginForm, RegistrationForm,
                   AdminItemStatusForm, AdminClaimForm, EditItemForm, BulkActionForm,
                   UserManagementForm, CategoryForm, LocationForm, SystemSettingForm, SearchForm,
                   ProfileEditForm, PasswordChangeForm, ItemSearchForm)
from models import (LostItemModel, FoundItemModel, ClaimModel, User, Category,
                   Location, SystemSetting, UserActivity, ClaimHistory)
import os
from datetime import datetime, timedelta
import json

load_dotenv()

app = create_app()

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need admin privileges to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def log_activity(user_id, action, details=None, ip_address=None):
    """Log user activity"""
    activity = UserActivity(
        user_id=user_id,
        action=action,
        details=details,
        ip_address=ip_address
    )
    db.session.add(activity)
    db.session.commit()


@app.route('/')
def index():
    # Get recent items for display on home page
    recent_lost = LostItemModel.query.filter_by(status='active').order_by(LostItemModel.created_at.desc()).limit(6).all()
    recent_found = FoundItemModel.query.filter_by(status='active').order_by(FoundItemModel.created_at.desc()).limit(6).all()
    
    return render_template('home.html', 
                         title='Home',
                         recent_lost=recent_lost,
                         recent_found=recent_found)

@app.route('/home')
def home():
    # Get recent items for display on home page
    recent_lost = LostItemModel.query.filter_by(status='active').order_by(LostItemModel.created_at.desc()).limit(6).all()
    recent_found = FoundItemModel.query.filter_by(status='active').order_by(FoundItemModel.created_at.desc()).limit(6).all()
    
    return render_template('home.html', 
                         title='Home',
                         recent_lost=recent_lost,
                         recent_found=recent_found)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect based on user role
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_banned:
                flash('Your account has been banned. Please contact administrator.', 'error')
                return render_template('login.html', title='Login', form=form)
            
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_activity(user.id, 'login', ip_address=request.remote_addr)
            flash('Login successful!', 'success')
            
            # Redirect based on user role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # Redirect based on user role
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Check if username or email already exists
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists', 'error')
                return render_template('register.html', title='Register', form=form)
            
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered', 'error')
                return render_template('register.html', title='Register', form=form)
            
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            log_activity(user.id, 'register', ip_address=request.remote_addr)
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
            # Log the actual error for debugging (in production, be careful about what you log)
            app.logger.error(f'Registration error: {str(e)}')
    
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'logout', ip_address=request.remote_addr)
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# User Dashboard Routes
@app.route('/dashboard')
@login_required
def user_dashboard():
    # Get user's submitted items
    user_lost_items = LostItemModel.query.filter_by(
        student_email=current_user.email
    ).order_by(LostItemModel.created_at.desc()).limit(10).all()
    
    user_found_items = FoundItemModel.query.filter_by(
        student_email=current_user.email
    ).order_by(FoundItemModel.created_at.desc()).limit(10).all()
    
    # Get user's claims
    user_claims = ClaimModel.query.filter_by(
        student_email=current_user.email
    ).order_by(ClaimModel.created_at.desc()).limit(10).all()
    
    # Get user's recent activity
    user_activities = UserActivity.query.filter_by(
        user_id=current_user.id
    ).order_by(UserActivity.created_at.desc()).limit(10).all()
    
    return render_template('user_dashboard.html',
                         title='My Dashboard',
                         user_lost_items=user_lost_items,
                         user_found_items=user_found_items,
                         user_claims=user_claims,
                         user_activities=user_activities)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    form = ProfileEditForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if username or email already exists (excluding current user)
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already exists', 'error')
            return render_template('profile.html', title='Profile', form=form)
        
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email and existing_email.id != current_user.id:
            flash('Email already registered', 'error')
            return render_template('profile.html', title='Profile', form=form)
        
        form.populate_obj(current_user)
        db.session.commit()
        
        log_activity(current_user.id, 'update_profile')
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_profile'))
    
    return render_template('profile.html', title='Profile', form=form)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'error')
            return render_template('change_password.html', title='Change Password', form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        log_activity(current_user.id, 'change_password')
        flash('Password changed successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('change_password.html', title='Change Password', form=form)

# Item Browsing Routes
@app.route('/lost-items')
def browse_lost_items():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', 'all')
    search_query = request.args.get('query', '')
    
    query = LostItemModel.query.filter_by(status='active')
    
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    if search_query:
        query = query.filter(
            LostItemModel.item_name.contains(search_query) |
            LostItemModel.description.contains(search_query) |
            LostItemModel.location.contains(search_query)
        )
    
    items = query.order_by(LostItemModel.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)
    
    return render_template('browse_lost.html',
                         title='Lost Items',
                         items=items,
                         category_filter=category_filter,
                         search_query=search_query)

@app.route('/found-items')
def browse_found_items():
    page = request.args.get('page', 1, type=int)
    category_filter = request.args.get('category', 'all')
    search_query = request.args.get('query', '')
    
    query = FoundItemModel.query.filter_by(status='active')
    
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    if search_query:
        query = query.filter(
            FoundItemModel.item_name.contains(search_query) |
            FoundItemModel.description.contains(search_query) |
            FoundItemModel.location.contains(search_query)
        )
    
    items = query.order_by(FoundItemModel.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)
    
    return render_template('browse_found.html',
                         title='Found Items',
                         items=items,
                         category_filter=category_filter,
                         search_query=search_query)

# Item Detail Routes
@app.route('/item/lost/<int:item_id>')
def lost_item_detail(item_id):
    item = LostItemModel.query.get_or_404(item_id)
    return render_template('item_detail.html',
                         title=f'Lost Item: {item.item_name}',
                         item=item,
                         item_type='lost')

@app.route('/item/found/<int:item_id>')
def found_item_detail(item_id):
    item = FoundItemModel.query.get_or_404(item_id)
    return render_template('item_detail.html',
                         title=f'Found Item: {item.item_name}',
                         item=item,
                         item_type='found')

# Search Routes
@app.route('/search')
def search_items():
    form = ItemSearchForm()
    results = {'lost': [], 'found': []}
    
    if form.validate_on_submit() or request.args.get('query'):
        query = form.query.data or request.args.get('query', '')
        category = form.category.data or request.args.get('category', 'all')
        item_type = form.item_type.data or request.args.get('item_type', 'all')
        
        if item_type in ['all', 'lost']:
            lost_query = LostItemModel.query.filter_by(status='active')
            if category != 'all':
                lost_query = lost_query.filter_by(category=category)
            if query:
                lost_query = lost_query.filter(
                    LostItemModel.item_name.contains(query) |
                    LostItemModel.description.contains(query) |
                    LostItemModel.location.contains(query)
                )
            results['lost'] = lost_query.order_by(LostItemModel.created_at.desc()).limit(20).all()
        
        if item_type in ['all', 'found']:
            found_query = FoundItemModel.query.filter_by(status='active')
            if category != 'all':
                found_query = found_query.filter_by(category=category)
            if query:
                found_query = found_query.filter(
                    FoundItemModel.item_name.contains(query) |
                    FoundItemModel.description.contains(query) |
                    FoundItemModel.location.contains(query)
                )
            results['found'] = found_query.order_by(FoundItemModel.created_at.desc()).limit(20).all()
    
    return render_template('search_results.html',
                         title='Search Results',
                         form=form,
                         results=results)

# File serving route for photos
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/report-lost-item', methods=['GET', 'POST'])
@login_required
def report_lost_item():
    form = LostItem()
    if form.validate_on_submit():
        item_name = form.item_name.data
        category = form.category.data
        description = form.description.data
        location = form.location.data
        full_names = form.full_names.data
        student_number = form.student_number.data
        student_email = form.student_email.data

        photo_filename = None
        if form.photo.data:
            photo_file = form.photo.data
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
            photo_file.save(photo_path)

        #save to database
        lost_item = LostItemModel(
            item_name=item_name,
            category=category,
            description=description,
            location=location,
            full_names=full_names,
            student_number=student_number,
            student_email=student_email,
            photo_filename=photo_filename
        )
        db.session.add(lost_item)
        db.session.commit()

        log_activity(current_user.id, 'report_lost_item', f'Reported lost item: {item_name}')
        flash('Lost item reported successfully!', 'success')
        return redirect(url_for('home'))

    return render_template('report_lost_item.html', title='Report Lost Item', form=form)

@app.route('/report-found-item', methods=['GET', 'POST'])
@login_required
def report_found_item():
    form = FoundItem()
    if form.validate_on_submit():
        item_name = form.item_name.data
        category = form.category.data
        description = form.description.data
        location = form.location.data
        full_names = form.full_names.data
        student_number = form.student_number.data
        student_email = form.student_email.data
        current_location = form.current_location.data

        # Handle photo upload
        photo_filename = None
        if form.photo.data:
            photo_file = form.photo.data
            photo_filename = secure_filename(photo_file.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], photo_filename)
            photo_file.save(photo_path)

        #(later you can store this in a DB)
        found_item = FoundItemModel(
            item_name=item_name,
            category=category,
            description=description,
            location=location,
            full_names=full_names,
            student_number=student_number,
            student_email=student_email,
            current_location=current_location,
            photo_filename=photo_filename
        )
        db.session.add(found_item)
        db.session.commit()

        log_activity(current_user.id, 'report_found_item', f'Reported found item: {item_name}')
        flash('Found item reported successfully!', 'success')
        return redirect(url_for('home'))  # After success

    return render_template('report_found_item.html', title='Report Found Item', form=form)

@app.route('/claim', methods=['GET', 'POST'])
@login_required
def claim():
    form = Claim()
    
    # Pre-fill form if item information is provided in URL
    if request.method == 'GET':
        item_type = request.args.get('item_type')
        item_id = request.args.get('item_id')
        if item_type and item_id:
            form.item_type.data = item_type
            form.item_id.data = item_id
    
    if form.validate_on_submit():
        full_names = form.full_names.data
        student_number = form.student_number.data
        student_email = form.student_email.data
        description = form.description.data
        item_type = form.item_type.data
        item_id = form.item_id.data
        
        claim = ClaimModel(
            full_names=full_names,
            student_number=student_number,
            student_email=student_email,
            description=description,
            item_type=item_type,
            item_id=item_id if item_id else None
        )
        
        db.session.add(claim)
        db.session.commit()
        
        # Log claim history
        history = ClaimHistory(
            claim_id=claim.id,
            action='created',
            notes='Claim submitted'
        )
        db.session.add(history)
        db.session.commit()
        
        log_activity(current_user.id, 'submit_claim', f'Submitted claim for {item_type} item')
        flash('Claim submitted successfully! Admin will review your claim.', 'success')
        return redirect(url_for('home'))
    
    return render_template('claim.html', title='Claim', form=form)

# Admin Dashboard Routes
@app.route('/admin_dashboard')
@login_required
@admin_required
def admin_dashboard():
    # Get statistics
    total_lost = LostItemModel.query.count()
    total_found = FoundItemModel.query.count()
    total_claims = ClaimModel.query.count()
    pending_claims = ClaimModel.query.filter_by(status='pending').count()
    active_lost = LostItemModel.query.filter_by(status='active').count()
    active_found = FoundItemModel.query.filter_by(status='active').count()
    
    # Recent items
    recent_lost = LostItemModel.query.order_by(LostItemModel.created_at.desc()).limit(5).all()
    recent_found = FoundItemModel.query.order_by(FoundItemModel.created_at.desc()).limit(5).all()
    recent_claims = ClaimModel.query.order_by(ClaimModel.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html', 
                         title='Admin Dashboard',
                         total_lost=total_lost,
                         total_found=total_found,
                         total_claims=total_claims,
                         pending_claims=pending_claims,
                         active_lost=active_lost,
                         active_found=active_found,
                         recent_lost=recent_lost,
                         recent_found=recent_found,
                         recent_claims=recent_claims)

@app.route('/admin/lost-items')
@login_required
@admin_required
def admin_lost_items():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')
    
    query = LostItemModel.query
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(getattr(LostItemModel, sort_by).desc())
    else:
        query = query.order_by(getattr(LostItemModel, sort_by).asc())
    
    items = query.paginate(page=page, per_page=20, error_out=False)
    
    form = AdminItemStatusForm()
    
    return render_template('admin_lost_items.html', 
                         title='Manage Lost Items',
                         items=items,
                         form=form,
                         status_filter=status_filter,
                         category_filter=category_filter,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/admin/found-items')
@login_required
@admin_required
def admin_found_items():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    category_filter = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')
    
    query = FoundItemModel.query
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(getattr(FoundItemModel, sort_by).desc())
    else:
        query = query.order_by(getattr(FoundItemModel, sort_by).asc())
    
    items = query.paginate(page=page, per_page=20, error_out=False)
    
    form = AdminItemStatusForm()
    
    return render_template('admin_found_items.html', 
                         title='Manage Found Items',
                         items=items,
                         form=form,
                         status_filter=status_filter,
                         category_filter=category_filter,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/admin/claims')
@login_required
@admin_required
def admin_claims():
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    item_type_filter = request.args.get('item_type', 'all')
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')
    
    query = ClaimModel.query
    
    # Apply filters
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    if item_type_filter != 'all':
        query = query.filter_by(item_type=item_type_filter)
    
    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(getattr(ClaimModel, sort_by).desc())
    else:
        query = query.order_by(getattr(ClaimModel, sort_by).asc())
    
    claims = query.paginate(page=page, per_page=20, error_out=False)
    
    form = AdminClaimForm()
    
    return render_template('admin_claims.html', 
                         title='Manage Claims',
                         claims=claims,
                         form=form,
                         status_filter=status_filter,
                         item_type_filter=item_type_filter,
                         sort_by=sort_by,
                         sort_order=sort_order)

@app.route('/admin/update-item-status/<item_type>/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def admin_update_item_status(item_type, item_id):
    form = AdminItemStatusForm()
    if form.validate_on_submit():
        if item_type == 'lost':
            item = LostItemModel.query.get_or_404(item_id)
        else:
            item = FoundItemModel.query.get_or_404(item_id)
        
        item.status = form.status.data
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, f'update_{item_type}_status', f'Updated {item_type} item {item_id} status to {form.status.data}')
        flash(f'{item_type.title()} item status updated successfully!', 'success')
    else:
        flash('Invalid form data', 'error')
    
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin/update-claim/<int:claim_id>', methods=['POST'])
@login_required
@admin_required
def admin_update_claim(claim_id):
    try:
        claim = ClaimModel.query.get_or_404(claim_id)
        old_status = claim.status
        
        # Get form data directly from request
        new_status = request.form.get('status')
        admin_notes = request.form.get('admin_notes', '').strip()
        
        # Validate status
        if new_status not in ['pending', 'approved', 'rejected']:
            flash('Invalid status selected', 'error')
            return redirect(request.referrer or url_for('admin_claims'))
        
        # Update claim
        claim.status = new_status
        claim.admin_notes = admin_notes if admin_notes else None
        claim.updated_at = datetime.utcnow()
        
        # If claim is approved, update the related item status
        if new_status == 'approved' and claim.item_id:
            if claim.item_type == 'lost':
                item = LostItemModel.query.get(claim.item_id)
            else:
                item = FoundItemModel.query.get(claim.item_id)
            
            if item:
                item.status = 'claimed'
                item.updated_at = datetime.utcnow()
        
        # Log claim history
        history = ClaimHistory(
            claim_id=claim.id,
            admin_id=current_user.id,
            action=new_status,
            notes=admin_notes
        )
        db.session.add(history)
        db.session.commit()
        
        log_activity(current_user.id, 'update_claim', f'Updated claim {claim_id} from {old_status} to {new_status}')
        flash('Claim status updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating the claim. Please try again.', 'error')
        app.logger.error(f'Error updating claim {claim_id}: {str(e)}')
    
    return redirect(request.referrer or url_for('admin_claims'))

@app.route('/admin/delete-item/<item_type>/<int:item_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_item(item_type, item_id):
    if item_type == 'lost':
        item = LostItemModel.query.get_or_404(item_id)
    else:
        item = FoundItemModel.query.get_or_404(item_id)
    
    # Delete associated photo if exists
    if item.photo_filename:
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], item.photo_filename)
        if os.path.exists(photo_path):
            os.remove(photo_path)
    
    db.session.delete(item)
    db.session.commit()
    
    log_activity(current_user.id, f'delete_{item_type}_item', f'Deleted {item_type} item {item_id}')
    flash(f'{item_type.title()} item deleted successfully!', 'success')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin/delete-claim/<int:claim_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_claim(claim_id):
    claim = ClaimModel.query.get_or_404(claim_id)
    db.session.delete(claim)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_claim', f'Deleted claim {claim_id}')
    flash('Claim deleted successfully!', 'success')
    return redirect(request.referrer or url_for('admin_dashboard'))

@app.route('/admin/statistics')
@login_required
@admin_required
def admin_statistics():
    # Get detailed statistics
    lost_by_status = db.session.query(
        LostItemModel.status, 
        db.func.count(LostItemModel.id)
    ).group_by(LostItemModel.status).all()
    
    found_by_status = db.session.query(
        FoundItemModel.status, 
        db.func.count(FoundItemModel.id)
    ).group_by(FoundItemModel.status).all()
    
    claims_by_status = db.session.query(
        ClaimModel.status, 
        db.func.count(ClaimModel.id)
    ).group_by(ClaimModel.status).all()
    
    lost_by_category = db.session.query(
        LostItemModel.category, 
        db.func.count(LostItemModel.id)
    ).group_by(LostItemModel.category).all()
    
    found_by_category = db.session.query(
        FoundItemModel.category, 
        db.func.count(FoundItemModel.id)
    ).group_by(FoundItemModel.category).all()
    
    return render_template('admin_statistics.html',
                         title='Statistics Dashboard',
                         lost_by_status=lost_by_status,
                         found_by_status=found_by_status,
                         claims_by_status=claims_by_status,
                         lost_by_category=lost_by_category,
                         found_by_category=found_by_category)

# New Admin Routes for Advanced Features

@app.route('/admin/edit-item/<item_type>/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_item(item_type, item_id):
    if item_type == 'lost':
        item = LostItemModel.query.get_or_404(item_id)
    else:
        item = FoundItemModel.query.get_or_404(item_id)
    
    form = EditItemForm(obj=item)
    
    if form.validate_on_submit():
        form.populate_obj(item)
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, f'edit_{item_type}_item', f'Edited {item_type} item {item_id}')
        flash(f'{item_type.title()} item updated successfully!', 'success')
        return redirect(url_for(f'admin_{item_type}_items'))
    
    return render_template('admin_edit_item.html', 
                         title=f'Edit {item_type.title()} Item',
                         form=form,
                         item=item,
                         item_type=item_type)

@app.route('/admin/bulk-action/<item_type>', methods=['POST'])
@login_required
@admin_required
def admin_bulk_action(item_type):
    form = BulkActionForm()
    if form.validate_on_submit():
        item_ids = json.loads(form.item_ids.data)
        action = form.action.data
        
        if item_type == 'lost':
            items = LostItemModel.query.filter(LostItemModel.id.in_(item_ids)).all()
        else:
            items = FoundItemModel.query.filter(FoundItemModel.id.in_(item_ids)).all()
        
        for item in items:
            if action == 'delete':
                if item.photo_filename:
                    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], item.photo_filename)
                    if os.path.exists(photo_path):
                        os.remove(photo_path)
                db.session.delete(item)
            elif action == 'approve':
                item.is_verified = True
            elif action == 'reject':
                item.is_verified = False
            elif action == 'expire':
                item.status = 'expired'
            elif action == 'verify':
                item.is_verified = True
        
        db.session.commit()
        
        log_activity(current_user.id, f'bulk_{action}_{item_type}', f'Applied {action} to {len(items)} {item_type} items')
        flash(f'Bulk action "{action}" applied to {len(items)} items successfully!', 'success')
    
    return redirect(request.referrer or url_for('admin_dashboard'))


from forms import DeleteUserForm

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20, error_out=False)
    delete_forms = {user.id: DeleteUserForm() for user in users.items}
    return render_template('admin_users.html',
                         title='Manage Users',
                         users=users,
                         delete_forms=delete_forms)

@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserManagementForm(obj=user)
    
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        
        log_activity(current_user.id, 'edit_user', f'Edited user {user_id}')
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_users'))
    
    return render_template('admin_edit_user.html',
                         title='Edit User',
                         form=form,
                         user=user)

@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the current user
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin_users'))
    
    # Prevent deleting the main admin user (you might want to adjust this logic)
    if user.username == 'admin' and user.role == 'admin':
        flash('You cannot delete the main admin user.', 'error')
        return redirect(url_for('admin_users'))
    
    # Delete all user activities for this user first
    UserActivity.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    
    log_activity(current_user.id, 'delete_user', f'Deleted user {user_id}')
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_create_user():
    form = RegistrationForm()
    # Remove the confirm_password field from the form since it's not needed for admin creation
    del form.confirm_password
    
    if form.validate_on_submit():
        try:
            # Check if username or email already exists
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already exists', 'error')
                return render_template('admin_create_user.html', title='Create User', form=form)
            
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered', 'error')
                return render_template('admin_create_user.html', title='Create User', form=form)
            
            user = User(
                username=form.username.data,
                email=form.email.data,
                role=form.role.data
            )
            
            # Generate a random password for the new user
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(12))
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            log_activity(current_user.id, 'create_user', f'Created user {user.id}')
            flash(f'User created successfully! Temporary password: {password}', 'success')
            return redirect(url_for('admin_users'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during user creation. Please try again.', 'error')
            app.logger.error(f'User creation error: {str(e)}')
    
    return render_template('admin_create_user.html', title='Create User', form=form)

@app.route('/admin/categories')
@login_required
@admin_required
def admin_categories():
    categories = Category.query.all()
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            is_active=form.is_active.data
        )
        db.session.add(category)
        db.session.commit()
        
        log_activity(current_user.id, 'add_category', f'Added category: {form.name.data}')
        flash('Category added successfully!', 'success')
        return redirect(url_for('admin_categories'))
    
    return render_template('admin_categories.html',
                         title='Manage Categories',
                         categories=categories,
                         form=form)

@app.route('/admin/locations')
@login_required
@admin_required
def admin_locations():
    locations = Location.query.all()
    form = LocationForm()
    
    if form.validate_on_submit():
        location = Location(
            name=form.name.data,
            description=form.description.data,
            is_active=form.is_active.data
        )
        db.session.add(location)
        db.session.commit()
        
        log_activity(current_user.id, 'add_location', f'Added location: {form.name.data}')
        flash('Location added successfully!', 'success')
        return redirect(url_for('admin_locations'))
    
    return render_template('admin_locations.html',
                         title='Manage Locations',
                         locations=locations,
                         form=form)

@app.route('/admin/settings')
@login_required
@admin_required
def admin_settings():
    settings = SystemSetting.query.all()
    form = SystemSettingForm()
    
    if form.validate_on_submit():
        setting = SystemSetting(
            key=form.key.data,
            value=form.value.data,
            description=form.description.data
        )
        db.session.add(setting)
        db.session.commit()
        
        log_activity(current_user.id, 'add_setting', f'Added setting: {form.key.data}')
        flash('Setting added successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    return render_template('admin_settings.html',
                         title='System Settings',
                         settings=settings,
                         form=form)

@app.route('/admin/activity-logs')
@login_required
@admin_required
def admin_activity_logs():
    page = request.args.get('page', 1, type=int)
    activities = UserActivity.query.order_by(UserActivity.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False)
    
    return render_template('admin_activity_logs.html',
                         title='Activity Logs',
                         activities=activities)

@app.route('/admin/search')
@login_required
@admin_required
def admin_search():
    form = SearchForm()
    results = []
    
    if form.validate_on_submit():
        query = form.query.data
        search_type = form.search_type.data
        
        if search_type == 'items':
            # Search in both lost and found items
            lost_items = LostItemModel.query.filter(
                LostItemModel.item_name.contains(query) |
                LostItemModel.description.contains(query) |
                LostItemModel.full_names.contains(query)
            ).all()
            
            found_items = FoundItemModel.query.filter(
                FoundItemModel.item_name.contains(query) |
                FoundItemModel.description.contains(query) |
                FoundItemModel.full_names.contains(query)
            ).all()
            
            results = {'lost': lost_items, 'found': found_items}
            
        elif search_type == 'users':
            results = User.query.filter(
                User.username.contains(query) |
                User.email.contains(query)
            ).all()
            
        elif search_type == 'claims':
            results = ClaimModel.query.filter(
                ClaimModel.full_names.contains(query) |
                ClaimModel.description.contains(query)
            ).all()
    
    return render_template('admin_search.html',
                         title='Search',
                         form=form,
                         results=results)

@app.route('/admin/expire-old-items')
@login_required
@admin_required
def admin_expire_old_items():
    # Auto-expire items older than 30 days
    expiry_date = datetime.utcnow() - timedelta(days=30)
    
    lost_items = LostItemModel.query.filter(
        LostItemModel.created_at < expiry_date,
        LostItemModel.status == 'active'
    ).all()
    
    found_items = FoundItemModel.query.filter(
        FoundItemModel.created_at < expiry_date,
        FoundItemModel.status == 'active'
    ).all()
    
    for item in lost_items + found_items:
        item.status = 'expired'
        item.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    log_activity(current_user.id, 'expire_old_items', f'Expired {len(lost_items)} lost and {len(found_items)} found items')
    flash(f'Expired {len(lost_items)} lost items and {len(found_items)} found items successfully!', 'success')
    
    return redirect(url_for('admin_dashboard'))

# Temporary route to create default users
@app.route('/create-default-users')
def create_default_users():
    try:
        # Create admin user
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', email='admin@example.com', role='admin', is_verified=True)
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            admin_created = True
        else:
            admin_created = False
        
        # Create student user
        student_user = User.query.filter_by(username='22211013').first()
        if not student_user:
            student_user = User(username='22211013', email='student@example.com', role='student', is_verified=True)
            student_user.set_password('password123')
            db.session.add(student_user)
            db.session.commit()
            student_created = True
        else:
            student_created = False
        
        # Get all users
        all_users = User.query.all()
        
        result = f"""
        <h2>User Creation Results</h2>
        <p>Admin user {'created' if admin_created else 'already exists'}: username='admin', password='admin123'</p>
        <p>Student user {'created' if student_created else 'already exists'}: username='22211013', password='password123'</p>
        
        <h3>All Users in Database:</h3>
        <ul>
        """
        
        for user in all_users:
            result += f"<li>{user.username} ({user.email}) - Role: {user.role}</li>"
        
        result += "</ul><p><a href='/'>Go to Home</a></p>"
        
        return result
        
    except Exception as e:
        return f"Error creating users: {str(e)}"

if __name__ == '__main__':
    app.run(debug=False)





