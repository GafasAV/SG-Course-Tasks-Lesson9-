import unittest
import asyncio
import scraper
import aiohttp


class TestScraper(unittest.TestCase):

    def setUp(self):
        self.content = None
        self.event = asyncio.new_event_loop()
        asyncio.set_event_loop(self.event)

        self.session = self.event.run_until_complete(scraper.init_session())

        with open('test_coin.html', 'r') as f:
            self.content = f.read()

    def tearDown(self):
        if self.session:
            self.session.close()

        self.event.close()

    def test_url(self):
        url = scraper.url

        self.assertIsInstance(url, str, "Url not string."
                                        "Must be a string.")

        self.assertEqual(url, "https://coinmarketcap.com/all/views/all/")

    def test_session(self):
        self.assertNotEqual(self.session, None, "Session not initing."
                                                "Must be initing."
                                                "Check it !")
        self.assertIsInstance(self.session, aiohttp.client.ClientSession,
                              "Wrong session type !")

    def test_session_fail(self):
        async def wrapper():
            response = await self.session.get('https://httpbin.org/get')
            content = await response.text()

            return response.status, content

        status, content = self.event.run_until_complete(wrapper())

        self.assertNotEqual(status, 400, "Some wrong. This is Bad request."
                                         "Check it ! Must be = 400")

    def test_session_success(self):
        async def wrapper():
            response = await self.session.get(scraper.url)
            content = await response.text()

            return response.status, content

        status, content = self.event.run_until_complete(wrapper())

        self.assertEqual(status, 200, "Status != 200."
                                      "Must be a 200."
                                      "Check it !")
        self.assertNotEqual(len(content), 0, "Right request ! Content must be..."
                                             "Content = 0. Check it !")

    def test_parser(self):
        result = scraper.parse(self.content)

        self.assertIsInstance(result, list, "Parse result not list."
                                            "Must be a list of tuples."
                                            "Check it !")
        self.assertIsInstance(result[0], tuple, "Parse result list is not a tuple."
                                                "Must be a tuple 9 elements."
                                                "Check it !")
        self.assertEqual(len(result[0]), 9, "Tuple size not 9."
                                            "Must be a 9 elements."
                                            "Check it !")

    def test_scrap_wrong_url(self):
        async def wrapper():
            result = await scraper.scrap(url=1)

            return result

        with self.assertRaises(TypeError):
            result = self.event.run_until_complete(wrapper())
            self.assertEqual(result, None)

    def test_scrap_good_url(self):
        async def wrapper():
            result = await scraper.scrap(url="http://google.com")

            return result

        result = self.event.run_until_complete(wrapper())
        self.assertNotEqual(result, None, "Result is None !")
        self.assertNotEqual(len(result), 0, "No data in result !")

    def test_scrap_bad_url(self):
        async def wrapper():
            result = await scraper.scrap(url="https://www.google.com.ua/get")

            return result

        result = self.event.run_until_complete(wrapper())
        self.assertIsNone(result, "Not None - but None expected !")

    def test_start_bad_url(self):
        url = 123

        with self.assertRaises(TypeError):
            result = scraper.start(url)

    def test_start(self):
        url = scraper.url

        result = scraper.start(url)

        self.assertIsNotNone(result, "Result None. Check it !")
        self.assertIsInstance(result, list, "Result must be list type !")
