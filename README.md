**Index of Files Included**
* Source Code Files:
    * myapp
    * web_scraper
    * .gitignore
    * db.sqlite3
    * manage.py
    * requirements.txt
* Web App Architecture Diagram
* Web App Wireframe Design
* Original dataset used for recommender system: Amazon_Video_Games_Ratings.csv

***Source code can also be accessed at***: https://github.com/FabCat2018/Final_Year_Project

***As the system is an un-deployed web app, follow the instructions below to run the system***

**How to Setup the Project**
* Extract the ZIP file's inner folder to the desired location
* (Optional) Create a virtual Python environment
    * Install Anaconda (https://docs.anaconda.com/anaconda/install/)
    * Run the following commands in the folder directly containing manage.py using the Anaconda shell:
        * `conda create --name <name> python=3.7`
        * `conda activate <name>`

**How to Run the Project**

* *First time running the project*: Run the following commands using the shell in the folder the content was extracted into:
    * `pip install --upgrade pip`
    * `pip install --user -r requirements.txt`
* Run the following command to start the local server: `python manage.py runserver`
* Open a Chrome browser and insert the following URL into the URL bar: 127.0.0.1:8000
* Search for a game as desired using the search-bar

**How to Run the Test Suite**

* **WARNING**: These tests took around 3 hours to run during development. Run only if bored for three hours.
* Ensure that the server is already running by using the command indicated above: `python manage.py runserver`
* Follow the instructions at
https://zwbetz.com/download-chromedriver-binary-and-add-to-your-path-for-automated-functional-testing/
to setup the webdriver used for testing.
    * **Make sure the driver matches the version of Chrome your PC uses.**
* Open a new Anaconda prompt and either access the virtual environment if virtual environment was used, or simply run
`python manage.py test` in the folder where the content was extracted
* Alternatively, to run the feature tests only, as these complete very quickly, run
`python manage.py test web_scraper.tests.ProjectTests`