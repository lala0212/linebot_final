#%%
import os
import requests
from lxml import etree
from func import sentmail
from fake_useragent import UserAgent
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
user_agent = UserAgent()
import time
import random as rd
from apscheduler.schedulers.background import BackgroundScheduler
#%%
app = Flask(__name__)
pjdir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(pjdir, 'database.db')
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    delet_tmp = db.Column(db.Text)
    list_tmp = db.Column(db.Text)
    email = db.Column(db.String(120), unique=True)
    act = db.Column(db.Integer)
    Book_lists_rel = db.relationship('Book_list', backref='u')

    def __repr__(self):
        return '<User %r>' % self.username

class Book_list(db.Model):
    __tablename__ = 'Book_lists'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    url = db.Column(db.String)
    num = db.Column(db.String)
    fig = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return 'contact_style:%s, contact_context:%s' % \
            (self.contact_style, self.contact_context)
    
#
#%%
def check_database():
    print("start")
    with app.app_context():
        list_all = [ Bkurl.url for Bkurl in Book_list.query.all()]
    list_all = [item for item in list_all if item is not None]
    list_all = list(set(list_all))
    for url in list_all:
        time.sleep(5)
        user_agent = UserAgent()
        content_ = requests.get(url, headers={ 'user-agent': user_agent.random })
        time.sleep(rd.random())
        content = content_.content
        html = etree.HTML(content)
        try:
            num = html.xpath("//li[@class='status']/span/a[@class='blue']")[0].text
            with app.app_context():
                num_ = Book_list.query.filter_by(url=url).first().num
            if num != num_:
                with app.app_context():
                    name = Book_list.query.filter_by(url=url).first().title
                    ids = [ Bkurl.user_id for Bkurl in Book_list.query.filter_by(url=url).all()]
                print("yes")
                for id in ids:
                    with app.app_context():
                        Book_list.query.filter_by(user_id=id,url=url).first().num = num
                        mail = User.query.filter_by(id=id).first().email
                        db.session.commit()
                    if mail != None:    
                        sentmail(name,num,url,mail)
                        
        except:
            pass # doing nothing on exception

# 启动后台任务
            
check_database()
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_database, trigger="interval", hours=4)
scheduler.start()
if __name__ == '__main__':
    app.run(debug=True)
