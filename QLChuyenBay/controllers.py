import stripe
from QLChuyenBay import app, login, otp, mail, endpoint_secret
from flask import render_template, request, redirect, url_for, session, jsonify, json, request
import dao
import cloudinary.uploader
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import *

from QLChuyenBay.dao import check_flight_sche_in_route
from QLChuyenBay.models import UserRole

def home():
    airport_list = dao.get_air_port_list()
    return render_template("index.html", airport_list= airport_list)

def user_verify():
    err_msg = ''
    if request.method.__eq__("POST"):
        email = request.form.get('email')
        if email:
            check= dao.check_mail_exit(email=email)
            if check:
                session['email']=email
                msg = Message(subject='OTP', sender='anhqui04062004@gmail.com', recipients=[email])
                msg.body = str(otp)
                mail.send(msg)
                return redirect(url_for('user_validate'))
            else:
                err_msg= 'Email không tồn tại!!!'
    return render_template('verify.html', err_msg=err_msg)


def user_validate():
    if request.method.__eq__("POST"):
        user_otp = request.form.get('otp')
        if otp == int(user_otp):
            return render_template('reset_password.html')
    return render_template("otp.html", msg='Thất bại!!!')


def reset_pwd():
    err_msg=''
    if request.method.__eq__("POST"):
        password= request.form.get("password")
        confirm= request.form.get("confirm")
        if not password.strip().__eq__(confirm.strip()):
            err_msg="Mật khẩu không khớp"
        else:
            dao.override_password(email= session.get('email'), password=password)

            return redirect(url_for('user_login'))
    return render_template('verify.html', err_msg=err_msg)


def user_register():
    err_msg = ''
    if request.method.__eq__("POST"):
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar_path = None

        try:
            if password.strip().__eq__(confirm.strip()):
                avatar = request.files.get('avatar')
                if avatar:
                    res = cloudinary.uploader.upload(avatar)
                    avatar_path = res['secure_url']
                dao.add_user(name=name, username=username, password=password,
                             email=email, avatar=avatar_path)
                return redirect(url_for('user_login'))
            else:
                err_msg = 'Mật khẩu không trùng khớp'
        except Exception as ex:
            err_msg = 'Hệ thống lỗi!!!'
    return render_template('register.html', err_msg=err_msg)


def user_login():
    err_msg = ''
    if request.method.__eq__("POST"):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user=user)
            next_page = request.args.get('next')

            if user.user_role.value == UserRole.ADMIN.value:
                return redirect('/admin')
            if user.user_role.value == UserRole.STAFF.value:
                return redirect('/admin')

            return redirect(next_page) if next_page else render_template('index.html')
        else:
            err_msg = "Tài khoản hoặc mật khẩu không chính xác!!!"
    return render_template('login.html', err_msg=err_msg)


def user_logout():
    logout_user()
    session.clear()
    return redirect(url_for('user_login'))


def save_admin_rules():
    data= request.json
    min_time_flight = data.get('min_flight'),
    max_quantity_between_airport = data.get('max_quan_ba'),
    min_time_stay_airport = data.get('min_time_air'),
    max_time_stay_airport = data.get('max_time_air'),
    time_book_ticket = data.get('time_book'),
    time_buy_ticket = data.get('time_buy')

    sa= dao.save_admin_rules(min_time_flight= min_time_flight,
                             max_quantity_between_airport= max_quantity_between_airport,
                             min_time_stay_airport= min_time_stay_airport,
                             max_time_stay_airport= max_time_stay_airport,
                             time_book_ticket= time_book_ticket,
                             time_buy_ticket= time_buy_ticket)



    if not sa:
        return {
            'status': 500,
            'data': 'error'
        }
    return {
        'status': 200,
        'data': 'success'
    }


def save_route_flight():
    data= request.json
    departure_airport= data.get('depart_airport')
    arrival_airport= data.get('arrival_airport')

    if departure_airport and arrival_airport:
        route_exists= dao.check_route_exists(departure_airport_id= dao.get_id_by_name_airport(departure_airport),
                                        arrival_airport_id= dao.get_id_by_name_airport(arrival_airport))
        if not route_exists:
            fr= dao.add_route_flight(departure_airport_id= dao.get_id_by_name_airport(departure_airport),
                                            arrival_airport_id= dao.get_id_by_name_airport(arrival_airport))
            return {
                'status': 200,
                'data': 'success'
            }
    return {
        'status': 500,
        'data': 'error'
    }


def delete_route(route_id):
    del_route= dao.del_route_id(route_id= route_id)
    if del_route:
        return {
            'status': 200,
            'data': 'success'
        }
    return {
        'status': 500,
        'data': 'error'
    }


def edit_route(flight_route):
    data= request.json
    departure_airport = data.get('departure_airport')
    arrival_airport = data.get('arrival_airport')
    flight_route_id= flight_route

    if departure_airport and arrival_airport:
        route_exists= dao.check_route_exists(departure_airport_id= dao.get_id_by_name_airport(departure_airport),
                                        arrival_airport_id= dao.get_id_by_name_airport(arrival_airport))
        check_flight_sche= dao.check_flight_sche_in_route(id= flight_route)
        if route_exists:
            return {
                'status': 500,
                'data': 'error'
            }

        if check_flight_sche:
            return {
                'status': 300,
                'data': 'Đã có chuyến bay tồn tại trong tuyến bay'
            }
        ed = dao.edit_flight_route(departure_airport_id= dao.get_id_by_name_airport(departure_airport),
                                   arrival_airport_id= dao.get_id_by_name_airport(arrival_airport), id= flight_route_id)

        if ed:
            return {
                'status': 200,
                'data': 'success'
            }
    return {
        'status': 500,
        'data': 'error'
    }
    pass


def create_flight_schedule():
    data = request.json
    depart_airport= data.get('depart_airport')
    arrival_airport= data.get('arrival_airport')
    time_start= data.get('time_start')
    time_end= data.get('time_end')
    quantity_1st_ticket= data.get('quantity_1st_ticket')
    quantity_2nd_ticket= data.get('quantity_2nd_ticket')
    price_type_1= data.get('price_type_1')
    price_type_2= data.get('price_type_2')
    airport_between_list= data.get('airportBetweenList')

    try:
        f = dao.create_flight_sche(depart_airport=depart_airport,
                                   arrival_airport=arrival_airport,
                                   time_start=time_start,
                                   time_end=time_end,
                                   quantity_1st_ticket=quantity_1st_ticket,
                                   quantity_2nd_ticket=quantity_2nd_ticket,
                                   price_type_1= price_type_1,
                                   price_type_2= price_type_2)
        for i in airport_between_list:
            bwa= dao.create_between_airport(airport_id=int(i['ap_id']),
                                            flight_sche_id=int(f.id),
                                            time_stay=float(i['ap_stay']),
                                            note=i['ap_note'])
    except Exception as err:
        return {
            'status': 500,
            'data': err
        }
    return {
        'status': 200,
        'data': 'success'
    }


def get_data_details_schedule():
    data= request.json

    details= dao.get_flight_sche_json(request.json.get('flight_schedule_id'))
    if details:
        return {
            'data': 'success',
            'status': 200
        }
    return {

        'data': 'err',
        'status': 500
    }


def search_flight_schedule():
    data = request.json
    departure_airport_id= data.get('departure_airport_id')
    departure_airport_name= data.get('departure_airport_name').strip()
    arrival_airport_id= data.get('arrival_airport_id')
    arrival_airport_name= data.get('arrival_airport_name').strip()
    time_start= data.get('time_start')
    ticket_type= data.get('ticket_type')
    try:
        inp_search = dao.get_inp_search_json(departure_airport_id=departure_airport_id,
                                             departure_airport_name=departure_airport_name,
                                             arrival_airport_id=arrival_airport_id,
                                             arrival_airport_name=arrival_airport_name,
                                             time_start=time_start,
                                             ticket_type=ticket_type)

        data_search = dao.search_flight_sche(departure_airport_id= departure_airport_id,
                                             arrival_airport_id= arrival_airport_id,
                                             time_start=time_start,
                                             ticket_type=ticket_type)

        session['data_search'] = data_search
        session['inp_search'] = inp_search

    except Exception as error:
        return {
            'status': 500,
            'data': error
        }
    return {
        'status': 200,
        'data': data_search
    }


def flight_list():
    admin_rules= dao.get_rule_admin()
    return render_template('flightList.html', admin_rules= admin_rules)


def get_ticket(flight_id):
    ticket_type= request.args.get('ticket-type')
    f = dao.get_flight_sche_json(flight_id)
    seat_active= dao.get_seat_number_active(flight_id)
    return render_template('ticket.html',ticket_type=ticket_type, f=f,
                           user_role=UserRole, seat_active= seat_active)


def bill_ticket(f_id):
    user_id = current_user.get_id()
    quantity_customers= int(session['ticket']['customers_info'][0]['quantity'])
    flight_id = session['ticket']['f_id']
    package_price = (int(session['ticket']['package_price'])/ quantity_customers)
    ticket_type = session['ticket']['ticket_type']
    ticket_price = ((int(session['ticket']['total']))/ quantity_customers- package_price)

    for d in range(len(session['ticket']['customers_info'][0]['data'])):
        cr = dao.create_ticket(user_id=user_id, flight_id=flight_id,
                               customer_id=session['ticket']['customers_info'][0]['data'][d]['id'],
                               ticket_price=ticket_price,
                               ticket_type=ticket_type, package_price=package_price,
                               customer_email=session['ticket']['customers_info'][0]['data'][d]['customer_email'],
                               customer_phone=session['ticket']['customers_info'][0]['data'][d]['customer_phone'],
                               customer_name=session['ticket']['customers_info'][0]['data'][d]['name'],
                               seat_number=session['ticket']['customers_info'][0]['data'][d]['seat_number'],
                               customer_cccd= session['ticket']['customers_info'][0]['data'][d]['customer_cccd'],
                                customer_date = session['ticket']['customers_info'][0]['data'][d]['customer_date'])

    if current_user.user_role.value == UserRole.USER.value:
        email = dao.get_email_by_user(user_id)
        msg = Message(subject='Thông báo về việc thanh toán vé máy bay PhuQuiAirFlight',
                      sender='anhqui04062004@gmail.com', recipients=[email])
        msg.body = ('Bạn đã thanh toán thành công: ' + "{:,.0f}".format(session['ticket']['total']) +
                    ' VND. Chúc bạn có một chuyến đi tốt lành')
        mail.send(msg)
    ticket_list_json=dao.get_ticket_list_json(user_id= user_id, quantity_customers= quantity_customers)
    return render_template('billTicket.html', ticket_list_json= ticket_list_json, quantity_customers= quantity_customers)


def create_ticket(f_id):
    data= request.json
    id = data.get('f_id')
    type_ticket= data.get('ticket_type')
    session['ticket']= data
    remain_ticket=dao.get_ticket_remain(id, type_ticket)

    if remain_ticket < data['customers_info'][0]['quantity']:
        return {
            'status': 500,
            'data': "Chỉ có thể đặt tối đa %s vé!" % remain_ticket
        }
    return {
        'status': 200,
        'data': data['f_id']
    }


def create_checkout_session(f_id):
    try:
        checkout_session= stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'vnd',
                        'product_data': {
                            'name': 'PhuQuiAirFlight',
                        },
                        'unit_amount': int(session['ticket']['total']),
                    },
                    'quantity': 1
                }
            ],
            mode='payment',
            success_url=app.config['MY_DOMAIN'] + '/bill_ticket/' + session['ticket']['f_id'],
            cancel_url= app.config['MY_DOMAIN'] + '/error'
        )
    except Exception as e:
        return str(e)
    return redirect(checkout_session.url, code= 303)


@app.route('/error')
def error():
    return 'error'


def about():
    comments = dao.get_comments()
    return render_template('about.html', comments=comments)


def list_flight_payment(f_id):
    quantity_customers= int(session['ticket']['customers_info'][0]['quantity'])
    data= session['ticket']['customers_info'][0]['data']
    f = dao.get_flight_sche_json(f_id)
    quantity_ticket= dao.count_ticket()
    return render_template('listFlightChoose.html',
                           quantity_ticket= quantity_ticket, quantity_customers= quantity_customers, data= data,f=f)


def get_stats_revenue(month):
    if int(month).__eq__(0):
        return dao.get_revenue_stats_json_list()
    return dao.get_revenue_stats_json_list(month)


def get_stats_ticket(month):
    if int(month).__eq__(0):
        return dao.get_ticket_stats_json_list()
    return dao.get_ticket_stats_json_list(month)


def get_stats_flight(month):
    if int(month).__eq__(0):
        return dao.get_flight_stats_json_list()
    return dao.get_flight_stats_json_list(month)


def get_stats_total(month):
    if int(month).__eq__(0):
        return dao.get_data_stats_json_list()
    return dao.get_data_stats_json_list(month)

@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.context_processor
def common_attributes():
    return {
        'user_role': UserRole
    }


def add_comment():
    data = request.json
    content = data.get('content')
    user_id= current_user.get_id()
    if content:
        c= dao.add_comment(content=content, user_id= user_id)
        return {
            'status': 200,
            'data': 'success'
        }
    return {
        'status': 500,
        'err': 'Lỗi bình luận'
    }

def find_ticket():
    return render_template('findTicket.html')


def res_ticket():
    info_cus = request.json.get('info_cus')
    customer = dao.get_ticket_by_customer(info_user=info_cus)
    if customer:
        return {
            'status': 200,
            'data': 'success'
        }
    return {
        'status': 400
    }

def response_search():
    return render_template('responseTicket.html')
