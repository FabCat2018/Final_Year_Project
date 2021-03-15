from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.expected_conditions import _find_element
from selenium.webdriver.support.wait import WebDriverWait
import numpy as np
import os
import unittest

from .user_item_matrix_creator import build_user_item_matrix
from .matrix_factorisation import _get_item_rating_predictions as mf
from .user_based_collaborative_filtering import _normalisation, _score_items_for_target_user_cf as cf


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


class RecommenderSystemTests(unittest.TestCase):

    def setUp(self):
        self.target_item = "B003ZSP0WW"     # Item rated by most users in DB
        self.user_item_matrix = build_user_item_matrix(self.target_item)
        self.test_users = self._get_test_user_ids(self.user_item_matrix, 5)

    def test_recommender_systems_for_each_user(self):
        test_users = self.test_users
        user_texts = ["Very low", "Low", "Medium", "High", "Very high"]
        for i in range(len(self.test_users)):
            self._compare_recommender_systems(test_users[i], self.target_item, self.user_item_matrix, user_texts[i])

    # region Private Functions

    # Retrieve num_users which are evenly spaced throughout all users sorted by number of unrated items,
    # i.e. first in result has least rated items
    @staticmethod
    def _get_test_user_ids(user_item_matrix, num_users):
        unrated_items_for_users = user_item_matrix[user_item_matrix == 0].count(axis=0)
        sorted_unrated_items_for_users = unrated_items_for_users.nlargest(len(user_item_matrix.columns), 'first')\
            .index.values
        evenly_spaced_indices = np.linspace(0, len(sorted_unrated_items_for_users)-1, num_users)
        return sorted_unrated_items_for_users[np.round(evenly_spaced_indices).astype(int)]

    # Compare results of recommender systems for user with many ratings
    @staticmethod
    def _compare_recommender_systems(test_user, target_item, user_item_matrix, user_text):
        user_item_matrix = user_item_matrix.copy()

        # Get adjusted user_item_matrix rating for CF comparison
        adjusted_target_item_rating = _normalisation(user_item_matrix).loc[target_item].loc[test_user]

        # Remove and store rating for test_user and target_item
        original_rating = user_item_matrix.loc[target_item].loc[test_user]
        user_item_matrix.loc[target_item].loc[test_user] = 0

        # Get predictions for rating
        mf_rating_prediction = mf(user_item_matrix).loc[target_item].loc[test_user]
        cf_rating_prediction = cf(user_item_matrix, test_user).transpose().loc[target_item][0]

        print(user_text, " rating user")
        print("Actual: ", original_rating, "\tMF Prediction: ", mf_rating_prediction, "\tDifference: ",
              abs(original_rating - mf_rating_prediction))
        print("Adjusted item rating: ", adjusted_target_item_rating, "\tCF Prediction: ", cf_rating_prediction,
              "\tDifference: ", abs(adjusted_target_item_rating - cf_rating_prediction))
        print("\n")

    # @staticmethod
    # def _get_item_count_for_users():
    #     cursor = DatabaseConnector.setup_db_connection()
    #     get_item_count_for_users_query = """
    #         SELECT [user_id], COUNT(*) [item_id]
    #         FROM [Final Year Project].[dbo].[Amazon_Video_Games_Ratings_Subset]
    #         GROUP BY [user_id]
    #         ORDER BY [item_id] DESC
    #     """
    #     cursor.execute(get_item_count_for_users_query)
    #
    #     user_item_count_list = list()
    #     for row in cursor.fetchall():
    #         user_item_count_list.append({"user_id": row.user_id, "item_count": row.item_id})
    #
    #     test_users = list()
    #     test_users.append(user_item_count_list[0]["user_id"])
    #     return user_item_count_list

    # endregion
