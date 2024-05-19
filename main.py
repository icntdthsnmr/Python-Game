"""
Platformer Game
"""
import arcade

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720 
SCREEN_TITLE = "Swordance"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 1
Z_HEAD_SCALING = 1
ENEMY_SCALING = 1

PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
HIGH_JUMP_SPEED = 30
HIGH_JUMP_COOLDOWN = 1

'''JUMP_MAX_HEIGHT = 100

PLAYER_X_SPEED = 5
PLAYER_Y_SPEED = 5
'''


class MyGame(arcade.Window):
 
    def __init__(self):

        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.character_direction = "right"

        self.game_over = False

        self.tile_map = None

        self.scene = None

        '''self.wall_list = None
        self.player_list = None'''

        self.player_sprite = None

        self.physics_engine = None

        self.camera = None

        self.gui_camera = None

        self.score = 0

        self.high_jump_active = False

        self.player_jump = False
        self.player_start = None
        self.camera_max = 0

        self.high_jump_cooldown = HIGH_JUMP_COOLDOWN
        self.high_jump_timer = 0
        self.can_high_jump = True

        self.attack_timer = 0
        self.attack_duration = 0.5
        self.is_attacking = False

    def setup(self):
        self.camera = arcade.Camera(self.width, self.height)

        self.gui_camera = arcade.Camera(self.width, self.height)

        self.score = 0

        map_name = "maps/map.json"

        layer_options = {
            "Floor": {
                "use_spatial_hash": True,
            },
            "Obstacle": {
                "use_spatial_hash": False,
            },
        }
        
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.player_list = arcade.SpriteList() 
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        image_source = "img/main_pers.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 250
        self.scene.add_sprite("Player", self.player_sprite)

        coordinate_list = [[646, 175], [880, 718], [2451, 555], [1855, 625], [1396, 462], [3236, 180], [4560, 620], [4590, 845], [3783, 272], [1106, 590], [2100, 780], [4227, 272]]

        for i in range(12):
            z_head = arcade.Sprite("img/zombie_head.png", Z_HEAD_SCALING)
            z_head.center_x = coordinate_list[i][0]
            z_head.center_y = coordinate_list[i][1]
            self.scene.add_sprite("z_heads", z_head)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, gravity_constant=GRAVITY, walls=self.scene["Floor"])

        for sprite in self.scene["Floor"]:
            self.wall_list.append(sprite)

        self.background_music = arcade.load_sound("sounds/KOHTA YAMAMOTO - Ashes on The Fire.mp3")
        arcade.play_sound(self.background_music, volume=0.01)

        self.enemy_sprite = arcade.Sprite("img/zombie.png", ENEMY_SCALING)
        self.enemy_sprite.center_x = 750
        self.enemy_sprite.center_y = 222
        self.scene.add_sprite("enemies", self.enemy_sprite)

        self.portal_sprite = None

        if self.score >= 12 and self.portal_sprite is None:

            portal_sprite = arcade.Sprite("img/portal.png")

            portal_sprite.center_x = 5064
            portal_sprite.center_y = 935

            self.scene.add_sprite("portals", portal_sprite)


        self.game_over = False

    def on_draw(self):
        arcade.start_render()

        self.clear()  

        self.camera.use()

        self.scene.draw()

        if self.player_sprite.center_y < -60:
            arcade.draw_text(f"Press R to restart", self.player_sprite.center_x, 350, arcade.color.WHITE, 12, anchor_x="center")
        
        self.gui_camera.use()

        score_text = f"Собрано голов: {self.score} из 12"
        arcade.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)

        if not self.can_high_jump:
            cooldown_text = f"Перезарядка способности: {self.high_jump_timer:.1f}"
            arcade.draw_text(cooldown_text, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20, arcade.csscolor.WHITE, 18, anchor_x="center")


    def center_camera_to_player(self):

        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)

        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0

        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)
    
    def on_update(self, delta_time):
        if not self.game_over:
            self.physics_engine.update()

            move_vector = self.player_sprite.change_x, self.player_sprite.change_y
        
            self.player_sprite.change_x, self.player_sprite.change_y = move_vector

            self.calculate_collision_with_enemy()

            if self.check_for_collision_manual():

                self.player_sprite.center_x -= self.player_sprite.change_x
                self.player_sprite.center_y -= self.player_sprite.change_y

            z_head_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.scene["z_heads"])

            for z_head in z_head_hit_list:
                z_head.remove_from_sprite_lists()
                self.score += 1
            
            self.center_camera_to_player()

            print("Координаты персонажа: ", self.player_sprite.center_x, self.player_sprite.center_y)
            if self.player_sprite.center_y < -60:
                self.game_over = True

            if not self.can_high_jump:
                self.high_jump_timer -= delta_time
                if self.high_jump_timer <= 0:
                    self.can_high_jump = True
                    self.high_jump_timer = 0

            if self.score >= 12 and self.portal_sprite is None:
                portal_sprite = arcade.Sprite("img/portal.png")
                portal_sprite.center_x = 5064
                portal_sprite.center_y = 924

                self.portal_sprite = portal_sprite
                self.scene.add_sprite("portals", portal_sprite)

            if self.portal_sprite and arcade.check_for_collision(self.player_sprite, self.portal_sprite):
                
                new_x = 6294 
                new_y = 988  

                self.player_sprite.center_x = new_x
                self.player_sprite.center_y = new_y

    def _get_width(self) -> float:
        return self.width
    
    def _get_height(self) -> float:
        return self.height

    arcade.Sprite._get_width = _get_width
    arcade.Sprite._get_height = _get_height

    def calculate_collision_with_enemy(self):

        self.collide_with_enemy = False
        player_left = self.player_sprite.center_x - self.player_sprite.width / 2
        player_right = self.player_sprite.center_x + self.player_sprite.width / 2
        player_bottom = self.player_sprite.center_y - self.player_sprite.height / 2
        player_top = self.player_sprite.center_y + self.player_sprite.height / 2

        enemy_left = self.enemy_sprite.center_x - self.enemy_sprite.width / 2
        enemy_right = self.enemy_sprite.center_x + self.enemy_sprite.width / 2
        enemy_bottom = self.enemy_sprite.center_y - self.enemy_sprite.height / 2
        enemy_top = self.enemy_sprite.center_y + self.enemy_sprite.height / 2

        if (
            player_right >= enemy_left
            and player_left <= enemy_right
            and player_top >= enemy_bottom
            and player_bottom <= enemy_top
        ):
            self.collide_with_enemy = True

    def check_for_collision_manual(self):
        player_center_x = self.player_sprite.center_x
        player_center_y = self.player_sprite.center_y
        enemy_center_x = self.enemy_sprite.center_x
        enemy_center_y = self.enemy_sprite.center_y
        
        distance_x = abs(player_center_x - enemy_center_x)
        distance_y = abs(player_center_y - enemy_center_y)
        
        collision_threshold = 80
        
        if distance_x < collision_threshold and distance_y < collision_threshold:
            if self.player_sprite.change_y > 0:
                # Если персонаж движется вверх (прыгает), то позволяем продолжить движение вверх
                return False
            else:
                # Иначе, позволяем продолжить движение в том направлении, в котором он двигался до коллизии
                return True
        else:
            return False
        
   
    def on_key_press(self, key, modifiers):

        if key == arcade.key.R and self.game_over:
            self.setup()
            self.game_over = False
        if not self.game_over:
            if key == arcade.key.UP or key == arcade.key.SPACE:
                if self.physics_engine.can_jump():
                    self.player_sprite.change_y = PLAYER_JUMP_SPEED
            elif key == arcade.key.LEFT or key == arcade.key.A:
                self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
                self.character_direction = "left"
                self.player_sprite.texture = arcade.load_texture("img/main_pers_running_left.png")
            elif key == arcade.key.RIGHT or key == arcade.key.D: 
                self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
                self.character_direction = "right"
                self.player_sprite.texture = arcade.load_texture("img/main_pers_running.png")
            elif key == arcade.key.LSHIFT:  
                if self.physics_engine.can_jump() and self.can_high_jump:
                    self.player_sprite.change_y = HIGH_JUMP_SPEED
                    self.can_high_jump = False
                    self.high_jump_timer = HIGH_JUMP_COOLDOWN

    def on_key_release(self, key, modifiers):

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0
        self.player_sprite.texture = arcade.load_texture("img/main_pers.png")
        if key == arcade.key.SPACE:
            if self.character_direction == "left":
                self.player_sprite.texture = arcade.load_texture("img/main_pers_running_left.png")
            elif self.character_direction == "right":
                self.player_sprite.texture = arcade.load_texture("img/main_pers_running.png")
        if key == arcade.key.LSHIFT:
            self.high_jump_active = False
    
    def on_mouse_press(self, x, y, button, modifiers):
        if not self.game_over and button == arcade.MOUSE_BUTTON_LEFT:
            self.player_sprite.texture = arcade.load_texture("img/pers_attack.png")
            self.is_attacking = True
            self.attack_timer = self.attack_duration
                  
def main():
    """Main function"""
    window = MyGame()
    window.setup()
    arcade.run()    


if __name__ == "__main__":
    main()