from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category


class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_영롱서울 = User.objects.create_user(username='영롱서울', password='ap943939!')
        self.user_레브드제이 = User.objects.create_user(username='레브드제이', password='1234')

        self.category_ring = Category.objects.create(name='ring', slug='ring')
        self.category_necklace = Category.objects.create(name='necklace', slug='necklace')
        self.category_earrings = Category.objects.create(name='earrings', slug='earrings')

        self.post_001 = Post.objects.create(
            title = '첫 번째 포스트',
            content='첫 번째 포스트입니다.',
            category=self.category_ring,
            author=self.user_영롱서울
        )
        self.post_002 = Post.objects.create(
            title='두 번째 포스트',
            content='두 번째 포스트입니다.',
            category=self.category_necklace,
            author=self.user_영롱서울
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트',
            content='세 번째 포스트입니다.',
            category=self.category_earrings,
            author=self.user_레브드제이
        )
        self.post_004 = Post.objects.create(
            title='네 번째 포스트',
            content='네 번째 포스트입니다.',
            author=self.user_영롱서울
        )

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Shopping', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Shoppingmall')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        shopping_btn = navbar.find('a', text='Shopping')
        self.assertEqual(shopping_btn.attrs['href'], '/shopping/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_ring.name} ({self.category_ring.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_necklace.name} ({self.category_necklace.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_earrings.name} ({self.category_earrings.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

    def test_post_list(self):

       # 포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 4)

        response = self.client.get('/shopping/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.category.name, post_003_card.text)

        post_004_card = main_area.find('div', id='post-4')
        self.assertIn('미분류', post_004_card.text)
        self.assertIn(self.post_004.title, post_004_card.text)

        self.assertIn(self.user_영롱서울.username.upper(), main_area.text)
        self.assertIn(self.user_레브드제이.username.upper(), main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/shopping/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)


    def test_post_detail(self):

        self.assertEqual(self.post_001.get_absolute_url(), '/shopping/1/')

        # 2. 첫 번째 포스트이 상세 페이지 테스트
        # 2.1. 첫 번째 post url로 접근하면 정상적으로 작동한다(status code:200).
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')


        self.navbar_test(soup)

        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)

        # 2.4. 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_ring.name, post_area.text)

        # 2.5. 첫 번째 포스트의 작성자가 포스트 영역에 있다.
        self.assertIn(self.user_영롱서울.username.upper(), post_area.text)

        # 2.6. 첫 번째 포스트의 내용이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_ring.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_ring.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_ring.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)
        self.assertNotIn(self.post_004.title, main_area.text)
