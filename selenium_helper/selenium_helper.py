# imports ------------------
import time
import logging
import gc
import requests
from requests.exceptions import RequestException, ConnectionError, HTTPError, Timeout
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import *
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox import service as fs
from selenium.common.exceptions import TimeoutException

# Functions ------------------

# Private Functions ------------------

# Class ------------------


class SeleniumBrowser:
    """
    Selenium を便利に使うクラス
    """

    def __init__(
        self,
        geckodriver_path: str,
        headless: bool = True,
        tor_access: bool = False,
        tor_browser: bool = False,
        tor_setting: dict = {"tor_browser": "", "tor_profile": ""},
        addons: dict = {"dir": "", "apps": []},
        proxy: dict = {"ip": "", "port": ""},
        set_size: bool = False,
    ) -> None:
        """
        class function for selenium browser
        Args:
            geckodriver_path: geckodriver's path
            headless: Use headless mode (bool), default = True
            tor_access: Use Tor (bool), default = False
            tor_browser: Use Tor browser (bool), default = False
            tor_setting: Tor browser setting (dict), default = {"tor_browser": "", "tor_profile": ""}
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
        self.tor_setting = tor_setting
        self.addons = addons
        self.proxy = proxy
        self.set_size = set_size
        # initial check
        init_ok = self._init_check()
        if not init_ok:
            raise NotCorrectValueException
        # Firefoxのヘッドレスモードを有効にするための Option
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        # Selenium4からServiceオブジェクトにexecutable_pathを渡し、そのServiceオブジェクトを渡す必要があります。
        # https://qiita.com/yagaodekawasu/items/5813a8cb4c3d73386e7a
        firefox_servie = fs.Service(executable_path=geckodriver_path)

        if tor_access and tor_browser:
            # 現在はTorの自動接続が上手く動作していない
            # Torで起動する場合
            proxyHost = "127.0.0.1"
            proxyPort = 9150

            binary = FirefoxBinary(tor_setting["tor_browser"])
            fp = webdriver.FirefoxProfile(tor_setting["tor_profile"])
            # fp.set_preference('extensions.torlauncher.start_tor',True)
            fp.set_preference("network.proxy.type", 1)
            fp.set_preference("network.proxy.socks", proxyHost)  # SOCKS PROXY
            fp.set_preference("network.proxy.socks_port", proxyPort)
            fp.set_preference("network.proxy.socks_remote_dns", False)
            fp.update_preferences()

            # selenium用ブラウザ
            self.browser = webdriver.Firefox(firefox_binary=binary, firefox_profile=fp, options=options)

        elif tor_access:
            # Tor 経由でサイトへアクセス
            # Tor へ Proxy アクセス
            """事前に Tor Browser で Tor にアクセスしていないと利用不可のため注意"""
            proxyHost = "127.0.0.1"
            proxyPort = 9150
            fp = webdriver.FirefoxProfile()
            fp.set_preference("network.proxy.type", 1)
            fp.set_preference("network.proxy.socks", proxyHost)  # SOCKS PROXY
            fp.set_preference("network.proxy.socks_port", proxyPort)
            fp.update_preferences()

            # selenium用ブラウザ
            self.browser = webdriver.Firefox(service=firefox_servie, firefox_profile=fp, options=options)

        elif len(proxy["ip"]) > 0 and len(proxy["port"]) > 0:
            proxyHost = proxy["ip"]
            proxyPort = proxy["port"]
            fp = webdriver.FirefoxProfile()
            fp.set_preference("network.proxy.type", 1)
            fp.set_preference("network.proxy.http", proxyHost)
            fp.set_preference("network.proxy.http_port", proxyPort)
            fp.set_preference("network.proxy.ssl", proxyHost)  # SSL PROXY
            fp.set_preference("network.proxy.ssl_port", proxyPort)
            fp.update_preferences()

            # selenium用ブラウザ
            self.browser = webdriver.Firefox(service=firefox_servie, firefox_profile=fp, options=options)

        else:
            # 通常の Selenium 起動
            # selenium用ブラウザ
            self.browser = webdriver.Firefox(service=firefox_servie, options=options)

        if len(addons["dir"]) > 0 and len(addons["apps"]) > 0:
            # 拡張機能
            extensions_dir = addons["dir"]
            extensions = addons["apps"]
            for extension in extensions:
                self.browser.install_addon(extensions_dir + extension, temporary=True)

        self.browser.implicitly_wait(10)  # 暗黙のタイムアウト時間 (秒)

        # 他のタブが開いていたらクローズ
        time.sleep(1)
        self.close_other_tabs()

        if set_size:
            # ブラウザ位置・サイズ調整
            self.browser.set_window_position(0, 0)
            self.browser.set_window_size(900, 500)

        # delete parameters
        del self.geckodriver_path
        del self.headless
        del self.tor_access
        del self.tor_browser
        del self.tor_setting
        del self.addons
        del self.proxy
        del self.set_size

    # Class Public Fuctions -------

    def close_other_tabs(self) -> None:
        """
        close other tabs
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
        get current global IP
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
        access web page recursively.
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
        original: https://yuyuublog.com/seleniumscroll/
        Args:
            speed: it should be tuned, based on the bandwidth of the internet.
            start_height: start height value. it's 1 at the beginning.
        Returns:
            None
        """
        # ページの高さを取得
        height = self.browser.execute_script("return document.body.scrollHeight")

        # ループ処理で少しづつ移動
        for i in range(start_height, height, speed):
            self.browser.execute_script("window.scrollTo(0, " + str(i) + ");")

        # ページが動的に更新され、高さ情報が増加する場合、再帰的にスクロール
        new_height = self.browser.execute_script("return document.body.scrollHeight")
        if new_height - height > 0:
            self.recur_scroll_down(speed, height)
        else:
            return

    def close_selenium(self) -> None:
        """
        close browser.
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
        if len(self.geckodriver_path) == 0:
            # geckodriver_path の指定は必須
            init_ok = False
        elif (
            self.tor_browser
            and (len(self.tor_setting["tor_browser"]) == 0 or len(self.tor_setting["tor_profile"])) == 0
        ):
            # tor_browser 使用時には tor_setting が必須
            init_ok = False
        elif (len(self.proxy["ip"]) == 0) ^ (len(self.proxy["port"]) == 0):
            # proxy を使用するなら、ipとport指定が必要
            init_ok = False
        elif (len(self.addons["dir"]) == 0) ^ (len(self.addons["apps"]) == 0):
            # addons を使用するなら ["apps"],["dir"] 必須
            init_ok = False
        else:
            init_ok = True
        return init_ok


class NotCorrectValueException(Exception):
    pass
