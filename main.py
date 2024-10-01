from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, Clock
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line

class MainWidget(Widget):
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)
    
    V_NB_LINES = 10 # number of vertical lines that we going to use
    V_LINE_SPACING = .25 # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 15 # number of horizontal lines that we going to use
    H_LINE_SPACING = .1 # percentage in screen height
    horizontal_lines = []
    
    SPEED = 3
    current_offset_y = 0
    
    SPEED_X = 1
    current_offset_x = 0

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("INIT W : " + str(self.width) + ", H : " + str(self.height))
        self.init_vertical_lines()
        self.init_horizontal_lines()
        Clock.schedule_interval(self.update, 1.0/60.0)

    def on_parent (self, widget, parent):
        print("ON PARENT W : " + str(self.width) + ", H : " + str(self.height))

    def on_size (self, *args):
        # print("ON SIZE W : " + str(self.width) + ", H : " + str(self.height))
        # self.perspective_point_x = self.width/2
        # self.perspective_point_y = self.height * 0.75
        # self.update_vertical_lines()
        # self.update_horizontal_lines()
        pass

    def on_perspective_point_x (self, widget, value):
        # print("PX : " + str(value))
        pass
    
    def on_perspective_point_y (self, widget, value):
        # print("PY : " + str(value))
        pass

    def init_vertical_lines (self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[self.width/2, 0, self.width/2, 100])
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())
    
    def update_vertical_lines (self):
        center_line_x = int(self.width / 2)
        offset = - int(self.V_NB_LINES / 2) + 0.5
        spacing = int(self.V_LINE_SPACING * self.width)
        # self.line.points = [center_x, 0, center_x, 100]
        for i in range(0, self.V_NB_LINES):
            line_x = center_line_x + (offset * spacing) + self.current_offset_x 
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]
            offset += 1

    def init_horizontal_lines (self):
        with self.canvas:
            Color(1, 1, 1)
            # self.line = Line(points=[self.width/2, 0, self.width/2, 100])
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())
    
    def update_horizontal_lines (self):
        center_line_y = int(self.width / 2)
        offset = int(self.V_NB_LINES / 2) - 0.5
        spacing = int(self.V_LINE_SPACING * self.width)
        x_min = center_line_y - (offset * spacing) + self.current_offset_x
        x_max = center_line_y + (offset * spacing) + self.current_offset_x
        spacing_y = self.H_LINE_SPACING * self.height 
        for i in range(0, self.H_NB_LINES):
            line_y = i * spacing_y - self.current_offset_y
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def transform (self, x, y):
        # return self.transform_2D(x, y)
        return self.transform_perspective(x, y)

    def transform_2D (self, x, y):
        return int(x), int(y)
    
    def transform_perspective (self, x, y):
        linear_y = y * self.perspective_point_y / self.height
        if linear_y > self.perspective_point_y:
            linear_y = self.perspective_point_y

        gap_x = x - self.perspective_point_x
        gap_y = self.perspective_point_y - linear_y
        factor_y = gap_y/self.perspective_point_y # 1 when gap_y == self.perspective_point_y | 0 when gap_y == 0
        factor_y = pow(factor_y, 4)

        tr_x = self.perspective_point_x + (gap_x * factor_y)
        tr_y = (1 - factor_y) * self.perspective_point_y

        return int(tr_x), int(tr_y)
    
    def update (self, dt):
        # print("delta time : " + str(dt) + "- 1/60 : " + str(1.0/60.0))
        time_factor = dt * 60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.current_offset_y += self.SPEED * time_factor

        spacing_y = self.H_LINE_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y
        self.current_offset_x += self.SPEED_X * time_factor


class GalaxyApp (App):
    pass

GalaxyApp().run()