#Webscraping Tool


# Importing libraries :
from Login import login
import requests as rq
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import sys 


#FacebookInfo class

class FacebookInfo():
    
    
    POST_LOGIN_URL="https://m.facebook.com/login.php?refsrc=https%3A%2F%2Fm.facebook.com%2F&refid=8"
   
    payload=login()
      
   
    
    def parse_html(self,request_url,session):
        
        post=session.post(self.POST_LOGIN_URL,data=self.payload) 
        page =session.get(request_url)
        return page
    
    
    def Soup(self,page):
        soup=BeautifulSoup(page.content,"html.parser")
        return soup
    
    def get_country(self,country):
        country=country.lower()
        country=country.replace(' ','')
        return country
    """     
    def url_Keyword(self,key):
        key=key.lower()
        url=key.replace('www.facebook.com','mbasic.facebook.com')
        return url
    """
    def url_Keyword(self,key,country):
        key=key.lower()
        key=key.replace(' ','+')
        url="https://mbasic.facebook.com/search/pages/?q="+str(key)+"+"+str(country)
        #url=url[:-(len(country)+1)]+str(key)+url[-len(country)+1:]
        return url
    
    def get_page(self,request_url,session):
        page=session.get(request_url) 
        soup=self.Soup(page)
        return soup
    
    
    
    def more_page(self,soup):
        if soup.find('div',id='see_more_pager')!=None:
            more=soup.find('div',id='see_more_pager').find('a',href=True)['href']
        else:
            more=None
        return more
    
    
    def pages_urls(self,soup):
        if soup.find('td',class_="m by")!=None:
            class_by=soup.findAll('td',class_="m by")
            urls=[i.find('a', href=True)['href'] for i in class_by]
        else:
            urls=None
        return urls
            
    def fb_urls(self,urls,U):
        if urls!=None:
            for i in urls:
                i="https://www.facebook.com/"+i
                U.append(i)
        return U
    
    
    def urls_list(self,urls,URLsList):
        if urls!=None:
            for i in urls:
                i="https://mbasic.facebook.com/"+i.replace("?refid=46","about")
                URLsList.append(i)
        return URLsList
    
    
    
    
    def get_Nbr_Likes(self,soup,likes):
        
       if soup.findAll('div',class_="ck")!=[]:
             l=soup.findAll('div',class_="ck")
             for i in l:
                 k=i.find('span',class_='cm cn')
                 if k!=None:
                     likes.append(k.getText().replace("likes",""))
                 else :
                     likes.append('None')
       return likes
    
    
    def get_name(self,soup,names):
       
        n=soup.findAll('div',class_="ce")
        name=[i.getText() for i in n]
        
        for i in name:
            names.append(i)
        return names
    
     
    def search_Extraction(self,URLsList,U,Names,likes,soup,session):
        
        while 1:
            time.sleep(1)
            urls=self.pages_urls(soup)
            
            URLsList=self.urls_list(urls,URLsList)
            U=self.fb_urls(urls,U)
            
            likes=self.get_Nbr_Likes(soup,likes) 
            Names=self.get_name(soup,Names)

            more=self.more_page(soup)
            if more !=None:
                soup=self.get_page(more,session)
                
            else:
                break
        return URLsList,U,likes[:-1],Names
    
      
    def get_Email(self,about,Email):
        if re.findall('\S+@\S+', about)!=[]:
            email=re.findall('\S+@\S+', about)[0]
            Email.append(email)
        else:
            Email.append('None')
        return Email
    

    def get_Phone(self,about,Phone):
        regex=re.compile(r'\+\d{2}[-\.\s]\d*[-\.\s]?\d*[-\.\s]?\d*[-\.\s]?\d*')
        if re.findall(regex, about)!=[]:
            number =re.findall(regex, about)[0]
            Phone.append(number)
        else:
            Phone.append('None')
        return Phone
    
    
    def get_websit(self,about,websit):
        regex='https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        if re.findall(regex,about)!=[]:
            site=re.findall(regex,about)[0]
            if "http" in site:
                site="http"+site.replace('http','')
            elif "https" in site:    
                site="https"+site.replace('https','')
            websit.append(site)
        else:
            websit.append('None')
        return websit
    
  
    
    def About(self,soup):
        about=''
        info1=soup.find_all('div', id="unit_id_240488679671394")
        info2=soup.find_all('div', id="unit_id_1111597808900010")
        info3=soup.find_all('div', id="unit_id_138884119868710")
        for a in info1:
            about=about+' '+ a.getText()
        for a in info2:
            if a.find('a')!=None:
                about=about+' '+ a.find('a').getText()    
        for a in info3:
            about=about+' '+ a.getText()
        return about
    
    def LoginErr(self,page,URLsList):
        if page.status_code != 200:
            return sys.exit("\n 1-The email or password that you've entered is incorrect OR This keyword cannot find any pages :(\n2-Maybe Facebook is asking to conform your identity(cheek you account and change your IP adress).")
       
        else :
            return "--------------------------------\n|         Welcome to           |\n|    Facebook Scraping Tool    |\n--------------------------------"


    
#Main Program :


INFO=FacebookInfo()

Phone=[]
Email=[]
Websit=[]
U=[]
URLsList=[]  
Names=[] 
likes=[]

session=rq.Session()
country= str(input("Choose a country (vietnam | thailand | singapore) :"))
country=country.lower()
key=str(input("Enter a keyword :"))
Request_URL=INFO.url_Keyword(key,country)
page=INFO.parse_html(Request_URL,session)
soup=INFO.Soup(page)   
URLsList,U,likes,Names=INFO.search_Extraction(URLsList,U,Names,likes,soup,session)
print("\n\nNumber of pages availible for this keyword : ",len(URLsList))

a=INFO.LoginErr(page,URLsList) 
print(a)      


print('------------------------------------------------------------')
print('              Process of web scraping')
print('NB:This Process will take some time ')
print('------------------------------------------------------------')
s=rq.Session()
for i in range(len(URLsList)):
    url=URLsList[i]
    Upage=INFO.get_page(url,s)  
    about=INFO.About(Upage)
    Phone=INFO.get_Phone(about,Phone)
    Email=INFO.get_Email(about,Email)
    Websit=INFO.get_websit(about,Websit)
    time.sleep(1)
    
    print('Page{} successfully scraped :) ...'.format(i+1))
    print("----------------------------------")
print("-------------------------------------\n")

print("Saving the data ....")

df1=pd.DataFrame({"Name":Names,"Likes":likes,"Phone Number":Phone,"Email":Email,"FB url":U,"Websit":Websit})

df2=pd.read_excel("../Facebook Scraping Tool/data.xlsx")
data=pd.concat([df1,df2], ignore_index=True)

if 'Unnamed: 0' in data.columns[0]:
    data=data.drop(['Unnamed: 0'],axis=1)


if country=="vietnam":
    for i in data["Phone Number"]:
        if "+84" not in i and i !="None":
            data.drop(data[data["Phone Number"]==i].index,inplace=True)
if country=="thailand":
     for i in data["Phone Number"]:
        if "+66"  not in str(i) and i !="None":
            data.drop(data[data["Phone Number"]==i].index,inplace=True)
            
if country=="singapore":
     for i in data["Phone Number"]:
        if "+65"  not in str(i) and i !="None":
            data.drop(data[data["Phone Number"]==i].index,inplace=True)

data.to_excel("data.xlsx",index=False)

print("data successfully saved ")
time.sleep(1)

print("--------------------------------")       
print("|     This process is done     |")
print("|     See you next time :)     |")
print("--------------------------------")















               
        
        
            
            
            
            
            
   
            
            
            
            
            