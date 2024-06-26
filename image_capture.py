import time, getpass, selenium, os
import numpy as np
from datetime import datetime
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.common.exceptions as sce
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options



"""
Exception if web driver cannot navigate to a default link on initial startup.
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
    def __init__(self, username, password, save_path, home_link="https://www.google.com"):
        self.username = username
        self.password = password
        self.save_path = save_path
        self.home_link = home_link
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--mute-audio")
        # Open an instance of Chrome and navigate to google.com.  Throw an error if not initialized.
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.maximize_window()
            self.driver.get(home_link)
            if self.driver.title:
                #print(f"Web driver initialized and navigated to home: {home_link}.")
                pass
                #print(f"Web driver initialized and navigated to home: {home_link}.")
                pass
            else:
                raise NoDriverFunctionality(home_link) 
        except Exception as e:
            raise e

    """
    Click button by xpath.
    """
    def click_button_by_xpath(self, xpath, timeout=10, attempts=20):
        button = WebDriverWait(self.driver, timeout=timeout, poll_frequency=timeout/attempts).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        button.click()
    """
    Click button by class name.
    """
    def click_button_by_class(self, class_name, timeout=10, attempts=20):
        button = WebDriverWait(self.driver, timeout=timeout, poll_frequency=timeout/attempts).until(
            EC.visibility_of_element_located((By.CLASS_NAME, class_name))
        )
        button.click()
    """
    Attempts to fill out a form element until maximum attempts reached (i.e., throw exception).
    """
    def fill_form(self, xpath, text, timeout=10, attempts=20):
        field = WebDriverWait(self.driver, timeout=timeout, poll_frequency=timeout/attempts).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        field.send_keys(text)

    """
    Check if a web element exists.
    Returns: True or False
    """
    def check_element_exists_xpath(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
        except sce.NoSuchElementException:
            return False
        except Exception as e:
            raise e
        else:
            return True
    
    """
    Check if a web element exists by class name.
    """
    def check_element_exists_class(self, class_name):
        try:
            self.driver.find_element(By.CLASS_NAME, class_name)
        except sce.NoSuchElementException:
            return False
        except Exception as e:
            raise e
        else:
            return True
    """
    Delete an element by its class name.
    """
    def delete_element(self, class_name):
        element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, class_name))
        )
        self.driver.execute_script("arguments[0].setAttribute('style', 'display:none');", element)
    
    """
    Restore an element to its original state.
    """
    def restore_element(self, class_name):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
        self.driver.execute_script("arguments[0].removeAttribute('style');", element)
    """
    Simulate a map guess.
    """
    def click_map(self, xpath):
        element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        ActionChains(self.driver).move_to_element(element).click().perform()

    """
    Simulate a key press.
    """
    def press_key(self, key):
        action = ActionChains(self.driver)
        action.send_keys(key)
        action.perform()

    """
    Move the cursor to an element.
    """
    def move_to_element(self, class_name):
        element = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, class_name))
        )
        ActionChains(self.driver).move_to_element(element).perform()


    """
    Start browsing GeoGuessr.
    """
    def start_game(self, country, num_images):
        country = country.lower()
        geoguessr_link = f"https://www.geoguessr.com/maps/{country}/play"

        # Navigate to desired map.
        self.driver.get(geoguessr_link)

        # Accept cookies
        cookies_xpath = "/html/body/div[2]/div[2]/div/div/div[2]/div/div/button"
        self.click_button_by_xpath(xpath=cookies_xpath)

        # Click login button
        login_xpath = "/html/body/div[1]/div/div[2]/div[1]/div[2]/header/div[2]/div[2]/a"
        self.click_button_by_xpath(xpath=login_xpath)

        # Enter GG username
        username_field = "/html/body/div[1]/div/div[2]/div[1]/main/div/div/form/div/div[1]/div[2]/input"
        self.fill_form(username_field, self.username)
        
        # Enter GG password
        password_field = "/html/body/div[1]/div/div[2]/div[1]/main/div/div/form/div/div[2]/div[2]/input"
        self.fill_form(password_field, self.password)

        # Submit form
        userpass_xpath = "/html/body/div[1]/div/div[2]/div[1]/main/div/div/form/div/div[3]/div[1]/div/button"
        self.click_button_by_xpath(userpass_xpath)
        
        # Game settings
        # Make sure settings are default
        move_setting = "/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div/div/div[5]/div/div[2]/div/div[2]/label[1]/div[3]/input"
        pan_setting = "/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div/div/div[5]/div/div[2]/div/div[2]/label[2]/div[3]/input"
        zoom_setting = "/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div/div/div[5]/div/div[2]/div/div[2]/label[3]/div[3]/input"
        default_settings_button = "/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div/div/div[5]/div/div/div[2]/input"

        # Enable NMPZ with time limits (we remove timer later)
        if not self.check_element_exists_class("game-options_optionGroup__qNKx1"):
            self.click_button_by_xpath(default_settings_button)
            self.click_button_by_xpath(move_setting)
            self.click_button_by_xpath(pan_setting)
            self.click_button_by_xpath(zoom_setting)
        
        # Start the game.
        start_game = "/html/body/div[1]/div[2]/div[2]/div[1]/main/div/div/div/div/div[3]/div/div/button"
        self.click_button_by_xpath(start_game)

        progress_bar = tqdm(total=num_images, desc="Image capture progress")
        for i in range(int(num_images/5)):
            # Delete game status (top right)
            self.delete_element("game_status__q_b7N")
            # Delete game controls (bottom left)
            self.delete_element("game_controls___pIfC")
            # Delete top HUD
            self.delete_element("game_topHud__tAKJD")
            
            # Play 5 rounds
            for _ in range(5):
                self.play_round(country)
                WebDriverWait(self.driver, timeout=10).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, "round-result_wrapper__V1VCe"))
                )
                self.press_key(Keys.SPACE)
                progress_bar.update(1)

            WebDriverWait(self.driver, timeout=10).until(
                EC.visibility_of_element_located((By.XPATH, 
                                                  "/html/body/div[1]/div[2]/div[2]/main/div[2]/div/div[2]/div/div[2]/div[3]/div/div/button")))
            self.press_key(Keys.SPACE)
        
        
        progress_bar.close()
        print("Finished.")
    
    """
    Play one round of Geoguessr, and display the result.
    """
    def play_round(self, country):
        # Delete map.
        self.delete_element("game_guessMap__MTlQ_")
        time.sleep(2) # Ensure picture load
        # Save screenshot
        timestamp = datetime.now().strftime("%m.%d.%Y_%H%M%S")
        screenshot_path = os.path.join(self.save_path, country)
        if not os.path.exists(screenshot_path):
            os.makedirs(screenshot_path)
        self.driver.save_screenshot(os.path.join(screenshot_path, f"{timestamp}_{country}.png"))
        self.restore_element("game_guessMap__MTlQ_") # Restore map visibility for the next round.
        # Click map.
        map_xpath = "/html/body/div[1]/div[2]/div[2]/main/div/div/div[4]/div/div[3]/div/div/div/div[3]/div[1]/div[2]"
        self.click_map(map_xpath)
        WebDriverWait(self.driver, timeout=10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "button_variantPrimary__xc8Hp"))
        )
        # Submit the guess.
        self.press_key(Keys.SPACE)


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
def get_credentials(admin_name="", admin=False):
    username = ""
    password = ""
    path = ""

    
    # I know it's bad...but please store user/pw in plain text, each on separate line
    if admin:
        path = os.path.join("/Users", admin_name, "admin.txt")
        with open(path) as f:
            lines = f.read().splitlines()
            username = lines[0]
            password = lines[1]
    else:
        username = input("Enter your GeoGuessr username: ")
        password = getpass.getpass("Enter your GeoGuessr password: ")

    return (username, password)

if __name__ == "__main__":
    """Only need to change country name below. Then hit run."""
    
    country = "colombia"

    """Optionally, include an "admin.txt" in your home folder.
    path to GG credentials is located in default home folder/admin_name"""
    username, password = get_credentials(admin_name=getpass.getuser(), admin=True)
    
    overnight = True
    batches = 40
    batch_size = 500
    
    # The parent GG path. Sub-dirs are automatically created for ea. country.
    save_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(save_path)

    if overnight:
        while overnight:
            try:
                for i in tqdm(range(batches), desc="Total batch progress", miniters=0):
                    data_acq = Browser(username, password, save_path)
                    data_acq.start_game(country=country, num_images=batch_size)
            except:
                pass
            finally:
                data_acq.driver.quit()
    else:
        for i in tqdm(range(batches), desc="Total batch progress", miniters=0):
            data_acq = Browser(username, password, save_path)
            data_acq.start_game(country=country, num_images=batch_size)
            data_acq.driver.quit()