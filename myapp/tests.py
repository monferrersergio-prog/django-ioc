from django.test import TestCase


# Create your tests here.
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class MySeleniumTests(StaticLiveServerTestCase):

    # Crear l'usuari de prova abans de cada test
    def setUp(self):
        super().setUp()

        User = get_user_model()
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123"
        )

    # Inicialitzar Selenium i Firefox
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        opts = Options()

        # Execucio sense interfície grafica (SSH)
        opts.add_argument("-headless")

        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)

    # Tancar Firefox en finalitzar els tests
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "selenium"):
            cls.selenium.quit()

        super().tearDownClass()

    # TEST 1: autenticacio correcta
    def test_login(self):

        # Accedir al login de Django
        self.selenium.get(
            self.live_server_url + "/admin/login/"
        )

        # Comprovar el titol inicial
        self.assertEqual(
            self.selenium.title,
            "Log in | Django site admin"
        )

        # Introduir l'usuari
        username_input = self.selenium.find_element(
            By.NAME, "username"
        )
        username_input.send_keys("admin")

        # Introduir la contrasenya
        password_input = self.selenium.find_element(
            By.NAME, "password"
        )
        password_input.send_keys("admin123")

        # Clicar el boto de login
        self.selenium.find_element(
            By.XPATH, '//input[@type="submit"]'
        ).click()

        # Esperar que aparegui el panell d'administracio
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.title ==
            "Site administration | Django site admin"
        )

        # Verificar l'autenticacio correcta
        self.assertEqual(
            self.selenium.title,
            "Site administration | Django site admin"
        )

    # TEST 2: autenticacio incorrecta
    def test_login_error(self):

        # Accedir al formulari de login
        self.selenium.get(
            self.live_server_url + "/admin/login/"
        )

        self.assertEqual(
            self.selenium.title,
            "Log in | Django site admin"
        )

        # Introduir un usuari inexistent
        username_input = self.selenium.find_element(
            By.NAME, "username"
        )
        username_input.send_keys("usuari_no_existent")

        # Introduir una contrasenya incorrecta
        password_input = self.selenium.find_element(
            By.NAME, "password"
        )
        password_input.send_keys("contrasenya_incorrecta")

        # Intentar iniciar sessio
        self.selenium.find_element(
            By.XPATH, '//input[@type="submit"]'
        ).click()

        # Esperar que aparegui el missatge d'error
        WebDriverWait(self.selenium, 10).until(
            lambda driver: driver.find_elements(
                By.CLASS_NAME, "errornote"
            )
        )

        # Verificar que continuem al login
        self.assertEqual(
            self.selenium.title,
            "Log in | Django site admin"
        )

        # Verificar que NO hem entrat a l'administracio
        self.assertNotEqual(
            self.selenium.title,
            "Site administration | Django site admin"
        )
