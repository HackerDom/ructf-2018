import random
import mimesis

top = 200000000
down = -200000000


def get_random_cords():
    return random.randint(down, top), random.randint(down, top), random.randint(down, top)


def get_random_header():
    generator = mimesis.Science()
    return "{} {}ous #{}".format(generator.chemical_element(), generator.chemical_element(), random.randint(1, 1000))


def get_random_body():
    generator = mimesis.Food()
    return "Buy our {}! Drink our {}! Fresh {} & {}! Anything at our store!"\
        .format(generator.dish(), generator.drink(), generator.fruit(), generator.vegetable())