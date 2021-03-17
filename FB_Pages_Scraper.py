import requests as rq
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import sys 
import maskpass

#Facebook Class:
class FBPages():
    
    def login():
        """
        Login to Facebook
        
        """
        email=str(input("Email : "))
        password=maskpass.advpass()
        login={
            'email':email,
            'pass':password
            }
        return login
    
    
    POST_LOGIN_URL="https://m.facebook.com/login.php?refsrc=https%3A%2F%2Fm.facebook.com%2F&refid=8"

    payload=login()
    
    
    def parse_html(self,request_url,session):
        post=session.post(self.POST_LOGIN_URL,data=self.payload) 
        page =session.get(request_url)
        return page
    
    
    def Soup(self,page):
        """
        Return:
        ------
        soup : Beautiful Soup object 
        """
        soup=BeautifulSoup(page.content,"html.parser")
        return soup

    
    def url_Keyword(self,key):
        """
        search for the post key using mbasic.facebook.com
        
        """
        
        url=key.replace('www','mbasic')
      
        return url
    
    
    def get_page(self,request_url,session):
        
        page=session.get(request_url) 
        soup=self.Soup(page)
        return soup
    
    
    
    def more_page(self,soup):
        """
        returns : url of the next search page
        
        """
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
                i="https://www.facebook.com"+i.replace("?refid=46","about")
                URLsList.append(i)
        return URLsList
     
    
    def get_Nbr_Likes(self,soup,likes):
        
        """
        Extract Number of likes
        """   
        if soup.findAll('div',class_="ck")!=[]:
              l=soup.findAll('div',class_="ck")
              for i in l:
                 k=i.find('div',class_='cl ch ci')
                 h=i.find('div',class_='co ch ci')
                 if k!=None:
                     l=k.find('span',class_='cm cn')
                     if l!=None:
                         likes.append(l.getText().replace("likes",""))
                     else:
                         likes.append('0')
                 elif h!=None:
                     l=h.find('span',class_='cp cq')
                     if l!=None:
                         likes.append(l.getText().replace("likes",""))
                     else:
                         likes.append('0')
                 else: 
                     if i.get_text()=='' or i.get_text()==None:
                         likes.append('0')
        return likes
    
    
    
    def get_name(self,soup,names):
        """
        Extract page names

        """
        n=soup.findAll('div',class_="ce")
        name=[i.getText() for i in n]
        
        for i in name:
            names.append(i)
        return names
    
     
    def search_Extraction(self,URLsList,U,Names,likes,soup,session):
        """
        Extraction of Names, URLs list ....

        """
        while 1:
            time.sleep(1)
            urls=self.pages_urls(soup)
            
            URLsList=self.urls_list(urls,URLsList)
            U=self.fb_urls(urls,U)
            time.sleep(0.5)
            likes=self.get_Nbr_Likes(soup,likes)
            
            Names=self.get_name(soup,Names)
            
            more=self.more_page(soup)
            if more !=None:
                soup=self.get_page(more,session)
                
            else:
                break
        return URLsList,U,likes[:-1],Names
    
      

    def About(self,soup):
        """
        Extract about page 
        Return:
        ------
        Text
        """
        a=soup.find_all('a')
        Text=' '
        if a!=[]:      
            for i in a:
                Text+=i.get_text()+' '
        return Text
    
            
    def get_Email(self,Text,Email):
        """
        Extract email from Text

        """
        regex='\S+@\S+'
        if re.findall(regex,Text)!=[]:
            email=re.findall(regex,Text)[0]
        else :
            email='None'
        Email.append(email)
        return Email
    
    
    def get_Website(self,Text,Website):
        """
         Extract website from Text
        """
    
        regex='https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        if re.findall(regex,Text)!=[]:
            website=re.findall(regex,Text)[0]
        else :
            website='None'
            
        Website.append(website)
        return Website
    
    
    def get_Phone(self,soup,Phone):
        """
         Extract Phone from Text
         
        """    
        Text=soup.get_text()
        regex=re.compile(r'\+\d*[-\.\s]\d*[-\.\s]?\d*[-\.\s]?\d*[-\.\s]?\d*')
        if re.findall(regex,Text)!=[]:
            L=re.findall(regex,Text)
            if len(L)==1:    
                number =re.findall(regex,Text)[0]
            elif len(L)!=1:
                number =re.findall(regex,Text)[1]
            Phone.append(number)
        else:
            Phone.append('None')
        return Phone        
        

    
    def LoginErr(self,page):
        
        if page.status_code != 200:
            return sys.exit("\n 1-The email or password that you've entered is incorrect OR This keyword cannot find any pages :(\n2-Maybe Facebook is asking to conform your identity(cheek you account and change your IP adress).")
       
        else :
            return "--------------------------------\n|         Welcome to           |\n|    Facebook Scraping Tool    |\n--------------------------------"



    
###################################################
# main program :       
#################################################### 


FB=FBPages()  # create a new object of FBPage class

#Session:
session=rq.Session()
adapter = rq.adapters.HTTPAdapter(max_retries=20)
session.mount('https://', adapter)
session.mount('http://', adapter)

#OUTPUTS:
Phone,Email,Website,U,URLsList,Names,likes=([] for i in range(7))

#User intput:
country= str(input("Choose a country (vietnam | thailand | singapore) :"))
file_name=str(input("Enter the name you want for saving the output file:"))    
key=str(input("Enter the keyword URL :")) 


Request_URL=FB.url_Keyword(key)
page=FB.parse_html(Request_URL,session)

#Test if the page is successfully loaded :
a=FB.LoginErr(page) 
print(a)


#Beautiful Soup Object:
soup=FB.Soup(page)   

print("\nPLEASE WAIT... THIS PROCESS WILL TAKE SOME TIME")


#Start the Extraction:



#first part 

URLsList,U,likes,Names=FB.search_Extraction(URLsList,U,Names,likes,soup,session)

print("\n\nNumber of pages availible for this keyword : ",len(URLsList))


Nbr_pages=int(input("How many pages do you want to scrape: "))

print('------------------------------------------------------------')
print('                  WEB SCRAPING PROCESS')
print('------------------------------------------------------------')

#second part:

session=rq.Session()
adapter = rq.adapters.HTTPAdapter(max_retries=20)
session.mount('https://', adapter)
session.mount('http://', adapter)

if Nbr_pages >len(URLsList):
    Nbr_pages=len(URLsList)

for i in range(Nbr_pages):
    
    url=URLsList[i]
    Upage=FB.get_page(url,session) 
    Phone=FB.get_Phone(Upage,Phone)
    Text=FB.About(Upage)
    Email=FB.get_Email(Text,Email)
    Website=FB.get_Website(Text,Website)
    
    time.sleep(1)
    
    print('Page{} successfully scraped :) ...'.format(i+1))
    print("----------------------------------")
print("-------------------------------------\n")


#Saving the data

print("Saving the data ....")

#DataFrame:

if len(likes)<len(Names):
    diff=len(Names)-len(likes)
    for i in range(diff):
        likes.append('_')

df=pd.DataFrame({"Name":Names[:Nbr_pages],"Likes":likes[:Nbr_pages],
                  "Phone Number":Phone[:Nbr_pages],"Email":Email[:Nbr_pages],
                  "Page URL":U[:Nbr_pages],"Website":Website[:Nbr_pages]})

file_name=file_name+'.xlsx'

#Data Filtring 
if country=="vietnam":
    for i in df["Phone Number"]:
        if "+84" not in i and i !="None":
            df.drop(df[df["Phone Number"]==i].index,inplace=True)
if country=="thailand":
     for i in df["Phone Number"]:
        if "+66"  not in str(i) and i !="None":
            df.drop(df[df["Phone Number"]==i].index,inplace=True)
            
if country=="singapore":
     for i in df["Phone Number"]:
        if "+65"  not in str(i) and i !="None":
            df.drop(df[df["Phone Number"]==i].index,inplace=True)
            
            

w=pd.ExcelWriter(file_name, engine='xlsxwriter', options={'strings_to_formulas':False})
df.to_excel(w, sheet_name='Sheet1', index=False)
w.save()
#w.close()


print("data successfully saved ")
time.sleep(1)

print("--------------------------------")       
print("|     This process is done     |")
print("|     See you next time :)     |")
print("--------------------------------")

############################################
#End 
