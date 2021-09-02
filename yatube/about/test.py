from django.test import Client, TestCase
from django.urls.base import reverse


class AboutURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_about_author(self):
        pass
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/author.html')

    def test_about_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'about/tech.html')


class AboutViewsTests (TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()

    def test_author(self):
        """
        URL, генерируемый при помощи имени about:author, доступен.\n
        При запросе к about:author применяется шаблон about/author.html
        """
        response = self.guest_client.get(reverse('about:author'))
        self.assertEqual(response.status_code, 200)
        response = self.guest_client.get(reverse('about:author'))
        self.assertTemplateUsed(response, 'about/author.html')

    def test_tech(self):
        """
        URL, генерируемый при помощи имени about:tech, доступен.\n
        При запросе к about:tech применяется шаблон about/tech.html
        """
        response = self.guest_client.get(reverse('about:tech'))
        self.assertEqual(response.status_code, 200)
        response = self.guest_client.get(reverse('about:tech'))
        self.assertTemplateUsed(response, 'about/tech.html')
