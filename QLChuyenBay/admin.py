from QLChuyenBay import app, db
from flask_admin import Admin, expose, AdminIndexView
from QLChuyenBay.models import UserRole, User, AirPort, FlightSchedule, FlightRoute
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView
from flask_login import current_user, logout_user
from flask import redirect, render_template, abort, json, jsonify
import dao

class Authenticated(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated and (current_user.user_role.value == UserRole.ADMIN.value
                                        or current_user.user_role.value == UserRole.STAFF.value):
            return True
        else:
            return abort(403, 'Unauthorized Access')

class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class AuthenticatedAdminView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.value == UserRole.ADMIN.value

class AuthenticatedStaffView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.value == UserRole.STAFF.value

class AuthenticatedAdmin(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.value == UserRole.ADMIN.value

class AuthenticatedStaff(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.value == UserRole.STAFF.value


class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return render_template('login.html')

class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

class FlightScheduleView(AuthenticatedStaff):
    @expose('/')
    def index(self):
        rules= dao.get_rule_admin()
        list_airport = dao.get_air_port_list()
        route_list = dao.get_route_list()
        flight_sche_list= dao.get_flight_sche_list()

        return self.render('admin/flightSche.html',  list_airport= list_airport, route_list= route_list,
                           rules= rules, flight_sche_list=flight_sche_list)

class FlightRouteAvailableView(AuthenticatedStaffView):
    @expose('/')
    def index(self):
        list_airport = dao.get_air_port_list()
        route_list = dao.get_route_list()
        return self.render('admin/flightRouteAvailable.html', list_airport=list_airport, route_list=route_list)

class UserView(AuthenticatedAdmin):
    column_searchable_list = ['username', 'user_role']
    form_excluded_columns = ['password']
    column_list = ('username', 'name')
    column_labels = dict(username='Tên đăng nhập', name='Họ tên', images="Ảnh đại diện", user_role="Vai trò")

class HomeView(AuthenticatedView):
    @expose('/')
    def __index__(self):
        return self.render('index.html')

class AirportView(AuthenticatedAdmin):
    column_searchable_list = ['name']
    column_labels = dict(name='Tên sân bay')

class RouteFlightView(AuthenticatedAdminView):
    @expose('/')
    def index(self):
        list_airport= dao.get_air_port_list()
        route_list = dao.get_route_list()
        return self.render('admin/flightRoute.html', list_airport= list_airport,
                           route_list= route_list)

class RulesView(AuthenticatedAdminView):
    @expose('/')
    def index(self):
        admin_rules= dao.get_rule_admin()
        return self.render('admin/rules.html', admin_rules=admin_rules)

class StatsView(AuthenticatedAdminView):
    @expose('/')
    def index(self):
        stats = dao.get_data_stats_json_list()
        route_list = dao.get_route_list()
        states_revenue= dao.get_revenue_stats_json_list()
        states_ticket = dao.get_ticket_stats_json_list()
        states_flight= dao.get_flight_stats_json_list()
        return self.render('admin/stats.html', route_list= route_list,
                           states_revenue= states_revenue, states_ticket= states_ticket,
                           states_flight= states_flight, stats= stats)


admin= Admin(app=app, name='Quản lý chuyến bay', template_mode='bootstrap4', index_view= MyAdminIndex())
admin.add_view(UserView(User, db.session, name='Người dùng'))
admin.add_view(AirportView(AirPort, db.session, name='Sân bay'))
admin.add_view(FlightRouteAvailableView(name= 'Tuyến bay sẵn có'))
admin.add_view(FlightScheduleView(FlightSchedule, db.session, name= 'Lập lịch bay'))
admin.add_view(RouteFlightView(name= 'Tuyến bay'))
admin.add_view(RulesView(name='Quản lý quy định'))
admin.add_view(StatsView(name= 'Thống kê'))
admin.add_view(HomeView(name= 'Trang khách hàng'))
admin.add_view(LogoutView(name= 'Đăng xuất'))