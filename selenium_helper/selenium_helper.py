# imports ------------------
import time
import logging
import gc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox import service as fs
from selenium.common.exceptions import TimeoutException

# Functions ------------------

# Private Functions ------------------

# Class ------------------


class SeleniumBrowser:
    """
    This is a module to support to use a selenium with several functions.
    """

    def __init__(
        self,
        geckodriver_path: str,
        headless: bool = True,
        tor_access: bool = False,
        tor_browser: bool = False,
        browser_setting: dict = {"browser_path": "", "browser_profile": ""},
        addons: dict = {"dir": "", "apps": []},
        proxy: dict = {"ip": "", "port": 3128},
        set_size: bool = False,
    ) -> None:
        """
        Class function for selenium browser
        Args:
            geckodriver_path: geckodriver's path
            browser_path: browser's path, such as, Firefox or Tor
            headless: Use headless mode (bool), default = True
            tor_access: Use Tor (bool), default = False
            tor_browser: Use Tor browser (bool), default = False
            browser_setting: Browser setting (dict), default = {"browser_path": "", "browser_profile": ""}
            addons: Use installed addons (dict), default = {"dir": "", "apps": []}
            proxy: Use proxy server (dict), default = {"ip": "", "port": ""}
            set_size: set windows size as (900, 500) (bool), default = false
        Returns:
            browser: self.browser
        """
        # input parameters
        self.geckodriver_path = geckodriver_path
        self.headless = headless
        self.tor_access = tor_access
        self.tor_browser = tor_browser
        self.browser_setting = browser_setting
        self.addons = addons
        self.proxy = proxy
        self.set_size = set_size
        # initial check
        init_ok = self._init_check()
        if not init_ok:
            raise NotCorrectValueException
        # Activate headless mode of Firefox
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        # Profile should be set with options from Selenium4
        options.set_preference("profile", browser_setting["browser_profile"])
        # Use Service for executable_path from Selenium4
        firefox_service = fs.Service(executable_path=geckodriver_path)

        if tor_access and tor_browser:
            """
            Use tor network with tor browser.

            [Caution] As of now, my browser doesn't connect to tor network automatically.
            You need to connect to the tor network manually.
            """
            proxyHost = "127.0.0.1"
            proxyPort = 9150

            options.binary_location = browser_setting["browser_path"]
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.socks", proxyHost)  # SOCKS PROXY
            options.set_preference("network.proxy.socks_port", proxyPort)
            options.set_preference("network.proxy.socks_remote_dns", False)

        elif tor_access:
            """
            Use tor network with Firefox.

            [Caution] You need to connect to the tor network manually,
            such as, tor browser, and it provides proxy access with localhost and port 9150.
            """
            proxyHost = "127.0.0.1"
            proxyPort = 9150
            options.binary_location = browser_setting["browser_path"]
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.socks", proxyHost)  # SOCKS PROXY
            options.set_preference("network.proxy.socks_port", proxyPort)

        elif len(proxy["ip"]) > 0 and len(str(proxy["port"])) > 0:
            # Proxy access with specified ip and port.
            proxyHost = proxy["ip"]
            proxyPort = proxy["port"]
            options.binary_location = browser_setting["browser_path"]
            options.set_preference("network.proxy.type", 1)
            options.set_preference("network.proxy.http", proxyHost)
            options.set_preference("network.proxy.http_port", proxyPort)
            options.set_preference("network.proxy.ssl", proxyHost)  # SSL PROXY
            options.set_preference("network.proxy.ssl_port", proxyPort)

        else:
            # Normal access with selenium.
            # get browser for selenium
            options.binary_location = browser_setting["browser_path"]

        self.browser = webdriver.Firefox(service=firefox_service, options=options)

        if len(addons["dir"]) > 0 and len(addons["apps"]) > 0:
            # Use addons
            extensions_dir = addons["dir"]
            extensions = addons["apps"]
            for extension in extensions:
                self.browser.install_addon(extensions_dir + extension, temporary=True)

        self.browser.implicitly_wait(10)  # set implicit time until a timeout (sec)

        # Close other tabs.
        time.sleep(1)
        self.close_other_tabs()

        if set_size:
            # set position and size.
            self.browser.set_window_position(0, 0)
            self.browser.set_window_size(900, 500)

        # delete parameters
        del self.geckodriver_path
        del self.headless
        del self.tor_access
        del self.tor_browser
        del self.browser_setting
        del self.addons
        del self.proxy
        del self.set_size

    # Class Public Fuctions -------

    def close_other_tabs(self) -> None:
        """
        Close other tabs
        Args:
            None
        Returns:
            None
        """
        if len(self.browser.window_handles) > 1:
            for tabs in reversed(self.browser.window_handles):
                if tabs == self.browser.window_handles[0]:
                    self.browser.switch_to.window(tabs)
                else:
                    self.browser.switch_to.window(tabs)
                    self.browser.close()

    def check_gip(self) -> str:
        """
        Get current global IP
        Args:
            None
        Returns:
            gip: global IP (str)
        """
        try:
            self.browser.get("http://checkip.amazonaws.com")
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
        except Exception:
            logging.info("Timeout to check IP")
            return ""

        gip = self.browser.find_element(By.TAG_NAME, "pre").text
        logging.info(f"Global ip: {gip}")
        return gip

    def recur_selenium_get(self, url: str) -> None:
        """
        Access web page recursively.
        Args:
            url: web page url (str)
        Returns:
            None
        """
        try:
            self.browser.get(url)
        except TimeoutException as e:
            logging.error(f"Timeout Error to access {url}. Retry ", e)
            self.recur_selenium_get(url)

    def recur_scroll_down(self, speed: int, start_height: int = 1) -> None:
        """
        Scroll down recursively until bottom of the page.
        Args:
            speed: it should be tuned, based on the bandwidth of the internet.
            start_height: start height value. it's 1 at the beginning.
        Returns:
            None
        """
        # get page height
        height = self.browser.execute_script("return document.body.scrollHeight")

        # scroll down slowly with loop
        for i in range(start_height, height, speed):
            self.browser.execute_script("window.scrollTo(0, " + str(i) + ");")

        # In case the rest of the page is dynamically loaded, execute this function recursively.
        new_height = self.browser.execute_script("return document.body.scrollHeight")
        if new_height - height > 0:
            self.recur_scroll_down(speed, height)
        else:
            return

    def close_selenium(self) -> None:
        """
        Close browser.
        Args:
            None
        Returns:
            None
        """
        self.browser.quit()
        time.sleep(1)
        del self.browser
        gc.collect()

    # Class Private Fuctions -------

    def _init_check(self) -> bool:
        """
        Check parameters at the initialization.
        Args:
            None
        Returns:
            init_check_result: True or False
        """
        if (
            len(self.geckodriver_path) == 0
            or len(self.browser_setting["browser_path"]) == 0
            or len(self.browser_setting["browser_profile"]) == 0
        ):
            # geckodriver_path and browser setting are mandatory.
            init_ok = False
        elif (len(self.addons["dir"]) == 0) ^ (len(self.addons["apps"]) == 0):
            # addons needs ["apps"] and ["dir"].
            init_ok = False
        else:
            init_ok = True
        return init_ok


class NotCorrectValueException(Exception):
    pass
