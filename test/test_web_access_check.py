import unittest
import os
import selenium_helper


class TestWebAccess(unittest.TestCase):
    def test_web_access(self):
        github_gekodriver_path = os.path.join("opt", "hostedtoolcache", "geckodriver", "0.33.0", "x64", "geckodriver")
        brsr = selenium_helper.SeleniumBrowser(github_gekodriver_path)
        test_gip = brsr.check_gip()
        self.assertGreater(len(test_gip), 0)


if __name__ == "__main__":
    unittest.main()
