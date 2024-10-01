def transform (self, x, y):
        return self.transform_2D(x, y)
        # return self.transform_perspective(x, y)

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