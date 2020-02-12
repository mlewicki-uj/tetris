import pygame
import random

pygame.init()

# Settings
gridWidth = 10
gridHeight = 25
blockSize = 40

menuAreaWidth = blockSize * 5
playAreaWidth = int(gridWidth * blockSize)
playAreaHeight = int(gridHeight * blockSize)
screenWidth = playAreaWidth + menuAreaWidth
screenHeight = playAreaHeight

topGridX = menuAreaWidth
topGridY = 0

title = 'TETRIS ML'

# Shapes
O=(('00000','00000','01100','01100','00000'),)
S=(('00000','00000','00110','01100','00000'),('00000','00100','00110','00010','00000'))
L=(('00000','00010','01110','00000','00000'),('00000','00100','00100','00110','00000'),('00000','00000','01110','01000','00000'),('00000','01100','00100','00100','00000'))
Z=(('00000','00000','01100','00110','00000'),('00000','00100','01100','01000','00000'))
J=(('00000','01000','01110','00000','00000'),('00000','00110','00100','00100','00000'),('00000','00000','01110','00010','00000'),('00000','00100','00100','01100','00000'))
I=(('00100','00100','00100','00100','00000'),('00000','11110','00000','00000','00000'))
T=(('00000','00100','01110','00000','00000'),('00000','00100','00110','00100','00000'),('00000','00000','01110','00100','00000'),('00000','00100','01100','00100','00000'))

shapesList = [S, Z, I, O, J, L, T]

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_LIGHT_GRAY = (30, 30, 30)
COLOR_GRAY = (128, 128, 128)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_LIGHT_BLUE = (0, 255, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_ORANGE = (255, 128, 0)
COLOR_PURPLE = (128, 0, 128)
COLOR_DARK_GREEN = (0, 60, 60)

borderColor = COLOR_WHITE
textColor = COLOR_WHITE
gridColor = COLOR_GRAY
windowColor = COLOR_LIGHT_GRAY
emptyColor = COLOR_DARK_GREEN
shapeColorsDict = {S: COLOR_LIGHT_BLUE, Z: COLOR_YELLOW, I: COLOR_GREEN, O: COLOR_PURPLE, J: COLOR_RED, L: COLOR_BLUE, T: COLOR_ORANGE}


class Piece:
    def __init__(self, x, y, shapeFormat):
        self.x = x
        self.y = y
        self.shapeFormat = shapeFormat
        self.color = shapeColorsDict[shapeFormat]
        self.rotation = 0
        self.positions = self.convertShapeFormat()

    def tryMove(self, x, y, board):
        oldX = self.x
        oldY = self.y
        self.x = x
        self.y = y
        positions = self.validSpace(board.getGrid(), board)
        if positions is None:
            self.x = oldX
            self.y = oldY
            return False
        else:
            self.positions = positions
            return True

    def tryRotate(self, board):
        self.rotation += 1
        positions = self.validSpace(board.getGrid(), board)
        if positions is None:
            self.rotation -= 1
        else:
            self.positions = positions

    def convertShapeFormat(self):
        positions = []
        shapeFormat = self.shapeFormat[self.rotation % len(self.shapeFormat)]

        for i, line in enumerate(shapeFormat):
            row = list(line)
            for j, column in enumerate(row):
                if column == '1':
                    positions.append((self.x + j, self.y + i))

        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 3)

        return positions

    def validSpace(self, grid, board):
        acceptedPositionList = []
        for i in range(board.tilesY):
            for j in range(board.tilesX):
                if grid[i][j] == emptyColor:
                    acceptedPositionList.append((j, i))
        positions = self.convertShapeFormat()
        for pos in positions:
            if pos not in acceptedPositionList:
                if pos[1] > -1 or (pos[0] < 0 or pos[0] >= board.tilesX):
                    return None
        return positions


class Board:
    def __init__(self, tilesX, tilesY):
        self.tilesX = tilesX
        self.tilesY = tilesY
        self.usedTiles = {}

    def getGrid(self):
        grid = [[emptyColor for x in range(self.tilesX)] for y in range(self.tilesY)]
        for i in range(self.tilesX):
            for j in range(self.tilesY):
                if (i, j) in self.usedTiles:
                    color = self.usedTiles[(i, j)]
                    grid[j][i] = color
        return grid


def checkLost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def getShape():
    return Piece(gridWidth // 2, 0, random.choice(shapesList))


def drawTextMiddle(surface, text, size, color):
    font = pygame.font.SysFont("arial", size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (screenWidth // 2 - (label.get_width() // 2), screenHeight // 2 - label.get_height() // 2))


def drawGrid(surface, grid):
    for i in range(len(grid)):
        pygame.draw.line(surface, gridColor, (topGridX, topGridY + i * blockSize), (topGridX + playAreaWidth, topGridY + i * blockSize))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, gridColor, (topGridX + j * blockSize, topGridY),
                             (topGridX + j * blockSize, topGridY + playAreaHeight))
    pygame.draw.rect(surface, borderColor, (topGridX, 0, playAreaWidth, playAreaHeight), 3)


def drawNextShape(shape, surface):
    shapeFormat = shape.shapeFormat[shape.rotation % len(shape.shapeFormat)]

    for i, line in enumerate(shapeFormat):
        row = list(line)
        for j, column in enumerate(row):
            if column == '1':
                pygame.draw.rect(surface, shape.color, (j * blockSize, (1 + i) * blockSize, blockSize, blockSize), 0)


def drawWindow(surface, grid):
    surface.fill(windowColor)
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (topGridX + j * blockSize, topGridY + i * blockSize, blockSize, blockSize))
    drawGrid(surface, grid)


def clearRows(grid, usedTiles):
    counter = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if emptyColor not in row:
            counter += 1
            lastRow = i
            for j in range(len(row)):
                try:
                    del usedTiles[(j, i)]
                except:
                    continue

    if counter > 0:
        for key in sorted(list(usedTiles), key=lambda e: e[1])[::-1]:
            x, y = key
            if y < lastRow:
                newKey = (x, y + counter)
                usedTiles[newKey] = usedTiles.pop(key)
    return counter


def main(window):
    board = Board(gridWidth, gridHeight)
    changePiece = False
    run = True
    currentPiece = getShape()
    nextPiece = getShape()
    clock = pygame.time.Clock()
    autoFallTime = 0
    manualFallTime = 0
    autoFallSpeed = 0.25
    manualFallSpeed = 0.003
    score = 0
    difficultyIncreaseTime = 0
    difficultyIncreaseSpeed = 3

    while run:
        grid = board.getGrid()
        autoFallTime += clock.get_rawtime()
        manualFallTime += clock.get_rawtime()
        difficultyIncreaseTime += clock.get_rawtime()
        clock.tick(120)

        if autoFallTime / 1000 > autoFallSpeed:
            autoFallTime = 0
            if not (currentPiece.tryMove(currentPiece.x, currentPiece.y + 1, board)):
                changePiece = True

        if difficultyIncreaseTime / 1000 > difficultyIncreaseSpeed and autoFallSpeed > 0.03:
            difficultyIncreaseTime = 0
            autoFallSpeed *= 0.9

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    currentPiece.tryMove(currentPiece.x - 1, currentPiece.y, board)
                if event.key == pygame.K_RIGHT:
                    currentPiece.tryMove(currentPiece.x + 1, currentPiece.y, board)
                if event.key == pygame.K_UP:
                    currentPiece.tryRotate(board)
                if event.key == pygame.K_ESCAPE:
                    run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            if manualFallTime / 1000 > manualFallSpeed:
                autoFallTime = 0
                manualFallTime = 0
                if not (currentPiece.tryMove(currentPiece.x, currentPiece.y + 1, board)):
                    changePiece = True

        shapePosition = currentPiece.positions

        for i in range(len(shapePosition)):
            x, y = shapePosition[i]
            if y > -1:
                grid[y][x] = currentPiece.color

        if changePiece:
            for pos in shapePosition:
                board.usedTiles[pos] = currentPiece.color
            currentPiece = nextPiece
            nextPiece = getShape()
            changePiece = False
            score += clearRows(grid, board.usedTiles) * 10

        drawWindow(window, grid)
        drawNextShape(nextPiece, window)

        if checkLost(board.usedTiles):
            run = False

        if not run:
            window.fill(windowColor)
            drawTextMiddle(window, "Score: " + str(score), blockSize * 2, textColor)
            pygame.display.update()
            pygame.time.delay(3000)
            pygame.event.clear()

        pygame.display.update()


def mainMenu(window):
    run = True
    while run:
        window.fill(windowColor)
        drawTextMiddle(window, 'Press Space', blockSize * 2, textColor)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main(window)
                if event.key == pygame.K_ESCAPE:
                    run = False
    pygame.display.quit()


if __name__ == '__main__':
    window = pygame.display.set_mode((screenWidth, screenHeight))
    pygame.display.set_caption(title)
    mainMenu(window)
