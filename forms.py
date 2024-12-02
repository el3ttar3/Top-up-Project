from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
        validators=[DataRequired(), Length(min=2, max=20)],
        render_kw={"autocomplete": "username"})
    
    email = StringField('Email', 
        validators=[DataRequired(), Email()],
        render_kw={"autocomplete": "email"})
    
    password = PasswordField('Password', 
        validators=[DataRequired(), Length(min=6)],
        render_kw={"autocomplete": "new-password"})
    
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password')],
        render_kw={"autocomplete": "new-password"})
    
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', 
        validators=[DataRequired(), Email()],
        render_kw={"autocomplete": "email"})
    
    password = PasswordField('Password', 
        validators=[DataRequired()],
        render_kw={"autocomplete": "current-password"})
    
    remember = BooleanField('Remember Me')
    
    submit = SubmitField('Login')