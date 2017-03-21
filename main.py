import requests
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import (
    Screen,
    ScreenManager,
)


class MainScreen(Screen):
    pass


class ConnectScreen(Screen):
    pass


class ControlScreen(Screen):
    pass


class CommandScreen(Screen):
    pass


class IdentifyScreen(Screen):
    pass


class MainApp(App):
    def build(self):
        """Main app building method creating necessary window components and binding return key."""

        self.token = None
        self.ip = None
        self.login = None
        self.password = None
        self.timeout = 3

        self.screen_manager = ScreenManager()
        self.main_creen = MainScreen(name='main')
        self.connect_screen = ConnectScreen(name='connect')
        self.command_screen = CommandScreen(name='command')
        self.control_screen = ControlScreen(name='control')

        self.screen_manager.add_widget(self.main_creen)
        self.screen_manager.add_widget(self.connect_screen)
        self.screen_manager.add_widget(self.command_screen)
        self.screen_manager.add_widget(self.control_screen)

        EventLoop.window.bind(on_keyboard=self.bind_return_button)
        return self.screen_manager

    def bind_return_button(self, window, key, *args):
        """Bind [Return] key to handle moving back between windows."""
        if key == 27:
            if self.screen_manager.current != 'main':
                self.screen_manager.current = 'main'
            else:
                App.get_running_app().stop()
            return True

    def on_pause(self):
        """Default method handling pausing the application."""
        return True

    def on_resume(self):
        """Default method handling resuming application."""
        return True

    def get_credentials(self, ip, login, password):
        """Method extracting login credentials from user input."""
        if self.is_empty(ip):
            self.inform('missing ip', 'please specify ip address')

        elif self.is_empty(login):
            self.inform('missing login', 'please specify user login')

        elif self.is_empty(password):
            self.inform('missing login', 'please specify user password')

        else:
            self.authenticate_token(ip, login, password)

    def is_empty(self, chain):
        """Method to ensure that user provided non-empty input."""
        if chain == '':
            return True
        return False

    def inform(self, title, message):
        """Custom display popup with label informing about app state."""
        if len(message)>=500:
            message=message[-500:]
        info_label = Label(
            text=message,
            size_hint_y=1,
            text_size=(300, None),
        )
        popup = Popup(
            title=title,
            content=info_label,
            size_hint=(None, None),
            size=(400, 400)
        )
        popup.open()

    def normalize(self, chain):
        """Method stripping text chain from white spaces."""
        return ''.join(str(chain).split()).strip()

    def authenticate_token(self, ip, login, password):
        """Custom method to authenticate user using expiring token."""
        try:
            response = requests.post(
                'http://'+self.normalize(ip)+'/api/auth/',
                data={
                    'username': self.normalize(login),
                    'password': self.normalize(password)
                },
                timeout=self.timeout,
            )
        except:
            self.inform('error', 'cannot connect to the server')
            return False

        if response and response.status_code == 200:
            self.ip = self.normalize(ip)
            self.login = self.normalize(login)
            self.password = self.normalize(password)
            self.token = response.json()['token']
            self.inform('logged in', 'user authenticated')

        elif response.status_code != 200:
            self.inform('error', 'cannot authenticate user')


    def post_signal(self, value):
        """Connect to REST API on desktop PC."""
        try:
            if self.token:
                response = requests.post(  # NOQA
                        'http://'+self.ip+'/api/allowed_requests/',
                        data={'value': value},
                        headers={'Authorization': 'Token ' + self.token},
                        timeout=self.timeout,
                    )
        except requests.exceptions.ConnectionError:
            self.inform('error', 'cannot retrieve response')
            return False

    def identify(self):
        """Identify system and PC components."""
        try:
            if self.token:
                response = requests.get(
                    'http://'+self.ip+'/api/identify/',
                    headers={'Authorization': 'Token ' + self.token},
                    timeout=self.timeout,
                )

                if response and response.status_code == 200:
                    self.inform(
                        'system info',
                        'system: ' + str(response.json()['system']) + '\n' +
                        'name: ' + str(response.json()['name']) + '\n' +
                        'release: ' + str(response.json()['release']) + '\n' +
                        'cpu: ' + str(response.json()['cpu']) + '\n' +
                        'cores: ' + str(response.json()['cores']) + '\n' +
                        'memory: ' + str(int(response.json()['memory']) /
                                         (1024*1024)),
                    )
                else:
                    self.inform('error', 'connection error')
            else:
                self.inform('error', 'login required')
        except:
            self.inform('error', 'cannot retrieve response')
            return False

    def execute(self, command):
        """Execute python command in interpreter."""
        try:
            if self.token:
                response = requests.post(
                    'http://'+self.ip+'/api/external_requests/',
                    data={'external': command},
                    headers={'Authorization': 'Token ' + self.token},
                    timeout=self.timeout,
                )

                if response and response.status_code == 200:
                    self.inform('output', str(response.json()['result'][0]))
                else:
                    self.inform('error', 'cannot process request')
            else:
                self.inform('error', 'login required')

        except:
            self.inform('error', 'cannot retrieve response')
            return False

    def long_press_left(self):
        Clock.schedule_interval(self._move_left, 0.01)

    def long_release_left(self):
        Clock.unschedule(self._move_left)

    def long_press_right(self):
        Clock.schedule_interval(self._move_right, 0.01)

    def long_release_right(self):
        Clock.unschedule(self._move_right)

    def long_press_up(self):
        Clock.schedule_interval(self._move_up, 0.01)

    def long_release_up(self):
        Clock.unschedule(self._move_up)

    def long_press_down(self):
        Clock.schedule_interval(self._move_down, 0.01)

    def long_release_down(self):
        Clock.unschedule(self._move_down)

    def _move_left(self, dt):
        self.post_signal(9)

    def _move_right(self, dt):
        self.post_signal(10)

    def _move_up(self, dt):
        self.post_signal(11)

    def _move_down(self, dt):
        self.post_signal(12)


MainApp().run()
