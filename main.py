"""
File: asteroids.py
Original Author: Br. Burton
Designed to be completed by others
This program implements the asteroids game.
"""
import arcade
import random
import math  # used for sin, cos, and M_PI
from abc import ABC, abstractmethod

# These are Global constants to use throughout the game
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

BULLET_RADIUS = 30
BULLET_SPEED = 10
BULLET_LIFE = 60

SHIP_TURN_AMOUNT = 3
SHIP_THRUST_AMOUNT = 0.25
SHIP_RADIUS = 30

INITIAL_ROCK_COUNT = 5

BIG_ROCK_SPIN = 1
BIG_ROCK_SPEED = 1.5
BIG_ROCK_RADIUS = 15

MEDIUM_ROCK_SPIN = -2
MEDIUM_ROCK_RADIUS = 5

SMALL_ROCK_SPIN = 5
SMALL_ROCK_RADIUS = 2


def random_angle():
    return random.uniform(1, 360)


class Point:
    """Defines points x/y"""
    def __init__(self):
        self.x = random.uniform(0, 3)
        self.y = random.uniform(0, 3)


class Velocity:
    """Defines Velocity dx/dy"""

    def __init__(self):
        self.dx = float()
        self.dy = float()


class SpaceObject(ABC):
    """Gives base class for all space objects in the game."""

    def __init__(self):
        self.center = Point()
        self.center.x = 0
        self.center.y = 0
        self.radius = 1
        self.height = 0
        self.width = 0
        self.velocity = Velocity()
        self.alive = True
        self.angle = random_angle()

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def advance(self):
        pass

    def update(self):
        self.boundary_right = self.center.x + (self.width / 2)
        self.boundary_left = self.center.x - (self.width / 2)
        self.boundary_top = self.center.y + (self.height / 2)
        self.boundary_bottom = self.center.y - (self.height / 2)
        if self.boundary_right > SCREEN_WIDTH:
            self.center.x = 0 + (self.width / 2)
        if self.boundary_left < 0:
            self.center.x = SCREEN_WIDTH - (self.width / 2)
        if self.boundary_bottom < 0:
            self.center.y = SCREEN_HEIGHT - (self.height / 2)
        if self.boundary_top > SCREEN_HEIGHT:
            self.center.y = 0 + (self.height / 2)


class Ship(SpaceObject):
    """Defines the ship that the player controls."""

    def __init__(self):
        super().__init__()
        self.radius = SHIP_RADIUS
        self.center.x = SCREEN_WIDTH / 2
        self.center.y = SCREEN_HEIGHT / 2
        self.inertia = False
        self.speed = 0
        self.ship_img = "images/playerShip1_orange.png"
        self.texture = arcade.load_texture(self.ship_img)
        self.width = self.texture.width
        self.height = self.texture.height
        self.last_angle_rad = 0
        self.lives = 3

    def draw(self):
        super().draw()
        alpha = 255
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.width, self.height, self.texture, self.angle,
                                      alpha)

    def advance(self):
        super().advance()
        self.center.x += self.velocity.dx
        self.center.y += self.velocity.dy

    def update(self):
        super().update()
        if 65361 in window.held_keys:
            self.turn_left()

        if 65363 in window.held_keys:
            self.turn_right()

        if (65362 in window.held_keys) or self.inertia:
            self.move_forward()

    def turn_left(self):
        self.angle += SHIP_TURN_AMOUNT

    def turn_right(self):
        self.angle -= SHIP_TURN_AMOUNT

    def move_forward(self):
        """this moves the ship in the direction it's pointing"""
        self.speed = .05
        angle_rad = math.radians(self.angle)
        self.last_angle_rad = angle_rad
        self.velocity.dx -= self.speed * math.sin(angle_rad)
        self.velocity.dy += self.speed * math.cos(angle_rad)

    def hit(self):
        self.lives -= 1
        if self.lives <= 0:
            self.alive == False


class Lives:
    """This class tracks the lives the player has, represented by ships in the lower left hand corner of the game."""
    def __init__(self):
        self.center = Point()
        self.center.x = 35
        self.center.y = 20
        self.texture = arcade.load_texture("images/playerLife1_orange.png")
        self.width = self.texture.width
        self.height = self.texture.height
        self.angle = 180
        self.ship = window.ship
        # the lives aren't updating because it's not getting the active lives and that's VERY FRUSTRATING.

    def draw(self):
        """used for drawing the ships in the lower left hand corner."""
        for x in range(self.ship.lives):
            print(self.ship.lives)
            arcade.draw_texture_rectangle(self.center.x * x + 20, self.center.y, self.width, self.height, self.texture, self.angle, 255)


class Bullets(SpaceObject):
    """Defines the bullets that the spaceship shoots"""

    def __init__(self):
        super().__init__()
        self.bullet_img = "images/laserBlue01.png"
        self.texture = arcade.load_texture(self.bullet_img)
        self.width = self.texture.width
        self.height = self.texture.height
        self.radius = BULLET_RADIUS
        self.ship = window.ship
        self.center.x = window.ship.center.x
        self.center.y = window.ship.center.y
        self.angle = window.ship.angle
        self.speed = BULLET_SPEED
        self.shoot_sound = arcade.load_sound(":resources:sounds/laser2.wav")
        self.life_count = 60

    def draw(self):
        super().draw()

        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.width, self.height, self.texture, self.angle)
        self.life_count -= 1
        if self.life_count <= 0:
            self.alive = False
        self.velocity.dx = math.cos(math.radians(self.angle)) * self.speed
        self.velocity.dy = math.sin(math.radians(self.angle)) * self.speed

    def advance(self):
        super().advance()
        angle_rad = math.radians(self.angle)
        self.center.x -= (self.speed * math.sin(angle_rad)) - self.ship.velocity.dx
        self.center.y += (self.speed * math.cos(angle_rad)) + self.ship.velocity.dy

    def fire(self):
        arcade.play_sound(self.shoot_sound)


class Asteroid(SpaceObject):
    """Base class for Asteroids, inherits from Space Objects"""

    def __init__(self):
        super().__init__()
        self.center.x = random.uniform(0, SCREEN_WIDTH)
        self.center.y = random.uniform(0, SCREEN_HEIGHT)
        self.velocity.dx = math.cos(math.radians(self.angle))
        self.velocity.dy = math.sin(math.radians(self.angle))

    def draw(self):
        super().draw()
        arcade.draw_texture_rectangle(self.center.x, self.center.y, self.width, self.height, self.texture,
                                      self.angle, 255)

    def advance(self):
        super().advance()
        self.angle += BIG_ROCK_SPIN
        self.center.x += self.velocity.dx * BIG_ROCK_SPEED
        self.center.y += self.velocity.dy * BIG_ROCK_SPEED

    def hit(self):
        pass


class LargeAsteroid(Asteroid):
    """Defines Large Asteroids, inheriting from the Asteroid Base Class"""

    def __init__(self):
        super().__init__()
        self.radius = BIG_ROCK_RADIUS
        self.img = "images/meteorGrey_big1.png"
        self.texture = arcade.load_texture(self.img)
        self.width = self.texture.width
        self.height = self.texture.height

    def hit(self):
        """If a large asteroid is hit it breaks into 2 medium asteroids and one small asteroid"""
        super().hit()
        window.rock_list.append(MedAsteroid(self.center.x, self.center.y, "up"))
        window.rock_list.append(MedAsteroid(self.center.x, self.center.y, "down"))
        window.rock_list.append(SmallAsteroid(self.center.x ,self.center.y, "default" ))


class MedAsteroid(Asteroid):
    """Defines Medium Asteroids. Inherits from the base Asteroid class. Rotates -2 degrees per frame, radius 5,
    breaks into two small asteroids"""

    def __init__(self, x_position=(random.uniform(0, SCREEN_WIDTH)), y_position=(random.uniform(0, SCREEN_HEIGHT)),
                 position="default"):
        super().__init__()
        self.radius = MEDIUM_ROCK_RADIUS
        self.img = "images/meteorGrey_med1.png"
        self.texture = arcade.load_texture(self.img)
        self.width = self.texture.width
        self.height = self.texture.height
        self.center.x = x_position
        self.center.y = y_position
        self.position = position

    def advance(self):
        #super().advance()
        self.angle += MEDIUM_ROCK_SPIN
        if self.position == "up":
            #print(self.position, "velo was:\t", self.velocity.dy, ",", self.velocity.dx)
            self.velocity.dy = abs(self.velocity.dy)
            #print(self.position, "velo is:\t", self.velocity.dy, ",", self.velocity.dx)
            self.center.y += self.velocity.dy * (BIG_ROCK_SPEED + 2)

        elif self.position == "down":
            #print(self.position, "velo was:\t", self.velocity.dy, ",", self.velocity.dx)
            if self.velocity.dy > 0:
                self.velocity.dy = -self.velocity.dy
            #print(self.position, "velo is:\t", self.velocity.dy, ",", self.velocity.dx)
            self.center.y += self.velocity.dy * (BIG_ROCK_SPEED + 2)

        else:
            self.center.y += self.velocity.dy * BIG_ROCK_SPEED
        self.center.x += self.velocity.dx * BIG_ROCK_SPEED

    def hit(self):
        """if a medium asteroid is hit it should break into two small asteroids"""
        window.rock_list.append(SmallAsteroid(self.center.x + random.uniform(-50, 50),
                                                self.center.y + random.uniform(-50, 50), "up/left"))
        window.rock_list.append(SmallAsteroid(self.center.x + random.uniform(-50, 50),
                                                self.center.y + random.uniform(-50, 50),"down/right"))


class SmallAsteroid(Asteroid):
    """Defines Small Asteroids, inheriting from the base Asteroid class. Rotates 5 degrees per frame, radius 2,
    if hit remove from game."""

    def __init__(self, x_position=(random.uniform(0, SCREEN_WIDTH)), y_position=(random.uniform(0, SCREEN_HEIGHT)), position="default"):
        super().__init__()
        self.radius = SMALL_ROCK_RADIUS
        self.img = "images/meteorGrey_small1.png"
        self.texture = arcade.load_texture(self.img)
        self.width = self.texture.width
        self.height = self.texture.height
        self.center.x = x_position
        self.center.y = y_position
        self.position = position

    def advance(self):
        super().advance()
        self.angle += SMALL_ROCK_SPIN
        if self.position == "up/left":
            self.velocity.dy = abs(self.velocity.dy)  # up
            self.center.y += self.velocity.dy * (BIG_ROCK_SPEED + 1.5)
            if self.velocity.dx > 0:
                self.velocity.dx = -self.velocity.dx  # making x negative
            self.center.x += self.velocity.dx * (BIG_ROCK_SPEED - 1.5)  # left

        elif self.position =="down/right":
            if self.velocity.dy > 0:  # makes it go down.
                self.velocity.dy = -self.velocity.dy
            self.center.y += self.velocity.dy * (BIG_ROCK_SPEED + 1.5)
            self.velocity.dx = abs(self.velocity.dx)  # right
            self.center.x += self.velocity.dx * (BIG_ROCK_SPEED + 1.5)
        else:
            self.center.x += self.velocity.dx * (BIG_ROCK_SPEED + 5)
            self.center.y += self.velocity.dy * BIG_ROCK_SPEED


class Game(arcade.Window):
    """
    This class handles all the game callbacks and interaction
    This class will then call the appropriate functions of
    each of the above classes.
    You are welcome to modify anything in this class.
    """

    def __init__(self, width, height):
        """
        Sets up the initial conditions of the game
        :param width: Screen width
        :param height: Screen height
        """
        super().__init__(width, height)
        arcade.set_background_color(arcade.color.SMOKY_BLACK)
        self.ship = Ship()
        self.rock_list = []
        self.title = "It Came from Outer Space!"
        for x in range(5):
            self.rock_list.append(LargeAsteroid())
        self.background = arcade.load_texture("images/background.png")
        self.gameover = arcade.load_texture("images/gameover2.png")
        self.magazine = []
        self.held_keys = set()
        self.lives = Lives()
        self.chances = 3
        self.set_vsync(True)  # locking frame update logic to the frame rate of the monitor.


    def on_draw(self):
        """
        Called automatically by the arcade framework.
        Handles the responsibility of drawing all elements.
        """

        # clear the screen to begin drawing
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background, 0, 255)
        self.lives.draw()
        for x in self.rock_list:
            x.draw()

        for bullet in self.magazine:
            bullet.draw()

        if self.ship.alive:
            self.ship.draw()
        else:
            arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.gameover, 0, 255)


    def update(self, delta_time):
        """
        Update each object in the game.
        :param delta_time: tells us how much time has actually elapsed
        """
        self.check_keys()

        for x in self.rock_list:
            x.advance()
            x.update()
        self.ship.advance()
        self.ship.update()
        for bullet in self.magazine:
            bullet.advance()
            bullet.update()

        # TODO: Tell everything to advance or move forward one step in time

        # TODO: Check for collisions
        for bullet in self.magazine:
            for rock in self.rock_list:
                # Make sure they are both alive before checking for a collision
                if bullet.alive and rock.alive:
                    too_close = (bullet.radius + 3) + (rock.radius + 3)

                    if (abs(bullet.center.x - rock.center.x) < too_close and
                            abs(bullet.center.y - rock.center.y) < too_close):
                        # its a hit!
                        bullet.alive = False
                        rock.alive = False
                        """I want to say, for each rock.alive that is false, append 2 self.stone and 1 self.pebble"""
                if self.ship.alive and rock.alive:
                    close = (self.ship.radius + 25) + (rock.radius + 15)
                    if (abs(self.ship.center.x - rock.center.x) < close and abs(self.ship.center.y - rock.center.y) <
                            close):
                        self.ship.hit()


        self.cleanup_zombies()

    def split_asteroid(self, origin_rock):
        origin_rock.hit()

    def cleanup_zombies(self):
        """
        Removes any dead bullets or targets from the list.
        :return:
        """
        for bullet in self.magazine:
            if not bullet.alive:
                self.magazine.remove(bullet)
        for rock in self.rock_list:
            if not rock.alive:
                self.split_asteroid(rock)
                self.rock_list.remove(rock)
        if not self.ship.alive:
            pass #remove ship??

    def check_keys(self):
        """
        This function checks for keys that are being held down.
        You will need to put your own method calls in here.
        """
        if arcade.key.LEFT in self.held_keys:
            self.ship.turn_left()

        if arcade.key.RIGHT in self.held_keys:
            self.ship.turn_right()

        if arcade.key.UP in self.held_keys:
            pass

        if arcade.key.DOWN in self.held_keys:
            pass

        # Machine gun mode...
        # if arcade.key.SPACE in self.held_keys:
        #    pass

    def on_key_press(self, key: int, modifiers: int):
        """
        Puts the current key in the set of keys that are being held.
        You will need to add things here to handle firing the bullet.
        """
        if self.ship.alive:
            self.held_keys.add(key)

            if key == arcade.key.SPACE:
                bullet = Bullets()
                bullet.fire()

                self.magazine.append(bullet)

                # TODO: Fire the bullet here!
                pass

    def on_key_release(self, key: int, modifiers: int):
        """
        Removes the current key from the set of held keys.
        """
        if key in self.held_keys:
            self.held_keys.remove(key)


# Creates the game and starts it going
window = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
window.set_caption(window.title)
arcade.run()
