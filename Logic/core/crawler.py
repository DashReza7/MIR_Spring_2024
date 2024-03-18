import requests
from bs4 import BeautifulSoup
import json


class IMDbCrawler:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    top_250_URL = "https://www.imdb.com/chart/top/"
    crawled_file_path = "IMDB_Crawled.json"
    not_crawled_file_path = "IMDB_Not_Crawled.json"
    added_ids_path = "Added_ids_path.json"

    def __init__(self, crawling_threshold=1000):
        """
        Initialize the crawler

        Parameters
        ----------
        crawling_threshold: int
            The number of pages to crawl
        """
        self.crawling_threshold = crawling_threshold
        self.not_crawled = []
        self.crawled = []
        self.added_ids = []

    def get_id_from_URL(self, URL):
        """
        Get the id from the URL of the site. The id is what comes exactly after title.
        for example the id for the movie https://www.imdb.com/title/tt0111161/?ref_=chttp_t_1 is tt0111161.

        Parameters
        ----------
        URL: str
            The URL of the site
        Returns
        ----------
        str
            The id of the site
        """
        return URL.split("/")[4]

    def get_url_from_id(self, id):
        return f"https://www.imdb.com/title/{id}"

    def write_to_file_as_json(self):
        """
        Save the crawled files into json
        """
        try:
            with open(self.crawled_file_path, "w") as json_file:
                json.dump(self.crawled, json_file)
            with open(self.not_crawled_file_path, "w") as json_file:
                json.dump(self.not_crawled, json_file)
            with open(self.added_ids_path, "w") as json_file:
                json.dump(self.added_ids, json_file)
        except IOError as e:
            print("Error writing to JSON file: ", e)

    def read_from_file_as_json(self):
        """
        Read the crawled files from json
        """
        try:
            with open(self.crawled_file_path, "r") as f:
                self.crawled = json.load(f)
                # print(type(self.crawled[0]))
            with open(self.not_crawled_file_path, "r") as f:
                self.not_crawled = json.load(f)
                # print(type(self.not_crawled[0]))
            with open(self.added_ids_path, "r") as f:
                self.added_ids = json.load(f)
                # print(type(self.added_ids[0]))
        except IOError as e:
            print("Error reading from JSON file: ", e)

    def crawl(self, URL):
        """
        Make a get request to the URL and return the response

        Parameters
        ----------
        URL: str
            The URL of the site
        Returns
        ----------
        requests.models.Response
            The response of the get request
        """
        r = requests.get(URL, headers=self.headers)
        return r

    def extract_top_250(self):
        """
        Extract the top 250 movies from the top 250 page and use them as seed for the crawler to start crawling.
        """
        try:
            response = requests.get(self.top_250_URL, headers=self.headers)
            response.raise_for_status()
            tmp_soup = BeautifulSoup(response.text, "html.parser")
            movie_links = tmp_soup.find_all("a", href=True, attrs={"class": "ipc-lockup-overlay ipc-focusable"})
            movie_links_list = [f"https://www.imdb.com{link['href']}" for link in movie_links]

            for movie_link in movie_links_list:
                self.added_ids.append(self.get_id_from_URL(movie_link))
                # self.check_dup()
                self.not_crawled.append(self.get_id_from_URL(movie_link))

        except requests.RequestException as e:
            print("Error fetching page: ", e)
        except AttributeError as e:
            print("Error parsing HTML: ", e)

    def get_imdb_instance(self):
        return {
            "id": None,  # str
            "title": None,  # str
            "first_page_summary": None,  # str
            "release_year": None,  # str
            "mpaa": None,  # str
            "budget": None,  # str
            "gross_worldwide": None,  # str
            "rating": None,  # str
            "directors": None,  # List[str]
            "writers": None,  # List[str]
            "stars": None,  # List[str]
            "related_links": None,  # List[str]
            "genres": None,  # List[str]
            "languages": None,  # List[str]
            "countries_of_origin": None,  # List[str]
            "summaries": None,  # List[str]
            "synopsis": None,  # List[str]
            "reviews": None,  # List[List[str]]
        }

    def start_crawling(self):
        """
        Start crawling the movies until the crawling threshold is reached.
            replace WHILE_LOOP_CONSTRAINTS with the proper constraints for the while loop.
            replace NEW_URL with the new URL to crawl.
            replace THERE_IS_NOTHING_TO_CRAWL with the condition to check if there is nothing to crawl.
            delete help variables.

        ThreadPoolExecutor is used to make the crawler faster by using multiple threads to crawl the pages.
        You are free to use it or not. If used, not to forget safe access to the shared resources.
        """
        if len(self.crawled) == 0 and len(self.added_ids) == 0 and len(self.not_crawled) == 0:
            self.extract_top_250()
        for i in range(self.crawling_threshold):
            URL = self.get_url_from_id(self.not_crawled[0])
            # self.not_crawled.remove(self.not_crawled[0])
            self.not_crawled.pop(0)
            self.crawl_page_info(URL)
            self.write_to_file_as_json()

    def crawl_page_info(self, URL):
        """
        Main Logic of the crawler. It crawls the page and extracts the information of the movie.
        Use related links of a movie to crawl more movies.

        Parameters
        ----------
        URL: str
            The URL of the site
        """
        new_movie = self.get_imdb_instance()
        self.extract_movie_info(self.crawl(URL), new_movie, URL)
        if len(self.added_ids) <= self.crawling_threshold:
            for related_movie_id in new_movie["related_links"]:
                if related_movie_id not in self.added_ids:
                    self.added_ids.append(related_movie_id)
                    # self.check_dup()
                    self.not_crawled.append(related_movie_id)
        self.crawled.append(new_movie)
        if new_movie["title"] is None:
            print("finished: ", new_movie["id"])
        else:
            print("finished: ", new_movie["title"])

    def extract_movie_info(self, res, movie, URL):
        """
        Extract the information of the movie from the response and save it in the movie instance.

        Parameters
        ----------
        res: requests.models.Response
            The response of the get request
        movie: dict
            The instance of the movie
        URL: str
            The URL of the site
        """
        soup = BeautifulSoup(res.text, "html.parser")
        movie["id"] = self.get_id_from_URL(URL)
        movie["title"] = self.get_title(soup)
        if movie["title"] is None:
            print("working on: ", movie["id"])
        else:
            print("working on: ", movie["title"])
        movie["first_page_summary"] = self.get_first_page_summary(soup)
        movie["release_year"] = self.get_release_year(soup)
        movie["mpaa"] = self.get_mpaa(URL)
        movie["budget"] = self.get_budget(soup)
        movie["gross_worldwide"] = self.get_gross_worldwide(soup)
        movie["directors"] = self.get_director(soup)
        movie["writers"] = self.get_writers(soup)
        movie["stars"] = self.get_stars(soup)
        movie["related_links"] = self.get_related_links(soup)
        movie["genres"] = self.get_genres(soup)
        movie["languages"] = self.get_languages(soup)
        movie["countries_of_origin"] = self.get_countries_of_origin(soup)
        movie["rating"] = self.get_rating(soup)
        movie["summaries"] = self.get_summary(URL)
        movie["synopsis"] = self.get_synopsis(URL)
        movie["reviews"] = self.get_reviews_with_scores(URL)

    def get_summary_link(self, url):
        """
        Get the link to the summary page of the movie
        Example:
        https://www.imdb.com/title/tt0111161/ is the page
        https://www.imdb.com/title/tt0111161/plotsummary is the summary page

        Parameters
        ----------
        url: str
            The URL of the site
        Returns
        ----------
        str
            The URL of the summary page
        """
        return f"{url}/plotsummary"
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get summary link")

    def get_review_link(self, url):
        """
        Get the link to the review page of the movie
        Example:
        https://www.imdb.com/title/tt0111161/ is the page
        https://www.imdb.com/title/tt0111161/reviews is the review page
        """
        return f"{url}/reviews"
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get review link")

    def get_title(self, soup):
        """
        Get the title of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The title of the movie

        """
        element = soup.find("script", type="application/ld+json")
        if element is None:
            return None
        data = json.loads(element.contents[0])
        return str(data["name"])
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get title")

    def get_first_page_summary(self, soup):
        """
        Get the first page summary of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The first page summary of the movie
        """
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        if data["props"]["pageProps"]["aboveTheFoldData"]["plot"] is None or data["props"]["pageProps"]["aboveTheFoldData"]["plot"]["plotText"] is None or data["props"]["pageProps"]["aboveTheFoldData"]["plot"]["plotText"]["plainText"] is None:
            return None
        foo = data["props"]["pageProps"]["aboveTheFoldData"]["plot"]["plotText"]["plainText"]
        return str(foo)
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get first page summary")

    def get_director(self, soup):
        """
        Get the directors of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The directors of the movie
        """
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        if data["props"]["pageProps"]["aboveTheFoldData"]["directorsPageTitle"] is None or len(data["props"]["pageProps"]["aboveTheFoldData"]["directorsPageTitle"]) == 0:
            return None
        foo = data["props"]["pageProps"]["aboveTheFoldData"]["directorsPageTitle"][0]["credits"]
        bar = []
        for fooz in foo:
            bar.append(str(fooz["name"]["nameText"]["text"]))
        return bar
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get director")

    def get_stars(self, soup):
        """
        Get the stars of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The stars of the movie
        """
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        foo = data["props"]["pageProps"]["mainColumnData"]["cast"]["edges"]
        bar = []
        for fooz in foo:
            bar.append(str(fooz["node"]["name"]["nameText"]["text"]))
        return bar
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get stars")

    def get_writers(self, soup):
        """
        Get the writers of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The writers of the movie
        """
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        if data["props"]["pageProps"]["mainColumnData"]["writers"] is None or len(data["props"]["pageProps"]["mainColumnData"]["writers"]) == 0:
            return None
        foo = data["props"]["pageProps"]["mainColumnData"]["writers"][0]["credits"]
        bar = []
        for fooz in foo:
            bar.append(str(fooz["name"]["nameText"]["text"]))
        return bar
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get writers")

    def get_related_links(self, soup):
        """
        Get the related links(movie ID's) of the movie from the More like this section of the page from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The related links(movie ID's) of the movie
        """
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        foo = data["props"]["pageProps"]["mainColumnData"]["moreLikeThisTitles"]["edges"]
        bar = []
        for fooz in foo:
            bar.append(str(fooz["node"]["id"]))
        return bar
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get related links")

    def get_summary(self, URL):
        """
        Get the summary of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The summary of the movie
        """
        summary_page_url = self.get_summary_link(URL)
        r = requests.get(summary_page_url, headers=self.headers)
        soup = BeautifulSoup(r.text, "html.parser")
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        foo = data["props"]["pageProps"]["contentData"]["categories"]
        bar = []
        for fooz in foo:
            if fooz["id"] != "summaries" and fooz["id"] != "summary":
                continue
            items = fooz["section"]["items"]
            for item in items:
                bar.append(item["htmlContent"])
        return bar
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get summary")

    def get_synopsis(self, URL):
        """
        Get the synopsis of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The synopsis of the movie
        """
        summary_page_url = self.get_summary_link(URL)
        r = requests.get(summary_page_url, headers=self.headers)
        soup = BeautifulSoup(r.text, "html.parser")
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        if element is None:
            return None
        data = json.loads(element.contents[0])
        foo = data["props"]["pageProps"]["contentData"]["categories"]
        bar = []
        for fooz in foo:
            if fooz["id"] != "synopsis" and fooz["id"] != "synopses":
                continue
            items = fooz["section"]["items"]
            for item in items:
                bar.append(item["htmlContent"])
        return bar
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get synopsis")

    def get_reviews_with_scores(self, URL):
        """
        Get the reviews of the movie from the soup
        reviews structure: [[review,score]]

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[List[str]]
            The reviews of the movie
        """
        review_link = self.get_review_link(URL)
        r = requests.get(review_link, headers=self.headers)
        soup = BeautifulSoup(r.text, "html.parser")
        bar = []
        element = soup.find_all("div", attrs={"class": "review-container"})
        for foo in element:
            title = foo.find_next("a", attrs={"class": "title"}).get_text()
            body = foo.find_next("div", attrs={"class": "text show-more__control"}).get_text()
            rating = foo.find_next("span", attrs={"class": "rating-other-user-rating"})
            bar.append([f"{title}{body}".strip(), None if rating is None else str(rating.get_text()).strip()])
        return bar
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get reviews")

    def get_genres(self, soup):
        """
        Get the genres of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The genres of the movie
        """
        element = soup.find("script", type="application/ld+json")
        data = json.loads(element.contents[0])
        foo = data["genre"]
        genres = []
        for bar in foo:
            genres.append(str(bar))
        return genres
        # try:
            ## TODO
            # pass
        # except:
            # print("Failed to get generes")

    def get_rating(self, soup):
        """
        Get the rating of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The rating of the movie
        """
        element = soup.find("script", type="application/ld+json")
        data = json.loads(element.contents[0])
        if "aggregateRating" not in data:
            return "No rating"
        return str(data["aggregateRating"]["ratingValue"])
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get rating")

    def get_mpaa(self, URL):
        """
        Get the MPAA of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The MPAA of the movie
        """
        mpaa_url = f"{URL}/parentalguide"
        r = requests.get(mpaa_url, headers=self.headers)
        soup = BeautifulSoup(r.text, "html.parser")
        element = soup.find("tr", id="mpaa-rating")
        if element is None:
            return None
        return str(element.contents[3].get_text())
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get mpaa")

    def get_release_year(self, soup):
        """
        Get the release year of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The release year of the movie
        """
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        if data["props"]["pageProps"]["aboveTheFoldData"]["releaseYear"] is None:
            return None
        return str(data["props"]["pageProps"]["aboveTheFoldData"]["releaseYear"]["year"])
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get release year")

    def get_languages(self, soup):
        """
        Get the languages of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The languages of the movie
        """
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        if data["props"]["pageProps"]["mainColumnData"]["spokenLanguages"] is None or data["props"]["pageProps"]["mainColumnData"]["spokenLanguages"]["spokenLanguages"] is None:
            return None
        foo = data["props"]["pageProps"]["mainColumnData"]["spokenLanguages"]["spokenLanguages"]
        langs = []
        for dic in foo:
            langs.append(str(dic["text"]))
        return langs
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get languages")
            # return None

    def get_countries_of_origin(self, soup):
        """
        Get the countries of origin of the movie from the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        List[str]
            The countries of origin of the movie
        """
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        if data["props"]["pageProps"]["mainColumnData"]["countriesOfOrigin"] is None or data["props"]["pageProps"]["mainColumnData"]["countriesOfOrigin"]["countries"] is None:
            return None
        foo = data["props"]["pageProps"]["mainColumnData"]["countriesOfOrigin"]["countries"]
        counts = []
        for dic in foo:
            counts.append(str(dic["text"]))
        return counts
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get countries of origin")

    def get_budget(self, soup):
        """
        Get the budget of the movie from box office section of the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The budget of the movie
        """
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        if data["props"]["pageProps"]["mainColumnData"]["productionBudget"] is None:
            return None
        return str(data["props"]["pageProps"]["mainColumnData"]["productionBudget"]["budget"]["amount"])
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get budget")

    def get_gross_worldwide(self, soup):
        """
        Get the gross worldwide of the movie from box office section of the soup

        Parameters
        ----------
        soup: BeautifulSoup
            The soup of the page
        Returns
        ----------
        str
            The gross worldwide of the movie
        """
        element = soup.find("script", id="__NEXT_DATA__", type="application/json")
        data = json.loads(element.contents[0])
        if data["props"]["pageProps"]["mainColumnData"]["worldwideGross"] is None:
            return None
        foo = str(data["props"]["pageProps"]["mainColumnData"]["worldwideGross"]["total"]["amount"])
        return foo
        # try:
            ## TODO
            # pass
        # except:
            # print("failed to get gross worldwide")

    # def check_dup(self):
    #     foo = set(self.added_ids)
    #     if len(foo) != len(self.added_ids):
    #         print("FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF")


def main():
    imdb_crawler = IMDbCrawler(crawling_threshold=600)
    imdb_crawler.read_from_file_as_json()
    imdb_crawler.start_crawling()
    imdb_crawler.write_to_file_as_json()


if __name__ == "__main__":
    main()
