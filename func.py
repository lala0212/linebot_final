#%%
from linebot.models import TemplateSendMessage,\
ConfirmTemplate, MessageAction,ButtonsTemplate, MessageTemplateAction,CarouselTemplate,PostbackAction
from email.mime.text import MIMEText
import smtplib
import requests
from lxml import etree

from fake_useragent import UserAgent
import time
import random as rd
from urllib.parse import quote
#%%
#==============================================================
#menu
global menu
menu = TemplateSendMessage(
    alt_text='選單',
    template=ButtonsTemplate(
        title='Menu',
        text='選擇以下操作',
        actions=[
            MessageTemplateAction(
                label='新增漫畫',
                text='@新增漫畫',
            ),
            MessageTemplateAction(
                label='漫畫列表',
                text='@漫畫列表',
            ),
            MessageTemplateAction(
                label='編輯信箱',
                text='@編輯信箱',
            )
        ]
    )
)
#=============================================
#confirm
def confirm(title):
    return  TemplateSendMessage(
    alt_text="確認",
    template=ConfirmTemplate(
            text='是 '+title+" 嗎?",
            actions=[
                PostbackAction(
                    label='否/輸入網址',
                    data='enter_url'
                ),
                MessageAction(
                    label='是',
                    text='@是',                    
                )
            ]
        ) 
)
#=============================================
#delet

def delet_book(carousel_columns):

    return TemplateSendMessage(
    alt_text='漫畫列表',
    template=CarouselTemplate(
        columns=carousel_columns
    )
)

#==============================================================
#sentmail
def sentmail(name,num,url,mail):
    mime=MIMEText("你追蹤的漫畫 {} 已更新:{}\n立刻看-- {}".format(name,num,url),"plain", "utf-8") #撰寫內文內容以及指定格式為plain，語言為中文
    mime["Subject"]="{}更新".format(name) #撰寫郵件標題
    mime["From"]="漫畫更新" #撰寫你的暱稱或是信箱
    mime["To"]=mail #撰寫你要寄的人
    msg=mime.as_string() #將msg將text轉成str
    smtp=smtplib.SMTP("smtp.gmail.com", 587)  #googl的ping
    smtp.ehlo() #申請身分
    smtp.starttls() #加密文件，避免私密信息被截取
    smtp.login("magen00212@gmail.com ", "astj wmcn hgqg edgw") 
    from_addr="magen00212@gmail.com "
    to_addr=[mail]
    status=smtp.sendmail(from_addr, to_addr, msg)
    if status=={}:
        print("郵件傳送成功!")
    else:
        print("郵件傳送失敗!")
    smtp.quit()
#==============================================================
#welcome
def welcome(my_mail):
    mime=MIMEText("您的信箱已綁定成功","plain", "utf-8") #撰寫內文內容以及指定格式為plain，語言為中文
    mime["Subject"]="漫畫更新: 信箱綁定成功" #撰寫郵件標題
    mime["From"]="漫畫更新" #撰寫你的暱稱或是信箱
    mime["To"]=my_mail#撰寫你要寄的人
    msg=mime.as_string() #將msg將text轉成str
    smtp=smtplib.SMTP("smtp.gmail.com", 587)  #googl的ping
    smtp.ehlo() #申請身分
    smtp.starttls() #加密文件，避免私密信息被截取
    smtp.login("magen00212@gmail.com ", "astj wmcn hgqg edgw") 
    from_addr="magen00212@gmail.com "
    to_addr=[my_mail]
    try: 
        smtp.sendmail(from_addr, to_addr, msg)
        smtp.quit()
        return "suc"
        
    except: 
        smtp.quit()
        return "fail"
#==============================================================
#search_book
#%% Selenium 
# def search_book(name):
#     chrome_options = webdriver.ChromeOptions()
#     user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"
#     chrome_options.add_argument('--user-agent=%s' % user_agent)
#     chrome_options.add_argument('--headless') # 啟動無頭模式
#     chrome_options.add_argument('--disable-gpu')
#     chrome_options.page_load_strategy = 'eager' # 
#     driver = webdriver.Chrome(options=chrome_options) 
#     url = list(search(name+" 漫畫人 最新", tld="co.in",stop=1, pause=1))[0]
#     driver.get(url)
#     # soup = BeautifulSoup(driver.page_source, "html.parser")
#     # print(soup.prettify())
#     html = etree.HTML(driver.page_source)
#     try:
#         title = str(html.xpath("//div[@class='detail-main-info'][1]/p[1]/text()")[0])
#         num = html.xpath("//a[@class='detail-list-title-2']")[0].text
#         fig = str(html.xpath("//div[@class='detail-main-cover']//img/@src")[0])
#         return title,url,num,fig
#     except:
#         return "notwork",0,0,0

#%%xpath
#from bs4 import BeautifulSoup
# def search_book(name):
#     user_agent = UserAgent()
#     urls = list(search(name+" tw.manhuagui 最新", tld="co.in",stop=3, pause=1))
#     url = next((item for item in urls if item.startswith("https://www.manhuagui")), urls[0])
#     content_ = requests.get(url, headers={ 'user-agent': user_agent.random })
#     time.sleep(rd.random())
#     content = content_.content
#     # soup = BeautifulSoup(content, "html.parser")
#     # print(soup.prettify())
#     html = etree.HTML(content)
#     try:
#         title = html.xpath("//div[@class='book-title']/h1")[0].text
#         num = html.xpath("//li[@class='status']/span/a[@class='blue']")[0].text
#         fig = str(html.xpath("//div[@class='book-cover fl']/p/img/@src")[0])
#         return title,url,num,fig
#     except:
#         return "notwork",0,0,0
    
#%%xpath--ver2

#%%
def search_book_new(name):
    url = "https://tw.manhuagui.com/s/"+quote(name)+".html"
    user_agent = UserAgent()
    content_ = requests.get(url, headers={ 'user-agent': user_agent.random })
    time.sleep(rd.random())
    content = content_.content
    html = etree.HTML(content)
    try:
        title = html.xpath("//div[@class='book-detail']/dl/dt/a")[0].text
        num = html.xpath("//div[@class='book-detail']/dl/dd/span/a")[0].text
        fig = str(html.xpath("//div[@class='book-cover']/a/img/@src")[0])
        url_book = "https://tw.manhuagui.com"+html.xpath("//div[@class='book-detail']/dl/dt/a/@href")[0]
        return title,url,num,fig,url_book
    except:
        return "notwork",0,0,0,0

# def search_book_url(url):
#     user_agent = UserAgent()
#     content_ = requests.get(url, headers={ 'user-agent': user_agent.random })
#     time.sleep(rd.random())
#     content = content_.content
#     html = etree.HTML(content)
#     try:
#         title = html.xpath("//div[@class='book-detail']/dl/dt/a")[0].text
#         num = html.xpath("//div[@class='book-detail']/dl/dd/span/a")[0].text
#         fig = str(html.xpath("//div[@class='book-cover']/a/img/@src")[0])
#         url_book = "https://tw.manhuagui.com"+html.xpath("//div[@class='book-detail']/dl/dt/a/@href")[0]
#         return title,url,num,fig,url_book
#     except:
#         return "notwork",0,0,0,0
#%%
def search_book_name(url):
    user_agent = UserAgent()
    content_ = requests.get(url, headers={ 'user-agent': user_agent.random })
    time.sleep(rd.random())
    content = content_.content
    html = etree.HTML(content)
    try:
        title = html.xpath("//div[@class='book-title']/h1")[0].text
        return title
    except:
        return "notwork" 
