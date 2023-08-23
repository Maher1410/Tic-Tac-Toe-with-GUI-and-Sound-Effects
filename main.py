import cv2
import numpy as np
from random import randint
import pygame


class Block:
    def __init__(self, i, j):
        self.value = None
        self.pos = (i, j)

    def set_value(self, value):
        self.value = value


class GUI:
    def __init__(self, window_name):
        pygame.mixer.init()
        self.player_turn_sound = pygame.mixer.Sound('player_turn_sound.wav')
        self.computer_turn_sound = pygame.mixer.Sound('computer_turn_sound.wav')
        self.draw_sound = pygame.mixer.Sound('draw_sound.wav')
        self.player_win_sound = pygame.mixer.Sound('player_win_sound.wav')
        self.computer_win_sound = pygame.mixer.Sound('computer_win_sound.wav')

        self.last_click_time = pygame.time.get_ticks()

        self.player_win_played = False
        self.computer_win_played = False
        self.draw_played = False

        self.window_name = window_name
        self.width, self.height = 400, 400
        self.menu_height = 100
        self.image = np.zeros((self.height + self.menu_height, self.width, 3), np.uint8)
        self.turn = 1
        self.win = False
        self.initialize_game()

    def check_win(self, blocks=None):
        if blocks is None:
            blocks = self.blocks

        for i in range(3):
            if blocks[i][0].value == blocks[i][1].value == blocks[i][2].value and blocks[i][0].value is not None:
                return True
            if blocks[0][i].value == blocks[1][i].value == blocks[2][i].value and blocks[0][i].value is not None:
                return True

        if blocks[0][0].value == blocks[1][1].value == blocks[2][2].value and blocks[0][0].value is not None:
            return True
        if blocks[0][2].value == blocks[1][1].value == blocks[2][0].value and blocks[0][2].value is not None:
            return True

        return False

    def check_draw(self):
        for row in self.blocks:
            for block in row:
                if block.value is None:
                    return False
        return True

    def initialize_game(self):
        self.blocks = [[Block(i, j) for j in range(3)] for i in range(3)]
        self.win = False
        self.player_win_played = False
        self.computer_win_played = False
        self.draw_played = False

    def draw(self):
        self.image.fill(0)
        for i in range(3):
            for j in range(3):
                start_point = (j * (self.width // 3) + 3, i * (self.height // 3) + 3)
                end_point = ((j + 1) * (self.width // 3) - 3, (i + 1) * (self.height // 3) - 3)
                cv2.rectangle(self.image, start_point, end_point, (255, 255, 255), -1)
                block_value = self.blocks[i][j].value

                if block_value == "x":
                    text_color = (0, 0, 255)
                elif block_value == "o":
                    text_color = (255, 0, 0)
                else:
                    continue

                cv2.putText(self.image, block_value, (start_point[0] + 25, start_point[1] + 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 5, text_color, 5)

        status_string = ""
        if self.check_win():
            status_string = "Computer Wins! Press R to restart"
            if not self.computer_win_played:
                self.computer_win_sound.play()
                self.computer_win_played = True
        elif self.check_draw():
            status_string = "It's a draw! Press R to restart"
            if not self.draw_played:
                self.draw_sound.play()
                self.draw_played = True
        elif self.turn == 1:
            status_string = "Your Turn"

        if status_string:
            cv2.putText(self.image, status_string, (self.width // 2 - 200, self.height + self.menu_height - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def computer_move(self):
        self.computer_turn_sound.play()
        empty_blocks = [(i, j) for i in range(3) for j in range(3) if self.blocks[i][j].value is None]

        for x, y in empty_blocks:
            temp_block = Block(x, y)
            temp_block.set_value("o")
            if self.check_win(blocks=[[temp_block if (i == x and j == y) else self.blocks[i][j] for j in range(3)] for i in range(3)]):
                return self.blocks[x][y]

        for x, y in empty_blocks:
            temp_block = Block(x, y)
            temp_block.set_value("x")
            if self.check_win(blocks=[[temp_block if (i == x and j == y) else self.blocks[i][j] for j in range(3)] for i in range(3)]):
                return self.blocks[x][y]

        x, y = empty_blocks[randint(0, len(empty_blocks) - 1)]
        return self.blocks[x][y]

    def main_loop(self):
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.on_mouse_click)

        while True:
            self.draw()
            cv2.imshow(self.window_name, self.image)

            current_time = pygame.time.get_ticks()
            time_diff = current_time - self.last_click_time

            # Check if the time difference has exceeded 6 seconds and the player's turn hasn't ended
            if time_diff > 6000 and self.turn == 1:
                block = self.computer_move()
                block.set_value("o")
                if self.check_win():
                    self.win = True
                else:
                    self.turn = 1
                self.last_click_time = current_time  # Reset the timer

            if self.turn == -1 and not self.win and not self.check_draw():
                block = self.computer_move()
                block.set_value("o")
                if self.check_win():
                    self.win = True
                else:
                    self.turn = 1

            key = cv2.waitKey(1)
            if key == 27:
                break
            elif key == ord('r'):
                self.initialize_game()

        cv2.destroyAllWindows()

    def on_mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            i, j = y // (self.height // 3), x // (self.width // 3)
            block = self.blocks[i][j]
            if not self.win and block.value is None:
                block.set_value("x")
                self.player_turn_sound.play()
                if self.check_win():
                    self.win = True
                    if not self.player_win_played:
                        self.player_win_sound.play()
                        self.player_win_played = True
                else:
                    self.turn = -1
                    self.last_click_time = pygame.time.get_ticks()

if __name__ == "__main__":
    game = GUI("Tic Tac Toe")
    game.main_loop()
