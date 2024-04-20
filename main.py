"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1000 
SCREEN_HEIGHT = 650 
SCREEN_TITLE = "Swordance"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 0.3
TILE_SCALING = 0.5

JUMP_MAX_HEIGHT = 100
PLAYER_JUMP_SPEED = 3

PLAYER_X_SPEED = 5
PLAYER_Y_SPEED = 5

PLATFORM_SCALE = 0.5

# Movement speed of player, in pixels per frame (мне не нужно)
# PLAYER_MOVEMENT_SPEED = 5 

class MyGame(arcade.Window):
    """
    Main application class.
    """

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.wall_list = None
        self.player_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        self.camera = None

        self.player_jump = False
        self.player_start = None
        self.camera_max = 0

        self.key_right_pressed = False
        self.key_left_pressed = False

        self.collide = False

        self.player_dx = PLAYER_X_SPEED
        self.player_dy = PLAYER_Y_SPEED

        arcade.set_background_color(arcade.csscolor.BLUE)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        
        self.camera = arcade.Camera(self.width, self.height)

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        # Set up the player, specifically placing it at these coordinates.
        image_source = "img/prob_pers.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 125
        self.player_list.append(self.player_sprite)

        self.jump_start = self.player_sprite.center_y

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        # Put some crates on the ground
        # This shows using a coordinate list to place sprites
        coordinate_list = [[512, 96], [256, 96], [768, 96]]

        for coordinate in coordinate_list:
            # Add a crate on the ground
            wall = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png", PLATFORM_SCALE
            )
            #wall.position = coordinate
            wall.center_x = coordinate[0]
            wall.center_y = coordinate[1]
            self.wall_list.append(wall)

    def on_draw(self):
        """Render the screen."""

        self.clear()
        # Code to draw the screen goes here

        self.camera.use()

        # Draw our sprites
        self.wall_list.draw()
        self.player_list.draw()


    #НЕ ДЛЯ МОЕЙ ИГРЫ !!! !!! !!!
    #
    #
    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.
        viewport_width / 2)
        if self.player_sprite.center_y - (self.camera.viewport_height / 2) >= self.camera_max:
            screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)
            self.camera_max = self.player_sprite.center_y - (self.camera.viewport_height / 2)
        else:
            screen_center_y = self.camera_max


        # Don't let camera travel past 0
        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def player_movement(self):

        if self.collide:
            self.player_dx = 0
            self.player_dy = 0
        else:
            self.player_dx = PLAYER_X_SPEED
            self.player_dy = PLAYER_Y_SPEED

        if self.key_left_pressed:
            self.player_sprite.center_x -= self.player_dx
        if self.key_right_pressed:
            self.player_sprite.center_x += self.player_dx


        if self.player_jump:
            self.player_sprite.center_y += self.player_dy
            if self.player_sprite.center_y > self.jump_start + JUMP_MAX_HEIGHT:
                self.player_jump = False
        else:
            if self.player_sprite.center_y > self.jump_start:
                self.player_sprite.center_y -= self.player_dy


    def _get_width(self) -> float:
        return self.width
    
    def _get_height(self) -> float:
        return self.height

    arcade.Sprite._get_width = _get_width
    arcade.Sprite._get_height = _get_height


    def calculate_collision(self):
        self.collide = False
        for block in self.wall_list:
            if block.center_x + block._get_width() / 2 >= self.player_sprite.center_x >= block.center_x - block._get_width() / 2 \
            and block.center_y + block._get_height() / 2 >= self.player_sprite.center_y >= block.center_y - block._get_height() / 2:
                self.collide = True
            


    def on_update(self, delta_time):
        """Movement and game logic"""


        self.center_camera_to_player()
        #self.player_sprite.center_y += 0.5
        #self.player_sprite.center_x += 0.5

        self.player_movement()

        if self.player_jump:
            self.collide = False
        else:
            self.calculate_collision()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_jump = True
            self.jump_start = self.player_sprite.center_y
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.center_y -= 20
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.key_left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.key_right_pressed = True
        #elif key == arcade.key.SPACE:  (если нужно будет, то 148-149 строка копир)

    def on_key_release(self, key, modifiers):

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.key_left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.key_right_pressed = False
        
        
def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()