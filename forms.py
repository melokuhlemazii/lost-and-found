from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField, PasswordField, HiddenField, BooleanField, DateField, IntegerField
from wtforms.validators import DataRequired, InputRequired, Length, Email, EqualTo, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('student', 'Student'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    submit = SubmitField('Register')

class ProfileEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class LostItem(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('select_category', 'Select Category'),
        ('electronics', 'Electronics'),
        ('bags', 'Bags'),
        ('books', 'Books'),
        ('personal_items', 'Personal Items'),
        ('clothing', 'Clothing'),
        ('jewelry', 'Jewelry'),
        ('sports', 'Sports'),
        ('other', 'Other')])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    location = SelectField('Where did you lose it?', choices=[
        ('select_location', 'Select Location'),
        ('library_steve_biko', 'Library(Steve Biko)'),
        ('library_ml_sultan', 'Library(M.L. Sultan)'),
        ('it_labs_ritson', 'IT Labs(Ritson)')
    ])
    full_names = StringField('Full Names', validators=[DataRequired()])
    student_number = StringField('Student Number', validators=[DataRequired()])
    student_email = StringField('Student Email', validators=[DataRequired()])
    submit = SubmitField('Submit Lost Item')
    photo = FileField('Upload Item Photo')

class FoundItem(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('', ''),
        ('electronics', 'Electronics'),
        ('bags', 'Bags'),
        ('books', 'Books'),
        ('personal_items', 'Personal Items'),
        ('clothing', 'Clothing'),
        ('jewelry', 'Jewelry'),
        ('sports', 'Sports'),
        ('other', 'Other')])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    location = SelectField('Where did you find it?', choices=[
        ('select_location', 'Select Location'),
        ('library_steve_biko', 'Library(Steve Biko)'),
        ('library_ml_sultan', 'Library(M.L. Sultan)'),
        ('it_labs_ritson', 'IT Labs(Ritson)')
    ])
    full_names = StringField('Full Names', validators=[DataRequired()])
    student_number = StringField('Student Number', validators=[DataRequired()])
    student_email = StringField('Student Email', validators=[DataRequired()])
    current_location = SelectField('Where is it now?', choices=[
        ('select_location', 'Select Location'),
        ('i_have_it_with_me', 'I have it with me'),
        ('department_office', 'Department Office'),
        ('library_information_desk', 'Library Information Desk')
    ])
    submit = SubmitField('Submit Found Item')
    photo = FileField('Upload Item Photo')    

class Claim(FlaskForm):
    full_names = StringField('Full Names', validators=[DataRequired()])
    student_number = StringField('Student Number', validators=[DataRequired()])
    student_email = StringField('Student Email', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    item_type = SelectField('Item Type', choices=[
        ('lost', 'Lost Item'),
        ('found', 'Found Item')
    ], validators=[DataRequired()])
    item_id = HiddenField('Item ID')
    submit = SubmitField('Claim Item')

class AdminItemStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('claimed', 'Claimed'),
        ('returned', 'Returned'),
        ('expired', 'Expired')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Status')

class AdminClaimForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], validators=[DataRequired()])
    admin_notes = TextAreaField('Admin Notes', validators=[Length(max=500)])
    submit = SubmitField('Update Claim')

class EditItemForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    location = StringField('Location', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('claimed', 'Claimed'),
        ('returned', 'Returned'),
        ('expired', 'Expired')
    ], validators=[DataRequired()])
    is_verified = BooleanField('Verified')
    expires_at = DateField('Expires At', validators=[Optional()])
    submit = SubmitField('Update Item')

class BulkActionForm(FlaskForm):
    action = SelectField('Action', choices=[
        ('delete', 'Delete Selected'),
        ('approve', 'Approve Selected'),
        ('reject', 'Reject Selected'),
        ('expire', 'Mark as Expired'),
        ('verify', 'Verify Selected')
    ], validators=[DataRequired()])
    item_ids = HiddenField('Selected Items')
    submit = SubmitField('Apply Bulk Action')

class UserManagementForm(FlaskForm):
    is_verified = BooleanField('Verified')
    is_banned = BooleanField('Banned')
    role = SelectField('Role', choices=[
        ('student', 'Student'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    submit = SubmitField('Update User')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=50)])
    description = TextAreaField('Description', validators=[Length(max=200)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Category')

class LocationForm(FlaskForm):
    name = StringField('Location Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Length(max=200)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Location')

class SystemSettingForm(FlaskForm):
    key = StringField('Setting Key', validators=[DataRequired(), Length(max=100)])
    value = TextAreaField('Value', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=200)])
    submit = SubmitField('Save Setting')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    search_type = SelectField('Search Type', choices=[
        ('items', 'Items'),
        ('users', 'Users'),
        ('claims', 'Claims')
    ], validators=[DataRequired()])
    submit = SubmitField('Search')

class ItemSearchForm(FlaskForm):
    query = StringField('Search Items', validators=[Optional()])
    category = SelectField('Category', choices=[
        ('all', 'All Categories'),
        ('electronics', 'Electronics'),
        ('bags', 'Bags'),
        ('books', 'Books'),
        ('personal_items', 'Personal Items'),
        ('clothing', 'Clothing'),
        ('jewelry', 'Jewelry'),
        ('sports', 'Sports'),
        ('other', 'Other')
    ], validators=[Optional()])
    item_type = SelectField('Item Type', choices=[
        ('all', 'All Items'),
        ('lost', 'Lost Items'),
        ('found', 'Found Items')
    ], validators=[Optional()])
    submit = SubmitField('Search')
    



