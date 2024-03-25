from selenium import webdriver
from selenium.webdriver.common.by import By

import time
import getpass
import selenium

"""
Exception if web driver cannot navigate to a default link on initial startup.

Parameters:
home_link (str) - Link of website that the driver attempted to load.
message (str)
"""
class NoDriverFunctionality(Exception):
    def __init__(self, home_link, message=None):
        if message == None:
            self.message = f"Web driver initialized, but could not navigate to home: {home_link}"
        else:
            self.message = message

        super().__init__(self.message)


"""
A class that initializes a webdriver (browser) instance.

Attributes:
username (str) - The user's GeoGuessr username.
password (str) - The user's GeoGuessr password.
"""
class Browser():
    def __init__(self, username, password):
        self.username = username
        self.password = password

    """
    Attempts button clicks repeatedly until maximum attempts reached (i.e., throw exception).

    Parameters:
    xpath (str) - Path of XPATH element on the website.
    driver (selenium.webdriver) - A webdriver object.
    attempts (int) - Maximum number of attempts to click button.

    Returns:
    None
    """
    def click_button(self, xpath, driver, attempts=20):
        i = 0
        while i < attempts:
            try:
                button = driver.find_element(By.XPATH, xpath)
                button.click()
                break
            except:
                i += 1
                time.sleep(0.5)
        if i == attempts: # Last chance!
            button.click()
            
    """
    Attempts to fill out a form element until maximum attempts reached (i.e., throw exception).

    Parameters:
    xpath (str) - Path of XPATH element on the website.
    driver (selenium.webdriver) - A webdriver object.
    text (str) - The text to fill in.
    attempts (int) - Maximum number of attempts to click button.

    Returns:
    None
    """
    def fill_form(self, xpath, driver, text, attempts=20):
        i = 0
        while i < attempts:
            try:
                field = driver.find_element(By.XPATH, xpath)
                field.send_keys(text)
                break
            except:
                i += 1
                time.sleep(0.5)
        if i == attempts: # Last chance!
            field.send_keys(text)
    """
    Start browsing GeoGuessr.

    Parameters:
    country (str) - Name of country to explore.
    browser (str) - Type of browser

    Returns:
    None
    """
    def browser(self, browser, country):
        home_link = "https://www.google.com"
        country = country.lower()
        geoguessr_link = f"https://www.geoguessr.com/maps/{country}/play"


        # Open an instance of Chrome and navigate to google.com.  Throw an error if not initialized.
        try:
            driver = webdriver.Chrome()
            print(type(driver))
            driver.get(home_link)

            if driver.title:
                print(f"Web driver initialized and navigated to home: {home_link}.")
            else:
                raise NoDriverFunctionality(home_link) 
        except Exception as e:
            raise e
        
        # Navigate to desired map.
        driver.get(geoguessr_link)

        cookies_xpath = "/html/body/div[2]/div[2]/div/div/div[2]/div/div/button"
        self.click_button(xpath=cookies_xpath, driver=driver)

        login_xpath = "/html/body/div[1]/div/div[2]/div[1]/div[2]/header/div[2]/div[2]/a"
        self.click_button(xpath=login_xpath, driver=driver)

        
        username_field = "/html/body/div[1]/div/div[2]/div[1]/main/div/div/form/div/div[1]/div[2]/input"
        self.fill_form(username_field, driver, self.username)
        
        password_field = "/html/body/div[1]/div/div[2]/div[1]/main/div/div/form/div/div[2]/div[2]/input"
        self.fill_form(password_field, driver, self.password)

        userpass_xpath = "/html/body/div[1]/div/div[2]/div[1]/main/div/div/form/div/div[3]/div[1]/div/button"
        self.click_button(userpass_xpath, driver)

        while True:
            time.sleep(10000)
            print("i'm still here!")

"""
Grabs user's credentials to log into website.

Parameters:
os (str) - Enter as windows or mac, not case sensitive
admin_name (str) - The OS username (NOT GG USERNAME)
admin (bool) - Set to True if you have an admin.txt file in the default home directory. \
Otherwise, enter directly into the terminal.

Returns:
username, password (tuple, str)
"""
def get_credentials(os, admin_name="", admin=False):
    username = ""
    password = ""
    path = ""

    
    # I know it's bad...but please store user/pw in plain text, each on separate line
    if admin:
        if os.lower() == "mac":
            path = f"/Users/{admin_name}/admin.txt"
        elif os.lower() == "windows":
            path = f"C:\\Users\\{admin_name}\\admin.txt"
            # Implement with windows
        else:
            print("dirty linux abusers are not allowed")
            return
        with open(path) as f:
            lines = f.read().splitlines()
            username = lines[0]
            password = lines[1]
    else:
        username = input("Enter your GeoGuessr username: ")
        password = getpass.getpass("Enter your GeoGuessr password: ")

    return (username, password)
        

if __name__ == "__main__":
    # yo aidan please change the get_credentials parameters below or it will not work :)
    username, password = get_credentials(os="Mac", admin_name="ethan", admin=True)
    data_acq = Browser(username, password)
    data_acq.browser("chrome", "andorra")