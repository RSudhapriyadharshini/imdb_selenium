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

tv_studio_companies_list = [
    "Amazon Studios",
    "Marvel Studios",
    "Netflix Studios",
    "Apple Studios",
    "Amazon Prime Video",
    "Anonymous Content",
    "Paramount Pictures,"
    "Sony Pictures Releasing",
    "Walt Disney Pictures",
    "Blumhouse Productions",
    "HBO Max",
    "Apple TV+",
    "Disney+",
    "Lionsgate Productions",
    "Sony Pictures Television",
    "Sony Pictures Classics",
    "Highland Film Group (HFG)",
    "Lionsgate Television",
    "20th Television",
    "Thunder Road Pictures",
    "Hulu",
    "Temple Hill Entertainment",
    "Universal Pictures",
    "Warner Bros.",
    "Warner Bros. Discovery",
    "Warner Bros. Television",
    "Warner Bros. Animation",
    "Legendary Entertainment",
    "Lions Gate Films",
    "Buffalo 8 Productions",
    "Cinesite",
    "British Film Institute (BFI)",
    "British Broadcasting Corporation (BBC)",
    "SKY Studios",
    "YouTube",
    "Netflix",
    "The Walt Disney Company",
    "BBC Studios",
    "Fox Entertainment",
    "DreamWorks Animation",
    "Disney Television Animation",
    "Peacock",
    "Walt Disney Animation Studios",
    "Chernin Entertainment",
    "Bad Robot",
    "Endeavor Content",
    ]

production_companies_dup_filter_list = []

print("production_companies_dup_filter_list: ", production_companies_dup_filter_list)

index = 1

#To get the production company url
time.sleep(20)

#Input File

df = pd.read_csv(os.getenv('FILE_PATH'))

listofurls = df['url']
listofmovienames = df['movie_name']

# listofurls = ['https://pro.imdb.com/title/tt9218128?ref_=dsc_tt_res_pri_tt_view_1', 'https://pro.imdb.com/title/tt6263850?ref_=dsc_tt_res_pri_tt_view_2']
# listofmovienames = ['Gladiator 2', 'Deadpool & Wolverine']

vfx_data = []  

try:
    for url, movie_name in zip(listofurls, listofmovienames):

        print("url: ", url)

        driver.get(url)

        name_of_the_movie = movie_name
            
        all_filmmakers_url = ''.join(re.findall(r'(.*)\?',url))+'/filmmakers'

        driver.get(all_filmmakers_url)

        try:
            director = driver.find_element(By.CSS_SELECTOR, "#title_filmmakers_director_sortable_table > tbody > tr.filmmaker > td:nth-child(1) > div > span > span > a").text
        except:
            director = None

        try:
            director_url = driver.find_element(By.CSS_SELECTOR, "#title_filmmakers_director_sortable_table > tbody > tr.filmmaker > td:nth-child(1) > div > span > span > a").get_attribute('href')
        except:
            director_url = None 

        try:
            producers = []
            list_of_producers = driver.find_elements(By.CSS_SELECTOR, "#title_filmmakers_producer_sortable_table > tbody > tr.filmmaker > td:nth-child(1) > div > span > span > a")
            for each_producer in list_of_producers:
                producer = each_producer.text
                producers.append(producer)
            all_producers = ', '.join(producers)    #in str
        except:
            all_producers = None

        try:
            moviemeter = driver.find_element(By.CSS_SELECTOR, "#popularity_widget > div.a-section.a-spacing-top-mini > div > div > div.a-fixed-left-grid-col.a-col-left > div.a-fixed-left-grid > div > div.a-text-left.a-fixed-left-grid-col.a-col-right > span > span > a").text
        except:
            moviemeter = None

        try:
            all_status_text = driver.find_element(By.CSS_SELECTOR, "#status_summary > div.a-section.a-spacing-top-mini").text
            status_01 = [i.strip() for i in all_status_text.split('\n') if i.strip()][1]
            status = [i.strip() for i in status_01.split(' ') if i.strip()][0]
        except:
            status = None

        to_see_all_company_credit_url = ''.join(re.findall(r'(.*)\?',url))+'/companycredits'
        driver.get(to_see_all_company_credit_url)
        
        try:
            all_production_company_urls = driver.find_elements(By.CSS_SELECTOR, "#production > tbody > tr > td:nth-child(1) > div > span > a")
            all_production_companies_urls = [each_production.get_attribute('href') for each_production in all_production_company_urls]
        except:
            all_production_companies_urls = []

        try:
            all_production_companies_names = [each_production.text for each_production in all_production_company_urls]
        except:
            all_production_companies_names = []
            
        for each_production_url, each_production_name in zip(all_production_companies_urls, all_production_companies_names):

            try:
                if not each_production_name in tv_studio_companies_list: # check the production company which is present in the list or not, to remove those companies

                    if not each_production_name in production_companies_dup_filter_list:

                        production_companies_dup_filter_list.append(each_production_name)
                    
                        print("each_production_url: ", each_production_url)

                        prod_url = each_production_url
                        
                        driver.get(prod_url)

                        try:
                            production_name = each_production_name.strip()
                        except:
                            production_name = None

                        try:
                            production_url = prod_url
                        except:
                            production_url = None
                        
                        try:
                            production_phone = driver.find_element(By.XPATH, '//section[@data-testid="company-contact-item"]//div[@class="sc-d806175d-3 fSCWlH"]/div/div[contains(.,"hone")]').text
                            production_phone = production_phone.replace('Phone', '').replace(':', '').strip()
                        except:
                            production_phone = None

                        try:
                            production_website = driver.find_element(By.XPATH, '//a[@data-testid="contact-website"]').get_attribute('href')
                        except:
                            production_website = None

                        try:
                            production_email = driver.find_element(By.XPATH, '//section[@data-testid="company-contact-item"]//div[@class="sc-d806175d-3 fSCWlH"]/div/div[contains(.,"mail")]').text
                            production_email = production_email.replace('Email', '').replace(':', '').strip()
                        except:
                            production_email = None
                        
                        try:
                            listofproductionfulladdress = driver.find_elements(By.XPATH, '(//div[@data-testid="contact-address"])[1]//div')
                            production_full_address = [each_production_address.text for each_production_address in listofproductionfulladdress]
                            production_full_address = ', '.join(production_full_address)
                        except:
                            production_full_address = None

                        all_staff_url = ''.join(re.findall(r'(.*)\?',prod_url))+'/staff/?ref_=co_ov_staff_all'
                        driver.get(all_staff_url)  #click on the all staff to navigate to all staffs
                        try:
                            listofstaffs = driver.find_elements(By.CSS_SELECTOR, "#company_staff_sortable > tbody > tr > td:nth-child(1) > div > div > div > div.a-fixed-left-grid-col.a-col-right > span > a")
                            listofstaffsurls = [staff.get_attribute('href') for staff in listofstaffs]

                        except:
                            listofstaffsurls = []

                        try:
                            listofstaffsname = driver.find_elements(By.CSS_SELECTOR, "#company_staff_sortable > tbody > tr > td:nth-child(1) > div > div > div > div.a-fixed-left-grid-col.a-col-right > span > a")
                            listofstaffsnames = [staffname.text for staffname in listofstaffsname]

                        except:
                            listofstaffsnames = []

                        try:
                            listofstaffstitle = driver.find_elements(By.CSS_SELECTOR, "#company_staff_sortable > tbody > tr > td:nth-child(3) > div")
                            listofstaffstitles = [title.text for title in listofstaffstitle]

                        except:
                            listofstaffstitles = []

                        try:
                            listofstaffsstarmeter = driver.find_elements(By.CSS_SELECTOR, "#company_staff_sortable > tbody > tr > td:nth-child(2) > div")
                            listofstaffsstarmeters = [starmeter.text for starmeter in listofstaffsstarmeter]

                        except:
                            listofstaffsstarmeters = []
                        
                        for each_staff_url, each_staff_name, each_staff_title, each_staff_starmeter in zip(listofstaffsurls, listofstaffsnames, listofstaffstitles, listofstaffsstarmeters):

                            print("each_staff_url: ", each_staff_url)

                            try:
                                driver.get(each_staff_url)

                                try:
                                    staff_title = each_staff_title
                                except:
                                    staff_title = None

                                try:
                                    staff_name = each_staff_name
                                except:
                                    staff_name = None

                                try:
                                    staff_startmeter = each_staff_starmeter
                                except:
                                    staff_startmeter = None

                                try:
                                    listofstafffulladdress = []

                                    all_staff_blocks = driver.find_elements(By.XPATH, "//div[preceding-sibling::div[contains(@class,'contacts_header')][contains(.,'Company')]]")
                                    for each_staff_block in all_staff_blocks:
                                        staff_company_name = each_staff_block.find_element(By.XPATH, "./ul//li//span[@class='aok-align-center']//a").text
                                        staff_company_name = staff_company_name.strip()

                                        try:
                                            staff_email = each_staff_block.find_element(By.XPATH,"./ul//li//span//a[contains(@class,'clickable_share_link')][contains(.,'@')]").text
                                        except:
                                            staff_email = None
                                        
                                        try:
                                            staff_address_line_1 = each_staff_block.find_element(By.XPATH, "./ul//li//div[preceding-sibling::div/span[contains(@class,'glyphicons-map-marker')]]/span").text
                                        except:
                                            staff_address_line_1 = ''

                                        try:   
                                            staff_city_states = each_staff_block.find_elements(By.XPATH, "./ul//li//div[@class='a-section a-spacing-top-none'][not(contains(.,'map'))]")
                                            staff_city_states = [i.text for i in staff_city_states if i]
                                            staff_city_states = ', '.join(staff_city_states)
                                        except:
                                            staff_city_states = ''
                                        
                                        if staff_address_line_1 and staff_city_states:
                                            staff_full_addresses = staff_address_line_1+','+staff_city_states
                                        elif staff_address_line_1:
                                            staff_full_addresses = staff_address_line_1
                                        elif staff_city_states:
                                            staff_full_addresses = staff_city_states
                                        else:
                                            staff_full_addresses = None

                                        if staff_company_name == production_name:
                                            listofstafffulladdress.append(staff_full_addresses)

                                    staff_full_address = ''.join(listofstafffulladdress)
                                except:
                                    staff_full_address = None

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

                                df = pd.DataFrame({
                                    'movie_name': [name_of_the_movie],
                                    'companies_credit_url': [to_see_all_company_credit_url],
                                    'producers': [all_producers],
                                    'directors': [director],
                                    'directors_url': [director_url],
                                    'moviemeter': [moviemeter],
                                    'status': [status],
                                    'staff_url': [each_staff_url],
                                    'staff_name': [staff_name],
                                    'staff_title': [staff_title],
                                    'staff_email': [staff_email],
                                    'staff_startmeter': [staff_startmeter],
                                    'staff_full_address': [staff_full_address],
                                    'production_name': [production_name],
                                    'production_url': [production_url],
                                    'production_phone': [production_phone],
                                    'production_website': [production_website],
                                    'production_email': [production_email],
                                    'production_full_address': [production_full_address],
                                    'direct_contact_name': [direct_contact_name],
                                    'direct_contact_twitter': [direct_contact_twitter],
                                    'direct_contact_facebook': [direct_contact_facebook],
                                    'direct_contact_instagram': [direct_contact_instagram],
                                    'direct_contact_phone': [direct_contact_phone],
                                    'direct_contact_email': [direct_contact_email]
                                })
		
		                        #output file

                                if index == 1:
                                    df.to_csv('IMDB USA Production TV Series Feb 22.csv', index=False, mode='a', header=True)
                                    index+=1   
                                else:
                                    df.to_csv('IMDB USA Production TV Series Feb 22.csv', index=False, mode='a', header=False)                        
                                    
                            except StaleElementReferenceException:
                                print("Element not found in staff response, skipping...")
                            except Exception as e:
                                print(f"Error processing staff URL: {e}")
                
            except StaleElementReferenceException:
                print("Element not found in production response, skipping...")
            except Exception as e:
                print(f"Error processing production URL: {e}")
        print("production_companies_dup_filter_list=======>", production_companies_dup_filter_list)
except StaleElementReferenceException:
    print("Element not found, skipping...")
except Exception as e:
    print(f"Error processing: {e}")
    driver.quit()
finally:
    pass

print("Run Completed!!!!!!")
driver.quit()