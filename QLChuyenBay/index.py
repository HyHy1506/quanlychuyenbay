import stripe
from QLChuyenBay import app, login, otp, mail, endpoint_secret
from flask import render_template, request, redirect, url_for, session, jsonify, json, request
import controllers
import cloudinary.uploader
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import *

app.add_url_rule('/', 'home', controllers.home, methods=['get', 'post'])

#Cac buoc xac thuc
app.add_url_rule('/verify', 'user_verify', controllers.user_verify, methods=['get', 'post'])
app.add_url_rule('/validate', 'user_validate', controllers.user_validate, methods=['get', 'post'])
app.add_url_rule('/reset-password', 'reset_pwd', controllers.reset_pwd, methods=['get', 'post'])
app.add_url_rule('/register', 'user_register', controllers.user_register, methods=['get', 'post'])
app.add_url_rule('/login-user', 'user_login', controllers.user_login, methods=['get', 'post'])
app.add_url_rule('/user-logout', 'user_logout', login_required(controllers.user_logout), methods=['get'])

#Admin
app.add_url_rule('/api/admin-rule', 'save_admin_rules', controllers.save_admin_rules, methods=['post'])
app.add_url_rule('/api/admin-route-flight', 'save_route_flight', controllers.save_route_flight, methods=['post'])
app.add_url_rule('/api/delete-route/<route_id>', 'delete_route', controllers.delete_route, methods=['delete'])
app.add_url_rule('/api/edit-route/<int:flight_route>', 'edit_route', controllers.edit_route, methods=['put'])

#staff
app.add_url_rule('/api/flight-schedule', 'create_flight_schedule', controllers.create_flight_schedule, methods=['post'])
app.add_url_rule('/api/flight-schedule/details-schedule', 'get_data_details_schedule', controllers.get_data_details_schedule, methods=['post'])
app.add_url_rule('/api/flight_schedule/search', 'search_flight_schedule', controllers.search_flight_schedule, methods=['post'])

#Tim ve
app.add_url_rule('/flight-list', 'flight_list', controllers.flight_list, methods=['get'])
app.add_url_rule('/ticket/<int:flight_id>', 'get_ticket', controllers.get_ticket, methods=['get'])
app.add_url_rule('/bill_ticket/<int:f_id>', 'bill_ticket', login_required(controllers.bill_ticket), methods=['get'])
app.add_url_rule('/api/ticket/<int:f_id>', 'create_ticket', controllers.create_ticket, methods=['post'])

#Thanh toan
app.add_url_rule('/create-checkout-session/<int:f_id>', 'create_checkout_session', login_required(controllers.create_checkout_session), methods=['post'])
app.add_url_rule('/list-flight-payment/<int:f_id>', 'list_flight_payment', login_required(controllers.list_flight_payment), methods=['get'])

#Thong ke
app.add_url_rule('/api/get_stats_revenue/<int:month>', 'get_stats_revenue', controllers.get_stats_revenue, methods=['post'])
app.add_url_rule('/api/get_stats_ticket/<int:month>', 'get_stats_ticket', controllers.get_stats_ticket, methods=['post'])
app.add_url_rule('/api/get_stats_flight/<int:month>', 'get_stats_flight', controllers.get_stats_flight, methods=['post'])
app.add_url_rule('/api/get_stats_total/<int:month>', 'get_stats_total', controllers.get_stats_total, methods=['post'])

#Comment
app.add_url_rule('/about', 'about', controllers.about, methods=['get'])
app.add_url_rule('/api/comments', 'add_comment', login_required(controllers.add_comment), methods=['post'])

#Tim ve
app.add_url_rule('/find-ticket', 'find_ticket', login_required(controllers.find_ticket), methods=['get'])
app.add_url_rule('/ticket-request', 'res_ticket', login_required(controllers.res_ticket), methods=['post'])
app.add_url_rule('/response-ticket', 'response_search', login_required(controllers.response_search), methods=['post'])


@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.context_processor
def common_attributes():
    return {
        'user_role': UserRole
    }

if __name__ == '__main__':
    from QLChuyenBay.admin import *
    app.run(debug=True, host='localhost', port=5002)
