from fileinput import filename
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from models import db, Currency, Department, Employee, EmployeeProjects, ProjectExpenseClaims
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
import os

# Initialize JWT
jwt = JWTManager()

# Create a Blueprint for API routes
api = Blueprint('api', __name__)

# --------------------------------
# Login Route
# --------------------------------

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')  # Assuming username maps to EmployeeID
    password = data.get('password')  # Assuming password maps to Password

    user = Employee.query.filter_by(EmployeeID=username, Password=password).first()

    if user:
        access_token = create_access_token(
            identity=str(user.EmployeeID),  # Corrected EmployeeID reference
            expires_delta=timedelta(hours=1),
            additional_claims={"roles": "ROLE_USER"}
        )
        return jsonify({"access_token": access_token, "message": f"Welcome, {user.FirstName}!"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401




# --------------------------------
# Dashboard Route
# --------------------------------
@api.route('/claims/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    try:
        # Retrieve the logged-in user's ID from the JWT
        user_id = get_jwt_identity()

        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Step 1: Fetch user to ensure they exist
        user = db.session.query(Employee).filter_by(EmployeeID=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Step 2: Fetch claims associated with the user
        claims = (
            db.session.query(ProjectExpenseClaims)
            .options(joinedload(ProjectExpenseClaims.currency))  # Eager load Currency details
            .filter(ProjectExpenseClaims.EmployeeID == user_id)
            .all()
        )

        if not claims:
            # If no claims exist, return empty categories
            return jsonify({"pending": [], "approved": [], "rejected": []}), 200

        # Step 3: Organize claims into categories and extract required fields
        result = {"pending": [], "approved": [], "rejected": []}
        for claim in claims:
            claim_data = {
                "ClaimID": claim.ClaimID,
                "ProjectID": claim.ProjectID,
                "Currency": claim.currency.CurrencyID,
                "Amount": float(claim.Amount),  # Convert Decimal to float
                "Status": claim.Status
            }
            # Categorize claims based on status
            if claim.Status.lower() == "pending":
                result["pending"].append(claim_data)
            elif claim.Status.lower() == "approved":
                result["approved"].append(claim_data)
            elif claim.Status.lower() == "rejected":
                result["rejected"].append(claim_data)

        return jsonify(result), 200

    except Exception as e:
        print(f"Error in /claims/dashboard: {e}")
        return jsonify({"error": "Failed to process the request"}), 422



# --------------------------------
# Manage Claims (Create, Update, Delete)
# --------------------------------

UPLOAD_FOLDER = 'uploads/invoices'  # Adjust path as needed
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/claims', methods=['POST'])
@jwt_required()
def create_claim():
    try:
        # Step 1: Get the logged-in user's ID from the JWT
        user_id = get_jwt_identity()
        print(f"User ID from token: {user_id}")  # Debugging

        # Step 2: Validate the input data (support both JSON and form data)
        data = request.get_json() if request.is_json else request.form

        required_fields = ['ProjectID', 'CurrencyID', 'ExpenseDate', 'Amount', 'Purpose', 'Status']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 422

        # Step 3: Create a new claim
        new_claim = ProjectExpenseClaims(
            ProjectID=data['ProjectID'],
            EmployeeID=user_id,
            CurrencyID=data['CurrencyID'],
            ExpenseDate=datetime.strptime(data['ExpenseDate'], '%Y-%m-%d'),
            Amount=data['Amount'],
            Purpose=data['Purpose'],
            ChargeToDefaultDept=data.get('ChargeToDefaultDept', 'false').lower() == 'true',  # Convert to boolean
            AlternativeDeptCode=data.get('AlternativeDeptCode', ''),
            Status=data['Status'],
            LastEditedClaimDate=datetime.now()
        )


        db.session.add(new_claim)
        db.session.commit()

        return jsonify({"message": "Claim created successfully!", "ClaimID": new_claim.ClaimID}), 201

    except Exception as e:
        print(f"Error in create_claim: {e}")
        return jsonify({"error": "Failed to create claim"}), 500


@api.route('/claims/<int:claim_id>', methods=['PUT'])
@jwt_required()
def update_claim(claim_id):
    try:
        # Step 1: Retrieve the logged-in user's ID from the JWT
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Step 2: Retrieve the claim and ensure it belongs to the logged-in user
        claim = db.session.query(ProjectExpenseClaims).filter(
            ProjectExpenseClaims.ClaimID == claim_id,
            ProjectExpenseClaims.EmployeeID == user_id
        ).first()

        if not claim:
            return jsonify({"error": "Claim not found or not authorized"}), 404

        # Step 3: Check if the claim is pending or rejected
        if claim.Status.lower() not in ['pending', 'rejected']:
            return jsonify({"error": "Only pending or rejected claims can be updated"}), 403

        # Step 4: Update the claim fields
        data = request.get_json()
        claim.ProjectID = data.get('ProjectID', claim.ProjectID)
        claim.CurrencyID = data.get('CurrencyID', claim.CurrencyID)
        claim.ExpenseDate = datetime.strptime(data.get('ExpenseDate', claim.ExpenseDate.strftime('%Y-%m-%d')), '%Y-%m-%d')
        claim.Amount = data.get('Amount', claim.Amount)
        claim.Purpose = data.get('Purpose', claim.Purpose)
        claim.ChargeToDefaultDept = data.get('ChargeToDefaultDept', claim.ChargeToDefaultDept)
        claim.AlternativeDeptCode = data.get('AlternativeDeptCode', claim.AlternativeDeptCode)
        claim.Status = data.get('Status', claim.Status)

        # Auto-update `LastEditedClaimDate`
        claim.LastEditedClaimDate = datetime.now()

        db.session.commit()

        return jsonify({"message": "Claim updated successfully!"}), 200

    except Exception as e:
        print(f"Error in update_claim: {e}")
        return jsonify({"error": "Failed to update the claim"}), 500

@api.route('/claims/<int:claim_id>', methods=['DELETE'])
@jwt_required()
def delete_claim(claim_id):
    try:
        # Step 1: Retrieve the logged-in user's ID from the JWT
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        # Step 2: Retrieve the claim and ensure it belongs to the logged-in user
        claim = db.session.query(ProjectExpenseClaims).filter(
            ProjectExpenseClaims.ClaimID == claim_id,
            ProjectExpenseClaims.EmployeeID == user_id
        ).first()

        if not claim:
            return jsonify({"error": "Claim not found or not authorized"}), 404

        # Step 3: Check if the claim is pending or rejected
        if claim.Status.lower() not in ['pending', 'rejected']:
            return jsonify({"error": "Only pending or rejected claims can be deleted"}), 403

        # Step 4: Delete the claim
        db.session.delete(claim)
        db.session.commit()
        return jsonify({"message": "Claim deleted successfully!"}), 200

    except Exception as e:
        print(f"Error in delete_claim: {e}")
        return jsonify({"error": "Failed to delete the claim"}), 500

@api.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logged out successfully!"}), 200

