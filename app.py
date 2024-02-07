#%%
import os
import time
import random as rd
from lxml import etree
import requests
from fake_useragent import UserAgent
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,PostbackEvent, TextMessage,\
TextSendMessage,CarouselColumn,URIAction,PostbackAction,ImageSendMessage
from flask_sqlalchemy import SQLAlchemy
from func import menu, welcome,search_book_name,confirm,delet_book,sentmail,search_book_new
from apscheduler.schedulers.background import BackgroundScheduler
#%%

app = Flask(__name__)
current_directory = os.path.dirname(os.path.abspath(__file__))
relative_image_path = 'example.png'
img_path = os.path.join(current_directory, relative_image_path)
pjdir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ os.path.join(pjdir, 'database.db')
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
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
    url_book = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return 'contact_style:%s, contact_context:%s' % \
            (self.contact_style, self.contact_context)
   
# with app.app_context():
#     db.create_all()
#%%
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
#%%
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'
@handler.add(PostbackEvent)
def handle_postback(event):
    # 处理 postback 事件
    payload = event.postback.data
    userid = event.source.user_id
    user = User.query.filter_by(name=userid).first()
    payload,Bid = payload.split('_')
    if payload == 'enter':
        line_bot_api.reply_message(
                event.reply_token,
                [
        TextSendMessage("請用以下網頁搜尋，並回傳網址"),
        TextSendMessage("https://tw.manhuagui.com/"),
        ImageSendMessage(original_content_url="https://i.pinimg.com/originals/96/09/c4/9609c4639d2b4b6edebce0adcc200311.jpg", preview_image_url="https://i.pinimg.com/originals/96/09/c4/9609c4639d2b4b6edebce0adcc200311.jpg")
    ])
        user.act = 2
        db.session.commit()

    elif payload == 'delet':
        db.session.delete(Book_list.query.get(Bid))
        db.session.commit()

        ll = user.Book_lists_rel
        carousel_columns = []
        for book_list in ll:
            column = CarouselColumn(
                thumbnail_image_url='https:'+book_list.fig,
                title=book_list.title,
                text=book_list.num,
                actions=[URIAction(
                    label='查看',
                    uri= book_list.url_book
                ),
                PostbackAction(
                    label='刪除',
                    data='delet_'+str(book_list.id)
        
                )],
            )
            carousel_columns.append(column) 
        rep = delet_book(carousel_columns)
        line_bot_api.reply_message(
                event.reply_token,
                rep)
        


    
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    userid = event.source.user_id
    user_ext = User.query.filter_by(name=userid).first()

    if user_ext == None:
        db.session.add(User(name=userid,act=0))
        db.session.commit()
    user = User.query.filter_by(name=userid).first()
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    text=event.message.text
    if text == "home" or text == "exit":
        line_bot_api.reply_message(
            event.reply_token,
            menu)
        user.act = 0
    elif text=="@新增漫畫":
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage("請輸入漫畫名稱"))
        user.act = 1
    elif text == "@漫畫列表":
        ll = user.Book_lists_rel
        carousel_columns = []
        for book_list in ll:
            column = CarouselColumn(
                thumbnail_image_url='https:'+book_list.fig,
                title=book_list.title,
                text=book_list.num,
                actions=[URIAction(
                    label='查看',
                    uri= book_list.url_book
                ),
                PostbackAction(
                    label='刪除',
                    data='delet_'+str(book_list.id)
        
                )],
            )
            carousel_columns.append(column) 
        rep = delet_book(carousel_columns)
        line_bot_api.reply_message(
                event.reply_token,
                rep)
        user.act = 0
    elif text=="@編輯信箱":
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage("請輸入信箱\n若要刪除請輸入: 刪除信箱"))
        user.act = 3

    elif text=="@是":
        title,url,num,fig,url_book= user.list_tmp.split('@')
        namenid = Book_list.query.filter_by(u=user,title=title).first()
        if namenid == None:
            db.session.add(Book_list(title=title,url=url,num=num,fig=fig,u=user,url_book=url_book))
        user.list_tmp = ""
        user.act = 0
        line_bot_api.reply_message(
        event.reply_token,[
        TextSendMessage("新增成功"),menu])
        
    elif user.act == 1:
        title,url,num,fig,url_book = search_book_new(text)
        if title == "notwork":
            line_bot_api.reply_message(
                event.reply_token,
                   [
        TextSendMessage("請用以下網頁搜尋，並回傳網址"),
        TextSendMessage("https://tw.manhuagui.com/"),
        ImageSendMessage(original_content_url="https://i.pinimg.com/originals/96/09/c4/9609c4639d2b4b6edebce0adcc200311.jpg", preview_image_url="https://i.pinimg.com/originals/96/09/c4/9609c4639d2b4b6edebce0adcc200311.jpg")
    ])
            user.act = 2
        else:
            rep = confirm(title)
            line_bot_api.reply_message(
                event.reply_token,
                rep)
            user.act = 0
            user.list_tmp = "{}@{}@{}@{}@{}".format(title,url,num,fig,url_book)    

    elif user.act == 2:
        title_ =  search_book_name(text)  
        if title_ == "notwork":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage("拍謝，出事拉"))
            user.act = 0
        else:
            title,url,num,fig,url_book = search_book_new(title_)
            rep = confirm(title)
            line_bot_api.reply_message(
                event.reply_token,
                rep)
            user.act = 0
            user.list_tmp = "{}@{}@{}@{}@{}".format(title,url,num,fig,url_book)              
    
    

    elif user.act == 3:
        if text =="刪除信箱":
            user.email = ""
            line_bot_api.reply_message(
                    event.reply_token,
                    [TextSendMessage('刪除成功'),menu])       
            user.act = 0
        else:
            user.email = text
            result = welcome(text)
            print(result)
            if result == 'suc':
                line_bot_api.reply_message(
                    event.reply_token,
                    [TextSendMessage('完成'),menu])       
                user.act = 0
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage('信箱無效，請重新輸入'))
                user.act = 3 
    else:   
        line_bot_api.reply_message(
                event.reply_token,
                menu)
        user.act = 0
    db.session.commit()

#%% check_database
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
            # num = html.xpath("//li[@class='status']/span/a[@class='blue']")[0].text
            num = html.xpath("//div[@class='book-detail']/dl/dd/span/a")[0].text
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
                        userid = User.query.filter_by(id=id).first().name
                        url_book = Book_list.query.filter_by(user_id=id,url=url).first().url_book
                        db.session.commit()
                    if mail != None:   
                        line_bot_api = LineBotApi('4q/qg3mb0gaInxBaRB882jaYgxkISoh7L4EN36n+U+ByoxLwWNziLX7468Fp+1zJ94f+OGC0X3q50q442xul1gSdT3DUYBd9kyVXqS00bJ2lUJHZ5slMS+tW7FmJG6tuoL94Wmn4m3TGm42MULHSwAdB04t89/1O/w1cDnyilFU=')
                        handler = WebhookHandler('0bb5f782197f3422a357205e2b03976e') 
                        line_bot_api.push_message(userid, TextSendMessage(text="你追蹤的漫畫 {} 已更新:{}\n{}".format(name,num,url_book)))
                        sentmail(name,num,url_book,mail)
                        
                        
        except:
            pass # doing nothing on exception
    
# check_database()
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_database, trigger="interval", hours=4)
scheduler.start()

if __name__ == "__main__":
    app.run()
    
