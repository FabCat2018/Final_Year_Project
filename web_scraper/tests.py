from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.expected_conditions import _find_element
from selenium.webdriver.support.wait import WebDriverWait
import numpy as np
import os
import unittest

from .user_item_matrix_creator import build_user_item_matrix
from .matrix_factorisation import _get_item_rating_predictions, _predict_item_ratings,\
    _recommend_top_7_items_for_target_user
from .user_based_collaborative_filtering import _normalisation, _recommend_top_7_items_for_users,\
    _score_items_for_target_user_cf


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
        self.driver = Chrome(os.path.join(os.environ['HOMEPATH'], 'Desktop/FYP Web Drivers/chromedriver.exe'))
        self.driver.maximize_window()
        self.driver.get("http://127.0.0.1:8000/")

    def tearDown(self):
        self.driver.close()

    # endregion

    # region Search By Keyword Tests

    def test_SearchByKeyword_WithOneRecommendation_OneRecommendationDisplayed(self):
        driver = self.driver

        # Enter search term
        driver.find_element_by_css_selector("#search-term").send_keys("Beautiful Katamari (Xbox 360)")
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
        driver.find_element_by_css_selector("#search-term").send_keys("Beautiful Katamari (Xbox 360)")
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
        driver.find_element_by_css_selector("#search-term").send_keys("Mystic Legacy: The Great Ring (PC CD)")
        driver.find_element_by_css_selector("#search-button").click()

        price_table_element = driver.find_element_by_css_selector("#price-table")
        WebDriverWait(driver, 20).until(expected_conditions.visibility_of(price_table_element))

        # Check price entries
        assert len(price_table_element.find_elements_by_css_selector("tr")) >= 3

        # Check recommendation entries
        recommendations = driver.find_elements_by_css_selector(".recommendation")
        assert len(recommendations) == 1

        # Click recommendation
        previous_recommendation_text = recommendations[0].text
        driver.find_element_by_css_selector(".recommendation").click()
        WebDriverWait(driver, 500).until(text_to_change(
            (By.CSS_SELECTOR, ".recommendation"), previous_recommendation_text))

        # Check prices and recommendations for new item
        assert len(price_table_element.find_elements_by_css_selector("tr")) >= 3
        assert len(driver.find_elements_by_css_selector(".recommendation")) >= 1

    # endregion


class RecommenderSystemTests(unittest.TestCase):

    def setUp(self):
        self.target_item = "B003ZSP0WW"     # Item rated by most users in DB
        self.user_item_matrix = build_user_item_matrix(self.target_item)
        self.test_users = self._get_test_user_ids(self.user_item_matrix, 5)
        self.test_iterations = 3

    def test_recommender_systems_for_each_user(self):
        test_users = self.test_users
        user_texts = ["Very low", "Low", "Medium", "High", "Very high"]
        for i in range(len(self.test_users)):
            self._compare_recommender_systems(test_users[i], self.target_item, self.user_item_matrix, user_texts[i],
                                              self.test_iterations)

    def test_mf_optimisations(self):
        user_item_matrix = self.user_item_matrix.copy()
        latent_dimensions = 2
        learning_rate = 0.1
        regularisation_parameter = 0.01
        iterations = 30
        error = "mse"

        for user in self.test_users:
            # Remove and store rating for test_user and target_item
            original_rating = user_item_matrix.loc[self.target_item].loc[user]
            user_item_matrix.loc[self.target_item].loc[user] = 0

            print("\nUser: ", user, "\tOriginal Rating: ", original_rating)

            # Get predictions for target_item with differing values for MF

            # Across first five users, only latent dimension of 2 returns values

            for i in range(5):
                dimensions = latent_dimensions + i
                mf_rating_prediction = _predict_item_ratings(user_item_matrix, dimensions, learning_rate,
                                                             regularisation_parameter, iterations, error).\
                    loc[self.target_item].loc[user]
                print(dimensions, " latent dimensions", "\tMF Rating Prediction: ", mf_rating_prediction,
                      "\tDifference: ", abs(original_rating - mf_rating_prediction))

            print()

            # Learning rate of 0.1 performs best out of first attempts

            for i in range(5):
                rate = learning_rate * i
                mf_rating_prediction = _predict_item_ratings(user_item_matrix, latent_dimensions, rate,
                                                             regularisation_parameter, iterations, error).\
                    loc[self.target_item].loc[user]
                print("Learning rate: ", rate, "\tMF Rating Prediction: ", mf_rating_prediction, "\tDifference: ",
                      abs(original_rating - mf_rating_prediction))

            print()

            # Regularisation parameter of 0.02 performs best overall

            for i in range(5):
                regularisation = regularisation_parameter * i
                mf_rating_prediction = _predict_item_ratings(user_item_matrix, latent_dimensions, learning_rate,
                                                             regularisation, iterations, error).loc[self.target_item].\
                    loc[user]
                print("Regularisation parameter: ", regularisation, "\tMF Rating Prediction: ", mf_rating_prediction,
                      "\tDifference: ", abs(original_rating - mf_rating_prediction))

            print()

            # Values between 32 and 34 perform best for iterations, but will check 20 to 39

            for i in range(5):
                new_iterations = iterations + (i * 2)
                mf_rating_prediction = _predict_item_ratings(user_item_matrix, latent_dimensions, learning_rate,
                                                             regularisation_parameter, new_iterations, error).\
                    loc[self.target_item].loc[user]
                print("Iterations: ", new_iterations, "\tMF Rating Prediction: ", mf_rating_prediction,
                      "\tDifference: ", abs(original_rating - mf_rating_prediction))

            print()

            # Exactly 0.1 for learning rate gives most accurate predictions

            for i in range(10):
                new_learning_rate = 0.1 + (i / 100)
                mf_rating_prediction = _predict_item_ratings(user_item_matrix, latent_dimensions, new_learning_rate,
                                                             regularisation_parameter, iterations, error).\
                    loc[self.target_item].loc[user]
                print("Learning Rate: ", new_learning_rate, "\tMF Rating Prediction: ", mf_rating_prediction,
                      "\tDifference: ", abs(original_rating - mf_rating_prediction))

            print()

            # Results are: 21, 26, 32, 37, 21. Mean is 27, so will use 27 iterations.

            for i in range(20):
                new_iterations = 20 + i
                mf_rating_prediction = _predict_item_ratings(user_item_matrix, latent_dimensions, learning_rate,
                                                             regularisation_parameter, new_iterations, error).\
                    loc[self.target_item].loc[user]
                print("Iterations: ", new_iterations, "\tMF Rating Prediction: ", mf_rating_prediction,
                      "\tDifference: ", abs(original_rating - mf_rating_prediction))

            print()

            #  RMSE appears to perform better overall

            for i in range(3):
                mf_rating_prediction = _predict_item_ratings(user_item_matrix, latent_dimensions, learning_rate,
                                                             regularisation_parameter, iterations, error).\
                    loc[self.target_item].loc[user]
                print("MSE \tMF Rating Prediction: ", mf_rating_prediction,
                      "\tDifference: ", abs(original_rating - mf_rating_prediction))

            print()

            for i in range(3):
                error = "rmse"
                mf_rating_prediction = _predict_item_ratings(user_item_matrix, latent_dimensions, learning_rate,
                                                             regularisation_parameter, iterations, error).\
                    loc[self.target_item].loc[user]
                print("RMSE\tMF Rating Prediction: ", mf_rating_prediction,
                      "\tDifference: ", abs(original_rating - mf_rating_prediction))

            print()

    def test_recommendations_for_similar_users(self):
        test_users = self.test_users
        user_texts = ["Very low", "Low", "Medium", "High", "Very high"]
        for i in range(len(self.test_users)):
            self._compare_recommendations_for_similar_users(test_users[i], self.target_item, self.user_item_matrix,
                                                            user_texts[i], self.test_iterations)

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

    # Compare results of recommender systems for user with different numbers of ratings
    @staticmethod
    def _compare_recommender_systems(test_user, target_item, user_item_matrix, user_text, test_iterations):
        user_item_matrix = user_item_matrix.copy()

        # Get adjusted user_item_matrix rating for CF comparison
        adjusted_target_item_rating = _normalisation(user_item_matrix).loc[target_item].loc[test_user]

        # Remove and store rating for test_user and target_item
        original_rating = user_item_matrix.loc[target_item].loc[test_user]
        user_item_matrix.loc[target_item].loc[test_user] = 0

        for i in range(test_iterations):
            # Get predictions for rating
            mf_rating_prediction = _get_item_rating_predictions(user_item_matrix, "rmse").loc[target_item].loc[test_user]
            cf_rating_prediction = _score_items_for_target_user_cf(user_item_matrix, test_user).transpose().\
                loc[target_item][0]

            print("\n", user_text, " rating user")
            print("Actual: ", original_rating, "\tMF Prediction: ", mf_rating_prediction, "\tDifference: ",
                  abs(original_rating - mf_rating_prediction))
            print("Adjusted item rating: ", adjusted_target_item_rating, "\tCF Prediction: ", cf_rating_prediction,
                  "\tDifference: ", abs(adjusted_target_item_rating - cf_rating_prediction))
            print("\n")

    # Compare recommendations for two similar users for users with different numbers of ratings
    @staticmethod
    def _compare_recommendations_for_similar_users(test_user, target_item, user_item_matrix, user_text, test_iterations):
        print("\n", user_text, " rating user")

        for i in range(test_iterations):
            print("Matrix Factorisation")
            user_item_matrix = user_item_matrix.copy()

            similarity_matrix = user_item_matrix.corr(method="pearson")
            all_similar_users = similarity_matrix.drop([test_user], axis=0)
            similar_user = all_similar_users.nlargest(1, [test_user]).index.values[0]

            predicted_user_item_matrix = _get_item_rating_predictions(user_item_matrix, "mse")
            test_user_recommendations = _recommend_top_7_items_for_target_user(predicted_user_item_matrix, test_user,
                                                                               target_item)
            print("Test User: ", test_user, "\tRecommendations: ", test_user_recommendations)

            similar_user_recommendations = _recommend_top_7_items_for_target_user(predicted_user_item_matrix, similar_user,
                                                                                  target_item)
            print("Similar User: ", similar_user, "\tRecommendations: ", similar_user_recommendations)

            exclusive_to_test_user = list(set(test_user_recommendations)-set(similar_user_recommendations))
            exclusive_to_similar_user = list(set(similar_user_recommendations)-set(test_user_recommendations))
            print("Exclusive to Test User: ", exclusive_to_test_user)
            print("Exclusive to Similar User: ", exclusive_to_similar_user)
            print()

            print("Collaborative Filtering")
            test_user_recommendations = _recommend_top_7_items_for_users(user_item_matrix, test_user)
            print("Test User: ", test_user, "\tRecommendations: ", test_user_recommendations)

            similar_user_recommendations = _recommend_top_7_items_for_users(user_item_matrix, similar_user)
            print("Similar User: ", similar_user, "\tRecommendations: ", similar_user_recommendations)

            exclusive_to_test_user = list(set(test_user_recommendations) - set(similar_user_recommendations))
            exclusive_to_similar_user = list(set(similar_user_recommendations) - set(test_user_recommendations))
            print("Exclusive to Test User: ", exclusive_to_test_user)
            print("Exclusive to Similar User: ", exclusive_to_similar_user)
            print()
            print()

    # endregion
