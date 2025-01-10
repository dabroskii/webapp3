from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from routes import api

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:82992505@localhost:3306/ExpenseClaimsData'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'uploads/invoices'  # Adjust path as needed

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Register the API blueprint
app.register_blueprint(api, url_prefix='/api')

# Health check route
@app.route('/', methods=['GET'])
def health_check():
    return {"status": "API is running successfully!"}, 200

if __name__ == '__main__':
    app.run(debug=True)
