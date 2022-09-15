from genericpath import isfile
import json
import platform
import time
import shutil


from dotenv import dotenv_values
from pathlib import Path
from pyautogui import press
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from typing import List, Dict

from webdriver_manager.firefox import GeckoDriverManager


CONFIGURATION_SELENIUM = dotenv_values(".env")

class Firefox_control():
    def __init__(self, login:str, password: str, load_strategie: str = 'eager') -> None:
        self.url = CONFIGURATION_SELENIUM['url']
        self.login = login
        self.password = password
        self.connect = False
        self._binary_location = CONFIGURATION_SELENIUM['binary_dir']
        self._options = self.set_options(load_strategie)
        self._service = self.set_service()
        self._profil = self.set_profil()
        self._profil_dir = self.set_profil_dir()
        self._driver = None
        self._selected_items = None
        self._found_items = None


    def wait_element_by_id(self, id_name:str, time_to_wait: int = 100) -> bool:
        try:
            WebDriverWait(self.driver(), time_to_wait).until(expected_conditions.presence_of_element_located((By.ID, id_name)))
            return True
        except TimeoutException:
            print(f"Erreur : impossible de localiser le champ {id_name}")
            return False
    
    def wait_element_by_class(self, id_name:str, time_to_wait: int = 100) -> bool:
        try:
            WebDriverWait(self.driver(), time_to_wait).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, id_name)))
            return True
        except TimeoutException:
            print(f"Erreur : impossible de localiser le champ {id_name}")
            return False
    
    def wait_element_by_xpath(self, id_name:str, time_to_wait: int = 100) -> bool:
        try:
            WebDriverWait(self.driver(), time_to_wait).until(expected_conditions.presence_of_element_located((By.XPATH, id_name)))
            return True
        except TimeoutException:
            print(f"Erreur : impossible de localiser le champ {id_name}")
            return False

    def find_element_by_id(self, list_items: List[str]) -> None:
        self.reset_found_item()
        elements: Dict[str, WebElement]
        for element in list_items:
            try:
                elements = self.driver().find_element(By.ID, element)
            except Exception:
                raise Exception(f"Element {element} not found")
        self._found_items = elements

    def find_element_by_tagname(self, tagname: str) -> bool:
        self.reset_found_item()
        elements: Dict[str, WebElement]
        try:
            elements = self.driver().find_element(By.TAG_NAME, tagname)
        except Exception:
            raise Exception(f"Element {tagname} not found")
        self._found_items = elements
        return True

    def find_element_by_text(self, text_to_search: str) -> bool:
        self.reset_found_item()
        try:
            elements = self.driver().findElement(By.linkText(text_to_search));
        except Exception:
            raise Exception(f"Element with '{text_to_search}' in not found")
        self._found_items = elements

    def element_exist_by_id(self, item: str) -> bool:
        try:
            self.find_element_by_id([item])
            return True
        except Exception:
            return False

    def select_items(self, list_items: List[str], type: str = 'ID') -> None:
        self.reset_selected_items()
        items: Dict[str, WebElement] = {}
        for item in list_items:
            try:
                if type == 'ID':
                    items[item] = self.driver().find_element(By.ID, item)
                elif type == 'CLASS_NAME':
                    items[item] = self.driver().find_element(By.CLASS_NAME, item)
                elif type == 'NAME':
                    items[item] = self.driver().find_element(By.NAME, item)
                elif type == 'XPATH':
                    items[item] = self.driver().find_element(By.XPATH, item)
                else:
                    print('nothing choose')
            except Exception:
                raise Exception(f"Items {item} not found")
        self._selected_items = items
    
    def reset_found_item(self) -> None:
        self._found_items = None

    def reset_selected_items(self) -> None:
        self._selected_items = None

    def set_profil_dir(self) -> str:
        return self.profil().profile_dir

    def set_options(self, load_strategie: str) -> Options:
        options = Options()
        options.binary_location = self._binary_location
        options.page_load_strategy = load_strategie
        options.set_preference("browser.link.open_newwindow", 3)
        options.set_preference("browser.link.open_external", 3)
        return options

    def set_profil(self) -> FirefoxProfile:
        root_path = Path.joinpath(Path(__file__).parent, 'ressources', 'profiles', CONFIGURATION_SELENIUM['firefox_profiles'])
        profile = FirefoxProfile(root_path)
        profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/99.0")
        profile.set_preference("browser.download.dir", str(Path.joinpath(Path(__file__).parent, CONFIGURATION_SELENIUM['export_xls_path'])))
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/csv,application/excel,application/vnd.ms-excel,application/vnd.msexcel,text/anytext,text/comma-separated-values,text/csv,text/plain,text/x-csv,application/x-csv,text/x-comma-separated-values,text/tab-separated-values,data:text/csv")
        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/xml,text/plain,text/xml,image/jpeg,application/octet-stream,data:text/csv")
        profile.set_preference("browser.download.folderList",2)
        profile.set_preference("browser.download.manager.showWhenStarting",False)
        profile.set_preference("browser.helperApps.neverAsk.openFile","application/csv,application/excel,application/vnd.ms-excel,application/vnd.msexcel,text/anytext,text/comma-separated-values,text/csv,text/plain,text/x-csv,application/x-csv,text/x-comma-separated-values,text/tab-separated-values,data:text/csv")
        profile.set_preference("browser.helperApps.neverAsk.openFile","application/xml,text/plain,text/xml,image/jpeg,application/octet-stream,data:text/csv")
        profile.set_preference("browser.helperApps.alwaysAsk.force", False)
        profile.set_preference("browser.download.useDownloadDir", True)
        profile.set_preference("dom.file.createInChild", True)
                
        profile.update_preferences()
        profile.accept_untrusted_certs = True
        profile.assume_untrusted_cert_issuer = True
        profile_dir = profile.profile_dir

        handlers = {
            "defaultHandlersVersion": {"fr": 3},
            "mimeTypes": {},
            "schemes": {
                "pulsesecure": {"action": 4}
            }
        }


        with open(profile_dir + '/handlers.json', 'w+', encoding='utf-8') as file:
            json.dump(handlers, file)
        return profile

    def selected_items(self) -> Dict[str, WebElement]:
        return self._selected_items

    def set_driver(self) -> None:
        self._driver = webdriver.Firefox(firefox_profile=self.profil(), service=self.service(), options=self.options())
        self._driver.get(self.url)

    def set_service(self) -> FirefoxService:
        driver_path = Path.joinpath(Path(__file__).parent, 'ressources')
        if driver_path.exists():
            os = platform.system()
            if os == 'Linux':
                driver_path = Path.joinpath(driver_path, 'geckodriver_linux')
            elif os == 'Windows':
                driver_path = Path.joinpath(driver_path, 'geckodriver_windows.exe')
            else:
                raise Exception('OS not supported')

            if driver_path.is_file():
                return FirefoxService(executable_path=driver_path)
            else:
                raise Exception('geckodriver not found in ressources respository')
        else:
            raise Exception('ressources repository not found.')
    
    def found_items(self) -> Dict[str, WebElement]:
        return self._found_items

    def profil_dir(self) -> str:
        return self._profil_dir

    def profil(self) -> FirefoxProfile:
        return self._profil

    def driver(self) -> webdriver:
        return self._driver

    def service(self) -> FirefoxService:
        return self._service
    
    def options(self) -> Options:
        return self._options