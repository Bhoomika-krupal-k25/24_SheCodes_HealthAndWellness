from flask import render_template, request, redirect, url_for, flash, session, jsonify
from app.models import db, User  # User model and database
from app.ml_model import load_model, predict_deficiency  # ML model functions

# Load the ML model at the start
model = load_model()

# Home Page (Login)
@app.route('/')
def index():
    return render_template('index.html')


# User Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash("Email already exists. Please log in.")
            return redirect(url_for('index'))
        
        # Create new user
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully. Please log in.")
        return redirect(url_for('index'))
    
    return render_template('signup.html')


# User Login
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        flash("Logged in successfully!")
        return redirect(url_for('input_form'))
    
    flash("Invalid email or password.")
    return redirect(url_for('index'))


# User Input Submission Form
@app.route('/input', methods=['GET', 'POST'])
def input_form():
    if 'user_id' not in session:
        flash("Please log in to access this page.")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Collect nutrient levels from the form
        nutrient_levels = {
            'vitamin_a': float(request.form['vitamin_a']),
            'iron': float(request.form['iron']),
            'calcium': float(request.form['calcium']),
            'vitamin_c': float(request.form['vitamin_c']),
        }
        
        # Redirect to the prediction results page
        return redirect(url_for('predict', **nutrient_levels))
    
    return render_template('input.html')


# Prediction Results and Food Recommendations
@app.route('/predict', methods=['GET'])
def predict():
    if 'user_id' not in session:
        flash("Please log in to access this page.")
        return redirect(url_for('index'))
    
    # Extract nutrient levels from query parameters
    nutrient_levels = {
        'vitamin_a': request.args.get('vitamin_a', type=float),
        'iron': request.args.get('iron', type=float),
        'calcium': request.args.get('calcium', type=float),
        'vitamin_c': request.args.get('vitamin_c', type=float),
    }
    
    # Use the ML model to predict deficiency
    deficiency_result = predict_deficiency(model, nutrient_levels)
    
    # Generate food recommendations based on the prediction
    food_recommendations = []
    if deficiency_result == "Vitamin A Deficiency":
        food_recommendations = ["Carrots", "Sweet Potatoes", "Spinach"]
    elif deficiency_result == "Iron Deficiency":
        food_recommendations = ["Lentils", "Red Meat", "Spinach"]
    elif deficiency_result == "Calcium Deficiency":
        food_recommendations = ["Milk", "Cheese", "Broccoli"]
    elif deficiency_result == "Vitamin C Deficiency":
        food_recommendations = ["Oranges", "Strawberries", "Bell Peppers"]
    else:
        deficiency_result = "No deficiency detected."
        food_recommendations = ["Maintain a balanced diet!"]

    return render_template(
        'results.html',
        deficiency=deficiency_result,
        recommendations=food_recommendations,
    )


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for('index'))



