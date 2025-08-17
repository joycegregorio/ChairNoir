import pygame
import sys
import math

class ChatNoir: 
    def __init__(self, size=11):
        self.size = size
        self.board = [" " for _ in range(self.size * self.size)]
        self.human_player = "O"  
        self.ia_player = "X"    
        self.current_player = self.human_player

        center = (self.size // 2) * self.size + (self.size // 2)
        self.cat_position = center

    def make_move(self, pos, player):
        if self.board[pos] == " " and pos != self.cat_position:
           self.board[pos] = player
           return True
        return False
    
    def move_cat(self, new_position):
        self.cat_position = new_position
    
    def switch_player(self): 
        self.current_player = self.ia_player if self.current_player == self.human_player else self.human_player

    def get_cat_moves(self):
        moves = []
        row, col = self.cat_position // self.size, self.cat_position % self.size

        for r_offset in [-1, 0, 1]:
            for c_offset in [-1, 0, 1]:
                if r_offset == 0 and c_offset == 0:
                    continue
                
                new_row, new_col = row + r_offset, col + c_offset

                if 0 <= new_row < self.size and 0 <= new_col < self.size:
                    pos = new_row * self.size + new_col
                    if self.board[pos] == " ":
                        moves.append(pos)
        return moves
    
    def check_winner(self):
        row, col = self.cat_position // self.size, self.cat_position % self.size
        if row == 0 or row == self.size - 1 or col == 0 or col == self.size - 1:
            return self.ia_player

        if not self.get_cat_moves():
            return self.human_player

        return None
        
    def evaluate_board(self):
        row, col = self.cat_position // self.size, self.cat_position % self.size
        dist_to_edge = min(row, col, self.size - 1 - row, self.size - 1 - col)
        return 10 - dist_to_edge

    def minimax(self, depth, alpha, beta, is_maximizing):
        winner = self.check_winner()
        if winner == self.ia_player: return 1000
        if winner == self.human_player: return -1000
        
        if depth == 0:
            return self.evaluate_board()
        
        if is_maximizing:
            max_eval = -math.inf
            original_pos =  self.cat_position
            for move in self.get_cat_moves():
                self.move_cat(move)
                evaluation = self.minimax(depth - 1, alpha, beta, False)
                self.move_cat(original_pos) 
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = math.inf
            possible_human_moves = [pos for pos, val in enumerate(self.board) if val == " "]
            for move in possible_human_moves:
                if move == self.cat_position: continue
                self.board[move] = self.human_player
                evaluation = self.minimax(depth - 1, alpha, beta, True)
                self.board[move] = " "
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha: break
            return min_eval
        
    def get_best_move(self):
        best_score = -math.inf
        best_move = None
        MAX_DEPTH = 3
        original_pos = self.cat_position

        for move in self.get_cat_moves():
            self.move_cat(move)
            score = self.minimax(MAX_DEPTH, -math.inf, math.inf, False)
            self.move_cat(original_pos)

            if score > best_score:
                best_score = score
                best_move = move

        if best_move is None and self.get_cat_moves():
            best_move = self.get_cat_moves()[0]

        return best_move

BOARD_SIZE = 11
CELL_SIZE = 50
WIDTH = BOARD_SIZE * CELL_SIZE
HEIGHT = BOARD_SIZE * CELL_SIZE
LINE_WIDTH = 2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FENCE_COLOR = (50, 50, 50) 

def draw_grid(screen):
    for i in range(1, BOARD_SIZE):
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), LINE_WIDTH)

def draw_pieces(screen, game):
    for pos, player in enumerate(game.board):
        if player == game.human_player:
            row, col = pos // game.size, pos % game.size
            pygame.draw.rect(screen, FENCE_COLOR, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    row, col = game.cat_position // game.size, game.cat_position % game.size
    center_x = col * CELL_SIZE + CELL_SIZE // 2
    center_y = row * CELL_SIZE + CELL_SIZE // 2
    pygame.draw.circle(screen, RED, (center_x, center_y), CELL_SIZE // 2 - 5)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chat Noir: O Gato vs. A Cerca")
    
    game = ChatNoir(size=BOARD_SIZE)
    running = True
    game_over = False
    winner = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and game.current_player == game.human_player:
                mouseX, mouseY = event.pos
                pos = (mouseY // CELL_SIZE) * BOARD_SIZE + (mouseX // CELL_SIZE)

                if game.make_move(pos, game.human_player):
                    winner = game.check_winner()
                    if winner:
                        game_over = True
                    else:
                        game.switch_player()

        if not game_over and game.current_player == game.ia_player:
            pygame.display.set_caption("IA (Gato) está pensando...")
            best_move = game.get_best_move()
            if best_move is not None:
                game.move_cat(best_move)

            winner = game.check_winner()
            if winner:
                game_over = True
            else:
                game.switch_player()
            pygame.display.set_caption("Chat Noir: O Gato vs. A Cerca")
        
        screen.fill(WHITE)
        draw_grid(screen)
        draw_pieces(screen, game)
        pygame.display.flip()

        if game_over and winner:
            print(f"Fim de jogo! O vencedor é: {winner} ({'Gato' if winner == game.ia_player else 'Cerca'})")
            pygame.time.wait(3000)
            running = False

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()