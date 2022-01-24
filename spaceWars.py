##################### Imports ################
import pygame
import random
import math

pygame.init()

_ANCHO = 800
_ALTO = 600

################### Images ###################

backgroundImage = pygame.image.load("background.jpg")
shipImage = pygame.image.load("ship.png")
enemyImage = pygame.image.load("enemy.png")


################### Font ##################
gameOverFont = pygame.font.Font("chintzy.ttf", 60)
gameOver = gameOverFont.render("Game over", True, (255, 0, 255))
gameOverRect = gameOver.get_rect()
gameOverRect.center = (_ANCHO // 2, _ALTO // 2)

askFont = pygame.font.Font("prstartk.ttf", 10)

ask = askFont.render("Presione ENTER para volver a jugar", True, (255, 255, 255))
askRect = ask.get_rect()
askRect.center = (_ANCHO // 2, (_ALTO // 2) + 50)
################### Ship ###################

ship = {
    "pos" : [_ANCHO // 2, _ALTO - 50],
    "size" : list(shipImage.get_size()),
    "color" : [0, 255, 0],
    "speed" : 5,
    "cooldown" : 20,
    "firewait" : 0,
    "respawncooldown" : 180,
    "respawnwait" : 0,
    "lives" : 3,
    "image" : shipImage
    }


def shipDraw(window, ship):
    """
    Función que se encarga de dibujar la nave en la ventana
    """
    x = ship["pos"][0] - ship["size"][0] // 2
    y = ship["pos"][1] - ship["size"][1] // 2
    window.blit(ship["image"], [x, y] + ship["size"])

def shipMoveRight(ship):
    """
    Función encargada del movimiento a la derecha de la nave
    """
    if ship["respawnwait"] == 0:
        ship["pos"][0] = min(ship["pos"][0] + ship["speed"], _ANCHO -ship["size"][0] //2)

def shipMoveLeft(ship):
    """
    Función encargada del movimiento a la izquierda de la nave
    """
    if ship["respawnwait"] == 0:
        ship["pos"][0] = max(ship["pos"][0] - ship["speed"], ship["size"][0] //2)

def shipFire(ship):
    if ship["firewait"] <= 0 and ship["respawnwait"] == 0:
        bullet = {
            "pos" : [ship["pos"][0], ship["pos"][1] - ship["size"][1] // 2],
            "speed" : -20,
            "radio" : 3,
            "color" : (255, 255, 255)
            }
        bullets.append(bullet)
        ship["firewait"] = ship["cooldown"]

def shipUpdate(ship):
    ship["firewait"] -= 1
    if ship["respawnwait"] > 0:
        ship["pos"][0] = -100
        ship["respawnwait"] -= 1
        if ship["respawnwait"] == 0:
            ship["pos"][0] = _ANCHO // 2

def shipDeath(ship):
    ship["lives"] -= 1
    ship["respawnwait"] = ship["respawncooldown"]

######################## Bullets ##########################

bullets = []

def bulletDraw(window, bullet):
    pygame.draw.circle(window, bullet["color"], bullet["pos"], bullet["radio"])

def bulletUpdate(bullet):
    bullet["pos"][1] += bullet["speed"]
    
def bulletsDraw(window, bullets):
    for b in bullets:
        bulletDraw(window, b)

def bulletsUpdate(bullets):
    for b in bullets:
        if b["pos"][1] < 0:
            bullets.remove(b)
        if b["pos"][1] > _ALTO:
            bullets.remove(b)
        else:
            bulletUpdate(b)

###################### Enemies ##########################
enemies = []
enemyBullets = []

def enemyCreate(pos, w, h):
    enemy = {
        "pos" : pos[:],
        "size" : list(enemyImage.get_size()),
        "color" : (255, 0, 0),
        "speed" : random.choice([3, -3]),
        "dirChangeProb" : 2,
        "time" : random.randrange(5),
        "timeincrease" : 0.05,
        "firerate" : 80,
        "firewait" : random.randrange(60),
        "image" : enemyImage
        }
    enemies.append(enemy)
    
def enemyDraw(window, enemy):
        x = enemy["pos"][0] - enemy["size"][0] // 2
        y = enemy["pos"][1] - enemy["size"][1] // 2
        window.blit(enemy["image"], [x, y] + enemy["size"])

def enemiesDraw(window, enemies):
    for e in enemies:
        enemyDraw(window, e)

def enemiesCreate(num):
    global enemies
    enemies = []
    for i in range(num):
        pos = [random.randint(20, _ANCHO - 20), random.randint(0, int(_ALTO // 2))]
        enemyCreate(pos, 20, 20)

def enemyIsHit(enemy, bullet):
    x1 = enemy["pos"][0] - enemy["size"][0] // 2 + bullet["radio"]
    x2 = enemy["pos"][0] + enemy["size"][0] // 2 + bullet["radio"]
    y1 = enemy["pos"][1] - enemy["size"][1] // 2 + bullet["radio"]
    y2 = enemy["pos"][1] + enemy["size"][1] // 2 + bullet["radio"]
    return x1 <= bullet["pos"][0] <= x2 and y1 <= bullet["pos"][1] <= y2

def enemyLeftBorderTouch(enemy):
    if enemy["pos"][0] < enemy["size"][0] // 2:
        return True
    return False

def enemyRightBorderTouch(enemy):
    if enemy["pos"][0] > _ANCHO - enemy["size"][0] // 2:
        return True
    return False

def enemyUpdate(enemy):
    if enemyRightBorderTouch(enemy) and enemy["speed"] > 0:
        enemy["speed"] *= -1
    if enemyLeftBorderTouch(enemy) and enemy["speed"] < 0:
        enemy["speed"] *= -1
    if random.randrange(100) < enemy["dirChangeProb"]:
        enemy["speed"] *= -1
    enemy["pos"][0] += enemy["speed"]
    minimumY = enemy["size"][1] // 2
    newY = enemy["pos"][1] + math.sin(enemy["time"])
    enemy["pos"][1] = max(minimumY, newY)
    enemy["time"] += enemy["timeincrease"]
    if enemy["firewait"] <= 0:
        enemyFire(enemy)
        enemy["firewait"] = enemy["firerate"]
    else:
        enemy["firewait"] -= 1

def enemiesUpdate(enemies):
    for e in enemies:
        enemyUpdate(e)

def enemyFire(enemy):
    bullet = {
        "pos" : [enemy["pos"][0], enemy["pos"][1] + enemy["size"][1] // 2],
        "speed" : 5,
        "radio" : 3,
        "color" : (255, 255, 0)
        }
    enemyBullets.append(bullet)

#################### Collisions ######################
def checkEnemyImpact(enemies, bullets):
    for e in enemies:
        for b in bullets:
            if enemyIsHit(e, b):
                enemies.remove(e)
                bullets.remove(b)

def checkShipImpact(ship, enemyBullets):
    for b in enemyBullets:
        if enemyIsHit(ship, b):
            enemyBullets.remove(b)
            shipDeath(ship)



###################### MAIN ######################

def main():
    enemiesNum = 5
    enemiesIncrease = 2
    window = pygame.display.set_mode((_ANCHO, _ALTO))
    loop = True
    enemiesCreate(enemiesNum)
    while loop:
        pygame.time.delay(16)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            shipMoveLeft(ship)
        if keys[pygame.K_RIGHT]:
            shipMoveRight(ship)
        if keys[pygame.K_SPACE]:
            shipFire(ship)

            
        window.fill((0, 0, 0))
        window.blit(backgroundImage, (0,0))
        
        if enemies == []:
            enemiesNum += enemiesIncrease
            enemiesIncrease += 2
            enemiesCreate(enemiesNum)
        checkEnemyImpact(enemies, bullets)
        if ship["lives"] > 0:
            checkShipImpact(ship, enemyBullets)
            shipDraw(window, ship)
            shipUpdate(ship)
        
        
        else:
            noContinuar = True
            window.fill((0, 0, 0))
            window.blit(gameOver, gameOverRect)
            window.blit(ask, askRect)
            pygame.display.update()
            while noContinuar:
                for event in pygame.event.get():
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_RETURN]:
                        enemiesNum = 5
                        enemiesIncrease = 2
                        ship["lives"] = 5
                        enemiesCreate(enemiesNum)
                        noContinuar = False
                    
        bulletsDraw(window, bullets)
        bulletsUpdate(bullets)
        bulletsDraw(window, enemyBullets)
        bulletsUpdate(enemyBullets)
        enemiesDraw(window, enemies)
        enemiesUpdate(enemies)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__": 
    main()
