import unittest
import selenium_helper


class TestWebAccess(unittest.TestCase):
    def test_web_access(self):
        brsr = selenium_helper.SeleniumBrowser(gekodriver_path)
        test_gip = brsr.check_gip()
        self.assertGreater(len(test_gip), 0)


if __name__ == "__main__":
    unittest.main()
