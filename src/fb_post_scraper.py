from  selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import json
import pandas as pd
from config import username, password, chrome_driver_path, number_posts_max, number_comments_max, output_file_name

class Post_Scraper:
    """
    Post_Scraper class allows to scrape Facebook Posts based on search queries.
    """
    LOGIN_URL = "https://www.facebook.com"
    REACTIONS_NAMES = ['Like', 'Angry', 'Love', 'Haha', 'Sad','Care', 'Wow']

    def __init__(self, driver_path, posts_url) -> None:
        self.driver = webdriver.Chrome(driver_path)
        self.posts_url = posts_url.replace("www", "mbasic")


    def login(self, username, password) -> None:
        """
        Login to a Facebook Account.

        Args:
            username (`str`)
                Facebook account username/email
            passward (`str`)
                Facebook account password    
        """
        self.driver.get(self.LOGIN_URL)
        time.sleep(2)
        email_ = self.driver.find_element_by_name("email")
        pass_ = self.driver.find_element_by_name("pass")
        email_.send_keys(username)
        time.sleep(1)
        pass_.send_keys(password)
        time.sleep(2)
        email_.submit()
        time.sleep(10)
       

    def get_content(self, url=None):
        """
        parsing html from a web page.

        Args:
            url (`str`)
                web page url.
        Return:
            A beautiful soup object.
        """
        if url is None:
            url = self.posts_url
        self.driver.get(url)
        page_content = self.driver.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        return soup

    def clean_url(self, posts_urls_list):
        """
        Convert posts urls to mbasic facebook format.

        Args:
            posts_urls_list (`list[str]`)
        Return:
            A list of urls after applying the cleaning formula.
        """
        clean_posts_urls_list = ["https://mbasic.facebook.com" + url.replace("https://m.facebook.com", '') for url in posts_urls_list]
        return clean_posts_urls_list

    def get_more_posts(self, soup):
        """
        get more posts by going to the next page if exist.
        
        Args:
            soup (`bs4.BeautifulSoup object`):
                post html content.
        Return:
            A url (`str`) to get the next page.
        """
        if soup.find("div", id="see_more_pager") is not None:
            more_posts_url = soup.find("div", id="see_more_pager").find('a',href=True)['href']
        else:
            more_posts_url = None
        return more_posts_url

    def get_posts_info(self, soup, posts_urls_list=None, post_date_list=None, likes_list=None):
        """
        Extract the full stoy url, the post reactions and the publishing date. 
        """
        if posts_urls_list is None:
            posts_urls_list = []
        if post_date_list is None:
            post_date_list = []
        if likes_list is None:
            likes_list = []

        while True:
            time.sleep(2)
            posts = soup.find_all("div", class_="by")
            for post in posts:
                like_span = post.find("span", id=re.compile("like_"))
                full_story_tag = post.find('a',href=re.compile("#footer_action_list"))
                if full_story_tag is None:
                    full_story_tag = post.find('a',href=re.compile("/story.php"))
                post_date_abbr = post.find("abbr")
                if full_story_tag:
                    full_story_href = full_story_tag["href"].replace("https://m.facebook.com", '').replace("https://mbasic.facebook.com", '')
                    posts_urls_list.append(full_story_href)
                    if post_date_abbr:
                        post_date = post_date_abbr.get_text()
                        post_date_list.append(post_date)
                    else:
                        post_date_list.append('None')  
                    if like_span:
                        if like_span.get_text():
                            likes = like_span.get_text()
                            if likes == "Like · React":
                                likes = '0'
                            else:
                                replacement = ["· Like · React", "· Like", "· Love", "· Haha", "· Care", "· Wow", "· Angry"]
                                [likes := likes.replace(item, '') for item in replacement]
                            likes_list.append(likes)
                        else:
                            likes_list.append('0')
                    else:
                        likes_list.append('0')
            more_posts_url = self.get_more_posts(soup)
            if more_posts_url:
                soup = self.get_content(more_posts_url)
            else:
                break
        posts_urls_list = self.clean_url(posts_urls_list)

        return posts_urls_list, likes_list, post_date_list


    def get_post_images(self, soup):
        """
        Extract the full stoy (post) images.
        Args:
            soup (`bs4.BeautifulSoup object`)
        Return:
            A string of multiple image urls ("url1 \n url2 \n").
        """

        img_a_tag_1 = soup.find_all('a', href=re.compile("/photo.php?fbid="))
        img_a_tag_2 = soup.find_all('a', href=re.compile("/photo"))
        
        if len(img_a_tag_1) > 0: 
            img_url = self.LOGIN_URL + img_a_tag_1[0]['href']
        elif len(img_a_tag_2) > 0: 
            img_url = self.LOGIN_URL + img_a_tag_2[0]['href']
        else : 
            img_a_tag_3 = soup.find_all('a', href=re.compile("pcb"))
            if len(img_a_tag_3) > 0:
                img_url = ''
                for item in img_a_tag_3:
                    img_url +=  self.LOGIN_URL + item['href'] + "\n"
            else: 
                img_a_tag_3 = soup.find_all('a', href=re.compile("photos"))
                if len(img_a_tag_3) > 0:
                    img_url = ''
                    for item in img_a_tag_3:
                        img_url +=  self.LOGIN_URL + item['href'] + "\n"
        return img_url

    def get_profile(self, soup):
        """
        Get the creator profile.
        Args:
            soup (`bs4.BeautifulSoup object`)
        Return:
            A string containing the creator name.
            A string containing the profile url.
        """
        h3 = soup.find("h3")
        if h3 is not None: 
            if h3.find('a') is not None:
                profile_name = h3.a.get_text()
                if h3.a.has_attr('href') :
                    h3_a_tag = h3.a['href']
                    h3_a_tag = h3_a_tag.replace("&__tn__=C-R",'')                  
                    profile_url = self.LOGIN_URL +  h3_a_tag
                else :
                    profile_url = "None"                  
        else :
            a_tag_actor = soup.find('a',class_="actor-link")
            if a_tag_actor is not None:
                profile_name = a_tag_actor.get_text()
                if a_tag_actor.has_attr('href'):
                    profile_url = self.LOGIN_URL + a_tag_actor['href']
                else:    
                    profile_url = "None"
            else:
                profile_name="None"
                profile_url="None"

        return profile_name, profile_url
    
    def get_post_description(self, soup):
        """
        Extract the post descrtiption (text).
        """
        p=soup.findAll("p")  
        if len(p) > 0:
            description_text =' ' 
            for item in p:
                description_text += item.get_text() + ' '    
        else :
            description_text = ' '
            div_tag = soup.find('div',{'data-ft':'{"tn":"*s"}'})
            if div_tag is not None:
                description_text += div_tag.get_text()
            else:
                div_tag =soup.find('div',{'data-ft':'{"tn":",g"}'})
                if div_tag is not None:
                    description_text += div_tag.get_text().split(" · in Timeline")[0].replace('· Public','')
        return description_text 

    def get_post_reactions(self, soup):
        """
        Extract the number of reactions for each reaction type.
        """
        nbr_reactions = ['0' for i in range(7)] 
        reactions_url_tag = soup.find('a',href=re.compile('/ufi/reaction/profile/'))
     
        if reactions_url_tag is not None:  
            reactions_url = self.LOGIN_URL + reactions_url_tag['href']
            #Beautiful Soup Object:
            self.driver.get(reactions_url)
            page_content = self.driver.page_source
            reactions_soup = BeautifulSoup(page_content, 'html.parser')
            #Extract the class of Reactions:
            reactions_a_tag = reactions_soup.findAll('a',class_='u')
            for item in reactions_a_tag:
                reactions_img = item.find('img')
                if reactions_img is not None:
                    if reactions_img.has_attr('alt'):
                        reactions_alt=reactions_img['alt']                  
                        for j in range(len(self.REACTIONS_NAMES)):
                            if reactions_alt == self.REACTIONS_NAMES[j]: 
                                nbr_reactions[j] = item.get_text()                         
                                                                                            
        return  nbr_reactions         
        
    def more_comments(self,soup):

        if soup.find('div',id=re.compile("see_next_")) is not None:
            more_comments_url = soup.find('div',id=re.compile("see_next_")).find('a',href=True)['href'].replace('https://m.facebook.com','')
        else:
            more_comments_url = None
        return more_comments_url

    
    def get_post_comments(self,soup, comments_dict={}, who_commented_dict={}, comments_max=1):

        count = 0
        while count <= comments_max: 
            who_commented_profiles, who_commented_names =[],[]
            comments_tag = soup.find_all('h3') 
            if len(comments_tag) > 0:
                for i in comments_tag:
                    a_tag = i.find('a')
                    if a_tag is not None:
                        if a_tag.has_attr('href'):
                            a_href = a_tag['href']
                            if ("refid=52&__tn__=R" in a_href) or ('refid=18&__tn__=R' in a_href) or ("?rc=p&__tn__=R" in a_href):
                                a_href = a_href.replace("&refid=52&__tn__=R",'')
                                a_href = a_href.replace("refid=52&__tn__=R",'')
                                a_href = a_href.replace("&refid=18&__tn__=R",'')
                                a_href = a_href.replace("?refid=18&__tn__=R",'')                                                                
                                a_href_url = self.LOGIN_URL + a_href
                                who_commented_profiles.append(a_href_url)
                                who_commented_names.append(a_tag.get_text())           
            #Comments Extraction:
            div=soup.find_all('div')
            div_text=[i.get_text() for i in div]
            
            aa,aa1=[],[]
            for i in div_text:
                if i not in aa:
                    aa.append(i)
            for j in aa:
                if 'Like · React · Reply · More ·' in j and 'View more comments…' not in j: 
                    aa1.append(j)
                    
            ll=[' ' for i in range(len(who_commented_names))]
            if len(who_commented_names) > 0:
                for i in range(len(who_commented_names)):
                    for j in aa1:
                        if who_commented_names[i] in j:
                            com=j.split(who_commented_names[i])[1]
                            ll[i]=com.split("Like")[0].replace('"','')
                            if 'Edited ·' in ll[i]:
                                ll[i]=com.split("Edited ·")[0]
               
                    for i in range(len(who_commented_names)):
                        
                        comments_dict[who_commented_names[i]] = ll[i]            
                        who_commented_dict[who_commented_names[i]] = who_commented_profiles[i]
            count = len(comments_dict.keys())
            
            more_comments = self.more_comments(soup)
            if more_comments is not None:
                more_comments_url = 'https://mbasic.facebook.com' + more_comments
                self.driver.get(more_comments_url)
                page_content = self.driver.page_source
                soup = BeautifulSoup(page_content, 'html.parser')
                
            else:
                break     

        comments_dict = json.dumps(comments_dict, ensure_ascii=False).encode('utf8').decode()
        who_commented_dict = json.dumps(who_commented_dict, ensure_ascii=False).encode('utf8').decode()
        return comments_dict, who_commented_dict

if __name__ == "__main__":

    posts_url = input(str("Enter Posts Url: "))
    scraper = Post_Scraper(chrome_driver_path, posts_url)
    scraper.login(username, password) 
    soup = scraper.get_content()
    posts_urls_list, post_date_list, likes_list = scraper.get_posts_info(soup)
    print(f">>> Number of Posts Availible: {len(posts_urls_list)}")

    profile_names_list, profile_urls_list, descriptions_list, who_commented_list, comments_list = [], [], [], [], []
    if number_posts_max > len(posts_urls_list):
        number_posts_max = len(posts_urls_list)

    for i in range(number_posts_max):
        post_url = posts_urls_list[i]
        post_soup = scraper.get_content(post_url)
        time.sleep(3)
        profile_name, profile_url = scraper.get_profile(post_soup)
        profile_names_list.append(profile_name)
        profile_urls_list.append(profile_url)
        descriptions_list.append(scraper.get_post_description(post_soup))
        who_commented, comments = scraper.get_post_comments(post_soup, comments_max=number_comments_max)
        who_commented_list.append(who_commented)
        comments_list.append(comments)
        print("----------------------------------")
        print(f"post {i+1} successfully scraped")
    data = {"profile_name":profile_names_list[:number_posts_max], "post_description":descriptions_list[:number_posts_max],
            "profile_url":profile_urls_list[:number_posts_max], "comments":comments_list[:number_posts_max],
            "who_commented":who_commented_list[:number_posts_max]}
    df = pd.DataFrame(data)
    df.to_csv(output_file_name)
    scraper.driver.close()