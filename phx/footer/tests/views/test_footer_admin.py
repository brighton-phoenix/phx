from django.test import TestCase
from ..factories import FooterSectionFactory, FooterLinkFactory
from django.urls import reverse
from pages.models import Page

from home.tests.factories import ContentFactory


class TestFooter(TestCase):

    def test_social_section_is_always_rendered(self):
        url = reverse('home-index')
        Page.objects.create(title='home')
        ContentFactory()

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Keep up to date_')
        self.assertContains(response, 'Follow us on social media')

    def test_custom_footer_sections_are_rendered(self):
        url = reverse('home-index')
        Page.objects.create(title='home')
        ContentFactory()
        section = FooterSectionFactory()
        link = FooterLinkFactory(section=section)

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, section.header)
        self.assertContains(response, section.sub_header)
        self.assertContains(response, link.text)
        self.assertContains(response, link.path)
