# Demonstrate the usage of namdtuple objects

import collections


def main():
    # TODO: create a Point namedtuple
    Point = collections.namedtuple("Point", "x y")
    p1 = Point(10,20)
    p2 = Point(30,40)
    print(p1.x,p2.x) #(10, 30)
    print(p1,p2) #(Point(x=10, y=20), Point(x=30, y=40))

    p1 = p1._replace(x=100)
    print(p1) #Point(x=100, y=20)
    # TODO: use _replace to create a new instance
    pass


if __name__ == "__main__":
    main()
