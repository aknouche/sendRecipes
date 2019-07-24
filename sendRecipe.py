import random
from bs4 import BeautifulSoup
import requests
import bs4
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from twilio.rest import Client
import datetime



urlList = ['https://zeinaskitchen.se/category/husmanskost/page/13/',
           'https://zeinaskitchen.se/category/husmanskost/page/12/',
           'https://zeinaskitchen.se/category/husmanskost/page/11/',
           'https://zeinaskitchen.se/category/husmanskost/page/10/',
           'https://zeinaskitchen.se/category/husmanskost/page/9/',
           'https://zeinaskitchen.se/category/husmanskost/page/8/',
           'https://zeinaskitchen.se/category/husmanskost/page/7/',
           'https://zeinaskitchen.se/category/husmanskost/page/6/',
           'https://zeinaskitchen.se/category/husmanskost/page/5/',
           'https://zeinaskitchen.se/category/husmanskost/page/4/',
           'https://zeinaskitchen.se/category/husmanskost/page/3/',
           'https://zeinaskitchen.se/category/husmanskost/page/2/',
           'https://zeinaskitchen.se/category/husmanskost/page/1/']


url = random.choice(urlList)

# Getting the url, creating a Response object.
response = requests.get(url)

# Extracting the source code of the page.
data = response.text

# Passing the source code to BeautifulSoup to create a BeautifulSoup object for it.
soup = BeautifulSoup(data, 'lxml')

# Extracting all the <h2> tags into a list.
h2_tags = soup.find_all('h2')

link_message = 'Recipes for the next week from Zeinas Kitchen:\n'
for tag in h2_tags[1:8]:
    link_message += (tag.a.text.strip())
    link_message += " "
    link_message += (tag.a['href'])
    link_message += " \n "

# Send email with all recipes their names and links
def sendEmail():
    msg = MIMEMultipart()
    msg['From'] = 'lamine.aknouche@malmo.se'
    msg['To'] = 'ml.aknouche@gmail.com'
    msg['Subject'] = 'Recipes'

    msg.attach(MIMEText(link_message))

    mailServer = smtplib.SMTP('smtp-mail.outlook.com', 587)
    # identify ourselves to smtp gmail client
    mailServer.ehlo()
    # secure our email with tls encryption
    mailServer.starttls()
    # re-identify ourselves as an encrypted connection
    mailServer.ehlo()
    password = input('Please enter your email password: ')  # Ask for password
    mailServer.login('lamine.aknouche@malmo.se', password)  # Login to mail server

    mailServer.sendmail('lamine.aknouche@malmo.se', 'ml.aknouche@gmail.com', msg.as_string())

    mailServer.quit()

def sendSmsMessage():
    recipe_list = []  # Create empty recipe list

    # Get all href recipe links and store in 'rec' variable
    href_rec = soup.select('h2 a[href]')

    # Add href links to list
    for item in href_rec:
        recipe_list.append(item['href'])

    res = requests.get(recipe_list[datetime.datetime.today().weekday()])  # Get today's recipe link (1-7)
    res.raise_for_status()
    noStarchSoup = bs4.BeautifulSoup(res.text, 'lxml')  # Create soup object
    p_ingredients = noStarchSoup.find_all('p')

    recipe_ingredients = "Remember the ingredients for today: "  # Empty list for ingredients for recipe
    for aTag in p_ingredients[0:2]:  # We only want the ingredients from the web page nothing else
        recipe_ingredients += str(aTag)  # Add the ingredients

    print(recipe_ingredients)
    # Send a text to remind of today's ingredients
    try:
        accountSID = 'AC620e24ce9259f3712bd893cf0391c8bf'
        authToken = '3fc430940fbc26b0bd9ec4e1428cc397'
        twilioCli = Client(accountSID, authToken)
        myTwilioNumber = '+46790645826'
        myCellPhone = '+46722515715'
        twilioCli.messages.create(body=recipe_ingredients, from_=myTwilioNumber, to=myCellPhone)
    except:
        print("SMS was not sent")


#  Send email on sundays only
if datetime.datetime.today().weekday() == 6:
    sendEmail()

#  Send sms att 9 o'clock every morning
if datetime.datetime.now().hour == 9 and datetime.datetime.now().minute == 0 and datetime.datetime.now().second == 0:
    sendSmsMessage()


