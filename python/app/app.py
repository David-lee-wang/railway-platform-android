# -*- coding: utf-8 -*-
"""
Railway Platform - Flask Application Factory
Mobile version for Android APK (Chaquopy)
"""
import os
import sys
from flask import Flask, render_template_string, redirect, url_for, flash, request, jsonify, session
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from functools import wraps
import json

from config import Config
from extensions import db, login_manager
from models import *

# ============================================================
# Templates (embedded as strings since we can't use external files in Chaquopy easily)
# ============================================================

LOGIN_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>登录 - 造价审价平台</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;
background:linear-gradient(135deg,#1a56db,#1e40af);min-height:100vh;display:flex;align-items:center;justify-content:center}
.login-card{background:#fff;border-radius:16px;padding:32px 28px;width:90%;max-width:380px;box-shadow:0 20px 60px rgba(0,0,0,.2)}
.logo{text-align:center;margin-bottom:28px}.logo-icon{width:64px;height:64px;background:#1a56db;border-radius:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 12px;color:#fff;font-size:30px}
.logo-text{font-size:18px;font-weight:700;color:#1e293b}.logo-sub{font-size:12px;color:#94a3b8;margin-top:4px}
.form-group{margin-bottom:18px}label{display:block;font-size:13px;font-weight:600;color:#334155;margin-bottom:6px}
input[type=text],input[type=password]{width:100%;padding:12px 14px;border:2px solid #e2e8f0;border-radius:10px;font-size:15px;transition:border .2s}
input:focus{outline:none;border-color:#1a56db}.btn-login{width:100%;padding:14px;background:#1a56db;color:#fff;border:none;border-radius:10px;font-size:16px;font-weight:600;cursor:pointer;margin-top:6px}
.btn-login:active{background:#1557c0}.error-msg{background:#fef2f2;border:1px solid #fecaca;color:#dc2626;padding:10px 14px;border-radius:8px;font-size:13px;margin-bottom:14px}
.footer{text-align:center;margin-top:24px;font-size:11px;color:#94a3b8}</style></head><body>
<div class="login-card"><div class="logo"><div class="logo-icon">🚂</div><div class="logo-text">造价审价中心</div><div class="logo-sub">江苏省铁路集团</div></div>
<form method="POST">{% if error %}<div class="error-msg">{{ error }}</div>{% endif %}
<div class="form-group"><label>用户名</label><input type="text" name="username" placeholder="请输入用户名" required autofocus></div>
<div class="form-group"><label>密码</label><input type="password" name="password" placeholder="请输入密码" required></div>
<button type="submit" class="btn-login">登 录</button></form>
<div class="footer">v1.0.0 &copy; 江苏省铁路集团</div></div></body></html>'''

DASHBOARD_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>工作台 - 造价审价平台</title>
<style>*{margin:0;padding:0;box-sizing:border-box}:root{--primary:#1a56db;--dark:#1e293b;--gray:#64748b;--bg:#f8fafc;--border:#e2e8f0}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;background:var(--bg);color:var(--dark)}
.header{background:var(--primary);color:#fff;padding:16px;text-align:center;font-size:17px;font-weight:600;position:sticky;top:0;z-index:100}
.nav-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding:16px}
.nav-item{background:#fff;border-radius:12px;padding:20px 12px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.06);text-decoration:none;color:var(--dark);transition:.2s}
.nav-item:active{transform:scale(.96)}.nav-icon{font-size:36px;margin-bottom:8px}.nav-label{font-size:13px;font-weight:600}
.nav-desc{font-size:10px;color:var(--gray);margin-top:2px}
.stats-row{display:flex;gap:12px;padding:0 16px 16px}.stat-card{flex:1;background:#fff;border-radius:12px;padding:16px;text-align:center;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.stat-num{font-size:26px;font-weight:700;color:var(--primary)}.stat-label{font-size:11px;color:var(--gray);margin-top:4px}
.section-title{font-size:15px;font-weight:700;padding:16px 16px 10px;color:var(--dark)}
.list-item{background:#fff;margin:0 16px 8px;padding:14px 16px;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.list-item-title{font-size:14px;font-weight:600}.list-item-meta{font-size:11px;color:var(--gray);margin-top:4px}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600}
.badge-pending{background:#fef3c7;color:#d97706}.badge-done{background:#d1fae5;color:#059669}.badge-reviewing{background:#dbeafe;color:#2563eb}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid var(--border);display:flex;z-index:100;padding-bottom:env(safe-area-inset-bottom)}
.bottom-nav a{flex:1;text-align:center;padding:10px 0;text-decoration:none;color:var(--gray);font-size:11px}
.bottom-nav .active{color:var(--primary)}.bottom-nav-icon{font-size:22px;display:block;margin-bottom:2px}
.content{padding-bottom:80px}</style></head><body>
<div class="header">江苏省铁路集团造价审价中心</div>
<div class="content">
<div class="stats-row">
<div class="stat-card"><div class="stat-num">{{ stats.total_projects }}</div><div class="stat-label">项目总数</div></div>
<div class="stat-card"><div class="stat-num">{{ stats.reviewing }}</div><div class="stat-label">审核中</div></div>
<div class="stat-card"><div="stat-num">{{ stats.approved }}</div><div class="stat-label">已审定</div></div>
</div>
<div class="section-title">功能模块</div>
<div class="nav-grid">
<a href="/standards" class="nav-item"><div class="nav-icon">⚖️</div><div class="nav-label">制度标准</div><div class="nav-desc">政策/定额</div></a>
<a href="/cost-review" class="nav-item"><div class="nav-icon">📁</div><div class="nav-label">造价审价</div><div class="nav-desc">项目审核</div></a>
<a href="/fee-review" class="nav-item"><div class="nav-icon">🧾</div><div class="nav-label">费用审核</div><div class="nav-desc">其他费/预警</div></a>
<a href="/fund" class="nav-item"><div class="nav-icon">🏦</div><div class="nav-label">资金管理</div><div class="nav-desc">拨付/验工</div></a>
<a href="/contract" class="nav-item"><div class="nav-icon">📋</div><div class="nav-label">招标合同</div><div class="nav-desc">风险扫描</div></a>
<a href="/review-records" class="nav-item"><div class="nav-icon">📜</div><div class="nav-label">审核记录</div><div class="nav-desc">全过程</div></a>
<a href="/data-overview" class="nav-item"><div class="nav-icon">📊</div><div class="nav-label">数据总览</div><div class="nav-desc">统计/预警</div></a>
<a href="/question-bank" class="nav-item"><div class="nav-icon">📝</div><div class="nav-label">问题库</div><div class="nav-desc">分类汇总</div></a>
<a href="/tasks" class="nav-item"><div class="nav-icon">✅</div><div class="nav-label">任务管理</div><div class="nav-desc">待办事项</div></a>
</div>
<div class="section-title">最近项目</div>
{% for p in recent_projects %}
<div class="list-item"><div class="list-item-title">{{ p.project_name }}</div><div class="list-item-meta">
{{ p.project_type or '未分类' }} | 报审¥{{ '%.2f'|format(p.total_amount or 0) }}
<span class="badge badge-{{ 'pending' if p.status == 'pending' else 'done' if p.status == 'approved' else 'reviewing' }}">{{ p.status }}</span></div></div>
{% endfor %}
</div>
<div class="bottom-nav"><a href="/" class="active"><span class="bottom-nav-icon">🏠</span>首页</a>
<a href="/cost-review"><span class="bottom-nav-icon">📁</span>审价</a>
<a href="/data-overview"><span class="bottom-nav-icon">📊</span>数据</a>
<a href="/profile"><span class="bottom-nav-icon">👤</span>我的</a></div></body></html>'''


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role.name == 'super_admin':
                return f(*args, **kwargs)
            if current_user.role.name not in roles:
                flash('您没有权限执行此操作', 'danger')
                return redirect('/')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    # ==================== AUTH ROUTES ====================

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                from flask_login import login_user
                login_user(user)
                user.last_login = datetime.utcnow()
                db.session.commit()
                return redirect(url_for('dashboard'))
            else:
                return render_template_string(LOGIN_TEMPLATE, error='用户名或密码错误')
        return render_template_string(LOGIN_TEMPLATE, error=None)

    @app.route('/logout')
    def logout():
        from flask_login import logout_user
        logout_user()
        return redirect('/login')

    # ==================== DASHBOARD ====================

    @app.route('/')
    @app.route('/dashboard')
    @login_required
    def dashboard():
        total = CostReviewProject.query.count()
        reviewing = CostReviewProject.query.filter_by(status='reviewing').count()
        approved = CostReviewProject.query.filter_by(status='approved').count()
        recent = CostReviewProject.query.order_by(CostReviewProject.created_at.desc()).limit(5).all()

        stats = {'total_projects': total, 'reviewing': reviewing, 'approved': approved}

        return render_template_string(DASHBOARD_TEMPLATE, stats=stats, recent_projects=recent)

    # ==================== STANDARDS ====================

    @app.route('/standards')
    @login_required
    def standards_index():
        docs = StandardDocument.query.filter_by(status='active').order_by(StandardDocument.created_at.desc()).all()
        html = make_list_page('制度标准', '⚖️', docs,
            lambda d: {'title': d.title, 'meta': f'{d.category or "未分类"} | {d.document_number or "无编号"}',
                      'url': f'/standards/{d.id}'})
        return render_template_string(html, items=docs)

    @app.route('/standards/<int:id>')
    @login_required
    def standards_detail(id):
        doc = StandardDocument.query.get_or_404(id)
        return render_template_string(make_detail_page(doc.title, doc.description or '暂无详情',
            [('文档编号', doc.document_number or '-'), ('类别', doc.category or '-'),
             ('状态', doc.status), ('创建时间', doc.created_at.strftime('%Y-%m-%d %H:%M'))]))

    # ==================== COST REVIEW ====================

    @app.route('/cost-review')
    @login_required
    def cost_review_index():
        projects = CostReviewProject.query.order_by(CostReviewProject.updated_at.desc()).all()
        html = make_list_page('造价审价', '📁', projects,
            lambda p: {'title': p.project_name, 'meta':
            f'{p.project_type or "未分类"} | ¥{"%.2f"|format(p.total_amount or 0)} | {p.stage}',
            'url': f'/cost-review/{p.id}', 'status': p.status})
        return render_template_string(html, items=projects)

    @app.route('/cost-review/<int:id>')
    @login_required
    def cost_review_detail(id):
        p = CostReviewProject.query.get_or_404(id)
        return render_template_string(make_detail_page(p.project_name,
            f'<p>报审金额：¥{"%.2f"|format(p.total_amount or 0)}</p>'
            f'<p>审定金额：¥{"%.2f"|format(p.review_amount or 0)}</p>'
            f'<p>核减金额：<strong style="color:red">¥{"%.2f"|format(p.deduction_amount or 0)}</strong></p>',
            [('项目编号', p.project_code or '-'), ('类型', p.project_type or '-'),
             ('阶段', p.stage), ('状态', p.status), ('备注', p.notes or '-')]))

    # ==================== FEE REVIEW ====================

    @app.route('/fee-review')
    @login_required
    def fee_review_index():
        records = FeeReviewRecord.query.order_by(FeeReviewRecord.created_at.desc()).all()
        html = make_list_page('费用审核', '🧾', records,
            lambda r: {'title': f"{r.fee_type or '未知'} - ¥{'%.2f'|format(r.amount or 0)}",
            'meta': r.status, 'url': f'/fee-review/{r.id}'})
        return render_template_string(html, items=records)

    # ==================== FUND MANAGEMENT ====================

    @app.route('/fund')
    @login_required
    def fund_index():
        records = FundRecord.query.order_by(FundRecord.payment_date.desc().nullslast()).all()
        html = make_list_page('资金管理', '🏦', records,
            lambda r: {'title': f"{r.record_type or ''} - ¥{'%.2f'|format(r.amount or 0)}",
            'meta': f"{r.recipient or '-'} | {(r.payment_date or '').strftime('%Y-%m-%d') if r.payment_date else '-'}"})
        return render_template_string(html, items=records)

    # ==================== CONTRACT REVIEW ====================

    @app.route('/contract')
    @login_required
    def contract_index():
        contracts = ContractReview.query.order_by(ContractReview.created_at.desc()).all()
        html = make_list_page('招标合同审核', '📋', contracts,
            lambda c: {'title': c.title, 'meta': f"{c.contract_number or '-'} | ¥{'%.2f'|format(c.contract_amount or 0) if c.contract_amount else '-'} | 风险:{c.risk_score}/100",
            'url': f'/contract/{c.id}', 'status': c.status})
        return render_template_string(html, items=contracts)

    # ==================== DATA OVERVIEW ====================

    @app.route('/data-overview')
    @login_required
    def data_overview_index():
        total_projects = CostReviewProject.query.count()
        total_contracts = ContractReview.query.count()
        total_funds = FundRecord.query.count()
        total_deduction = sum([p.deduction_amount or 0 for p in CostReviewProject.query.all()])
        total_amount = sum([p.total_amount or 0 for p in CostReviewProject.query.all()])

        html = '''<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>数据总览 - 造价审价平台</title>
<style>:root{--p:#1a56db;--d:#1e293b;--g:#64748b;--bg:#f8fafc;--b:#e2e8f0}
*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,sans-serif;background:var(--bg);color:var(--d)}
.header{background:var(--p);color:#fff;padding:16px;text-align:center;font-size:17px;font-weight:600;position:sticky;top:0}
.card{background:#fff;margin:12px 16px;border-radius:12px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.06)}
.card-title{font-size:13px;color:var(--g);margin-bottom:12px}.big-num{font-size:32px;font-weight:700;color:var(--p)}
.small-num{font-size:22px;font-weight:700;color:var(--p)}
.row{display:flex;gap:12px}.col{flex:1}
.chart-bar{height:24px;background:var(--p);border-radius:4px;margin-bottom:6px;display:flex;align-items:center;padding:0 8px;color:#fff;font-size:11px}</style></head><body>
<div class="header">数据总览</div>
<div class="card"><div class="card-title">项目概览</div><div class="row"><div class="col"><div class="big-num">%s</div><div style="font-size:12px;color:var(--g)">总项目数</div></div>
<div class="col"><div class="small-num">%s</div><div style="font-size:12px;color:var(--g)">合同数</div></div>
<div class="col"><div class="small-num">%s</div><div style="font-size:12px;color:var(--g)">资金记录</div></div></div></div>
<div class="card"><div class="card-title">资金统计</div>
<div class="big-num">¥%.2f</div><div style="font-size:12px;color:var(--g)">报审总额</div>
<div style="margin-top:12px;font-size:14px;color:#dc2626">核减总额：¥%.2f</div>
<div style="margin-top:6px;font-size:12px;color:var(--g)">核减率：%%.1f%%%%</div></div>
</body></html>''' % (
            total_projects, total_contracts, total_funds,
            total_amount, total_deduction,
            (total_deduction / total_amount * 100) if total_amount > 0 else 0
        )
        return html

    # ==================== REVIEW RECORDS ====================

    @app.route('/review-records')
    @login_required
    def review_records_index():
        records = ReviewRecord.query.order_by(ReviewRecord.created_at.desc()).limit(50).all()
        html = make_list_page('审核记录', '📜', records,
            lambda r: {'title': r.action, 'meta': f"{r.module_type or ''} | {(r.operator.real_name if r.operator else '系统')} | {r.created_at.strftime('%m-%d %H:%M')}"})
        return render_template_string(html, items=records)

    # ==================== QUESTION BANK ====================

    @app.route('/question-bank')
    @login_required
    def question_bank_index():
        items = QuestionBankItem.query.order_by(QuestionBankItem.created_at.desc()).all()
        html = make_list_page('问题库', '📝', items,
            lambda q: {'title': q.title[:50], 'meta': f"{q.category or '-'} | {q.severity}",
            'severity': q.severity})
        return render_template_string(html, items=items)

    # ==================== TASKS ====================

    @app.route('/tasks')
    @login_required
    def task_list():
        tasks = Task.query.filter(Task.assignee_id == current_user.id).order_by(Task.created_at.desc()).all()
        html = make_list_page('任务管理', '✅', tasks,
            lambda t: {'title': t.title, 'meta': f"{t.priority or 'normal'} | 截止:{t.due_date or '未设定'}",
            'status': t.status})
        return render_template_string(html, items=tasks)

    # ==================== PROFILE ====================

    @app.route('/profile')
    @login_required
    def profile():
        u = current_user
        return render_template_string(
            make_detail_page('个人信息',
            f"<p><strong>用户名：</strong>{u.username}</p>"
            f"<p><strong>姓名：</strong>{u.real_name}</p>"
            f"<p><strong>角色：</strong>{u.role.value}</p>"
            f"<p><strong>部门：</strong>{(u.department.name if u.department else '未分配')}</p>"
            f"<p><strong>最后登录：</strong>{(u.last_login.strftime('%%Y-%%m-%%d %%H:%%M') if u.last_login else '从未')}</p>",
            []))

    # ==================== ERROR HANDLERS ====================

    @app.errorhandler(404)
    def not_found(e):
        return '<html><head><meta charset=UTF-8><meta name=viewport content="width=device-width,initial-scale=1">'
        '<body style="font-family:sans-serif;display:flex;align-items:center;justify-content:center;'
        'min-height:100vh;background:#f8fafc;color:#1e293b;text-align:center;padding:20px">'
        '<div><h1 style="font-size:48px;color:#1a56db">404</h1><p>页面不存在</p>'
        '<a href="/" style="color:#1a56db">返回首页</a></div></body></html>', 404

    return app


# ==================== TEMPLATE HELPERS ====================

BASE_PAGE_CSS = '''
:root{--primary:#1a56db;--dark:#1e293b;--gray:#64748b;--bg:#f8fafc;--border:#e2e8f0}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;background:var(--bg);color:var(--dark)}
.header{background:var(--primary);color:#fff;padding:16px;text-align:center;font-size:17px;font-weight:600;position:sticky;top:0;z-index:100}
.back-btn{position:absolute;left:16px;top:16px;color:#fff;font-size:18px;text-decoration:none}
.content{padding:16px;padding-bottom:80px}
.item{background:#fff;margin-bottom:8px;padding:14px 16px;border-radius:10px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.item-title{font-size:14px;font-weight:600}.item-meta{font-size:11px;color:var(--gray);margin-top:4px}
.badge{display:inline-block;padding:2px8px;border-radius:10px;font-size:10px;font-weight:600}
.b-pending{background:#fef3c7;color:#d97706}.b-done{background:#d1fae5;color:#059669}
.b-reviewing{background:#dbeafe;color:#2563eb}.b-high{background:#fecaca;color:#dc2626}
.b-medium{background:#fef3c7;color:#d97706}.b-low{background:#d1fae5;color:#059669}
.detail-row{display:flex;padding:10px 0;border-bottom:1px solid var(--border)}
.detail-label{width:90px;color:var(--gray);font-size:13px;flex-shrink:0}
.detail-value{font-size:13px;color:var(--dark);flex:1}
.bottom-nav{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid var(--border);
display:flex;z-index:100;padding-bottom:env(safe-area-inset-bottom)}
.bottom-nav a{flex:1;text-align:center;padding:10px 0;text-decoration:none;color:var(--gray);font-size:11px}
.bottom-nav .active{color:var(--primary)}.bn-icon{font-size:22px;display:block;margin-bottom:2px}
.empty{text-align:center;padding:60px 20px;color:var(--gray);font-size:14px}.empty-icon{font-size:48px;margin-bottom:12px}
'''


def make_list_page(title, icon, items, item_mapper):
    """Generate a list page template string."""
    return f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>{title} - 造价审价平台</title><style>{BASE_PAGE_CSS}</style></head><body>
<div class="header"><a href="/" class="back-btn">←</a>{icon} {title}</div>
<div class="content">
{{% if items %}}
{{% for item in items %}}
{{% set info = item_mapper(item) %}}
<div class="item"><div class="item-title">{{ info["title"] }}</div>
<div class="item-meta">{{ info["meta"] }}
{{%- if info.get("status") %}} <span class="badge b-{{ info["status"] }}">{{ info["status"] }}</span>{{%- endif -%}}
{{%- if info.get("severity") %}} <span class="badge b-{{ info["severity"] }}">{{ info["severity"] }}</span>{{%- endif -%}}
</div></div>
{{% endfor %}}
{{% else %}}
<div class="empty"><div class="empty-icon">📭</div>暂无数据</div>
{{% endif %}}
</div>
<div class="bottom-nav"><a href="/"><span class="bn-icon">🏠</span>首页</a>
<a href="/cost-review"><span class="bn-icon">📁</span>审价</a>
<a href="/data-overview"><span class="bn-icon">📊</span>数据</a>
<a href="/profile"><span class="bn-icon">👤</span>我的</a></div></body></html>'''


def make_detail_page(title, body_html, rows=None):
    """Generate a detail page template string."""
    rows_html = ''
    if rows:
        for label, value in rows:
            safe_val = str(value).replace('<', '&lt;').replace('>', '&gt;') if not ('<' in str(value)) else str(value)
            rows_html += f'<div class="detail-row"><div class="detail-label">{label}</div><div class="detail-value">{safe_val}</div></div>'

    return f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>{title} - 造价审价平台</title><style>{BASE_PAGE_CSS}
.detail-body{{padding:16px;line-height:1.7;font-size:14px}}</style></head><body>
<div class="header"><a href="javascript:history.back()" class="back-btn">←</a>{title}</div>
<div class="content">
<div class="item">{rows_html}<div class="detail-body">{body_html}</div></div>
</div>
<div class="bottom-nav"><a href="/"><span class="bn-icon">🏠</span>首页</a>
<a href="/cost-review"><span class="bn-icon">📁</span>审价</a>
<a href="/data-overview"><span class="bn-icon">📊</span>数据</a>
<a href="/profile"><span class="bn-icon">👤</span>我的</a></div></body></html>'''
