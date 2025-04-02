from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from QLChuyenBay import db, login, app
from enum import Enum as UserEnum
import dao
from flask_login import login_user
from flask_login import UserMixin
from datetime import datetime

class BaseModel(db.Model):
    __abstract__= True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    ADMIN = 1
    STAFF = 2
    USER = 3

class User(BaseModel, UserMixin):
    __table_args__ = {'extend_existing': True}
    name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False, unique= True)
    password = Column(String(100), nullable=False)
    avatar = Column(String(100))
    email = Column(String(50), nullable= False, unique= True)
    active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER)


    def __str__(self):
        return self.name

class Rule(BaseModel):
    __table_args__ = {'extend_existing': True}
    min_time_flight= Column(Float, default=30)
    max_quantity_between_airport= Column(Integer, default=2)
    min_time_stay_airport= Column(Float, default= 20)
    max_time_stay_airport= Column(Float, default= 30)
    time_book_ticket= Column(Float, default= 12)
    time_buy_ticket= Column(Float, default= 4)
    created_at= Column(DateTime, default= datetime.now())
    author_id= Column(Integer, ForeignKey(User.id))

class AirPort(BaseModel):
    __table_args__ = {'extend_existing': True}
    name= Column(String(100), nullable=False)

    def __str__(self):
        return self.name
#
class FlightRoute(BaseModel):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'flight_routes'
    departure_airport_id= Column(Integer, ForeignKey(AirPort.id))
    arrival_airport_id= Column(Integer, ForeignKey(AirPort.id))
    created_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return str(self.id)

class FlightSchedule(BaseModel):
    __tablename__ = 'flight_schedules'
    __table_args__ = {'extend_existing': True}
    i_act= Column(Boolean, default= False)
    i_del= Column(Boolean, default= False)
    flight_route_id = Column(Integer, ForeignKey('flight_routes.id'))

    time_start= Column(DateTime, nullable= False)
    time_end= Column(DateTime, nullable= False)
    ticket1_quantity= Column(Integer, nullable= False)
    ticket1_book_quantity= Column(Integer, default= 0)
    ticket2_quantity= Column(Integer, nullable= False)
    ticket2_book_quantity= Column(Integer, default= 0)
    price_type_1= Column(Float, default=0)
    price_type_2= Column(Float, default=0)
    created_date = Column(DateTime, default=datetime.now())



    def __str__(self):
        return str(self.id)

class BetweenAirport(BaseModel):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'between_airport'
    airport_id = Column(Integer, ForeignKey(AirPort.id))
    flight_sche_id= Column(Integer, ForeignKey(FlightSchedule.id))

    time_stay= Column(Float, nullable= False)
    note= Column(String(100))
    is_deleted = Column(Boolean, default=False)

class Customer(BaseModel):
    __table_args__ = {'extend_existing': True}
    customer_name= Column(String(100), nullable= False)
    customer_email= Column(String(50))
    customer_phone= Column(String(12), nullable= False)
    customer_cccd= Column(String(12), nullable= False)
    customer_date= Column(DateTime, nullable= False)

    def __str__(self):
        return self.customer_name


class Ticket(BaseModel):
    __table_args__ = {'extend_existing': True}
    author_id = Column(Integer, ForeignKey(User.id), nullable=True)
    customer_id = Column(Integer, ForeignKey(Customer.id))
    flight_sche_id = Column(Integer, ForeignKey(FlightSchedule.id), nullable=True)
    ticket_price = Column(Integer, nullable= False)
    ticket_type= Column(Integer, nullable= False)
    ticket_package_price= Column(Integer, default=0)
    created_at= Column(DateTime, default= datetime.now())


class Seat(BaseModel):
    __table_args__ = {'extend_existing': True}
    seat_number= Column(Integer, nullable=False)
    flight_sche_id= Column(Integer, ForeignKey(FlightSchedule.id), nullable= False)
    ticket_id= Column(Integer, ForeignKey(Ticket.id), nullable= False)
    is_active= Column(Boolean, default= False)

class Comment(BaseModel):
    __table_args__ = {'extend_existing': True}
    content = Column(String(255),nullable=False)
    customer_id = Column(Integer,ForeignKey(User.id),nullable=False)
    created_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content


@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id=user_id)

if __name__=="__main__":
    with app.app_context():
        db.create_all()
        pass
        # #
        # a1 = AirPort(name="Tân Sơn Nhất")
        # a2 = AirPort(name="Nội Bài")
        # a3 = AirPort(name="Côn Đảo")
        # a4 = AirPort(name="Cà Mau")
        # a5 = AirPort(name="Cần Thơ")
        # a6 = AirPort(name="Phú Bài")
        # a7 = AirPort(name="Vân Đồn")
        # a8 = AirPort(name="Đà Nẵng")
        # a9 = AirPort(name="Phú Quốc")
        # a10 = AirPort(name="Vinh")
        #
        # db.session.add_all([a1, a2, a3, a4, a5, a6, a7, a8, a9, a10])
        # db.session.commit()
        # a = Rule()
        # db.session.add(a)
        # db.session.commit()