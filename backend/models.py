from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Currency model
class Currency(db.Model):
    __tablename__ = 'Currency'
    CurrencyID = db.Column(db.String(3), primary_key=True, nullable=False)
    ExchangeRate = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<Currency(CurrencyID={self.CurrencyID}, ExchangeRate={self.ExchangeRate})>"

# Department model
class Department(db.Model):
    __tablename__ = 'Department'
    DepartmentCode = db.Column(db.String(3), primary_key=True, nullable=False)
    DepartmentName = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Department(DepartmentCode={self.DepartmentCode}, DepartmentName={self.DepartmentName})>"

# Employee model
class Employee(db.Model):
    __tablename__ = 'Employee'
    EmployeeID = db.Column(db.Integer, primary_key=True, nullable=False)
    SupervisorID = db.Column(db.Integer, db.ForeignKey('Employee.EmployeeID'), nullable=True)
    DepartmentCode = db.Column(db.String(3), db.ForeignKey('Department.DepartmentCode'), nullable=True)
    Password = db.Column(db.String(50), nullable=True)
    FirstName = db.Column(db.String(50), nullable=True)
    LastName = db.Column(db.String(50), nullable=True)
    BankAccountNumber = db.Column(db.String(50), nullable=True)

    supervisor = db.relationship('Employee', remote_side=[EmployeeID], backref='subordinates')
    department = db.relationship('Department', backref='employees')

    def __repr__(self):
        return f"<Employee(EmployeeID={self.EmployeeID}, FirstName={self.FirstName}, LastName={self.LastName})>"

# EmployeeProjects model
class EmployeeProjects(db.Model):
    __tablename__ = 'EmployeeProjects'
    ProjectID = db.Column(db.Integer, primary_key=True, nullable=False)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employee.EmployeeID'), nullable=True)
    ProjectName = db.Column(db.String(100), nullable=True)
    ProjectStatus = db.Column(db.String(50), nullable=True)
    ProjectBudget = db.Column(db.Float, nullable=True)
    ProjectLeadID = db.Column(db.Integer, db.ForeignKey('Employee.EmployeeID'), nullable=True)

    employee = db.relationship('Employee', foreign_keys=[EmployeeID], backref='projects')
    project_lead = db.relationship('Employee', foreign_keys=[ProjectLeadID], backref='led_projects')

    def __repr__(self):
        return f"<EmployeeProjects(ProjectID={self.ProjectID}, ProjectName={self.ProjectName})>"

# ProjectExpenseClaims model
class ProjectExpenseClaims(db.Model):
    __tablename__ = 'ProjectExpenseClaims'
    ClaimID = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Ensure autoincrement=True
    ProjectID = db.Column(db.Integer, db.ForeignKey('EmployeeProjects.ProjectID'), nullable=False)
    EmployeeID = db.Column(db.Integer, db.ForeignKey('Employee.EmployeeID'), nullable=True)
    CurrencyID = db.Column(db.String(3), db.ForeignKey('Currency.CurrencyID'), nullable=False)
    ExpenseDate = db.Column(db.DateTime, nullable=False)
    Amount = db.Column(db.Numeric(10, 2), nullable=False)
    Purpose = db.Column(db.String(255), nullable=False)
    ChargeToDefaultDept = db.Column(db.Boolean, nullable=False)
    AlternativeDeptCode = db.Column(db.String(50), nullable=False)
    Status = db.Column(db.String(20), nullable=False)
    LastEditedClaimDate = db.Column(db.DateTime, nullable=False)

    project = db.relationship('EmployeeProjects', backref='claims')
    employee = db.relationship('Employee', backref='claims')
    currency = db.relationship('Currency', backref='claims')

    def __repr__(self):
        return f"<ProjectExpenseClaims(ClaimID={self.ClaimID}, Amount={self.Amount}, Status={self.Status})>"
