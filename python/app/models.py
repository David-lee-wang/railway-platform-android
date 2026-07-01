# -*- coding: utf-8 -*-
import enum
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db


class UserRole(enum.Enum):
    super_admin = "super_admin"
    center_leader = "center_leader"
    reviewer = "reviewer"
    staff = "staff"
    external = "external"


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    real_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.staff)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    position = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # Relationship
    department = db.relationship('Department', backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(20), unique=True)
    description = db.Column(db.Text)


class StandardDocument(db.Model):
    """制度标准文档"""
    __tablename__ = 'standards'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))  # 政策/定额/规范
    document_number = db.Column(db.String(50))
    file_path = db.Column(db.String(500))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active/archived
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CostReviewProject(db.Model):
    """造价审价项目"""
    __tablename__ = 'cost_reviews'
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    project_code = db.Column(db.String(50))
    project_type = db.Column(db.String(50))  # 铁路/地铁/轻轨
    total_amount = db.Column(db.Float)  # 报审金额
    review_amount = db.Column(db.Float)  # 审定金额
    deduction_amount = db.Column(db.Float)  # 核减金额
    stage = db.Column(db.String(20), default='draft')  # draft/reviewing/approved
    status = db.Column(db.String(20), default='pending')
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    reviewer = db.relationship('User', backref='cost_review_projects')


class FeeReviewRecord(db.Model):
    """费用审核记录"""
    __tablename__ = 'fee_reviews'
    id = db.Column(db.Integer, primary_key=True)
    fee_type = db.Column(db.String(50))  # 其他费/预警费用
    amount = db.Column(db.Float)
    project_id = db.Column(db.Integer, db.ForeignKey('cost_reviews.id'))
    status = db.Column(db.String(20), default='pending')
    reviewer_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FundRecord(db.Model):
    """资金管理记录"""
    __tablename__ = 'funds'
    id = db.Column(db.Integer, primary_key=True)
    record_type = db.Column(db.String(20))  # 拨付/验工
    amount = db.Column(db.Float)
    project_id = db.Column(db.Integer, db.ForeignKey('cost_reviews.id'))
    payment_date = db.Column(db.Date)
    recipient = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContractReview(db.Model):
    """招标合同审核"""
    __tablename__ = 'contracts'
    id = db.Column(db.Integer, primary_key=True)
    contract_number = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(200), nullable=False)
    party_a = db.Column(db.String(200))
    party_b = db.Column(db.String(200))
    contract_amount = db.Column(db.Float)
    risk_score = db.Column(db.Integer, default=0)  # 风险评分 0-100
    risk_items = db.Column(db.Text)  # JSON: risk items list
    status = db.Column(db.String(20), default='pending')
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notice(db.Model):
    """通知公告"""
    __tablename__ = 'notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    is_urgent = db.Column(db.Boolean, default=False)
    published_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    published_at = db.Column(db.DateTime, default=datetime.utcnow)


class Task(db.Model):
    """任务管理"""
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    priority = db.Column(db.String(10), default='normal')  # high/normal/low
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending/in_progress/done
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)


class ReviewRecord(db.Model):
    """审核记录（全过程）"""
    __tablename__ = 'review_records'
    id = db.Column(db.Integer, primary_key=True)
    module_type = db.Column(db.String(30))  # cost/fee/fund/contract
    target_id = db.Column(db.Integer)
    action = db.Column(db.String(30))  # create/approve/reject/comment
    operator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    operator = db.relationship('User', backref='review_records')


class QuestionBankItem(db.Model):
    """问题库条目"""
    __tablename__ = 'question_bank'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))  # 分类
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(10), default='medium')  # high/medium/low
    related_project = db.Column(db.String(200))
    solution = db.Column(db.Text)
    source_module = db.Column(db.String(30))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
