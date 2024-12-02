from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Course, Enrollment, Feedback
from forms import RegistrationForm, LoginForm
import os
from supabase import create_client, Client
import json
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Supabase client
supabase: Client = create_client(
    app.config['SUPABASE_URL'],
    app.config['SUPABASE_KEY']
)

# Initialize Flask extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        response = supabase.table('users').select("*").eq('id', user_id).execute()
        if response.data:
            user_data = response.data[0]
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email']
            )
    except Exception as e:
        print(f"Error loading user: {str(e)}")
    return None
# Add datetime filter
@app.template_filter('datetime')
def format_datetime(value):
    if value is None:
        return ""
    try:
        # Parse the datetime string if it's a string
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        else:
            dt = value
        return dt.strftime('%B %d, %Y')  # Format: January 01, 2024
    except Exception as e:
        print(f"Error formatting datetime: {e}")
        return str(value)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        try:
            response = supabase.table('users').insert({
                'username': form.username.data,
                'email': form.email.data,
                'password': hashed_password
            }).execute()
            
            if response.data:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please try again.', 'error')
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            response = supabase.table('users').select("*").eq('email', form.email.data).execute()
            if response.data and check_password_hash(response.data[0]['password'], form.password.data):
                user = User(
                    id=response.data[0]['id'],
                    username=response.data[0]['username'],
                    email=response.data[0]['email']
                )
                login_user(user, remember=form.remember.data)
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(url_for('index'))
            flash('Invalid email or password', 'error')
        except Exception as e:
            flash(f'Error during login: {str(e)}', 'error')
    return render_template('login.html', form=form)

# Add this route to test Supabase connection
@app.route('/test_connection')
def test_connection():
    try:
        # Try to fetch a single user (limit 1)
        response = supabase.table('users').select("*").limit(1).execute()
        return jsonify({
            'status': 'success',
            'message': 'Connected to Supabase successfully',
            'data': response.data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Connection error: {str(e)}'
        })

@app.route('/')
def index():
    try:
        # Get top 4 courses with all required fields
        top_courses_response = supabase.table('courses')\
            .select('id, title, instructor, image_url, rating')\
            .order('rating', desc=True)\
            .limit(4)\
            .execute()

        print("Courses data:", top_courses_response.data)  # Debug print

        return render_template('index.html',
                            courses=top_courses_response.data)

    except Exception as e:
        print(f"Error in index route: {str(e)}")
        return render_template('index.html', courses=[])

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/courses')
def courses():
    try:
        # Fetch all courses with full details
        courses_response = supabase.table('courses')\
            .select('*')\
            .execute()
        
        return render_template('courses.html', 
                             courses=courses_response.data if courses_response.data else [],
                             current_user=current_user)
    except Exception as e:
        print(f"Error in courses route: {str(e)}")
        return render_template('courses.html', courses=[], current_user=current_user)

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/detail/<int:course_id>')
def detail(course_id):
    try:
        # Fetch course details
        course_response = supabase.table('courses')\
            .select('*')\
            .eq('id', course_id)\
            .single()\
            .execute()
            
        course = course_response.data if course_response.data else None
        
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('courses'))
            
        return render_template('detail.html', 
                             course=course,
                             current_user=current_user)
                             
    except Exception as e:
        print(f"Error in detail route: {str(e)}")
        return redirect(url_for('courses'))

@app.route('/process_payment/<int:course_id>', methods=['POST'])
@login_required
def process_payment(course_id):
    try:
        # Fetch course price
        course_response = supabase.table('courses')\
            .select('price, title')\
            .eq('id', course_id)\
            .single()\
            .execute()
            
        course = course_response.data
        
        if not course:
            flash('Course not found', 'error')
            return redirect(url_for('courses'))
            
        # Here you would integrate with your payment gateway (e.g., Stripe)
        # For now, we'll just simulate enrollment
        
        # Record the enrollment
        enrollment = {
            'user_id': current_user.id,
            'course_id': course_id,
            'enrolled_at': datetime.now().isoformat(),
            'payment_status': 'completed',
            'amount_paid': course['price']
        }
        
        supabase.table('enrollments').insert(enrollment).execute()
        
        flash(f'Successfully enrolled in {course["title"]}!', 'success')
        return redirect(url_for('detail', course_id=course_id))
        
    except Exception as e:
        print(f"Error in payment processing: {str(e)}")
        flash('Payment processing failed. Please try again.', 'error')
        return redirect(url_for('detail', course_id=course_id))

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    try:
        # Fetch user's enrolled courses
        enrolled_response = supabase.table('enrollments')\
            .select('*, courses(id, title)')\
            .eq('user_id', current_user.id)\
            .execute()
        
        print("DEBUG - Enrolled courses:", enrolled_response.data)  # Debug print
        
        # Fetch all feedbacks with user and course information
        feedback_response = supabase.table('feedbacks')\
            .select('''
                id,
                rating,
                comment,
                created_at,
                user_id,
                course_id,
                users!inner(username),
                courses!inner(title)
            ''')\
            .execute()
        
        print("DEBUG - Feedback response:", feedback_response.data)  # Debug print
        
        # Check if we have valid feedback data
        if not feedback_response.data:
            print("DEBUG - No feedback data found")
        else:
            print(f"DEBUG - Number of feedbacks: {len(feedback_response.data)}")
            # Print first feedback for structure verification
            print("DEBUG - First feedback structure:", feedback_response.data[0])
        
        return render_template('feedback.html',
                             user_courses=enrolled_response.data if enrolled_response.data else [],
                             feedbacks=feedback_response.data if feedback_response.data else [],
                             current_user=current_user)
                             
    except Exception as e:
        print(f"ERROR in feedback route: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full error traceback
        return render_template('feedback.html',
                             user_courses=[],
                             feedbacks=[],
                             current_user=current_user,
                             error=str(e))

@app.route('/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    try:
        data = request.get_json()
        
        if not data or 'course_id' not in data or 'rating' not in data or 'comment' not in data:
            return jsonify({
                'error': 'Missing required fields'
            }), 400

        print(f"Received feedback data: {data}")  # Debug print
        
        # Validate user is enrolled in the course
        enrollment = supabase.table('enrollments')\
            .select('id')\
            .eq('user_id', current_user.id)\
            .eq('course_id', data['course_id'])\
            .execute()
        
        print(f"Enrollment check result: {enrollment.data}")  # Debug print
        
        if not enrollment.data:
            return jsonify({
                'error': 'You are not enrolled in this course'
            }), 403
        
        # Check if user already gave feedback for this course
        existing_feedback = supabase.table('feedbacks')\
            .select('id')\
            .eq('user_id', current_user.id)\
            .eq('course_id', data['course_id'])\
            .execute()
        
        print(f"Existing feedback check: {existing_feedback.data}")  # Debug print
        
        current_time = datetime.now().isoformat()
        
        feedback_data = {
            'user_id': current_user.id,
            'course_id': data['course_id'],
            'rating': data['rating'],
            'comment': data['comment'],
            'updated_at': current_time
        }
        
        if existing_feedback.data:
            # Update existing feedback
            update_response = supabase.table('feedbacks')\
                .update(feedback_data)\
                .eq('id', existing_feedback.data[0]['id'])\
                .execute()
                
            print(f"Update response: {update_response.data}")  # Debug print
                
            if hasattr(update_response, 'error') and update_response.error is not None:
                raise Exception(update_response.error)
                
            message = 'Feedback updated successfully!'
        else:
            # Create new feedback
            feedback_data['created_at'] = current_time
            insert_response = supabase.table('feedbacks')\
                .insert(feedback_data)\
                .execute()
                
            print(f"Insert response: {insert_response.data}")  # Debug print
                
            if hasattr(insert_response, 'error') and insert_response.error is not None:
                raise Exception(insert_response.error)
                
            message = 'Thank you for your feedback!'
        
        return jsonify({
            'status': 'success',
            'message': message
        }), 200
        
    except Exception as e:
        print(f"Error submitting feedback: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full error traceback
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 400
        
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route('/search', methods=['GET'])
def search_courses():
    query = request.args.get('query', '').strip()
    try:
        if query:
            # Search in courses table with case-insensitive match on title or description
            response = supabase.table('courses')\
                .select('*')\
                .ilike('title', f'%{query}%')\
                .execute()
            
            if response.data:
                return jsonify({'courses': response.data})
            else:
                # Try searching in description if no title matches
                response = supabase.table('courses')\
                    .select('*')\
                    .ilike('description', f'%{query}%')\
                    .execute()
            
            return jsonify({'courses': response.data})
        return jsonify({'courses': []})
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': 'Failed to search courses'}), 500

if __name__ == '__main__':
    app.run(debug=True)
