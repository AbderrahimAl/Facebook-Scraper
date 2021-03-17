# Importing libraries :
import requests as rq
from bs4 import BeautifulSoup
import re
import time
import sys
import pandas as pd
import maskpass
from datetime import datetime
import json

# FacebookPost class

class FacebookPost():
    
    POST_LOGIN_URL="https://m.facebook.com/login.php?refsrc=https%3A%2F%2Fm.facebook.com%2F&refid=8"
   
    
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
    
    payload=login() 
    
        
    def parse_html(self,request_url,session):
     
        post=session.post(self.POST_LOGIN_URL,data=self.payload) 
        page =session.get(request_url)
        return page


    def Soup(self,page):
        """
        Returns
        -------
        soup : Beautiful Soup object 
        """
  
        soup=BeautifulSoup(page.content,"html.parser")
        return soup
    
    
    def get_page(self,request_url,session):

        page=session.get(request_url) 
        soup=self.Soup(page)
        return soup
    
    
    
    def url_Keyword(self,key):
        """
        search for the post key using mbasic.facebook.com
        
        """
        url=key.replace('www','mbasic')
        #url=key.replace("%20","+")
        
        return url
    
    
    
    def clean_url(self,Urls_list,URLS):
        """
        Clean post URL
        
        """
        for i in range(len(Urls_list)):
            
            #www.facebook.com
            f_url=Urls_list[i].replace('https://m.facebook.com','')
            f_url=f_url.replace("&__tn__=%2As",'')
            f_url=f_url.replace("&__tn__=%2AW",'')
            f_url=f_url.replace("&__tn__=EH",'')
            f_url=f_url.replace("?__tn__=%2AW",'')            
            f_url=f_url.replace("?#footer_action_list",'')
            f_url=f_url.replace("#footer_action_list",'')
            URLS.append('https://www.facebook.com'+ f_url)
            
            #mbasic urls:
            Urls_list[i]=Urls_list[i].replace('https://m.facebook.com','')
            Urls_list[i]='https://mbasic.facebook.com'+ Urls_list[i]
        
        return Urls_list,URLS
    
   
    
    def get_images(self,soup,Images):
        """
        Extract and Clean Images URLs

        """
        
        img=soup.find_all('a',href=re.compile("/photo.php?fbid="))
        img1=soup.find_all('a',href=re.compile("/photo"))
        m=' '
        if img !=[]:
            img_href='https://www.facebook.com'+img[0]['href']
            m+=img_href+'\n'
            
        elif img1 !=[]:
            img_href='https://www.facebook.com'+img1[0]['href']
            m+=img_href+'\n'
            
        else:
            img=soup.find_all('a',href=re.compile("pcb"))
            if img !=[]:
                for i in img:
                    img_href='https://www.facebook.com'+i['href']
                    m+=img_href+'\n'    
    
            
            else:
                img=soup.find_all('a',href=re.compile("photos"))
                if img !=[]:
                    for i in img:
                        img_href='https://www.facebook.com'+i['href']
                        m+=img_href+'\n'
                                                 
        Images.append(m)
        
        return Images
      
    
    
    def posts_info(self,soup,Urls_list,Likes,URLS,Date):
        """
        This function returns the posts urls list  and also the posts descriptions
        
        """
        
        while 1:
            time.sleep(0.2)
            post=soup.find_all('div',class_="by")        
            for i in post:
                l=i.find('span',id=re.compile("like_"))
                Hr=i.find('a',href=re.compile("#footer_action_list"))
                if Hr==None:
                    Hr=i.find('a',href=re.compile("/story.php"))
                   
                        
                d=i.find('abbr')
                
                if Hr!=None:
                    Href=Hr['href']
                    Href=Href.replace('https://m.facebook.com','')
                    Href=Href.replace('https://mbasic.facebook.com','')                    
                    Urls_list.append(Href)
                    if d !=None:
                        date=d.get_text()
                        Date.append(date)
                    else:
                        Date.append('None')
   
                    if l!=None:    
                        if l.get_text()!=None:
                            likes=l.get_text()
                            if likes=="Like · React":
                                likes='0'
                            else:
                                likes=likes.replace('· Like · React','')                                
                                likes=likes.replace("· Like",'')
                                likes=likes.replace("· Love",'')
                                likes=likes.replace("· Haha",'')
                                likes=likes.replace("· Care",'')
                                likes=likes.replace("· Wow",'')
                                likes=likes.replace("· Angry",'')
                            Likes.append(likes)
                        else:
                           Likes.append("0")
                    else:
                        Likes.append("0")
           
                        
            more=self.more_page(soup)
            if more !=None:
                soup=self.get_page(more,session)
                
            else:
                break
                        
        Urls_list,URLS=self.clean_url(Urls_list,URLS)            
                
        return Urls_list,URLS,Likes,Date

    
    
    def get_profile(self,soup,Name,Profile_url):
        """
        Extract Profiles (Name and URLs)
        """
        h3=soup.find("h3")
        
        if h3 !=None:
            if h3.find("a")!=None:           
                name=h3.a.get_text()
                if h3.a.has_attr('href') :
                    h3_a_tag=h3.a['href']
                    h3_a_tag=h3_a_tag.replace("&__tn__=C-R",'')
                                        
                    profile_url='https://www.facebook.com'+h3_a_tag
                else :
                    profile_url="None"
            
        else :
            h31=soup.find('a',class_="actor-link")
            if h31!=None:
                name=h31.get_text()
                if h31.has_attr('href'):
                    profile_url='https://www.facebook.com'+h31['href']
                else:    
                    profile_url="None"
            else:
 
                name="None"
                profile_url="None"
       
            
        Name.append(name)
        Profile_url.append(profile_url)
        
        return Name,Profile_url
    
    
    
    def get_description(self,soup,descreption):
        """
        Extract Post description
        
        """
     
        p=soup.findAll("p")
            
        if p!=[]:
            s=' ' 
            for i in p:
                s+=i.get_text()+' '
            description.append(s)     
        else :
            s=' '
            h11=soup.find('div',{'data-ft':'{"tn":"*s"}'})
            if h11!=None:
                s+=h11.get_text()
                description.append(s)
                
                
            else:
                h12=soup.find('div',{'data-ft':'{"tn":",g"}'})
                if h12!=None:
                    s+=h12.get_text().split(" · in Timeline")[0].replace('· Public','')
                    description.append(s)
                
                else:
                    
                    description.append("None")
                
        return description  
    
    
         
    
    def more_page(self,soup):
        """
        returns : url of the next search page
        
        """
        if soup.find('div',id='see_more_pager')!=None:
            more=soup.find('div',id='see_more_pager').find('a',href=True)['href']
        else:
            more=None
        return more
       
        
    
    
    def get_reactions(self,Post_soup,session):
        """
        get_reactions returns a list of the psot reactions

        """
        React=['Like', 'Angry', 'Love', 'Haha', 'Sad','Care', 'Wow']        
        Nbr_Reactions=['0' for i in range(7)]
        Reactions_url_tag=Post_soup.find('a',href=re.compile('/ufi/reaction/profile/'))
        
        
        if Reactions_url_tag != None:
            
            Reactions_url="https://mbasic.facebook.com/"+Reactions_url_tag['href']
            
            #Beautiful Soup Object:
            Reaction_soup=FP.get_page(Reactions_url,session)
            
            #Extract the class of Reactions:
            React_a=Reaction_soup.findAll('a',class_='u')
            
            for i in React_a:
                React_img=i.find('img')
                if React_img !=None:
                    if React_img.has_attr('alt'):
                        R_alt=React_img['alt']
                                        
                        for j in range(len(React)):
                            if R_alt==React[j]:
                               
                                Nbr_Reactions[j]=i.get_text()
                                
                                                                                            
        return  Nbr_Reactions   
    
        
    
    def more_comments(self,soup):
        """
        Returns
        -------
        more_comments 
        """
        if soup.find('div',id=re.compile("see_next_"))!=None:
            more_comments=soup.find('div',id=re.compile("see_next_")).find('a',href=True)['href'] 
            more_comments=more_comments.replace('https://m.facebook.com','')
        else:
            more_comments=None
        return more_comments
    
            
    def get_comments(self,soup,d_comments,d_profiles,comments_limit):
        
        nbr=0
        while nbr<=comments_limit: #the maximum value of comments we want to scrap
        #Extraction of who comments in this post :
            
            CommentsTag=soup.find_all('h3')
            profile_comments,Name=[],[]
            
            if CommentsTag!=[]:
                for i in CommentsTag:
                    a_tag=i.find('a')
                    if a_tag !=None:
                        if a_tag.has_attr('href'):
                            a_href=a_tag['href']
                            if ("refid=52&__tn__=R" in a_href) or('refid=18&__tn__=R' in a_href)or("?rc=p&__tn__=R" in a_href) :
                                a_href=a_href.replace("&refid=52&__tn__=R",'')
                                a_href=a_href.replace("refid=52&__tn__=R",'')
                                a_href=a_href.replace("&refid=18&__tn__=R",'')
                                a_href=a_href.replace("?refid=18&__tn__=R",'')                                                                
                                a_href_url='https://www.facebook.com'+a_href
                                profile_comments.append(a_href_url)
                                Name.append(a_tag.get_text())    
                
            #Extraction of comments :
                                
            div=soup.find_all('div')
            div_text=[i.get_text() for i in div]
            
            aa,aa1=[],[]
            for i in div_text:
                if i not in aa:
                    aa.append(i)
            for j in aa:
                if 'Like · React · Reply · More ·' in j and 'View more comments…' not in j: 
                    aa1.append(j)
                    
            ll=[' ' for i in range(len(Name))]
            if Name !=[]:
                for i in range(len(Name)):
                    for j in aa1:
                        if Name[i] in j:
                            com=j.split(Name[i])[1]
                            ll[i]=com.split("Like")[0].replace('"','')
                            if 'Edited ·' in ll[i]:
                                ll[i]=com.split("Edited ·")[0]
               
                    for i in range(len(Name)):
                        
                        d_comments[Name[i]]=ll[i]            
                        d_profiles[Name[i]]=profile_comments[i]
            nbr=len(d_comments.keys())
            
            more=self.more_comments(soup)
            if more !=None:
                more='https://mbasic.facebook.com'+ more
                soup=self.get_page(more,session)
                
            else:
                break     
            
        
        d_comments=json.dumps(d_comments, ensure_ascii=False).encode('utf8').decode()
        d_profiles=json.dumps(d_profiles, ensure_ascii=False).encode('utf8').decode()
        return d_comments,d_profiles
        
    
    
        
    def LoginErr(self,page):
        if page.status_code != 200:
            return sys.exit("\n 1-The email or password that you've entered is incorrect OR This keyword cannot find any post :(\n2-Maybe Facebook is asking to conform your identity(cheek you account and change your IP adress).")
       
        else :
            return "--------------------------------\n|         Welcome to           |\n|    Facebook Scraping Tool    |\n--------------------------------"
    
    
    
    
###################################################
# main program :       
#################################################### 
            
FP=FacebookPost() # create a new object of FacebookPost class
   
session=rq.Session()
adapter = rq.adapters.HTTPAdapter(max_retries=20)
session.mount('https://', adapter)
session.mount('http://', adapter)

#OUTPUTS
Urls_list,description,ALL_Reactions,Name,Profile_url,URLS,Images,Date,Scraping_Date=([] for i in range(9))
Like,Angry,Love,Haha,Sad,Care,Wow=([] for i in range(7))#Reactions
Comments,Who_Comment=[],[] #Comments

#User intput:
file_name=str(input("Enter the name you want for the new output file (Maybe the keyword):"))    
key=str(input("Enter the keyword URL :")) 


NB_posts=int(input("How many posts do you want to scrape :"))

comments_limit=int(input("How many comments do you want to scrape :"))
#get the search page :  
Request_URL=FP.url_Keyword(key)
page=FP.parse_html(Request_URL,session)    
    
#Test if the page is successfully loaded :
a=FP.LoginErr(page) 
print(a)
   

#Beautiful Soup Object:    
soup=FP.Soup(page)  
   
print("\nPLEASE WAIT... THIS PROCESS WILL TAKE SOME TIME") 


#Start the Extraction:

#first part 

Urls_list,URLS,ALL_Reactions,Date=FP.posts_info(soup,Urls_list,ALL_Reactions,URLS,Date)
    
print("\n\nNumber of posts availible for this keyword : ",len(Urls_list))   

print('------------------------------------------------------------')
print('                  WEB SCRAPING PROCESS')
print('------------------------------------------------------------')

#second part 
if NB_posts>len(Urls_list):
    NB_posts=len(Urls_list)
    
    
for i in range(NB_posts):
    
    url=Urls_list[i]
    Post_soup=FP.get_page(url,session)
    time.sleep(0.5)
    
    Name,Profile_url=FP.get_profile(Post_soup,Name,Profile_url)    
    description=FP.get_description(Post_soup,description)
    Images=FP.get_images(Post_soup,Images)
    now = datetime.now()
    dt= now.strftime("%d/%m/%Y %H:%M:%S")
    Scraping_Date.append(dt)
    time.sleep(0.5)
    
    like,angry,love,haha,sad,care,wow=FP.get_reactions(Post_soup,session)
    Like.append(like)
    Angry.append(angry)
    Love.append(love)
    Haha.append(haha)
    Sad.append(sad)
    Care.append(care)
    Wow.append(wow)
    
    d_comments,d_profiles={},{}
    C,W=FP.get_comments(Post_soup,d_comments,d_profiles,comments_limit)  
    Who_Comment.append(W)
    Comments.append(C)
    
    print('Post{} successfully scraped :) ...'.format(i+1))
    print("----------------------------------")

    
print("-------------------------------------\n")

#Saving the data

df1=pd.DataFrame({"Name":Name[:NB_posts],"Post Description":description[:NB_posts],"ALL Reactions":ALL_Reactions[:NB_posts],
                 'Like':Like[:NB_posts], 'Angry':Angry[:NB_posts], 'Love':Love[:NB_posts], 'Haha':Haha[:NB_posts], 'Sad':Sad[:NB_posts],'Care':Care[:NB_posts], 
                 'Wow':Wow[:NB_posts],"Profile/Page url":Profile_url[:NB_posts],"Post url":URLS[:NB_posts],
                 "Images Urls":Images[:NB_posts],"Date":Date[:NB_posts],"Scraping date":Scraping_Date[:NB_posts],
                 "Comments":Comments[:NB_posts],"Who Comment id":Who_Comment[:NB_posts]}) # Data Frame


file_name=file_name+'.xlsx'
w=pd.ExcelWriter(file_name, engine='xlsxwriter', options={'strings_to_formulas':False})
df1.to_excel(w, sheet_name='Sheet1', index=False)
w.save()
w.close()


print("data successfully saved ")
time.sleep(1)
print("--------------------------------")       
print("|     This process is done     |")
print("|     See you next time :)     |")
print("--------------------------------")

############################################
#End
