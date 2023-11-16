from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

MAX_WAIT = 10


class NewVisitorTest(StaticLiveServerTestCase):
	"""Тест нового посетителя."""

	def setUp(self):
		"""Открыть."""
		self.browser = webdriver.Firefox()


	def tearDown(self):
		"""Закрыть."""
		self.browser.quit()


	def wait_for_row_in_list_table(self, row_text):
		"""Ожидать строку в таблице списка."""
		start_time = time.time()
		while True:
			try:
				table = self.browser.find_element(By.ID, 'id_list_table')
				rows = table.find_elements(By.TAG_NAME, 'tr')
				self.assertIn(row_text, [row.text for row in rows])
				return
			except (AssertionError, WebDriverException) as e:
				if time.time() - start_time > MAX_WAIT:
					raise e
				time.sleep(0.5)


	def test_can_start_a_list_for_one_user(self):
		"""Тест: можно добавить элемент в список и затем его получить."""
		# Эдит слышала про крутое новое онлайн-приложение со списком неотложенных дел. Она решает оценить его домашнюю страницу.
		self.browser.get(self.live_server_url)
	
		# Она видит, что заголовок и шапка страницы говорят о списках неотложеных дел.
		self.assertIn('To-Do', self.browser.title)
		header_text = self.browser.find_element(By.TAG_NAME, 'h1').text
		self.assertIn('To-Do', header_text)

		# Ей сразу же предлагается ввести элемент списка.
		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		self.assertEqual(
			inputbox.get_attribute('placeholder'),
			'Enter a to-do item'
		)
		
		# Она набирает в текстовом поле "Купить павлиньи перья" (ее хобби - вязание рыболовных мушек).
		inputbox.send_keys('Купить павлиньи перья')
		
		# Когда она нажимает enter, страница обновляется, и теперь страница содержит "1: Купить павлиньи перья" в качестве элемента списка.
		inputbox.send_keys(Keys.ENTER)
		self.wait_for_row_in_list_table('1: Купить павлиньи перья')
		
		# Текстовое поле по-прежнему приглашает ее добавить еще один элемент. Она вводит "Сделать мушку из павлиньих перьев".
		# (Эдит очень методична).
		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		inputbox.send_keys('Сделать мушку из павлиньих перьев')
		inputbox.send_keys(Keys.ENTER)
		
		# Страница снова обновляется, и теперь показывает оба элемента ее списка.
		self.wait_for_row_in_list_table('2: Сделать мушку из павлиньих перьев')
		self.wait_for_row_in_list_table('1: Купить павлиньи перья')
		
		# Удовлетворенная, она снова ложится спать.


	def test_multiple_users_can_start_lists_at_different_urls(self):
		"""Тест: многочисленные пользователи могут начать списки по разным url."""
		# Эдит начинает новый список.
		self.browser.get(self.live_server_url)
		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		inputbox.send_keys('Купить павлиньи перья')
		inputbox.send_keys(Keys.ENTER)
		self.wait_for_row_in_list_table('1: Купить павлиньи перья')

		# Она замечает, что ее список иммет уникальный URL-адрес.
		edith_list_url = self.browser.current_url
		self.assertRegex(edith_list_url, '/lists/.+')

		# Теперь новый пользователь Фрэнсис приходит на сайт.

		## Мы используем новый сеанс браузера, тем самым обеспечивая, чтобы никакая информация от Эдит не прошла через данные cookie и пр.
		self.browser.quit()
		self.browser = webdriver.Firefox()

		# Фрэнсис посещает домашнюю страницу. Нет никаких признаков списка Эдит.
		self.browser.get(self.live_server_url)
		page_text = self.browser.find_element(By.TAG_NAME, 'body').text
		self.assertNotIn('Купить павлиньи перья', page_text)
		self.assertNotIn('Сделать мушку', page_text)

		# Фрэнсис начинает новый список, вводя новый элемент. Он менее интересен, чем список Эдит.
		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		inputbox.send_keys('Купить молоко')
		inputbox.send_keys(Keys.ENTER)
		self.wait_for_row_in_list_table('1: Купить молоко')

		# Фрэнсис получает уникальный URL-адрес.
		francis_list_url = self.browser.current_url
		self.assertRegex(francis_list_url, '/lists/.+')
		self.assertNotEqual(francis_list_url, edith_list_url)

		# Опять-таки, нет ни следа от списка Эдит.
		page_text = self.browser.find_element(By.TAG_NAME, 'body').text
		self.assertNotIn('Купить павлиньи перья', page_text)
		self.assertIn('Купить молоко', page_text)

		# Удовлетворенные, они обы ложатся спать.


	def test_layout_and_styling(self):
		"""Тест макета и стилевого оформления."""
		# Эдит открывает домашнюю страницу.
		self.browser.get(self.live_server_url)
		self.browser.set_window_size(1024, 768)

		# Она замечает, что поле ввода аккуратно центрировано.
		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		self.assertAlmostEqual(
			inputbox.location['x'] + inputbox.size['width'] / 2,
			256,
			delta=10
		)

		# Она начинает новый список и видит, что поле ввода тоже находится по центру.
		inputbox.send_keys('testing')
		inputbox.send_keys(Keys.ENTER)
		self.wait_for_row_in_list_table('1: testing')
		inputbox = self.browser.find_element(By.ID, 'id_new_item')
		self.assertAlmostEqual(
			inputbox.location['x'] + inputbox.size['width'] / 2,
			256,
			delta=10
		)


if __name__ == '__main__':
	unittest.main(warnings='ignore')