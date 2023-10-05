"""
Creator: Teddy Barthelemy
23/09/2022 - 10:43

Projet personnel - Jeu de Rôle NSI
"""
import data.dependancies as dep
import data.map as mapping
import data.player as player
import data.gui as gui
import data.room as room
import data.screen as screen
import data.loots as loots
# import data.configuration as config

manager = gui.CommandManager(
    carte=None
)


def cm_createMap(*_args, gd):
    t = mapping.Map((12, 12))
    gd.carte = t
    carte = gd.carte
    carte.setPlayer(player.Player(carte))

    def replaceRooms(r: room.Room, **kwargs):
        if not dep.rnd.randint(0, 7):
            r.replaceWith(kwargs["type"])
    carte.forEachRoom(replaceRooms, ignoreSpawn=True, type=room.VoidRoom)
    carte.forEachRoom(replaceRooms, ignoreSpawn=True, type=room.DungeonRoom)
    carte.forEachRoom(replaceRooms, ignoreSpawn=True, type=room.LootRoom)

    # TEMP
    carte.putRoom(1, 0, room.DungeonRoom((1, 0), carte))
    carte.putRoom(0, 1, room.LootRoom((0, 1), carte))

    def patchEmptyRooms(r: dep.Union[room.Room, room.DungeonRoom, room.LootRoom], **kwargs):
        if carte.isAValidRoom(r):
            if isinstance(r, room.DungeonRoom):
                if len(r.creatures) == 0:
                    r.replaceWith(room.Room)

    carte.forEachRoom(patchEmptyRooms)

    def randomizeWalls(r: room.Room, **_kwargs):
        if carte.isAValidRoom(r):
            r.defineWalls(**{dep.rnd.choice("lrbt"): True})

    carte.forEachRoom(randomizeWalls)

    carte.patchWallsVoid()
    carte.patchWallsTransitons("random")
    carte.player.getTileOn().callEvent("enter")
    manager.redirect("#game")


manager.add(gui.Command(
    "#create_map",
    cm_createMap
))


def cm_game(*args, gd):
    manager.last = ["#game", ()]
    while True:
        def check_fight():
            if isinstance(gd.carte.player.getTileOn(), room.DungeonRoom):
                return not gd.carte.player.getTileOn().isConquired

        def computeMove():
            display = printMenu()
            if check_fight():
                display.printScreen()
                manager.redirect("#ask_fight")
            display.printScreen()
            manager.status = "#game"

        def printMenu():
            display = screen.PixelImage((119, 45),
                                        # screen.PixelImage.PatternPixel("[]")
                                        )

            def makeScreen():
                display.putGrid(0, 0, screen.PixelImage.TextPixel(
                    f" ╔[ MINIMAP ]═{'══' * (27 - 6)}╦[ INVENTORY ]{'══' * (89 - 6)}═╗"))
                display.putGrid(0, 44, screen.PixelImage.TextPixel(f" ╚{'══' * 27}╩═{'══' * 89}═╝"))
                for _design, _xpos in [(" ║", 0), ("║ ", 28), (" ║", 118)]:
                    display.putGrid(_xpos, 1, screen.PixelImage.TextPixel(f"{_design}\n" * 43))
                display.putGrid(0, 22, screen.PixelImage.TextPixel(f" ╠[ STATISTICS ]{'══' * (27 - 7)}╣ "))

            def fillInventory():
                formatter = " {:^2} │ {:^7} │ {:^35} │ {:^124}"
                display.putGrid(29, 1, screen.PixelImage.TextPixel(
                    f"{formatter.format('', '', '', '')}\n" +
                    f"{formatter.format('ID', 'Equiped', 'Name', 'Effects')}\n" +
                    f"{''.join(['┼' if _ == '│' else '─' for _ in formatter.format(0, 0, 0, 0)])}"
                ))
                # "{''.join(['┼' if _ == '│'else '─' for _ in formatter.format(0, 0, 0, 0)])}"
                for i in range(40):
                    if i < len(gd.carte.player.inventory):
                        obj: dep.Dict = gd.carte.player.inventory[i]
                        loot = obj.get('item')
                        display.putGrid(29, 4 + i, screen.PixelImage.TextPixel(
                            f"{formatter.format(i + 1, '[{}]'.format('X' if obj.get('equiped') else ' '), loot.format('[ {tier_name} ] {name}'), ' / '.join([loot.format('{effects.' + _ + '.value} {effects.' + _ + '.full}') for _ in loot.effects]))}"))
                        display.getGrid(29 + 7, 4 + i, False).endcolor = screen.colors.bold + loot.format("{tier_color}")
                        display.getGrid(29 + 26, 4 + i, False).incolor = screen.colors.reset
                    else:
                        display.putGrid(29, 4 + i,
                                        screen.PixelImage.TextPixel(f"{formatter.format(i + 1, '', 'Empty slot', '')}"))

            def fillStats():
                formatter = "{stat:^12} = {total:^8} : {base:^6} + {add:^8}"
                item = loots.Loot("coin")
                display.putGrid(2, 23, screen.PixelImage.TextPixel(
                    formatter.format(
                        icon="Icon",
                        stat="Name",
                        total="Total",
                        base="Base",
                        add="Added",
                    )
                ))
                for i, stat in enumerate(gd.carte.player.getStats().keys()):
                    display.putGrid(2, 25 + i, screen.PixelImage.TextPixel(
                        formatter.format(
                            icon=item.format("{effects." + stat + ".icon}"),
                            stat=item.format("{effects." + stat + ".full}"),
                            total=round(gd.carte.player.getStats().get(stat, -1), 2),
                            base=round(gd.carte.player.getStats(True).get(stat, -1), 2),
                            add=round(
                                gd.carte.player.getStats().get(stat, -1) - gd.carte.player.getStats(True).get(stat, -1), 2)
                        )
                    ))

            makeScreen()  # Make screen borders
            fillInventory()  # Fill inventory with loots data
            fillStats()  # Fill statistics with player data
            display.paste(gd.carte.player.createMinimap(size=(4, 3)), 1, 1)  # Add minimap to screen
            return display

        computeMove()
        manager.ask(">>>", *args)


manager.add(gui.Command(
    "#game",
    cm_game,
    redirections=lambda m, gd: ["move", "use", "m", "map"] \
                               + (["interact"] if gd.carte.player.getTileOn().interactive else []),
    auto=False
))


def cm_move(*args, gd):
    """Syntax: m left|right|up|down|l|r|u|d : Move player in a direction"""
    _direction = args[0][0]
    _vect = {"l": [-1, 0], "r": [1, 0], "u": [0, -1], "d": [0, 1]}

    gd.carte.player.move(*_vect[_direction])
    # manager.redirect("#game")


manager.add(gui.Command(
    "move",
    cm_move,
    lambda *args: False if len(args) < 1 else ((True if len(args) == 1 else args[1].isnumeric()) and args[0] in ["right", "left", "up", "down", "r", "l", "u", "d"])
))
manager.add(gui.Command(
    "m",
    cm_move,
    lambda *args: False if len(args) < 1 else ((True if len(args) == 1 else args[1].isnumeric()) and args[0] in ["right", "left", "up", "down", "r", "l", "u", "d"])
))


def cm_fullmap(*_args, gd):
    gd.carte.createMap().printScreen()
    input(" Press enter to close map... ")
    # manager.redirect("#game")


manager.add(gui.Command(
    "map",
    cm_fullmap,
    lambda *args: len(args) == 1 and args[0] == ""
))


def ask_for_fight(*_args, gd):
    dep.wait(1)
    manager.redirect("#fight")


manager.add(gui.Command(
    "#ask_fight",
    ask_for_fight
))


def fight(*_args, gd):
    gd.carte.player.getTileOn().fight(gd)
    # manager.redirect("#game")


manager.add(gui.Command(
    "#fight",
    fight
))


def interactRoom(*_args, gd):
    gd.carte.player.getTileOn().callEvent("interact")

manager.add(gui.Command(
    "interact",
    interactRoom
))


def useItem(*args, gd):
    if len(gd.carte.player.inventory) < int(args[0]) or int(args[0]) < 1:
        print(screen.color("Objet introuvable !", screen.colors.FG.red, screen.colors.reset))
        dep.wait(1)
    else:
        item: loots.Loot = gd.carte.player.inventory[int(args[0])-1]["item"]
        item.use(gd.carte.player)
        print(screen.color("Objet equipé !", screen.colors.FG.green, screen.colors.reset))


manager.add(gui.Command(
    "use",
    useItem,
    lambda *args: len(args) == 1 and args[0].isnumeric()
))

def initGame(*_args, gd):
    def info(txt):
        print(txt)
        input("Press enter to continue... ")
        dep.spaceScreen()

    if input("Appuyez sur 'entrée' pour passer les explications sur le jeu, sinon tappez autre chose et validez"):
        dep.spaceScreen()
        info("""Jeu de rôle NSI - Version 1.1
        Developpeur: Teddy Barthelemy
        Mise en ligne le 31/10/2022 à 01h30""")
        info("""Comment jouer ?:
        Durant le jeu vous vous trouverez principalement dans le menu par defaut.
        Ce menu vous affichera:
            - Votre position
            - Vos objects
            - Votre argent
            - Vos caractéristiques générales
        Les commandes alors disponibles sont:
            - 'm l/left | r/right | u/up | d/down
                Vous permet de vous deplacer à gauche, à droite, en haut, en bas
            - 'use x'
                Equipe/déséquipe l'item d'index x
            - 'map'
                Affiche une carte en plein ecran
            
        Si vous validez simplement sans avoir tapper de commande, la derniere commande effectuée sera réutilisée
                Affiche la carte en plein ecran""")
        info("""Exploration:
        Utilisez donc les commandes de mouvement pour vous déplacer dans la grille
        /!\\ Attention, ce labyrinthe est généré de façon totalement aléatoire
        Le jeu n'est pas encore muni de methodes de génération avancées
        La carte peut donc être coupée, rendant inaccessible certaines zones de la carte
        
        - Les salles marquées d'un '?' sont des salles encore non explorées
        - Les salles marquées d'un '✓' sont des salles conquisent (tous les enemis y sont morts)
        - Les salles marquées d'un carré rouge sont des salles presentant des enemies (salles de combats)
        - Les salles marquées d'un carré jaune sont des salles présentant un coffre (salles de récompenses)
        
        Les salles de la carte se découvre au fur et à mesure que vous avancez,
        Les salles de combat et de récompenses se découvrent quand vous entrez à l'interieur, impossible donc de 
        savoir de quelle type est une salle sans y être rentré""")
        info("""Combats:
        Les combats se découpent en deux phases:
            - Phase d'attaque de la part du joueur
            - Phase d'attaque de la part des monstres
        
        La logique dans chaques phase est semblable...
        A gauche s'affichera chaque monstres etant présent dans le combat,
        chacun d'entre eux aura à la droite de l'écran une barre, plus ou moins longue, de forme variée
        Vous aurez aussi marqué sur le bord haut de la fenetre le nombre d'essai que vous pouvez mettre dans le temps 
        imparti marqué par un chrono à coté
        Apres la pause de préparation (~1s), un curseur bougera en faisant des aller-retours dans la partie droite
        
        Si vous attaquez, les barres des enemies seront colorées en vert, jaune, rouge ou noir (selon la vie de 
        l'enemie)
        Si l'enemie vous attaque, elles seront colorées en rouge pale
        
        Votre but differe en fonction de qui attaque:
            - En cas d'attaque du joueur, visez le plus de barres enemie avec le nombre de coups qui vous est donné, 
            les barres tappées donneront des dégats au enemis qui y sont liées
            - En cas d'attaque des monstre, cherchez à tapper chaque barres au moins une fois, les barres non tappées 
            fera que l'enemie y etant lié vous frappera
        
        Les barres sont de formes differents, visez les zones les plus epaissent pour que vos attaques et votre 
        résistance au dégats soit maximisés
        Les zones sur les barres marqué de '↑' sont des zone à coup critiques, si vous les tappez, vous mettre un 
        coup causant plus de dégats que votre maximum possible""")
        info("""Prérequis affichage:
        Ce jeu utilise des characteres spéciaux pour afficher de la couleur et des effets particuliers
        
        Verifiez donc la compatibilité de votre invité de commande pour le bon affichage du jeu
        
        Si ces couleurs vous sont affichées correctement alors votre invité de commande est compatible:
            - \033[40m  \033[41m  \033[42m  \033[43m  \033[44m  \033[45m  \033[46m  \033[47m  \033[49m \033[0m
            - \033[100m  \033[101m  \033[102m  \033[103m  \033[104m  \033[105m  \033[106m  \033[107m  \033[109m \033[0m
            - \033[2mnormal \033[1mgras\033[0m
        
        Il est aussi conseillé de jouer dans un invité de commande classique et non pas dans une console de debugage 
        d'un IDE
        En cas de probleme, un invité compatible est 'Terminal' dans le Microsoft Store (dsl les macs)""")
        dep.spaceScreen()
        print("Bon jeu ;)")
        dep.wait(3)
    manager.redirect("#create_map")


manager.add(gui.Command(
    "#init",
    initGame
))
manager.redirect("#init")
