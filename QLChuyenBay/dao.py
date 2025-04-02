import json, os
from flask import url_for
from flask_login import current_user
from sqlalchemy.sql.operators import desc_op
import datetime
from QLChuyenBay import app, db
from QLChuyenBay.models import User, UserRole, Rule, AirPort, FlightRoute, FlightSchedule, BetweenAirport, Ticket, Customer, Seat, Comment
import hashlib
import re
import locale
from sqlalchemy import func, desc, extract, and_

locale.setlocale(locale.LC_ALL, 'vi_VN')

#Them vao 1 tai khoan dang ky vao database
def add_user(name, username, password, email, **kwarg):
    password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
    user = User(name = name, username = username, password = password,
                email = email, avatar = kwarg.get('avatar'))
    db.session.add(user)
    db.session.commit()


#Kiem tra tai khoan do co trong database hay khong
def auth_user(username, password, role=UserRole.USER):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()),
                          User.password.__eq__(password)).first()

def check_mail_exit(email):
    if email:
        return User.query.filter(User.email.__eq__(email)).first()

#Cap nhat lai mat khau moi
def override_password(email, password):
    password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
    user= User.query.filter(User.email.__eq__(email)).first()
    if user:
        user.password= password
        db.session.commit()


#Luu quan ly quy dinh moi vao database
def save_admin_rules(min_time_flight, max_quantity_between_airport, min_time_stay_airport,
                     max_time_stay_airport, time_book_ticket,time_buy_ticket):
    sa= Rule(min_time_flight= min_time_flight,
             max_quantity_between_airport= max_quantity_between_airport,
             min_time_stay_airport= min_time_stay_airport,
             max_time_stay_airport= max_time_stay_airport,
             time_book_ticket= time_book_ticket,
             time_buy_ticket= time_buy_ticket)
    db.session.add(sa)
    db.session.commit()
    return sa

def get_rule_admin():
    return Rule.query.order_by(Rule.created_at.desc()).first()

def get_email_by_user(id):
    return User.query.filter(User.id.__eq__(id)).first().email

def get_id_by_name_airport(name):
    return AirPort.query.filter(AirPort.name.__eq__(name)).first().id

def get_air_port_list():
    return AirPort.query.filter().all()

#Them tuyen bay
def add_route_flight(departure_airport_id, arrival_airport_id):
    if departure_airport_id and arrival_airport_id:
        fr= FlightRoute(departure_airport_id= departure_airport_id,
                        arrival_airport_id= arrival_airport_id)
        db.session.add(fr)
        db.session.commit()
        return fr
    return None

def get_route_list():
    return FlightRoute.query.order_by(FlightRoute.created_date.desc()).all()

def del_route_id(route_id):
    fd= FlightRoute.query.filter(FlightRoute.id.__eq__(route_id)).first()
    db.session.delete(fd)
    db.session.commit()
    return fd

def check_route_exists(departure_airport_id, arrival_airport_id):
    route_exist= FlightRoute.query.filter(FlightRoute.departure_airport_id.__eq__(departure_airport_id),
                                          FlightRoute.arrival_airport_id.__eq__(arrival_airport_id)).all()
    return route_exist

def edit_flight_route(departure_airport_id, arrival_airport_id, id):
    route= FlightRoute.query.get(id)
    if route:
        route.departure_airport_id= departure_airport_id
        route.arrival_airport_id = arrival_airport_id
        db.session.commit()
    return route

def create_flight_sche(depart_airport, arrival_airport, time_start, time_end,
                       quantity_1st_ticket, quantity_2nd_ticket, price_type_1, price_type_2):
    route_flight_id= FlightRoute.query.filter(FlightRoute.departure_airport_id.__eq__(depart_airport),
                                              FlightRoute.arrival_airport_id.__eq__(arrival_airport)).first()
    if route_flight_id:
        f = FlightSchedule(
            flight_route_id=route_flight_id.id,
            i_act= True,
            time_start=time_start,
            time_end=time_end,
            ticket1_quantity=quantity_1st_ticket,
            ticket2_quantity=quantity_2nd_ticket,
            price_type_1=price_type_1,
            price_type_2=price_type_2)

        db.session.add(f)
        db.session.commit()
        return f
    return {
        'status': 500,
        'data': 'error'
    }

def check_flight_sche_in_route(id):
    return FlightSchedule.query.filter(FlightSchedule.flight_route_id.__eq__(id)).first()

def create_between_airport(airport_id, flight_sche_id, time_stay, note):
    bwa= BetweenAirport(airport_id=int(airport_id), flight_sche_id=int(flight_sche_id), time_stay=float(time_stay),
                         note=note)
    db.session.add(bwa)
    db.session.commit()
    return bwa

def get_airport_by_id(a):
    return AirPort.query.filter(AirPort.id.__eq__(a)).first()

def get_route_json(fs):
    r= FlightRoute.query.get(fs.flight_route_id)

    if r:
        return {
            'departure_airport': get_airport_by_id(r.departure_airport_id).name,
            'arrival_airport': get_airport_by_id(r.arrival_airport_id).name
        }
    else:
        return {
            'departure_airport': '',
            'arrival_airport': ''
        }

def get_name_airport_by_id(id):
    return AirPort.query.filter(AirPort.id.__eq__(id)).first().name

def get_between_list(fs):
    bwa_list= BetweenAirport.query.filter(BetweenAirport.flight_sche_id.__eq__(fs.id)).all()
    airport_between_list = []
    if bwa_list:
        for bwa in bwa_list:
            obj = {
                'id': bwa.id,
                'airport_id': bwa.airport_id,
                'airport_name': get_name_airport_by_id(bwa.airport_id),
                'flight_sche_id': bwa.flight_sche_id,
                'time_stay': bwa.time_stay,
                'note': bwa.note
            }
            airport_between_list.append(obj)
    else:
        obj = {
            'id': '',
            'airport_id': '',
            'flight_sche_id': '',
            'time_stay': '',
            'note': ''
        }
        airport_between_list.append(obj)
    return airport_between_list

def get_flight_sche_json(id):
    fs= FlightSchedule.query.get(id)
    if fs:
        fr= get_route_json(fs)
        bwl= get_between_list(fs)
        return {
            "id": fs.id,
            'departure_airport': fr['departure_airport'],
            'arrival_airport': fr['arrival_airport'],
            'time_start': fs.time_start,
            'time_end': fs.time_end,
            'ticket1_quantity': fs.ticket1_quantity,
            'ticket2_quantity': fs.ticket2_quantity,
            'ticket1_book_quantity': fs.ticket1_book_quantity,
            'ticket2_book_quantity': fs.ticket2_book_quantity,
            'price_type_1': "{:,.0f}".format(fs.price_type_1),
            'price_type_2': "{:,.0f}".format(fs.price_type_2),
            'between_list': {
                'quantity': len(bwl),
                'data': bwl
            }
        }
    return {
        'status': 500,
        'data': 'error'
    }


def get_flight_sche_list():
    f_list = FlightSchedule.query.all()
    f_list.reverse()
    flight_sche_list = []
    for f in f_list:
        flight_sche = get_flight_sche_json(f.id)
        flight_sche_list.append(flight_sche)
    return flight_sche_list

def get_inp_search_json(departure_airport_id, departure_airport_name, arrival_airport_id,
                        arrival_airport_name, time_start, ticket_type):
    return {
        "departure_airport_id": departure_airport_id,
        "departure_airport_name": departure_airport_name,
        "arrival_airport_id": arrival_airport_id,
        "arrival_airport_name": arrival_airport_name,
        "time_start": time_start,
        "ticket_type": ticket_type
    }

def get_route_by_depart_and_arrival_id(departure_airport_id, arrival_airport_id):
    return FlightRoute.query.filter(FlightRoute.departure_airport_id.__eq__(departure_airport_id),
                                    FlightRoute.arrival_airport_id.__eq__(arrival_airport_id)).first()

def search_flight_sche(departure_airport_id, arrival_airport_id, time_start, ticket_type):
    time_array= time_start.split('-')
    time= datetime.datetime(int(time_array[0]), int(time_array[1]), int(time_array[2]))
    route= get_route_by_depart_and_arrival_id(departure_airport_id, arrival_airport_id)
    if route:
        flight_list= FlightSchedule.query.filter(FlightSchedule.i_act.__eq__(True), FlightSchedule.i_del.__eq__(False)).all()

        flight_list_arr_tmp=[]

        for fl in flight_list:
            if fl.flight_route_id.__eq__(route.id) and fl.time_start.__gt__(time):
                flight_list_arr_tmp.append(fl)

        flight_list_arr=[]
        if int(ticket_type)==1:
            for fla in flight_list_arr_tmp:
                if fla.ticket1_quantity.__gt__(fla.ticket1_book_quantity):
                    flight_list_arr.append(fla)
        if int(ticket_type)==2:
            for fla in flight_list_arr_tmp:
                if fla.ticket2_quantity.__gt__(fla.ticket2_book_quantity):
                    flight_list_arr.append(fla)

        flight_schedule_list=[]
        for f in flight_list_arr:
            f_sche= get_flight_sche_json(f.id)
            flight_schedule_list.append(f_sche)
        return flight_schedule_list

def get_ticket_json(t_id, quantity):
    t = Ticket.query.filter(Ticket.id.__eq__(t_id)).first()
    c = Customer.query.filter(Customer.id.__eq__(t.id)).first()
    return {
        'id': t.id,
        'author_id': t.author_id,
        'flight_sche_id': get_flight_sche_json(t.flight_sche_id),
        'ticket_price': t.ticket_price,
        'ticket_type': t.ticket_type,
        'ticket_package_price': t.ticket_package_price,
        'customer_name': c.customer_name,
        'customer_phone': c.customer_phone,
        'customer_cccd': c.customer_cccd,
        'customer_email': c.customer_email,
        'customer_id': c.id,
        'created_at': t.created_at,
        'quantity': quantity
    }

def get_ticket_list_json(user_id, quantity_customers):
    t_list = Ticket.query.filter(Ticket.author_id.__eq__(user_id)).order_by(Ticket.created_at.desc()).all()
    quantity= len(t_list)
    t_list= t_list[:int(quantity_customers)]
    t_list_json = []
    for t in t_list:
        t_list_json.append(get_ticket_json(t.id, quantity))
    return t_list_json


def get_ticket_remain(flight_id, ticket_type):
    f= FlightSchedule.query.filter(FlightSchedule.i_act.__eq__(True), FlightSchedule.i_del.__eq__(False),
                                   FlightSchedule.id.__eq__(flight_id)).all()[0]
    remain=0
    if int(ticket_type)==1:
        remain= f.ticket1_quantity- f.ticket1_book_quantity
    if int(ticket_type)==2:
        remain = f.ticket2_quantity - f.ticket2_book_quantity
    return remain


def save_customer(customer_name, customer_phone, customer_email, customer_cccd, customer_date):
    c = Customer(customer_name=customer_name, customer_phone=customer_phone, customer_email=customer_email,
                 customer_cccd= customer_cccd, customer_date= customer_date)
    db.session.add(c)
    db.session.commit()
    return c

def save_seat_number(seat_number, ticket_id, flight_sche_id):
    s= Seat(seat_number= seat_number, ticket_id= ticket_id, flight_sche_id=flight_sche_id, is_active= True)
    db.session.add(s)
    db.session.commit()
    return s

def count_ticket():
    return Ticket.query.count()

def get_latest_ticket():
    ticket = Ticket.query.order_by(Ticket.created_at.desc()).first()
    return ticket.id

def check_seat_and_flight_sche_exist(seat_number, flight_sche_id):
    return Seat.query.filter(Seat.flight_sche_id.__eq__(flight_sche_id), Seat.seat_number.__eq__(seat_number)).first()


def create_ticket(flight_id, ticket_type, package_price, ticket_price, customer_name, customer_phone,
                  customer_email, customer_id, user_id, seat_number, customer_cccd, customer_date):
    f = FlightSchedule.query.filter(FlightSchedule.id.__eq__(flight_id), FlightSchedule.i_act.__eq__(True),
                                    FlightSchedule.i_del.__eq__(False)).first()
    if int(ticket_type) == 1:
        f.ticket1_book_quantity = f.ticket1_book_quantity + 1
    if int(ticket_type) == 2:
        f.ticket2_book_quantity = f.ticket2_book_quantity + 1
    cus = save_customer(customer_name=customer_name, customer_phone=customer_phone,
                        customer_email= customer_email, customer_cccd=customer_cccd, customer_date= customer_date)

    t = Ticket(author_id=user_id, flight_sche_id=flight_id, customer_id=customer_id,
               ticket_type=ticket_type, ticket_price= ticket_price, ticket_package_price= package_price, created_at=datetime.datetime.now())
    db.session.add(t)
    db.session.commit()

    if not check_seat_and_flight_sche_exist(flight_sche_id= flight_id, seat_number= seat_number):
        ticket_id= get_latest_ticket()
        s = save_seat_number(seat_number=seat_number, ticket_id= ticket_id, flight_sche_id= flight_id)
        db.session.add(cus, s)
        db.session.commit()
        return {
            "cus":cus,
            "ticket": t,
            'seat': s
        }
    return {
        'status': 500,
        'data': 'err'
    }

def get_id_ticket(flight_sche_id, customer_id, author_id):
    return Ticket.query.filter(Ticket.flight_sche_id.__eq__(flight_sche_id),
                               Ticket.customer_id.__eq__(customer_id),
                               Ticket.author_id.__eq__(author_id)).first().id


def get_seat_number_active(f_id):
    seat_arr=[]
    seats= Seat.query.filter(Seat.flight_sche_id.__eq__(f_id))
    for s in seats:
        seat_arr.append(s.seat_number)
    return seat_arr

# Thông ke
def route_stats_in_month_json(id, total):
    return {
        'flight_route': get_depart_and_arrival_name_json(id),
        'total': total
    }

def get_depart_and_arrival_name_json(id):
    fr= FlightRoute.query.get(id)
    return {
        'id': id,
        'departure_airport': get_airport_by_id(fr.departure_airport_id).name,
        'arrival_airport': get_airport_by_id(fr.arrival_airport_id).name
    }

#Them binh luan
def add_comment(content, user_id):
    c = Comment(content=content,customer_id=user_id, created_date= datetime.datetime.now())

    db.session.add(c)
    db.session.commit()
    return c

def get_username_by_id(id):
    return User.query.get(id)

def get_avatar_by_id(id):
    return User.query.get(id).avatar

def get_comments(quantity=10):
    comments = Comment.query.order_by(Comment.created_date.desc()).limit(quantity).all()
    list_comments=[]
    for i in comments:
        if get_avatar_by_id(i.customer_id):
            info={
                'user_name': get_user_by_id(i.customer_id).name,
                'content': i.content,
                'avatar': get_avatar_by_id(i.customer_id)
            }
            list_comments.append(info)
        else:
            info = {
               'user_name': get_user_by_id(i.customer_id).name,
               'content': i.content,
               'avatar': 'https://res.cloudinary.com/do43r8nr0/image/upload/w_1000,c_fill,ar_1:1,g_auto,r_max,bo_5px_solid_red,b_rgb:262c35/v1729400798/samples/man-portrait.jpg',
               'created_date': i.created_date
            }
            list_comments.append(info)
    return list_comments


# Tinh tong doanh thu theo tung tuyen bay
def get_total_ticket_revenue_per_route():
    query = db.session.query(
        FlightRoute.id.label('flight_route_id'),
        func.sum(Ticket.ticket_price + Ticket.ticket_package_price).label('total_revenue')) \
        .select_from(FlightRoute)\
        .join(FlightSchedule, FlightRoute.id == FlightSchedule.flight_route_id) \
        .join(Ticket, FlightSchedule.id == Ticket.flight_sche_id) \
        .group_by(FlightRoute.id)
    return query.all()

def get_total_ticket_revenue_per_route_each_month(m):
    query = db.session.query(FlightRoute.id,
        func.sum(Ticket.ticket_price + Ticket.ticket_package_price).label('total_revenue'))\
        .select_from(FlightRoute) \
        .join(FlightSchedule, FlightRoute.id == FlightSchedule.flight_route_id) \
        .join(Ticket, FlightSchedule.id == Ticket.flight_sche_id) \
        .group_by(FlightRoute.id, func.month(Ticket.created_at)) \
        .filter(func.month(Ticket.created_at) == m) \
        .all()
    return query

def get_revenue_stats_json_list(m=None):
    if m is None:
        stats = get_total_ticket_revenue_per_route()
    else:
        stats = get_total_ticket_revenue_per_route_each_month(m)
    stats_list = []

    total_price = 0
    for s in stats:
        if s[0]:
            total_price = total_price + int(s[1])
        obj = route_stats_in_month_json(s[0], s[1])
        stats_list.append(obj)
    return {
        'data': stats_list,
        'total_price': total_price,
    }


#Tinh tong ve theo tung tuyen bay
def get_total_ticket_quantity_per_route():
    query = db.session.query(
        FlightRoute.id, func.count(Ticket.id).label('total_ticket')) \
        .select_from(FlightRoute) \
        .join(FlightSchedule, FlightRoute.id == FlightSchedule.flight_route_id) \
        .join(Ticket, FlightSchedule.id == Ticket.flight_sche_id) \
        .group_by(FlightRoute.id)
    return query.all()

def get_total_ticket_quantity_per_route_each_month(m):
    query= db.session.query(FlightRoute.id,
        func.count(Ticket.id).label('total_ticket'))\
        .select_from(FlightRoute) \
        .join(FlightSchedule, FlightRoute.id == FlightSchedule.flight_route_id) \
        .join(Ticket, FlightSchedule.id == Ticket.flight_sche_id) \
        .group_by(FlightRoute.id, func.month(Ticket.created_at)) \
        .filter(func.month(Ticket.created_at) == m) \
        .all()
    return query

def get_ticket_stats_json_list(m=None):
    if not m:
        stats = get_total_ticket_quantity_per_route()
    else:
        stats = get_total_ticket_quantity_per_route_each_month(m)
    stats_list = []
    total_ticket = 0
    for s in stats:
        if s[0]:
            total_ticket = total_ticket + int(s[1])
        obj = route_stats_in_month_json(s[0], s[1])
        stats_list.append(obj)

    return {
        'data': stats_list,
        'total_ticket': total_ticket,
    }

#Tinh so chuyen bay cua tung tuyen bay
def get_total_flight_quantity_per_route():
    return db.session.query(FlightRoute.id,
            func.count(FlightSchedule.id)) \
            .join(FlightSchedule, FlightRoute.id.__eq__(FlightSchedule.flight_route_id), isouter=True) \
            .group_by(FlightRoute.id).order_by(FlightRoute.id.asc()).all()

def get_total_flight_quantity_per_route_each_month(m):
    return db.session.query(FlightRoute.id,
            func.count(FlightSchedule.id), func.month(FlightSchedule.created_date)) \
            .join(FlightSchedule, FlightRoute.id.__eq__(FlightSchedule.flight_route_id), isouter=True) \
            .group_by(FlightRoute.id, func.month(FlightSchedule.created_date)) \
            .filter(func.month(FlightSchedule.created_date) == m).order_by(FlightRoute.id.asc()).all()

def get_flight_stats_json_list(m=None):
    if not m:
        stats = get_total_flight_quantity_per_route()
    else:
        stats = get_total_flight_quantity_per_route_each_month(m)
    stats_list = []
    total_flight = 0
    for s in stats:
        if s[1]:
            total_flight = total_flight + int(s[1])
        obj = route_stats_in_month_json(s[0], s[1])
        stats_list.append(obj)
    return {
        'data': stats_list,
        'total_flight': total_flight,
    }

#Tong thu
def get_total_data_stats():
   return db.session.query(
      FlightRoute.id,
      db.func.count(FlightSchedule.id).label('num_schedules'),
      db.func.count(Ticket.id).label('num_tickets'),
      db.func.sum(db.func.coalesce(Ticket.ticket_package_price, 0) + Ticket.ticket_price).label('total_revenue'))\
       .join(FlightSchedule, FlightRoute.id.__eq__(FlightSchedule.flight_route_id), isouter= True)\
       .join(Ticket, FlightSchedule.id.__eq__(Ticket.flight_sche_id), isouter= True)\
       .group_by(FlightRoute.id).order_by(FlightRoute.id).all()

def get_total_data_stats_per_month(m):
   return db.session.query(
      FlightRoute.id,
      db.func.count(FlightSchedule.id),
      db.func.count(Ticket.id),
      db.func.sum(db.func.coalesce(Ticket.ticket_package_price, 0) + Ticket.ticket_price).label('total_revenue'))\
       .join(FlightSchedule, FlightRoute.id == FlightSchedule.flight_route_id, isouter= True)\
       .join(Ticket, FlightSchedule.id == Ticket.flight_sche_id, isouter= True)\
        .filter(db.func.month(FlightSchedule.created_date) == m)\
        .group_by(FlightRoute.id).order_by(FlightRoute.id).all()


def get_data_stats_json(id, total_flight, total_ticket, total_price):
    return {
        'flight_route': get_depart_and_arrival_name_json(id),
        'total_flight': total_flight,
        'total_ticket': total_ticket,
        'total_price': total_price or 0
    }

def get_data_stats_json_list(m=None):
    if m is None:
        stats = get_total_data_stats()
    else:
        stats = get_total_data_stats_per_month(m)
    stats_list = []
    total_price = 0
    total_ticket = 0
    total_flight= 0
    for s in stats:
        if s[3]:
            total_price = total_price + int(s[3])
        total_ticket = total_ticket + int(s[2])
        total_flight= total_flight + int(s[1])
        obj = get_data_stats_json(s[0], s[1], s[2], s[3])
        stats_list.append(obj)
        if total_price:
            for sl in stats_list:
                sl['flight_rate'] = float(sl['total_flight'] / total_flight) * 100
    return {
        'data': stats_list,
        'total_price': total_price,
        'total_flight': total_flight,
        'total_ticket': total_ticket
    }

def get_info_user(info_user):
    if len(info_user) == 12:
        return Customer.query.filter(Customer.customer_cccd.__eq__(info_user)).first()
    if len(info_user) == 10:
        return Customer.query.filter(Customer.customer_phone.__eq__(info_user)).first()

def get_ticket_by_id_customer(cus):
    return Ticket.query.filter(Ticket.customer_id.__eq__(cus.id)).all()

def get_ticket_by_customer(info_user):
    cus= get_info_user(info_user=info_user)

    if cus:
        get_list_ticket= get_ticket_by_id_customer(cus)
        t_list_json = []

        for t in get_list_ticket:
            t_list_json.append(get_ticket_json(t.id, 10))
        return t_list_json

def get_user_by_id(user_id):
    return User.query.get(user_id)




