from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy import platform
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import NumericProperty, Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad

class MainWidget(Widget):

    from transforms import transform, transform_2D, transform_perspective
    from user_actions import on_touch_down, on_touch_up, _on_keyboard_down, _on_keyboard_up, _keyboard_closed

    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    
    V_NB_LINES = 4 # number of vertical lines that we going to use
    V_LINE_SPACING = .1 # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 15 # number of horizontal lines that we going to use
    H_LINE_SPACING = .1 # percentage in screen height
    horizontal_lines = []
    
    SPEED = 1
    current_offset_y = 0
    
    SPEED_X = 10
    current_speed_x = 0
    current_offset_x = 0
    current_y_loop = 0

    NB_TILES = 10
    tiles = []
    tiles_cordinates = []


    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("INIT W : " + str(self.width) + ", H : " + str(self.height))
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.generate_tiles_cordinates()
        
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        
        Clock.schedule_interval(self.update, 1.0/60.0)
    

    def is_desktop (self):
        if platform in ('win', 'linux', 'macosx'):
            return True
        return False


    def init_tiles (self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())


    def generate_tiles_cordinates (self):
        for i in range(0, self.NB_TILES):
            self.tiles_cordinates.append((0, i))


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
        self.current_offset_y += self.SPEED * time_factor

        spacing_y = self.H_LINE_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y
            self.current_y_loop += 1
            print("loop : " + str(self.current_y_loop))
        
        # self.current_offset_x += self.current_speed_x * time_factor


class GalaxyApp (App):
    pass

GalaxyApp().run()