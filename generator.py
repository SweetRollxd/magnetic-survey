from extras import Point, Cell, draw_mesh


def generate_mesh(point_start: Point,
                  point_end: Point,
                  count_x: int = 1,
                  count_y: int = 1,
                  count_z: int = 1):

    mesh = []
    length = (point_end.x - point_start.x) / count_x
    width = (point_end.y - point_start.y) / count_y
    height = (point_end.z - point_start.z) / count_z
    x = point_start.x
    # print(f"length = {length}, width = {width}, height = {height}")
    for i in range(count_x):
        y = point_start.y
        for j in range(count_y):
            z = point_start.z
            for k in range(count_z):
                mesh.append(Cell(x + length/2, y + width/2, z + height/2,
                                 length, width, height))
                z += height
            y += width
        x += length

    return mesh


if __name__ == '__main__':
    start_pnt = Point(-500, 0, 0)
    end_pnt = Point(400, 0, -300)
    generated_mesh = generate_mesh(start_pnt, end_pnt, 9, 1, 6)
    # generated_mesh[]
    # print(generated_mesh)
    # draw_mesh('generated_mesh.png', generated_mesh)
