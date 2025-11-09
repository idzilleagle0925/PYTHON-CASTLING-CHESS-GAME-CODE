import pygame
import sys
import math

pygame.init()

SQUARE_SIZE = 80
WIDTH = SQUARE_SIZE * 8
HEIGHT = SQUARE_SIZE * 8
FPS = 60

LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (186, 202, 68, 150)
CAPTURE = (255, 100, 100, 150)
SELECT = (255, 255, 0, 100)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")
CLOCK = pygame.time.Clock()

class Piece:
    def __init__(self, piece_type, team):
        self.type = piece_type
        self.team = team
        self.has_moved = False

    def draw(self, screen, x, y):
        cx, cy = x + SQUARE_SIZE//2, y + SQUARE_SIZE//2
        color = WHITE if self.team == 'w' else BLACK
        outline = BLACK if self.team == 'w' else WHITE
        
        if self.type == 'p':
            pygame.draw.circle(screen, color, (cx, cy), 12)
            pygame.draw.circle(screen, outline, (cx, cy), 12, 2)
            
        elif self.type == 'r':
            pygame.draw.rect(screen, color, (cx-15, cy-20, 30, 35))
            pygame.draw.rect(screen, outline, (cx-15, cy-20, 30, 35), 2)
            pygame.draw.rect(screen, color, (cx-18, cy-25, 8, 10))
            pygame.draw.rect(screen, color, (cx-3, cy-25, 8, 10))
            pygame.draw.rect(screen, color, (cx+10, cy-25, 8, 10))
            
        elif self.type == 'n':
            points = [(cx-10, cy+15), (cx-15, cy-10), (cx-5, cy-20), (cx+10, cy-15), (cx+15, cy+10), (cx, cy+15)]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, outline, points, 2)
            
        elif self.type == 'b':
            points = [(cx, cy-25), (cx-12, cy+15), (cx+12, cy+15)]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, outline, points, 2)
            pygame.draw.circle(screen, color, (cx, cy-25), 5)
            pygame.draw.circle(screen, outline, (cx, cy-25), 5, 2)
            
        elif self.type == 'q':
            pygame.draw.circle(screen, color, (cx, cy), 18)
            pygame.draw.circle(screen, outline, (cx, cy), 18, 2)
            for angle in [0, 72, 144, 216, 288]:
                px = cx + int(22 * math.cos(math.radians(angle - 90)))
                py = cy + int(22 * math.sin(math.radians(angle - 90)))
                pygame.draw.circle(screen, color, (px, py), 5)
                pygame.draw.circle(screen, outline, (px, py), 5, 2)
                
        elif self.type == 'k':
            pygame.draw.circle(screen, color, (cx, cy+5), 18)
            pygame.draw.circle(screen, outline, (cx, cy+5), 18, 2)
            pygame.draw.rect(screen, color, (cx-3, cy-28, 6, 25))
            pygame.draw.rect(screen, outline, (cx-3, cy-28, 6, 25), 2)
            pygame.draw.rect(screen, color, (cx-10, cy-20, 20, 6))
            pygame.draw.rect(screen, outline, (cx-10, cy-20, 20, 6), 2)

def init_board():
    board = [[' ' for _ in range(8)] for _ in range(8)]
    
    pieces = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
    for i in range(8):
        board[0][i] = Piece(pieces[i], 'b')
        board[1][i] = Piece('p', 'b')
        board[6][i] = Piece('p', 'w')
        board[7][i] = Piece(pieces[i], 'w')
    
    return board

board = init_board()
selected_piece = None
selected_pos = None
turn = 'w'
moves_made = 0

def board_to_screen(row, col):
    return col * SQUARE_SIZE, row * SQUARE_SIZE

def screen_to_board(pos):
    x, y = pos
    return y // SQUARE_SIZE, x // SQUARE_SIZE

def draw_board():
    for row in range(8):
        for col in range(8):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            x, y = board_to_screen(row, col)
            pygame.draw.rect(SCREEN, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces():
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if isinstance(piece, Piece):
                x, y = board_to_screen(row, col)
                piece.draw(SCREEN, x, y)

def highlight_moves(moves, captures):
    overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    for r, c in moves:
        x, y = board_to_screen(r, c)
        overlay.fill(HIGHLIGHT)
        SCREEN.blit(overlay, (x, y))
        font = pygame.font.SysFont(None, 40)
        text = font.render('·', True, (0, 0, 0))
        SCREEN.blit(text, (x + SQUARE_SIZE//2 - 10, y + SQUARE_SIZE//2 - 20))
    for r, c in captures:
        x, y = board_to_screen(r, c)
        overlay.fill(CAPTURE)
        SCREEN.blit(overlay, (x, y))
        pygame.draw.circle(SCREEN, (255,0,0), (x + SQUARE_SIZE//2, y + SQUARE_SIZE//2), SQUARE_SIZE//3, 5)

def get_king_pos(team):
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if isinstance(p, Piece) and p.type == 'k' and p.team == team:
                return r, c
    return None

def is_square_attacked(row, col, by_team):
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if isinstance(p, Piece) and p.team == by_team:
                moves, captures = get_legal_moves((r, c), check_king_safety=False)
                if (row, col) in moves or (row, col) in captures:
                    return True
    return False

def is_in_check(team):
    king_pos = get_king_pos(team)
    if not king_pos:
        return False
    return is_square_attacked(king_pos[0], king_pos[1], 'b' if team == 'w' else 'w')

def get_legal_moves(pos, check_king_safety=True):
    row, col = pos
    piece = board[row][col]
    if not isinstance(piece, Piece):
        return [], []
    if check_king_safety and piece.team != turn:
        return [], []

    moves = []
    captures = []

    if piece.type == 'p':
        direction = -1 if piece.team == 'w' else 1
        if 0 <= row + direction < 8 and board[row + direction][col] == ' ':
            moves.append((row + direction, col))
            if (piece.team == 'w' and row == 6 or piece.team == 'b' and row == 1) and board[row + 2*direction][col] == ' ':
                moves.append((row + 2*direction, col))
        for dc in [-1, 1]:
            if 0 <= col + dc < 8 and 0 <= row + direction < 8:
                target = board[row + direction][col + dc]
                if isinstance(target, Piece) and target.team != piece.team:
                    captures.append((row + direction, col + dc))

    elif piece.type == 'r':
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == ' ':
                    moves.append((r,c))
                elif isinstance(board[r][c], Piece):
                    if board[r][c].team != piece.team:
                        captures.append((r,c))
                    break
                r += dr
                c += dc

    elif piece.type == 'n':
        deltas = [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]
        for dr, dc in deltas:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == ' ':
                    moves.append((r,c))
                elif isinstance(board[r][c], Piece) and board[r][c].team != piece.team:
                    captures.append((r,c))

    elif piece.type == 'b':
        for dr, dc in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == ' ':
                    moves.append((r,c))
                elif isinstance(board[r][c], Piece):
                    if board[r][c].team != piece.team:
                        captures.append((r,c))
                    break
                r += dr
                c += dc

    elif piece.type == 'q':
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if board[r][c] == ' ':
                    moves.append((r,c))
                elif isinstance(board[r][c], Piece):
                    if board[r][c].team != piece.team:
                        captures.append((r,c))
                    break
                r += dr
                c += dc

    elif piece.type == 'k':
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr == 0 and dc == 0: continue
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    if board[r][c] == ' ':
                        moves.append((r,c))
                    elif isinstance(board[r][c], Piece) and board[r][c].team != piece.team:
                        captures.append((r,c))

        if check_king_safety and not piece.has_moved and not is_in_check(piece.team):
            if (col + 3 < 8 and isinstance(board[row][col+3], Piece) and 
                board[row][col+3].type == 'r' and not board[row][col+3].has_moved and
                board[row][col+1] == ' ' and board[row][col+2] == ' ' and
                not is_square_attacked(row, col+1, 'b' if piece.team == 'w' else 'w') and
                not is_square_attacked(row, col+2, 'b' if piece.team == 'w' else 'w')):
                moves.append((row, col + 2))
            if (col - 4 >= 0 and isinstance(board[row][col-4], Piece) and 
                board[row][col-4].type == 'r' and not board[row][col-4].has_moved and
                board[row][col-1] == ' ' and board[row][col-2] == ' ' and board[row][col-3] == ' ' and
                not is_square_attacked(row, col-1, 'b' if piece.team == 'w' else 'w') and
                not is_square_attacked(row, col-2, 'b' if piece.team == 'w' else 'w')):
                moves.append((row, col - 2))

    if not check_king_safety:
        return moves, captures

    valid_moves = []
    valid_captures = []
    for m in moves + captures:
        m_row, m_col = m
        orig_piece = board[row][col]
        dest_piece = board[m_row][m_col]
        
        board[row][col] = ' '
        board[m_row][m_col] = orig_piece
        in_check = is_in_check(piece.team)
        
        board[row][col] = orig_piece
        board[m_row][m_col] = dest_piece
        
        if not in_check:
            if m in moves:
                valid_moves.append(m)
            else:
                valid_captures.append(m)
    return valid_moves, valid_captures

def perform_castling(king_pos, target_pos):
    row, col = king_pos
    t_row, t_col = target_pos
    king = board[row][col]

    if t_col == col + 2:
        rook = board[row][7]
        board[row][7] = ' '
        board[row][5] = rook
        rook.has_moved = True
    elif t_col == col - 2:
        rook = board[row][0]
        board[row][0] = ' '
        board[row][3] = rook
        rook.has_moved = True

    board[t_row][t_col] = king
    board[row][col] = ' '
    king.has_moved = True

def main():
    global selected_piece, selected_pos, turn, moves_made
    running = True
    legal_moves = []
    legal_captures = []

    while running:
        CLOCK.tick(FPS)
        SCREEN.fill((50, 50, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = screen_to_board(pos)
                piece = board[row][col]

                if selected_piece:
                    target = (row, col)
                    if target in legal_moves or target in legal_captures:
                        if selected_piece.type == 'k' and abs(col - selected_pos[1]) == 2:
                            perform_castling(selected_pos, target)
                        else:
                            board[row][col] = selected_piece
                            board[selected_pos[0]][selected_pos[1]] = ' '
                            selected_piece.has_moved = True
                        selected_piece = None
                        selected_pos = None
                        legal_moves = []
                        legal_captures = []
                        turn = 'b' if turn == 'w' else 'w'
                        moves_made += 1
                    else:
                        selected_piece = None
                        selected_pos = None
                        legal_moves = []
                        legal_captures = []
                else:
                    if isinstance(piece, Piece) and piece.team == turn:
                        selected_piece = piece
                        selected_pos = (row, col)
                        legal_moves, legal_captures = get_legal_moves(selected_pos)

        draw_board()
        if selected_pos:
            x, y = board_to_screen(selected_pos[0], selected_pos[1])
            overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            overlay.fill(SELECT)
            SCREEN.blit(overlay, (x, y))
            highlight_moves(legal_moves, legal_captures)
        draw_pieces()

        font = pygame.font.SysFont(None, 36)
        text = font.render(f"Turn: {'White' if turn == 'w' else 'Black'}", True, WHITE)
        SCREEN.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
