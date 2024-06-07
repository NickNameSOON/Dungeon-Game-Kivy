from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import random
import time


class ImageButton(ButtonBehavior, Image):
    pass


class MonsterBattleApp(App):
    def build(self):
        self.current_monster = 1
        self.player_health = 3  # Reduced health to 3
        self.total_monsters = 5
        self.attack_sequence = self.generate_attack_sequence()
        self.sequence_index = 0
        self.press_time = 0

        self.root = BoxLayout(orientation='vertical')

        # Create the start screen layout
        self.start_screen = BoxLayout(orientation='vertical')
        self.start_screen.add_widget(Label(text="Monster Battle Game", font_size='30sp'))
        start_button = Button(text="Start Game", size_hint=(None, None), size=(200, 50))
        start_button.bind(on_press=self.start_game)
        self.start_screen.add_widget(start_button)

        # Create the main game layout
        self.game_layout = BoxLayout(orientation='vertical')

        # Set the background image for the game layout
        with self.game_layout.canvas.before:
            self.bg_image = Image(source='images/background.png', allow_stretch=True, keep_ratio=False)
            self.bg_image.size = self.game_layout.size
            self.bg_image.pos = self.game_layout.pos
            self.game_layout.bind(size=self.update_bg_image, pos=self.update_bg_image)
            self.game_layout.canvas.before.add(self.bg_image.canvas)

        self.info_label = Label(text=self.get_info_text(), font_size='20sp')
        self.game_layout.add_widget(self.info_label)

        self.monster_container = BoxLayout(orientation='horizontal', size_hint=(None, None), height=200)
        self.game_layout.add_widget(self.monster_container)

        # Move the attack button lower
        self.attack_button_container = AnchorLayout(anchor_y='bottom')
        self.attack_button = ImageButton(source='images/sword.png', size_hint=(None, None), size=(100, 100))
        self.attack_button.bind(on_press=self.on_button_press)
        self.attack_button.bind(on_release=self.on_button_release)
        self.attack_button_container.add_widget(self.attack_button)
        self.game_layout.add_widget(self.attack_button_container)

        self.result_label = Label(text='', font_size='20sp')
        self.game_layout.add_widget(self.result_label)

        # Create a container for player health images
        self.health_container = BoxLayout(orientation='horizontal', size_hint=(None, None), height=50)
        self.game_layout.add_widget(self.health_container)
        self.update_health_display()

        # Create the game over screen layout
        self.game_over_screen = BoxLayout(orientation='vertical')
        self.game_over_label = Label(text="", font_size='30sp')
        self.game_over_screen.add_widget(self.game_over_label)
        retry_button = Button(text="Retry", size_hint=(None, None), size=(200, 50))
        retry_button.bind(on_press=self.retry_game)
        self.game_over_screen.add_widget(retry_button)
        main_menu_button = Button(text="Main Menu", size_hint=(None, None), size=(200, 50))
        main_menu_button.bind(on_press=self.go_to_main_menu)
        self.game_over_screen.add_widget(main_menu_button)

        self.root.add_widget(self.start_screen)
        return self.root

    def update_bg_image(self, instance, value):
        self.bg_image.size = instance.size
        self.bg_image.pos = instance.pos

    def generate_attack_sequence(self):
        sequence = ''.join(random.choice(['.', '-']) for _ in range(random.randint(3, 6)))
        return sequence

    def get_info_text(self):
        if self.current_monster <= self.total_monsters:
            return f'Monster {self.current_monster} - Health: {self.attack_sequence}'
        else:
            return f'Monsters Pair {self.current_monster // 2} - Health: {self.attack_sequence}'

    def update_health_display(self):
        self.health_container.clear_widgets()
        for i in range(self.player_health):
            heart_image = Image(source='images/heart.png', size_hint=(None, None), size=(50, 50))
            self.health_container.add_widget(heart_image)

    def update_monster_display(self):
        self.monster_container.clear_widgets()
        if self.current_monster <= self.total_monsters:
            monster_image = Image(source=f'images/monster{self.current_monster}.png', size_hint=(None, None),
                                  size=(200, 200), allow_stretch=True)
            self.monster_container.add_widget(monster_image)
        else:
            for _ in range(2):
                monster_image = Image(source=f'images/monster{random.randint(1, self.total_monsters)}.png',
                                      size_hint=(None, None), size=(200, 200), allow_stretch=True)
                self.monster_container.add_widget(monster_image)

    def on_button_press(self, instance):
        self.press_time = time.time()
        with self.attack_button.canvas.before:
            Color(1, 1, 1, 1)  # Default white color
            self.rect = Rectangle(size=self.attack_button.size, pos=self.attack_button.pos)
        Clock.schedule_once(self.check_long_press, 1)  # Schedule check for long press (1 second)

    def on_button_release(self, instance):
        release_time = time.time()
        press_duration = release_time - self.press_time
        attack_type = 'short' if press_duration < 0.25 else 'long'  # Adjust the duration check to 1 second
        self.on_attack(attack_type)
        self.attack_button.canvas.before.clear()  # Clear color overlay
        Clock.unschedule(self.check_long_press)  # Unschedule long press check

    def check_long_press(self, dt):
        # Simulate long press effect
        with self.attack_button.canvas.before:
            Color(0, 1, 0, 0.5)  # Change color to green with 50% transparency for charged attack
            self.rect = Rectangle(size=self.attack_button.size, pos=self.attack_button.pos)

    def on_attack(self, attack_type):
        expected_attack = '.' if attack_type == 'short' else '-'
        if self.attack_sequence[self.sequence_index] == expected_attack:
            self.sequence_index += 1
            if self.sequence_index == len(self.attack_sequence):
                self.result_label.text = f'Monster {self.current_monster} defeated!'
                self.current_monster += 1
                if self.current_monster > self.total_monsters and self.current_monster % 2 == 0:
                    self.attack_sequence = self.generate_attack_sequence() + self.generate_attack_sequence()
                else:
                    self.attack_sequence = self.generate_attack_sequence()
                self.sequence_index = 0
                self.update_monster_display()
                self.info_label.text = self.get_info_text()
            else:
                self.info_label.text = self.get_info_text()
        else:
            self.player_health -= 1
            self.update_health_display()
            if self.player_health <= 0:
                self.info_label.text = 'You have been defeated!'
                self.show_game_over_screen(win=False)
            else:
                self.result_label.text = 'Wrong attack! You lose 1 health point.'

    def show_game_over_screen(self, win):
        self.root.clear_widgets()
        self.root.add_widget(self.game_over_screen)
        if win:
            self.game_over_label.text = "Congratulations! You won!"
        else:
            self.game_over_label.text = "Game Over! You lost!"

    def start_game(self, instance):
        self.root.clear_widgets()
        self.root.add_widget(self.game_layout)

    def retry_game(self, instance):
        self.current_monster = 1
        self.player_health = 3  # Reset health to 3
        self.attack_sequence = self.generate_attack_sequence()
        self.sequence_index = 0
        self.update_health_display()
        self.update_monster_display()
        self.result_label.text = ''
        self.info_label.text = self.get_info_text()
        self.attack_button.disabled = False
        self.root.clear_widgets()
        self.root.add_widget(self.game_layout)

    def go_to_main_menu(self, instance):
        self.root.clear_widgets()
        self.root.add_widget(self.start_screen)


if __name__ == '__main__':
    MonsterBattleApp().run()
