from bs4 import BeautifulSoup
import re
import requests


# Main method
def web_scrape(search_term):
    # User Agent List
    headers = ({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/87.0.4280.101 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US, en;q=0.9'
    })

    amazon_prices = _scrape_amazon(search_term, headers)
    ebay_prices = _scrape_ebay(search_term, headers)
    return amazon_prices + ebay_prices


# Method to coordinate retrieving information from Amazon page
def _scrape_amazon(search_term, headers):
    # Fetch the URL for Amazon
    formatted_search_term = _url_format(search_term)
    url = "https://www.amazon.co.uk/s?k=" + formatted_search_term + "&i=videogames"
    amazon_page = requests.get(url, headers=headers)

    # Create the object that will contain all the info in the URL
    soup = BeautifulSoup(amazon_page.content, features="lxml")

    # Get all prices on page, to find the lowest, highest and average
    # Setup default games object and empty list for game prices
    games = [{"seller": "Amazon", "price": "N/A", "price_with_postage": "N/A", "rating": "No ratings"}]
    relevant_games = list()

    key_terms = search_term.lower().split(" ")
    # Check search terms are present
    if key_terms:
        # Select the upper limit for relevant games on results page
        section_spans = soup.select("div.a-section.a-spacing-small.a-spacing-top-small span")
        if section_spans:
            results_line = section_spans[0].get_text().strip()
            number_of_results = int(re.findall(r"\d+", results_line)[-1])

            # Get each item on the results page that is not a sponsored item
            game_info = soup.select(
                'div[data-component-type="s-search-result"] div span > div.s-include-content-margin',
                limit=number_of_results)
            if game_info:
                # Iterate through all non-sponsored items and find each item whose title matches the keywords
                relevant_games = _find_relevant_games_amazon(game_info, key_terms, relevant_games)
            else:
                print("No games matching result")

        # Extract relevant information from game_prices
        if len(relevant_games) > 0:
            games = _find_lowest_games(relevant_games, "Amazon")

    return games


# Method to coordinate retrieving information from EBay page
def _scrape_ebay(search_term, headers):
    # EBay
    formatted_search_term = _url_format(search_term)

    url = "https://www.ebay.co.uk/sch/i.html?_nkw=" + formatted_search_term + "&_sacat=1249"
    ebay_page = requests.get(url, headers=headers)

    # Create the object that will contain all the info in the URL
    soup = BeautifulSoup(ebay_page.content, features="lxml")

    # Get all products containing the parts of the search term
    # Setup default games object and empty list for game prices
    games = [{"seller": "EBay", "price": "N/A", "price_with_postage": "N/A", "rating": "No ratings"}]
    relevant_games = list()

    # Check if any products are returned and that key_terms are present
    all_products = soup.select('.srp-results .s-item')
    if all_products:
        key_terms = search_term.lower().split(" ")
        if key_terms:
            # Iterate through all products to find those with titles containing all key terms
            relevant_games = _find_relevant_games_ebay(all_products, key_terms, relevant_games)

            # If there is at least one price in relevant_product_prices find the lowest and return
            if len(relevant_games) > 0:
                games = _find_lowest_games(relevant_games, "EBay")
            else:
                print("No relevant products found")
        else:
            print("Search terms invalid")
    else:
        print("No products found for search term")

    return games

    #
    # # Review score
    # review_score_element = soup.select('.a-star-4-5')[0].get_text().split(' ')[0]
    # review_score_stripped = review_score_element.replace(",", ".")
    # review_score = float(review_score_stripped)
    # print("Review Score: ", review_score)
    #
    # # Review count
    # review_count_element = soup.select('#acrCustomerReviewText')[0].get_text().split(' ')[0]
    # review_count_stripped = review_count_element.replace(".", "")
    # review_count = int(review_count_stripped)
    # print("Review Count: ", review_count)
    #
    # # Check if the product is Out of Stock
    # try:
    #     soup.select('#availability .a-color-state')[0].get_text().strip()
    #     stock = 'Out of Stock'
    # except:
    #     stock = 'Available'
    # print(stock)


# Amazon-specific methods

# Finds games matching key_terms on Amazon page
def _find_relevant_games_amazon(game_info, key_terms, relevant_games):
    for game in game_info:
        product_title = game.find("span", {"class": "a-size-medium"}).get_text().strip().lower()
        if _contains_all_terms(product_title, key_terms):
            # Get prices for each of these items
            price_list = game.find_all("span", attrs={'class': 'a-price-whole'})
            if price_list:
                for price_object in price_list:
                    base_price = _get_product_price_amazon(price_object)
                    price_with_postage = _get_postage_price_amazon(price_object, base_price)
                    rating = _get_rating_amazon(price_object)

                    relevant_games.append({
                        "base_price": base_price,
                        "price_with_postage": price_with_postage,
                        "rating": rating
                    })
            else:
                print("No price for item")
    return relevant_games


# Gets the price for a specific item on Amazon
def _get_product_price_amazon(price_object):
    price_whole = str(price_object.get_text().strip())
    price_fraction = str(price_object.find_next_sibling("span", attrs={'class': 'a-price-fraction'}).get_text().strip())
    return float(price_whole + price_fraction)


# Gets the postage price for a specific item on Amazon
def _get_postage_price_amazon(price_object, base_price):
    postage_section = price_object.find_parent("div", class_="a-section").find_next_sibling("div")
    if postage_section:
        # Checks for 'delivery' keyword, but 'd' may be upper or lowercase. Not a typo.
        postage = postage_section.select('span[aria-label*="elivery"] span')
        if postage:
            postage_price = re.findall(r"[\d, .]+", postage[0].get_text())[-1]
            try:
                return base_price + float(postage_price)
            except ValueError:
                return base_price
    return base_price


# Gets the rating for a specific item on Amazon
def _get_rating_amazon(price_object):
    rating_section = price_object.find_parent("div", class_="sg-row").find_previous_sibling("div")
    if rating_section:
        try:
            # Checks for 'stars' keyword
            rating = rating_section.select('span[aria-label*="stars"] span.a-icon-alt')[0].get_text().strip()
            return rating
        except ValueError:
            return "No rating"
    return "No rating"


# EBay-specific methods

# Finds games matching key_terms on EBay page
def _find_relevant_games_ebay(all_products, key_terms, relevant_games):
    for product in all_products:
        product_title = product.find("h3", {"class": "s-item__title"}).get_text().strip().lower()
        if _contains_all_terms(product_title, key_terms):
            prices = product.find_all("span", {"class", "s-item__price"})
            for price_object in prices:
                # Get base price and price + postage for each of these products
                base_price = float(re.findall(r"[\d, .]+", price_object.get_text())[-1])
                price_with_postage = _get_postage_price_ebay(price_object, base_price)
                rating = _get_rating_ebay(price_object)

                relevant_games.append({
                    "base_price": base_price,
                    "price_with_postage": price_with_postage,
                    "rating": rating
                })
    return relevant_games


# Gets the postage price for a specific item on EBay
def _get_postage_price_ebay(price_object, product_price):
    postage_section = price_object.find_parent("div", class_="s-item__info").find(
        "span", {"class": "s-item__shipping"})
    postage_price = re.findall(r"[\d, .]+", postage_section.get_text())[-1]
    try:
        price_with_postage = product_price + float(postage_price)
    except ValueError:
        price_with_postage = product_price
    return price_with_postage


# Gets the rating for a specific item on EBay
def _get_rating_ebay(price_object):
    rating_section = price_object.find_parent("div", class_="s-item__info").select(
        "div.s-item__reviews div.x-star-rating span.clipped")
    if rating_section:
        try:
            rating = rating_section[0].get_text().strip()
            return rating
        except ValueError:
            return "No ratings"
    return "No ratings"


# Helper Methods

# Checks that all terms are present in the product name
def _contains_all_terms(product, key_terms):
    for term in key_terms:
        if not product.__contains__(term):
            return False
    return True


# Finds games with lowest base_price and price_with_postage respectively
def _find_lowest_games(relevant_games, seller):
    lowest_by_base_price = _find_element_with_lowest_value_for_attribute(relevant_games, 'base_price')
    lowest_by_price_with_postage = _find_element_with_lowest_value_for_attribute(
        relevant_games, 'price_with_postage')
    games = [
        {
            "seller": seller,
            "price": lowest_by_base_price['base_price'],
            "price_with_postage": lowest_by_base_price['price_with_postage'],
            "rating": lowest_by_base_price['rating']
        },
        {
            "seller": seller,
            "price": lowest_by_price_with_postage['base_price'],
            "price_with_postage": lowest_by_price_with_postage['price_with_postage'],
            "rating": lowest_by_price_with_postage['rating']
        }
    ]
    return games


# Finds game with lowest value for specified attribute
def _find_element_with_lowest_value_for_attribute(collection, attribute):
    lowest_element = collection[0]
    for i in range(len(collection)):
        if lowest_element[attribute] > collection[i][attribute]:
            lowest_element = collection[i]
    return lowest_element


# Formats search term to be usable in URL
def _url_format(term):
    return term.replace(" ", "+")
