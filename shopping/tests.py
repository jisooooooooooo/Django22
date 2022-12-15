from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_영롱서울 = User.objects.create_user(username='영롱서울', password='ap943939!')
        self.user_레브드제이 = User.objects.create_user(username='레브드제이', password='1234')

        self.user_레브드제이.is_staff = True
        self.user_레브드제이.save()

        self.category_ring = Category.objects.create(name='ring', slug='ring')
        self.category_necklace = Category.objects.create(name='necklace', slug='necklace')
        self.category_earrings = Category.objects.create(name='earrings', slug='earrings')

        self.tag_sim = Tag.objects.create(name="심플", slug="심플")
        self.tag_daily = Tag.objects.create(name="데일리", slug="데일리")
        self.tag_pol = Tag.objects.create(name="세련", slug="세련")

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트',
            content='첫 번째 포스트입니다.',
            category=self.category_ring,
            author=self.user_영롱서울,
        )
        self.post_001.tag.add(self.tag_sim)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트',
            content='두 번째 포스트입니다.',
            category=self.category_ring,
            author=self.user_영롱서울
        )
        self.post_002.tag.add(self.tag_daily)
        self.post_002.tag.add(self.tag_pol)

        self.post_003 = Post.objects.create(
            title='세 번째 포스트',
            content='세 번째 포스트입니다.',
            category=self.category_ring,
            author=self.user_레브드제이
        )
        self.post_003.tag.add(self.tag_sim)
        self.post_003.tag.add(self.tag_daily)


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
        self.assertIn(
            f'{self.category_ring.name} ({self.category_ring.post_set.count()})', categories_card.text)
        self.assertIn(
            f'{self.category_necklace.name} ({self.category_necklace.post_set.count()})', categories_card.text)
        self.assertIn(
            f'{self.category_earrings.name} ({self.category_earrings.post_set.count()})', categories_card.text)

    def test_post_list(self):
       # Post가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/shopping/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual(soup.title.text, 'Shopping')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_sim.name, post_001_card.text)
        self.assertNotIn(self.tag_daily.name, post_001_card.text)
        self.assertNotIn(self.tag_pol.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertIn(self.post_002.author.username.upper(), post_002_card.text)
        self.assertNotIn(self.tag_sim.name, post_002_card.text)
        self.assertIn(self.tag_daily.name, post_002_card.text)
        self.assertIn(self.tag_pol.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.post_003.category.name, post_003_card.text)
        self.assertIn(self.post_003.author.username.upper(), post_003_card.text)
        self.assertIn(self.tag_sim.name, post_003_card.text)
        self.assertIn(self.tag_daily.name, post_003_card.text)
        self.assertNotIn(self.tag_pol.name, post_003_card.text)


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

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_ring.name, post_area.text)

        self.assertIn(self.user_영롱서울.username.upper(), post_area.text)
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.tag_sim.name, post_area.text)
        self.assertNotIn(self.tag_daily.name, post_area.text)
        self.assertNotIn(self.tag_pol.name, post_area.text)

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

    def test_tag_page(self):
        response = self.client.get(self.tag_sim.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_sim.name, soup.h1.text)

        main_area = soup.find('div', id="main-area")
        self.assertIn(self.tag_sim.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        #로그인하지 않으면 status code가 200이면 안 된다!
        response = self.client.get('/shopping/create_post/')
        self.assertNotEqual(response.status_code, 200)

        #staff가 아닌 레브드제이가 로그인을 한다.
        self.client.login(username='레브드제이', password='1234')
        response = self.client.get('/shopping/create_post/')
        self.assertEqual(response.status_code, 200)

        #staff인 레브드제이로 로그인을 한다.
        self.client.login(username='레브드제이', password='ap943939!')
        response = self.client.get('/shopping/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Shopping', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.fine('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/shopping/create_post',
            {
                'title': 'Post Form 만들기',
                'content': "Post Form 페이지를 만듭시다.",

            }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, '영롱서울')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='심플'))
        self.assertTrue(Tag.objects.get(name='데일리'))
        self.assertTrue(Tag.objects.get(name='세련'))

    def test_update_post(self):
        update_post_url = f'/shopping/update_post/{self.post_003.pk}/'

        #로그인하지 않은 경우
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        #로그인은 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_영롱서울)
        self.client.login(
            username=self.user_영롱서울.username,
            password='1234'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        #작성자가 접근하는 경우
        self.client.login(
            username=self.post_003.author.username,
            password='ap943939!'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tag_str_input = main_area.fine('input', id='id_tags_str')
        self.assertTrue(tag_str_input)
        self.assertIn('심플; 세련', tag_str_input.attrs['value'])

        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트를 수정했습니다. ',
                'content': '안녕 세계?',
                'category': self.category_ring.pk,
                'tags_str': '심플; 데일리, 세련'
            },
            follow=True
        )
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('안녕 세계?', main_area.text)
        self.assertIn(self.category_ring.name, main_area.text)
        self.assertIn('심플', main_area.text)
        self.assertIn('데일리', main_area.text)
        self.assertIn('세련', main_area.text)
