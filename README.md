# selenium_helper
This is a module to support to use a selenium with several functions.

## How to install
You can install this program as python a package with the following operation.
* https:
```
pip install git+https://github.com/toshi01kudo/selenium_helper.git
```
* ssh:
```
pip install git+ssh://git@github.com:toshi01kudo/selenium_helper.git
```

Or, you can get this repogitory with `git clone`, like the usual git operation.

## How to use
You need to specify several parameters.
```
from selenium_helper import SeleniumBrowser
geckodriver_path = r'input geckodriver's path here.'
firefox_binary_path = r"input your firefox.exe's path"
firefox_profile_path = r"input your firefox profiles's path"
brsr = SeleniumBrowser(geckodriver_path = geckodriver_path, browser_setting = {"browser_path": firefox_binary_path, "browser_profile": firefox_profile_path})
```
* geckodriver_path: You need to specify geckodriver path. (You need to install geckodriver before use this module.)
* headless: Use headless mode (bool), default = True
* tor_access: Use Tor (bool), default = False
* tor_browser: Use Tor browser (bool), default = False
* browser_setting: Browser setting (dict), default = {"browser_path": "", "browser_profile": ""}
* addons: Use installed addons (dict), default = {"dir": "", "apps": []}
* proxy: Use proxy server (dict), default = {"ip": "", "port": ""}
* set_size: set windows size as (900, 500) (bool), default = false

## Functions
* `pdoc3` automatically creates Github Pages, see: https://toshi01kudo.github.io/selenium_helper/ 

* close_other_tabs: close other tabs.
* check_gip: check current Global IP with AWS function.
* recur_selenium_get: access web page recursively until a page can be loaded successfully.
* recur_scroll_down: scroll down to bottom.
* close_selenium: close the selenium browser.


## References
* [Pythonで自分だけのクソライブラリを作る方法](https://zenn.dev/karaage0703/articles/db8c663640c68b) (Japanese)
* [GitHubリポジトリのブランチを指定して pip install する](https://qiita.com/tshimura/items/8ee857b7caf253736a81) (Japanese)
* [Use Service for executable_path from Selenium4](https://qiita.com/yagaodekawasu/items/5813a8cb4c3d73386e7a) (Japanese)
* [Scroll down recursively until bottom of the page](https://yuyuublog.com/seleniumscroll/) (Japanese)
