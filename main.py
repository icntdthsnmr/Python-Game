import arcade

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720 
SCREEN_TITLE = "Swordance"

CHARACTER_SCALING = 1
TILE_SCALING = 1
Z_HEAD_SCALING = 1
ENEMY_SCALING = 1

PLAYER_MOVEMENT_SPEED = 10
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
HIGH_JUMP_SPEED = 30
HIGH_JUMP_COOLDOWN = 3

ENEMY_MOVEMENT_SPEED = 7

class MyGame(arcade.Window):

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        self.character_direction = "right"
        self.game_over = False

        self.tile_map = None
        self.scene = None

        self.player_sprite = None
        self.player_speed_y = 0
        self.player_can_jump = False

        self.camera = None
        self.gui_camera = None

        self.score = 0
        self.high_jump_active = False
        self.high_jump_timer = 0
        self.can_high_jump = True

        self.attack_timer = 0
        self.attack_duration = 0.5
        self.is_attacking = False

        self.sword_sound = arcade.load_sound("sounds/sword_sound.mp3")
        self.jump_sound = arcade.load_sound("sounds/jump_sound.mp3")
        self.take_sound = arcade.load_sound("sounds/take_sound.mp3")

    def setup(self):

        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)

        self.score = 0

        map_name = "maps/map.json"
        layer_options = {
            "Floor": {"use_spatial_hash": False},
        }
        self.tile_map = arcade.load_tilemap(map_name, TILE_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)

        self.player_list = arcade.SpriteList()
        image_source = "img/main_pers.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 150
        self.player_sprite.center_y = 250
        self.scene.add_sprite("Player", self.player_sprite)

        coordinate_list = [[646, 175], [880, 718], [2451, 555], [1855, 625], [1396, 462], [3236, 180], [4560, 620], [4590, 845], [4000, 272], [1156, 590], [2100, 780], [4227, 272]]
        for coord in coordinate_list:
            z_head = arcade.Sprite("img/zombie_head.png", Z_HEAD_SCALING)
            z_head.center_x = coord[0]
            z_head.center_y = coord[1]
            self.scene.add_sprite("z_heads", z_head)

        self.enemy_sprite = arcade.Sprite("img/zombie_right.png", ENEMY_SCALING)
        self.enemy_sprite.center_x = 750
        self.enemy_sprite.center_y = 222
        self.enemy_sprite.change_x = ENEMY_MOVEMENT_SPEED  
        self.scene.add_sprite("enemies", self.enemy_sprite)

        self.portal_sprite = None
        if self.score >= 12 and self.portal_sprite is None:
            self.portal_sprite = arcade.Sprite("img/portal.png")
            self.portal_sprite.center_x = 5064
            self.portal_sprite.center_y = 935
            self.scene.add_sprite("portals", self.portal_sprite)

        self.game_over = False

    def on_draw(self):
        arcade.start_render()
        self.clear()
        self.camera.use()
        self.scene.draw()

        if self.player_sprite.center_y < -60:
            arcade.draw_text("Press R to restart", self.player_sprite.center_x, 350, arcade.color.WHITE, 12, anchor_x="center")
        
        self.gui_camera.use()
        score_text = f"Собрано голов: {self.score} из 12" if self.player_sprite.center_x <= 6300 else "Пройди до конца!"
        arcade.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)

        if not self.can_high_jump:
            cooldown_text = f"Перезарядка способности: {self.high_jump_timer:.1f}"
            arcade.draw_text(cooldown_text, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20, arcade.csscolor.WHITE, 18, anchor_x="center")

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player_sprite.center_y - (self.camera.viewport_height / 2)
        screen_center_x = max(screen_center_x, 0)
        screen_center_y = max(screen_center_y, 0)
        self.camera.move_to((screen_center_x, screen_center_y))

    def custom_check_for_collision(self, sprite1, sprite2):
        return (sprite1.right > sprite2.left and
                sprite1.left < sprite2.right and
                sprite1.top > sprite2.bottom and
                sprite1.bottom < sprite2.top)

    def check_player_floor_collisions(self):
        self.player_can_jump = False
        for sprite in self.scene["Floor"]:
            if self.custom_check_for_collision(self.player_sprite, sprite):
                if self.player_sprite.bottom <= sprite.top < self.player_sprite.center_y:
                    self.player_sprite.bottom = sprite.top
                    self.player_speed_y = 0
                    self.player_can_jump = True
                elif self.player_sprite.top >= sprite.bottom > self.player_sprite.center_y:
                    self.player_sprite.top = sprite.bottom
                    self.player_speed_y = 0
                elif self.player_sprite.right >= sprite.left > self.player_sprite.center_x:
                    self.player_sprite.right = sprite.left
                elif self.player_sprite.left <= sprite.right < self.player_sprite.center_x:
                    self.player_sprite.left = sprite.right

    def check_enemy_floor_collisions(self):
        for enemy in self.scene["enemies"]:
            enemy.center_x += enemy.change_x
            for wall in self.scene["Floor"]:
                if self.custom_check_for_collision(enemy, wall):
                    enemy.change_x *= -1
                    if enemy.change_x > 0:
                        enemy.texture = arcade.load_texture("img/zombie_right.png")  # Спрайт зомби смотрящий направо
                    else:
                        enemy.texture = arcade.load_texture("img/zombie.png")  # Спрайт зомби смотрящий налево
                    break


    def calculate_collision_with_enemy(self):
        for enemy in self.scene["enemies"]:
            if self.custom_check_for_collision(self.player_sprite, enemy):
                if self.player_speed_y > 0:
                    self.player_sprite.center_y = enemy.center_y + enemy.height / 2 + self.player_sprite.height / 2
                    self.player_speed_y = 0
                else:
                    if self.player_sprite.center_x < enemy.center_x:
                        self.player_sprite.right = enemy.left
                    else:
                        self.player_sprite.left = enemy.right
                    self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        if not self.game_over:
            self.player_speed_y -= GRAVITY

            self.player_sprite.center_x += self.player_sprite.change_x
            self.player_sprite.center_y += self.player_speed_y

            self.check_player_floor_collisions()
            self.calculate_collision_with_enemy()
            self.check_enemy_floor_collisions()

            for z_head in self.scene["z_heads"]:
                if self.custom_check_for_collision(self.player_sprite, z_head):
                    z_head.remove_from_sprite_lists()
                    self.score += 1
                    arcade.play_sound(self.take_sound)

            self.center_camera_to_player()

            if self.player_sprite.center_y < -60:
                self.game_over = True

            if not self.can_high_jump:
                self.high_jump_timer -= delta_time
                if self.high_jump_timer <= 0:
                    self.can_high_jump = True
                    self.high_jump_timer = 0

            if self.score >= 12 and self.portal_sprite is None:
                self.portal_sprite = arcade.Sprite("img/portal.png")
                self.portal_sprite.center_x = 5064
                self.portal_sprite.center_y = 924
                self.scene.add_sprite("portals", self.portal_sprite)

            if self.portal_sprite and self.custom_check_for_collision(self.player_sprite, self.portal_sprite):
                self.player_sprite.center_x = 6294 
                self.player_sprite.center_y = 988

            if self.player_sprite.center_x >= 11064 and self.player_sprite.center_y == 252:
                arcade.close_window()

            self.attack_timer += delta_time
            if self.is_attacking and self.attack_timer >= self.attack_duration:
                self.is_attacking = False
                self.attack_timer = 0
                self.player_sprite.texture = arcade.load_texture("img/main_pers.png")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R and self.game_over:
            self.setup()
            self.game_over = False
        if not self.game_over:
            if key in [arcade.key.UP, arcade.key.SPACE] and self.player_can_jump:
                arcade.play_sound(self.jump_sound, volume=0.5)
                self.player_speed_y = PLAYER_JUMP_SPEED
            elif key in [arcade.key.LEFT, arcade.key.A]:
                self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
                self.character_direction = "left"
                self.player_sprite.texture = arcade.load_texture("img/main_pers_running_left.png")
            elif key in [arcade.key.RIGHT, arcade.key.D]:
                self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
                self.character_direction = "right"
                self.player_sprite.texture = arcade.load_texture("img/main_pers_running.png")
            elif key == arcade.key.LSHIFT and self.player_can_jump and self.can_high_jump:
                self.player_speed_y = HIGH_JUMP_SPEED
                self.can_high_jump = False
                self.high_jump_timer = HIGH_JUMP_COOLDOWN

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LEFT, arcade.key.A, arcade.key.RIGHT, arcade.key.D]:
            self.player_sprite.change_x = 0
            self.player_sprite.texture = arcade.load_texture("img/main_pers.png")
        if key == arcade.key.LSHIFT:
            self.high_jump_active = False

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT and not self.game_over:
            arcade.play_sound(self.sword_sound)
            if self.character_direction == "right":
                self.player_sprite.texture = arcade.load_texture("img/pers_attack.png")
            elif self.character_direction == "left":
                self.player_sprite.texture = arcade.load_texture("img/pers_attack_left.png")
            self.is_attacking = True
            self.attack_timer = 0

def main():
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
