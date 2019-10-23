from django.test import TestCase
from selenium import webdriver
from django.urls import reverse

# Create your tests here.
"""
class FunctionalTest(TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def test_our_home_page(self):
        self.browser.get('http://localhost:8000')
        self.assertIn('Pages', self.browser.page_source)

    def test_discover(self):
        response = self.client.get(reverse('search'))
        self.assertTemplateUsed(response, 'search.html')

    def tearDown(self):
        self.browser.quit()

"""
