import random
from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy import platform
from kivy.app import App
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle

Builder.load_file("menu.kv")

class MainWidget(RelativeLayout):

    from transforms import transform, transform_2D, transform_perspective
    from user_actions import on_touch_down, on_touch_up, _on_keyboard_down, _on_keyboard_up, _keyboard_closed

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    
    V_NB_LINES = 10 # number of vertical lines that we going to use
    V_LINE_SPACING = .25 # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 15 # number of horizontal lines that we going to use
    H_LINE_SPACING = .15 # percentage in screen height
    horizontal_lines = []
    
    SPEED = 1
    current_offset_y = 0
    
    SPEED_X = 16
    current_speed_x = 0
    current_offset_x = 0
    current_y_loop = 0

    NB_TILES = 12
    tiles = []
    tiles_cordinates = []

    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.05
    ship = None
    ship_cordinates = [(0, 0), (0, 0), (0, 0)]

    menu_title = StringProperty("G  A   L   A   X   Y")
    menu_button_title = StringProperty("S T A R T")
    score_txt = StringProperty()

    state_game_over = False
    state_game_has_started = False

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("INIT W : " + str(self.width) + ", H : " + str(self.height))
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()
        
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        
        Clock.schedule_interval(self.update, 1.0/60.0)
        self.sound_galaxy.play()
    

    def init_audio (self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_impact.volume = .6
        self.sound_gameover_voice.volume = .25
        self.sound_music.volume = 1
        self.sound_restart.volume = .25


    def reset_game (self):
        self.current_offset_y = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.current_y_loop = 0
        self.tiles_cordinates = []
        self.score_txt = "SCORE : " + str(self.current_y_loop)
        self.pre_fill_tiles_cordinates()
        self.generate_tiles_cordinates()
        self.state_game_over = False


    def is_desktop (self):
        if platform in ('win', 'linux', 'macosx'):
            return True
        return False


    def init_ship (self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    
    def update_ship (self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width/2
        ship_height = self.SHIP_HEIGHT * self.height

        self.ship_cordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_cordinates[1] = (center_x, base_y + ship_height)
        self.ship_cordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_cordinates[0])     #      2
        x2, y2 = self.transform(*self.ship_cordinates[1])         #    /  \
        x3, y3 = self.transform(*self.ship_cordinates[2])     #   1 -- 3
        
        self.ship.points = [x1, y1, x2, y2, x3, y3]


    def check_ship_collision (self):
        for i in range(0, len(self.tiles_cordinates)):
            ti_x, ti_y = self.tiles_cordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False


    def check_ship_collision_with_tile (self, ti_x, ti_y):
        x_min, y_min = self.get_tile_cordinates(ti_x, ti_y)
        x_max, y_max = self.get_tile_cordinates(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_cordinates[i]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return True
        return False


    def init_tiles (self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())


    def pre_fill_tiles_cordinates (self):
        # 10 straight tiles
        for i in range(0, 10):
            self.tiles_cordinates.append((0, i))


    def generate_tiles_cordinates (self):
        last_y = 0 
        last_x = 0
        # clean the cordinates that are out of the screen
        for i in range(len(self.tiles_cordinates)-1, 0, -1):
            if self.tiles_cordinates[i][1] < self.current_y_loop:
                del self.tiles_cordinates[i]

        if len(self.tiles_cordinates) > 0:
            last_cordinates = self.tiles_cordinates[-1]
            last_y = last_cordinates[1] + 1
            last_x = last_cordinates[0]

        for i in range(len(self.tiles_cordinates), self.NB_TILES):
            r = random.randint(0, 2)
            start_index = - int(self.V_NB_LINES/2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            
            if last_x <= start_index + 1:
                r = 1
            if last_x >= end_index - 2:
                r = 2
            self.tiles_cordinates.append((last_x, last_y))
            
            if r == 1: # right
                last_x += 1
                self.tiles_cordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_cordinates.append((last_x, last_y))
            if r == 2: # left
                last_x -= 1
                self.tiles_cordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_cordinates.append((last_x, last_y))
            last_y += 1


    def init_vertical_lines (self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[self.width/2, 0, self.width/2, 100])
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())


    def get_line_x_from_index (self, index):
        center_line_x = self.perspective_point_x
        spacing = int(self.V_LINE_SPACING * self.width)
        offset = index - 0.5
        line_x = center_line_x + (offset * spacing) + self.current_offset_x
        return line_x
    

    def get_line_y_from_index (self, index):
        spacing_y = self.H_LINE_SPACING * self.height 
        line_y = index * spacing_y - self.current_offset_y
        return line_y


    def get_tile_cordinates (self, tile_x, tile_y):
        tile_y = tile_y - self.current_y_loop
        x = self.get_line_x_from_index(tile_x)
        y = self.get_line_y_from_index(tile_y)
        return x , y


    def update_tiles (self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_cordinates = self.tiles_cordinates[i]
            x_min, y_min = self.get_tile_cordinates(tile_cordinates[0], tile_cordinates[1])
            x_max, y_max = self.get_tile_cordinates(tile_cordinates[0]+1, tile_cordinates[1]+1)
            
            x1, y1 = self.transform(x_min, y_min)   #   2 - 3
            x2, y2 = self.transform(x_min, y_max)   #   |   |
            x3, y3 = self.transform(x_max, y_max)   #   1 - 4
            x4, y4 = self.transform(x_max, y_min)   #

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]


    def update_vertical_lines (self):
        # -1 | 0 | 1 | 2
        start_index = - int(self.V_NB_LINES/2) + 1
        for i in range(start_index, start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i) 
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]


    def init_horizontal_lines (self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[self.width/2, 0, self.width/2, 100])
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())


    def update_horizontal_lines (self):
        start_index = - int(self.V_NB_LINES/2) + 1
        end_index = start_index + self.V_NB_LINES - 1
        x_min = self.get_line_x_from_index(start_index)
        x_max = self.get_line_x_from_index(end_index)
        
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]


    def update (self, dt):
        # print("delta time : " + str(dt) + "- 1/60 : " + str(1.0/60.0))
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINE_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = "SCORE : " + str(self.current_y_loop)
                self.generate_tiles_cordinates()
                print("loop : " + str(self.current_y_loop))

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += self.current_speed_x * time_factor

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.menu_title = "G    A   M   E       O   V   E   R"
            self.menu_button_title = "R E S T A R T"
            self.menu_widget.opacity = 1
            self.sound_gameover_impact.play() 
            Clock.schedule_once(self.play_game_over_voice_sound, 3)
            self.sound_music.stop()
            print("GAME OVER!")


    def play_game_over_voice_sound (self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()

    def on_menu_button_pressed (self):
        print("BUTTON")

        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music.play()

        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        


class GalaxyApp (App):
    pass

GalaxyApp().run()