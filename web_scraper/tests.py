from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.expected_conditions import _find_element
from selenium.webdriver.support.wait import WebDriverWait
import os
import unittest


# region Nested Class
class text_to_change(object):
    def __init__(self, locator, text_):
        self.locator = locator
        self.text = text_

    def __call__(self, driver):
        actual_text = _find_element(driver, self.locator).text
        return actual_text != self.text

# endregion


class ProjectTests(unittest.TestCase):
    # region Setup and Teardown Methods

    # Open browser
    def setUp(self):
        self.driver = Chrome(os.path.join(os.environ['HOMEPATH'], 'Desktop/chromedriver.exe'))
        # self.driver.implicitly_wait(5)
        self.driver.maximize_window()
        self.driver.get("http://127.0.0.1:8000/")

    def tearDown(self):
        self.driver.close()

    # endregion

    # region Search By Keyword Tests

    def test_SearchByKeyword_WithOneRecommendation_OneRecommendationDisplayed(self):
        driver = self.driver

        # Enter search term
        driver.find_element_by_css_selector("#search-term").send_keys("Hexic Deluxe")
        driver.find_element_by_css_selector("#search-button").click()

        price_table_element = driver.find_element_by_css_selector("#price-table")
        WebDriverWait(driver, 20).until(expected_conditions.visibility_of(price_table_element))

        # Check price entries
        assert len(price_table_element.find_elements_by_css_selector("tr")) >= 3

        # Check recommendation entries
        assert len(driver.find_elements_by_css_selector(".recommendation")) == 1

    def test_SearchByKeyword_NoRecommendations_NoRecommendationsDisplayed(self):
        driver = self.driver

        # Enter search term
        driver.find_element_by_css_selector("#search-term").send_keys("Spiderman Miles Morales")
        driver.find_element_by_css_selector("#search-button").click()

        price_table_element = driver.find_element_by_css_selector("#price-table")
        WebDriverWait(driver, 20).until(expected_conditions.visibility_of(price_table_element))

        # Check price entries
        assert len(price_table_element.find_elements_by_css_selector("tr")) >= 3

        # Check recommendation entries
        assert len(driver.find_elements_by_css_selector(".recommendation")) == 0

    def test_SearchByKeyword_ManyRecommendations_ManyRecommendationsDisplayed(self):
        driver = self.driver

        # Enter search term
        driver.find_element_by_css_selector("#search-term").send_keys("Amalur PC")
        driver.find_element_by_css_selector("#search-button").click()

        price_table_element = driver.find_element_by_css_selector("#price-table")
        WebDriverWait(driver, 20).until(expected_conditions.visibility_of(price_table_element))

        # Check price entries
        assert len(price_table_element.find_elements_by_css_selector("tr")) >= 3

        # Check recommendation entries
        assert len(driver.find_elements_by_css_selector(".recommendation")) == 7

    # endregion

    # region Search from Suggestion Tests

    def test_SearchFromSuggestion_WithOneRecommendation_OneRecommendationDisplayed(self):
        driver = self.driver

        # Enter search term
        driver.find_element_by_css_selector("#search-term").send_keys("Hexic")
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, ".ui-menu-item div"))).click()

        price_table_element = driver.find_element_by_css_selector("#price-table")
        WebDriverWait(driver, 20).until(expected_conditions.visibility_of(price_table_element))

        # Check price entries
        assert len(price_table_element.find_elements_by_css_selector("tr")) >= 3

        # Check recommendation entries
        assert len(driver.find_elements_by_css_selector(".recommendation")) == 1

    def test_SearchFromSuggestion_NoRecommendations_NoRecommendationsDisplayed(self):
        driver = self.driver

        # Enter search term
        driver.find_element_by_css_selector("#search-term").send_keys("Spiderman Miles Morales")
        driver.find_element_by_css_selector("#search-button").click()

        price_table_element = driver.find_element_by_css_selector("#price-table")
        WebDriverWait(driver, 20).until(expected_conditions.visibility_of(price_table_element))

        # Check price entries
        assert len(price_table_element.find_elements_by_css_selector("tr")) >= 3

        # Check recommendation entries
        assert len(driver.find_elements_by_css_selector(".recommendation")) == 0

    def test_SearchFromSuggestion_ManyRecommendations_ManyRecommendationsDisplayed(self):
        driver = self.driver

        # Enter search term
        driver.find_element_by_css_selector("#search-term").send_keys("Amal")
        WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, ".ui-menu-item div")))
        driver.find_elements_by_css_selector(".ui-menu-item div")[1].click()

        price_table_element = driver.find_element_by_css_selector("#price-table")
        WebDriverWait(driver, 20).until(expected_conditions.visibility_of(price_table_element))

        # Check price entries
        assert len(price_table_element.find_elements_by_css_selector("tr")) >= 3

        # Check recommendation entries
        assert len(driver.find_elements_by_css_selector(".recommendation")) == 7

    # endregion

    # region Search from Recommendation Tests

    def test_SearchFromRecommendation_WithOneRecommendation_OneRecommendationDisplayed(self):
        driver = self.driver

        # Enter search term
        driver.find_element_by_css_selector("#search-term").send_keys("Hexic Deluxe")
        driver.find_element_by_css_selector("#search-button").click()

        price_table_element = driver.find_element_by_css_selector("#price-table")
        WebDriverWait(driver, 20).until(expected_conditions.visibility_of(price_table_element))

        # Check price entries
        assert len(price_table_element.find_elements_by_css_selector("tr")) >= 3

        # Check recommendation entries
        recommendations = driver.find_elements_by_css_selector(".recommendation")
        assert len(recommendations) == 1

        # Click recommendation
        driver.find_element_by_css_selector(".recommendation").click()
        WebDriverWait(driver, 500).until(text_to_change(
            (By.CSS_SELECTOR, ".recommendation"), recommendations[0].text))

        # Check prices and recommendations for new item
        assert len(price_table_element.find_elements_by_css_selector("tr")) >= 3
        assert len(driver.find_elements_by_css_selector(".recommendation")) >= 1

    # endregion
