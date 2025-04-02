from random import randint
import smtplib
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager
from flask_mail import *
from flask_principal import Principal
import stripe
from urllib.parse import quote


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/flightmanagement?charset=utf8mb4" % quote("Admin@123")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= True
app.secret_key='jiugyvIU*YGUFT*&&^T&GUHBOHIGY&(*)(U*HIJBHVFYFY%^&^&^&(*)*YUGBHOIB48451'

app.config["PAGE_SIZE"] = 8
app.config["CMT_SIZE"] = 10

app.config["MAIL_SERVER"]='smtp.gmail.com'
app.config["MAIL_PORT"]= 587
app.config["MAIL_USERNAME"]='anhqui04062004@gmail.com'
app.config["MAIL_PASSWORD"]='hsesebwdzpkqnzna'
app.config["MAIL_USE_TLS"]= True

app.config['MY_DOMAIN']= 'http://localhost:5002'

cloudinary.config(
    cloud_name= 'do43r8nr0',
    api_key='947875495844325',
    api_secret= 'evQEPk5TbxIMpCWbbXl8sLMbo6A'
)

stripe.api_key= 'sk_test_51QVbF6GdmuuxpPW1WKDGv0LbqFP9D7ilJcLKa2jLf5tE0r6TkWteM0GTeLTsGjHU3oaB3tHFNbydVhhdOyZmFdaX00BJJPujHJ'
endpoint_secret= 'whsec_ldgJn7UZz83pP87KLpAw5fkh8WT4hOJr'

otp= randint(000000, 999999)
mail=Mail(app=app)
db= SQLAlchemy(app=app)
login= LoginManager(app=app)
principals = Principal(app=app)
