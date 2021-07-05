#!/usr/bin/env python
# coding: utf-8

# In[226]:


# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager


# In[227]:


# Set the executable path and initialize Splinter
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)


# ### Visit the NASA Mars News Site

# In[228]:


# Visit the mars nasa news site
url = 'https://redplanetscience.com/'
browser.visit(url)

# Optional delay for loading the page
browser.is_element_present_by_css('div.list_text', wait_time=1)


# In[229]:


# Convert the browser html to a soup object and then quit the browser
html = browser.html
news_soup = soup(html, 'html.parser')

slide_elem = news_soup.select_one('div.list_text')


# In[230]:


slide_elem.find('div', class_='content_title')


# In[231]:


# Use the parent element to find the first a tag and save it as `news_title`
news_title = slide_elem.find('div', class_='content_title').get_text()
news_title


# In[232]:


# Use the parent element to find the paragraph text
news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
news_p


# ### JPL Space Images Featured Image

# In[233]:


# Visit URL
url = 'https://spaceimages-mars.com'
browser.visit(url)


# In[234]:


# Find and click the full image button
full_image_elem = browser.find_by_tag('button')[1]
full_image_elem.click()


# In[235]:


# Parse the resulting html with soup
html = browser.html
img_soup = soup(html, 'html.parser')
img_soup


# In[236]:


# find the relative image url
img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
img_url_rel


# In[237]:


# Use the base url to create an absolute url
img_url = f'https://spaceimages-mars.com/{img_url_rel}'
img_url


# ### Mars Facts

# In[238]:


df = pd.read_html('https://galaxyfacts-mars.com')[0]
df.head()


# In[239]:


df.columns=['Description', 'Mars', 'Earth']
df.set_index('Description', inplace=True)
df


# In[240]:


df.to_html()


# # D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles

# ### Hemispheres

# In[241]:


# 1. Use browser to visit the URL 
url = 'https://marshemispheres.com/'

browser.visit(url)

hemi_html=browser.html
hemi_soup = soup(hemi_html,'html.parser')

hemisphere_images = hemi_soup.find_all('div', class_='item')


# In[242]:


# 2. Create a list to hold the images and titles.
hemisphere_image_urls = []

# Create loop to scrape through all hemisphere information
for item in hemisphere_images:
    hemisphere = {}
    
    #find the title
    titles = item.find('h3').text
    
    #find the path for the corresponding title
    image_path = item.find('a', class_='itemLink product-item')['href']
    
    #scrape the image path to get the .jpg path
    browser.visit(url + image_path)
    
    # parse the data to get .jpg
    jpg_html = browser.html
    jpg_soup = soup(jpg_html, 'html.parser')
    jpg_image_path = image_soup.find('div', class_= 'downloads')
    image_url = jpg_image_path.find('a')['href']
    
    print(titles)
    print(image_url)
    
    # append list
    hemisphere['image_url'] = url + image_url
    hemisphere['title'] = titles
    hemisphere_image_urls.append(hemisphere)
    browser.back()


# In[243]:


# 4. Print the list that holds the dictionary of each image url and title.
# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    hemisphere_image_urls = mars_hemispheres(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "mars_hemisphere": hemisphere_image_urls  
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_paragrapah = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_paragraph


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


def mars_hemispheres(browser):

    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    hemi_html=browser.html
    hemi_soup = soup(hemi_html,'html.parser')

    hemisphere_images = hemi_soup.find_all('div', class_='item')

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    try:

        # Create loop to scrape through all hemisphere information
        for item in hemisphere_images:
            hemisphere = {}
            
            #find the title
            titles = item.find('h3').text
            
            #find the path for the corresponding title
            image_path = item.find('a', class_='itemLink product-item')['href']
            
            #scrape the image path to get the .jpg path
            browser.visit(url + image_path)
            
            # parse the data to get .jpg
            jpg_html = browser.html
            jpg_soup = soup(jpg_html, 'html.parser')
            jpg_image_path = jpg_soup.find('div', class_= 'downloads')
            image_url = jpg_image_path.find('a')['href']
            
            print(titles)
            print(image_url)
            
            # append list
            hemisphere['image_url'] = url + image_url
            hemisphere['title'] = titles
            hemisphere_image_urls.append(hemisphere)
            browser.back()

        except ValueError:
            return None 

        return hemisphere_image_urls
        
                   
if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())


# In[244]:


# 5. Quit the browser
browser.quit()


# In[ ]:




