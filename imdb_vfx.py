from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import time
import pandas as pd
import re
import os
from dotenv import load_dotenv

load_dotenv()

options = webdriver.ChromeOptions()
#options.add_argument('--headless')
options.add_argument("--enable-javascript")
options.add_argument('--no-sandbox')
userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
options.add_argument(f'user-agent={userAgent}')
options.add_argument("--lang=en-GB")
driver = webdriver.Chrome(options=options)

driver.get('https://www.imdb.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.imdb.com%2Fregistration%2Fap-signin-handler%2Fimdb_us&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=imdb_us&openid.mode=checkid_setup&siteState=eyJvcGVuaWQuYXNzb2NfaGFuZGxlIjoiaW1kYl91cyIsInJlZGlyZWN0VG8iOiJodHRwczovL3d3dy5pbWRiLmNvbS8_cmVmXz1sb2dpbiJ9&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&tag=imdbtag_reg-20')

driver.find_element(By.NAME, 'email').send_keys(os.getenv("IMDB_USERNAME"))
driver.find_element(By.NAME, 'password').send_keys(os.getenv("IMDB_PASSWORD"))
driver.find_element(By.ID, 'signInSubmit').click()

#To get the production company url
time.sleep(20)

#Input File

df = pd.read_csv(os.getenv('FILE_PATH'))

listofurls = df['url']
listofmovienames = df['movie_name']

# listofurls = ['https://pro.imdb.com/title/tt9218128?ref_=dsc_tt_res_pri_tt_view_1', 'https://pro.imdb.com/title/tt6263850?ref_=dsc_tt_res_pri_tt_view_2']
# listofmovienames = ['Gladiator 2', 'Deadpool & Wolverine']

index = 1

try:
    for url, movie_name in zip(listofurls, listofmovienames):

        print("url: ", url)

        driver.get(url)

        name_of_the_movie = movie_name
            
        all_filmmakers_url = ''.join(re.findall(r'(.*)\?',url))+'/filmmakers'

        driver.get(all_filmmakers_url)

        try:
            all_visual_effects_names = driver.find_elements(By.CSS_SELECTOR, "#title_filmmakers_visual_effects_sortable_table > tbody > tr.filmmaker > td:nth-child(1) > div > span > span > a")
            all_vfx_names = [each_vfx_name.text for each_vfx_name in all_visual_effects_names]
        except:
            all_vfx_names = [] 

        try:
            all_visual_effects_titles = driver.find_elements(By.CSS_SELECTOR, "#title_filmmakers_visual_effects_sortable_table > tbody > tr.filmmaker > td:nth-child(1) > div > div > span > span.see_more_text_collapsed")
            all_vfx_titles = [each_vfx_title.text for each_vfx_title in all_visual_effects_titles]
        except:
            all_vfx_titles = [] 

        try:
            all_visual_effects_urls = driver.find_elements(By.CSS_SELECTOR, "#title_filmmakers_visual_effects_sortable_table > tbody > tr.filmmaker > td:nth-child(1) > div > span > span > a")
            all_vfx_urls = [each_vfx_url.get_attribute('href') for each_vfx_url in all_visual_effects_urls]
        except:
            all_vfx_urls = [] 

        for vfx_name, vfx_title, vfx_url in zip(all_vfx_names, all_vfx_titles, all_vfx_urls):
            if 'Visual Effects' in vfx_title or 'CG Supervisor' in vfx_title or 'Head' in vfx_title:
                vfx_person_name = vfx_name

                print("vfx_name:", vfx_person_name)

                driver.get(vfx_url)

                try:
                    vfx_production_name = driver.find_element(By.XPATH,"(//div[preceding-sibling::div[contains(@class,'contacts_header')][contains(.,'Company')]]/ul//li//span[@class='aok-align-center']//a)[1]").text
                except:
                    vfx_production_name = None

                try:
                    vfx_production_email = driver.find_element(By.XPATH,"(//div[preceding-sibling::div[contains(@class,'contacts_header')][contains(.,'Company')]]/ul//li//span//a[contains(@class,'clickable_share_link')][contains(.,'@')])[1]").text
                except:
                    vfx_production_email = None
                
                try:
                    vfx_production_address_line_1 = driver.find_element(By.XPATH, "(//div[preceding-sibling::div[contains(@class,'contacts_header')][contains(.,'Company')]]/ul//li//div[preceding-sibling::div/span[contains(@class,'glyphicons-map-marker')]]/span)[1]").text
                except:
                    vfx_production_address_line_1 = ''

                try:   
                    vfx_production_city_states = driver.find_elements(By.XPATH, "(//div[preceding-sibling::div[contains(@class,'contacts_header')][contains(.,'Company')]])[1]/ul//li//div[@class='a-section a-spacing-top-none'][not(contains(.,'map'))]")
                    vfx_production_city_states = [i.text for i in vfx_production_city_states if i]
                    vfx_production_city_states = ', '.join(vfx_production_city_states)
                except:
                    vfx_production_city_states = ''
                
                if vfx_production_address_line_1 and vfx_production_city_states:
                    vfx_production_full_addresses = vfx_production_address_line_1+','+vfx_production_city_states
                elif vfx_production_address_line_1:
                    vfx_production_full_addresses = vfx_production_address_line_1
                elif vfx_production_city_states:
                    vfx_production_full_addresses = vfx_production_city_states
                else:
                    vfx_production_full_addresses = None
                
                try:
                    direct_contact_name = driver.find_element(By.XPATH, "//div[@id='contacts']//div[contains(.,'Direct Contact')]//div//ul/li//span[@class='aok-align-center']/span").text
                except:
                    direct_contact_name = None

                try:
                    direct_contact_twitter = driver.find_element(By.XPATH, "//div[@id='contacts']//div[contains(.,'Direct Contact')]//div//ul/li//span[contains(.,'twitter')]//a").get_attribute('href')
                except:
                    direct_contact_twitter = None

                try:
                    direct_contact_facebook = driver.find_element(By.XPATH, "//div[@id='contacts']//div[contains(.,'Direct Contact')]//div//ul/li//span[contains(.,'facebook')]//a").get_attribute('href')
                except:
                    direct_contact_facebook = None

                try:
                    direct_contact_instagram = driver.find_element(By.XPATH, "//div[@id='contacts']//div[contains(.,'Direct Contact')]//div//ul/li//span[contains(.,'instagram')]//a").get_attribute('href')
                except:
                    direct_contact_instagram = None

                try:
                    direct_contact_phone = driver.find_element(By.XPATH, "//div[@id='contacts']//div[contains(.,'Direct Contact')]//div//ul/li//span[contains(.,'phone')]").text
                    direct_contact_phone = direct_contact_phone.replace('phone','').strip()
                except:
                    direct_contact_phone = None

                try:
                    direct_contact_email = driver.find_element(By.XPATH, "//div[@id='contacts']//div[contains(.,'Direct Contact')]//div//ul/li//span[contains(.,'@')]/a").text
                except:
                    direct_contact_email = None

                vfx_df = pd.DataFrame({
                    'movie_name': [name_of_the_movie],
                    'companies_credit_url': [None],
                    'producers': [None],
                    'directors': [None],
                    'directors_url': [None],
                    'moviemeter': [None],
                    'status': [None],
                    'staff_url': [vfx_url],
                    'staff_name': [vfx_person_name],
                    'staff_title': [vfx_title],
                    'staff_email': [None],
                    'staff_startmeter': [None],
                    'staff_full_address': [None],
                    'production_name': [vfx_production_name],
                    'production_url': [None],
                    'production_phone': [None],
                    'production_website': [None],
                    'production_email': [vfx_production_email],
                    'production_full_address': [vfx_production_full_addresses],
                    'direct_contact_name': [direct_contact_name],
                    'direct_contact_twitter': [direct_contact_twitter],
                    'direct_contact_facebook': [direct_contact_facebook],
                    'direct_contact_instagram': [direct_contact_instagram],
                    'direct_contact_phone': [direct_contact_phone],
                    'direct_contact_email': [direct_contact_email]
                })
                    
                #output file - VFX data

                if index == 1:
                    vfx_df.to_csv('IMDB USA Production TV Series Feb 10.csv', index=False, mode='a', header=True)
                    index+=1   
                else:
                    vfx_df.to_csv('IMDB USA Production TV Series Feb 10.csv', index=False, mode='a', header=False)                        

except StaleElementReferenceException:
    print("Element not found, skipping...")
except Exception as e:
    print(f"Error processing: {e}")
    driver.quit()
finally:
    pass

print("Run Completed!!!!!!")
driver.quit()