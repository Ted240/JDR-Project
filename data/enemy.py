"""
Creator: Teddy Barthelemy
25/09/2022 - 04:09

main.sub
Creature class
"""
import data.dependancies as dep
import data.screen as screen
import data.entity as entity
import data.fight as fight


class Enemy(entity.Entity):
    """
    Enemy main class

    Spawn:
        - weight (float): Chance to spawn
        - level (int): Enemy difficulty

    Fights:
        - target_size (int): Target radius
        - attack_funct (funct[self, x]): Function used when player attacks enemy (self: target instance, x: validity
        at pos x)
        - damage_funct (funct[self, x]): Function used when enemy attack player (self: target instance, x: validity
        at pos x)
    """

    __slots__ = ("_drops", "_texture",)
    weight = 0
    level = 0

    target_size: entity.Entity.Property = entity.Entity.Property(5)

    @staticmethod
    def attack_funct(self: fight.AccuracyBar.CreatureTarget, x: int) -> float:
        return 1.0 if self.on(x) else 0.0

    @staticmethod
    def damage_funct(self: fight.AccuracyBar.CreatureTarget, x: int) -> float:
        return self.entity.fight_data.attack(self, x)

    def __init__(self,
                 *,
                 health,
                 attack,
                 drops,
                 texture: dep.Union[screen.CodeImage, dep.Dict[str, screen.CodeImage]]
                 ):
        """
        Create new Enemy

        :param EnemyFactory.Property health: Health setter
        :param EnemyFactory.Property attack: Attack setter
        :param dep.List[EnemyFactory.Property] drops: Drops setter
        :param texture: Creature's texture
        """
        super().__init__(health=health, attack=attack)
        self._base_health = health.define()
        self._drops = drops
        self._texture: dep.Dict[str, screen.CodeImage] = {".": texture} if isinstance(texture,
                                                                                      screen.CodeImage) else texture

    @property
    def fight_data(self):
        return dep.Return(
            size=self.target_size,
            funct=self.attack_funct,
            attack=self.attack_funct,
            damage=self.damage_funct
        )

    def makeTarget(self, name: dep.Callable = None, funct: dep.Callable = None,
                   color: dep.Callable = None) -> fight.AccuracyBar.CreatureTarget:
        """
        Return a target bind with entity

        :param dep.Callable name: Target name function
        :param dep.Callable funct: Target verify function
        :param dep.Callable color: Target color function
        :return fight.AccuracyBar.CreatureTarget: Binded target
        """
        return fight.AccuracyBar.CreatureTarget(entity=self, x=dep.rnd.randint(0, 100 - 1), name=name, funct=funct,
                                                color=color)

    def drops(self, **kwargs):
        return [], self._drops[1].define(**kwargs)

    def makeAttackTarget(self) -> fight.AccuracyBar.CreatureTarget:
        def _name(self: fight.AccuracyBar.CreatureTarget):  # Used when player attacks as name reference
            return f"{self.entity.name[:12]:<12} {self.entity.prop('health'):>2}/{self.entity.prop('base_health'):<2}❤"

        def _color(self: fight.AccuracyBar.CreatureTarget):  # Used when player attacks as hitbox color reference
            if self.entity.life_percent == .0:
                return screen.colors.FG.black
            if 0 < self.entity.life_percent <= .2:
                return screen.colors.FG.light_red
            if .2 < self.entity.life_percent <= .5:
                return screen.colors.FG.light_yellow
            if .5 < self.entity.life_percent <= 1.0:
                return screen.colors.FG.light_green
            # if self.entity.life_percent == 1.0: return screen.colors.FG.light_blue
            return screen.colors.reset

        return self.makeTarget(
            name=_name,
            funct=self.attack_funct,
            color=_color
        )

    def makeDamageTarget(self) -> fight.AccuracyBar.CreatureTarget:
        def _name(self: fight.AccuracyBar.CreatureTarget):  # Used when enemy attacks as name reference
            return f"{self.entity.name[:12]:<12} {self.entity.prop('attack').define():<2}⚔"

        def _color(self: fight.AccuracyBar.CreatureTarget):  # Used when enemy attacks as hitbox color reference
            return screen.colors.FG.red if self.entity.life_percent > 0 else screen.colors.FG.black

        return self.makeTarget(
            name=_name,
            funct=self.damage_funct,
            color=_color
        )

    def getDrops(self, player):
        return [_.define(player=player) for _ in self._drops]

    def getTexture(self, model: str = ".") -> screen.CodeImage:
        """
        Return model in shell

        :param model: Model to show [def "."]
        """
        return self._texture[model]

    def printTexture(self, model: str = ".") -> None:
        """
        Show model in shell

        :param model: Model to show [def "."]
        """
        print(self._texture[model].string())


class EnemyFactory:
    @classmethod
    def get(cls, name: str = None):
        """
        Retrieve entity class

        :param str name: Enemy's identifiant/name
        :return Enemy.__class__: Image corresponding to id
        """
        if name in cls.listAll():
            return getattr(cls, name)

    @classmethod
    def listAll(cls) -> dep.List[str]:
        """
        Return all entity available

        :return dep.List[str]: Enemies available
        """
        return [_ for _ in dir(cls) if not _.startswith("_") and _[0].isupper()]

    class _Design:
        @classmethod
        def get(cls, name: str) -> screen.CodeImage:
            """
            Retrieve image data and convert it as ~screen.Image~

            :param name: Image's identifiant/name
            :return: Image corresponding to id
            """
            return screen.CodeImage(getattr(cls, f"_{name}") if hasattr(cls, f"_{name}") else "")

        """
        Next code is encoded image:
        An image represented as string (converted using '.image2code.py')
        """
        _bowser = "###############d0#####d0########d0d0##############_##############d0w0d0d0#d0d0y+d0######d0w0y+d0" \
                  "#############_#############d0y+y0d0r0d0r0d0w0y0d0d0####d0w0y+d0#############_" \
                  "#############d0y0d0r0d0r0r-d0w0y0d0r0d0d0#d0y+y+y+y0d0#d0d0d0########_#############d0d0r0d0r0r" \
                  "-d0w0w0y0d0r0r0r0d0r0y0y0y0y0r-d0y+w0w0d0#######_############d0r0r0r-r-r-d0y+w0w0y0d0r0r-r" \
                  "-d0d0r0r0r0r0d0g-d0y+y0d0#######_#########d0d0d0r0r0d0d0r-d0y+y+y+y0d0r0r-d0d0d0g-d0d0d0d0g0g0g" \
                  "-d0y0d0#######_########d0r0r-d0r0d0r0r0d0r0r0y0y0d0r-r-d0w-w-d0g-g0g0g0w0w0g0g0g-d0d0#######_" \
                  "########d0r0d0d0d0d0r0r0r0d0r-r-r-d0d0d0w-w-w0w0d0d0d0d0g0g0g0g0d0d0d0d0d0#####_########d0r0d0g" \
                  "-d0r0r0r-d0g-d0d0d0g0g-d0d0w-w-w0w0w0w0w0d0g0g0d0r0y+w0w0y+d0####_#########d0r0d0r0r-d0d0g-g" \
                  "-g0g0g0g0g-g-d0d0d0d0d0d0w-w0w0d0g0d0r0r0y+y0y0d0####_#########d0r-d0r-d0w-w0d0g0g0g0g0g-g-g-g-d0d" \
                  "+d+d+d+d0w-w0d0g0g0d0r-y0y0d0d0####_#######d0d0d0d0g-r-d0d0w-d0d0d0d0g-g-g-g-d0d+w0d+d+w0d+d0w" \
                  "-w0d0g0d0r-r-d0g-d0d0d0d0#_######d0y+y+y+y+d0g-d0r0d0y+y+y+y+d0d0g-d0d+d+w-w-w-w-d+d" \
                  "+d0w0d0g0g0d0d0g0g-d0y+w0w0d0_#####d0y+d0y+d0y+y+d0d0d0y+y+y0y0y+y+y+d0d0w0w-d0d0d0d0w" \
                  "-w0d0w0d0g0g0g0g0g0g-g-d0y+y0d0_#####d0y+y0y+y0y+y+y+y+y+y0y0d0d0y0y+y+y0d0w-d0y-y0y0y-d0w" \
                  "-d0w0w0d0g0g0g0g0g-g-d0y0d0#_#####d0y0y+y+y+y+y0y0y0y0d0d0w0d0d0y+y+y0d0d0y-y0y0y0y0y" \
                  "-d0d0w0w0d0g0g0g0g-g-g-d0d0##_######d0y0y0y0y0y0d0d0d0d0w0w0d0d0y+y0y0d0d0y-y0y0y0y0y" \
                  "-d0w0w0w0d0g0g0g0g-g-g-d0###_####d0d0d0d0d0d0d0d0w0w0w0d0d0d0d0y0y0y0d0w-d0d0y-y0y0y0y" \
                  "-d0w0w0w0d0g0g0g-g-g-d0d0###_##d0d0y0y0y0y0d0w0d0w0d0d0d0w0d0y0y0y0y0d0d0d0d0y0y0y0y0y0y" \
                  "-d0w0w0w0d0g0g-g-g-d0r0d0###_#d0y0y0y-d0y-d0y-d0w0d0w0d0w0d0y0y0y0d0d0w-w-w0d+d0y0y0y0y0y-d0w" \
                  "-w0w0d0g-g-g-d0r0y+d0d0##_#d0y0y0d0y0y0y0y-d0d0d0d0d0d0y0y0y0d0d0d0d0d0w-d+d+d0y0y0y-y-d0w-w-w-d0g" \
                  "-g-g-d0r0y+y+d0d0#_d0y0y-d0y0y0y-d0y-d0y0y0y0y0y0y0d0d0y0y0y0y-d0d0w-w0d0y-y-y-y-d0w-w-w-w-d0g-g" \
                  "-d0r-y0y0y0d0#_d0d0y-d0d0y-d0y-y-y-d0y0y0y0y0d0y0y-d0y0y0y0y-d0w-d+d+d0y-y-d0d0d0w-w-w-d0g-g-g" \
                  "-d0d0d0d0##_d0w0d0d0w0d0y-y-d0d0#d0d0d0d0y0y-d0y0y0y0y0y0y-d0d+w0d0d0d0d0y-y-d0w-w-w-d0g-g-g-d0" \
                  "####_#d0d0y-d0y-d0d0######d0y0d0y0y0y-d0y0y0y-d0d+d+d0y0d0y-y-y-y-d0w-w-d0g-g-d0#####_#d0w0d0d0d0" \
                  "########d0d0d0y0y-d0y0y0y-y-d0d0d0y0d0y-y0y0y-y-y-d0w-w-d0d0d0#####_##d0d0w0d0########d0w0d0d0y" \
                  "-d0y0y-d0d0d0y0y0d0y-y0y0y0y0y-y-d0w-w-w-w-d0#####_####d0d0#########d0d0w0d0d0d0y-d0y0y0y-y" \
                  "-d0y0y0y0y0y0y0y-y-d0w-w-w-d0d0####_################d0d0d0d0w0d0y-y-y-y0y0d0y0y0y0y0y0y0y-y" \
                  "-d0d0d0d0w-d0d0d0##_###############d0y0y-d0y0d0d0y0y0y0y0y0d0y0y0y0y0y0y-y-d0d0y-y-d0d0d0w-w0d0#_" \
                  "###############d0y0y0y-d0y0y0y0y0y0y0y-d0y-y0y0y0y-y-y-y-d0y-y-y0y0d0d0w-d0#_" \
                  "###############d0y0y0y-d0y-y-y-y-y-y-y0y0d0y-y-y-y-y-y-y-y-d0y-y-y0y0y0d0d0d0_" \
                  "################d0y0y0y-d0y0y0y0y0y0y0y0d0y-y-y-y-y-y-y-y-d0y-y-y-y-y-y-y-d0_################d0y-y" \
                  "-y-y-d0d0y-y0y0y0y0y0d0d0d0y-y-y-y-d0d0y-y-y-y-y-y-d0#_###############d0d0d0y-y-y-y-y" \
                  "-d0d0d0d0d0d0y-d0y-y0y0y0y0y0y-d0y-y-y-d0d0##_#############d0d0d0y0y0y-y-y-y-y-y-d0####d0d0y" \
                  "-d0d0y0d0d0y-y-d0d0d0####_############d0w0d0w0d0y0y-y-y-y-y-y-y-d0##d0w0w-d0w0w-d0w0w-d0y-y-d0" \
                  "#####_###########d0w0d0w0w0w-d0y-y-y-y-y-y-y-d0#d0w0w-d0w0w0w-d0w0w0w-d0y-d0#####_" \
                  "###########d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0#d0d0d0d0d0d0d0d0d0d0d0d0d0d0#####_"
        _bowserjr = "################d0d0#########_#########d0##d0##d0r-d0d0d0#######_########d0r0d0d0d0d0" \
                    "#d0r0d0r0r0d0######_######d0d0r0r-d0g0g0d0d0r0r0r0r-r-r-d0#####_#####d0r0r-r-d0g0g0g0g0g0d0r" \
                    "-d0d0d0r-r-d0####_#####d0r-d0d0g0g0g0g0g0g0g-d0###d0d0d0####_#####d0d0w0d0g0g0g0g-g-g-g-d0" \
                    "##########_##d0d0d0d0w0d0d0g0d0d0d0g-g-g-g-d0#########_#d0y+y+y+y+d0d0d0d0y+y0y0d0g-g-g-d0" \
                    "#########_d0y+d0y+y+y+y+y+y+y+y+y+y0y0d0g-g-d0#d0d0######_d0y+y0y+y+y+y+y+y+y+y+y" \
                    "+y0y0d0d0d0d0d0w0d0######_d0y+y+y+y+y+y0y0d0y0y+y+y0y0d0w0w0d0w0w0d0######_d0y0y0y+d0y+d0d0d0y0y" \
                    "+y0y0d0w0w0d0g0g0g0g0d0d0d0###_#d0y0y0y0d0y+y+y+d0y+y0d0w0w0d0g0g0w0w0g0g0w0w0d0##_##d0d0y" \
                    "+y0y0y0y0y0y0y0d0w0w0d0g0g0g0w0g0g0g0w0d0##_####d0d0y0y0y0y0y0y0d0d0w0w0d0g-g-g0g0g0g0g0d0##_" \
                    "######d0d0d0d0d0d0y0y0d0w0w0d0g-g0g0g0g0g0d0d0d0_#######d0y0y0d0y0y0y0y-d0w0d0g" \
                    "-g0w0w0g0g0w0w0d0_######d0y0d0y0y-y0y0y-y-d0w0d0g-g-g0w0g0g-w0d0#_######d0y0y0y0y0y0y0y" \
                    "-d0d0w0w0d0g-g-g-g-g-d0##_######d0y-y0y0y0y-y-d0y0y-d0w0d0g-g-g-g-d0d0##_#######d0y-y-y" \
                    "-d0d0y0y0y-d0w0w0d0d0d0d0w0d0##_########d0d0d0d0y0y0y0y0y-d0w0w0w0w0w0d0###_" \
                    "############d0y0y0y0y-d0d0d0d0d0d0####_###########d0d0d0y0y0y0y-d0y0y0y0d0d0###_" \
                    "##########d0w0y0y0y0y0y-y-d0d0y-y0y-y-d0##_##########d0d0d0d0d0d0d0d0d0d0d0d0d0d0###_"
        _kamek = "###################d0d0d0###########_###################d0b+b+d0##########_##################d0b+b" \
                 "+b0b0d0#########_###############d0d0d0d0b+b0b0b0d0#########_#############d0d0b+b+b+b+d0b0b0b0b-d0" \
                 "########_##########d0d0d0d0d0d0b+b+b+b+b0b0b-b-d0########_#########d0d0b+b+b+b+b0d0d0b0b0b0b0b-b-d0" \
                 "########_#########d0b+b+b+b0b0b0b0b0d0d0b0b-b-b-d0########_#########d0b+d0d0b0d0d0d0b0b0b0d0d0b-b" \
                 "-d0########_#########d0d0w0w0d0w0w0w0d0b0b0b0d0d0b-d0########_##########d0w0w0d0w0w0w0d0d0b0b0b0b" \
                 "-d0d0########_#########d0d0d0d0d0w0w0w0d0y0d0b0b-b-b-d0########_#########d0y+y+y+y+d0d0d0y+y0y0d0b" \
                 "-b-b-d0########_########d0y+y+y+y+y+y+y+y+y+y+y0y0d0b-b-d0d0#######_########d0y+y+d0y+y+y+y+y+y+y" \
                 "+y0y0y0d0d0d0d0d0######_########d0y+y+y+y+y+y+y+y+y0y0y0y0y0y0d0b-b-d0######_########d0y0y+y" \
                 "+y0y0d0d0d0d0y0y0y0y0y0d0b0b-d0d0#####_##d0d0d0####d0y0y0y0d0y0y0y0y0d0y0y0y0d0b0b0b0b-d0d0####_" \
                 "#d0r0d0w0d0####d0d0d0d0d0d0y0y0y0y0d0d0d0b+b0b0b-b-d0####_d0r0r0d0w0d0d0###d0d0d0b+b" \
                 "+d0d0d0d0d0d0d0b+b+b0b-b-b-b-d0###_d0w0r0d0w0d0w0d0#d0d0w0w0d0b0b0d0b0d0d0w0w0d0b0b0b-b-b-b-d0" \
                 "###_d0r0d0w0w0d0w0w0d0y+d0w0w0d0b0b-d0d0y+d0w0w0d0b0b-b-b-b-b-b-d0##_#d0d0w0d0d0d0d0d0y+y+d0w0w0d0b" \
                 "-d0d0y+y+d0w0w0d0b-b-b-b-b-b-d0##_##d0d0d0###d0y+y0d0w0w0d0b-d0d0y+y0d0w0w0d0b-b-b-b-b-b-d0##_" \
                 "#########d0y0d0w0b+d0b-d0d0d0y0d0w0b+d0b-b-b-b-b-b-b-d0#_##########d0d0b+b+d0d0b+b+b0d0d0b+b+d0b-b" \
                 "-b-b-b-b-b-b-d0_###########d0b+b+d0d0b+b0b0b0d0b+b+d0b-b-b-b-b-b-b-b-d0_" \
                 "###########d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0_"
        _koopa = "#####d0d0##d0d0##########_####d0y0y+d0d0y+y0d0#########_###d0y0w0w0w0w0w0y+y0d0########_" \
                 "###d0w0d0w0d0w0w0w0y+d0########_###d0w0d0w0d0w0w0w0y+d0########_##d0d0w0d0w0d0w0w0w0y+d0########_" \
                 "#d0y0y+y+w0w0w0w0w0y0y0y0d0#######_d0y0y+w0w0y+y+y+y0y0y0y+y+y+d0######_d0y+d0w0d0y+y+y+y+y0y+w0w0y" \
                 "+d0######_d0y+y+y+y+y+y+y+y+y0y+w0y+y+d0######_d0y+y+y+y+y+y+y+y0y0y+y+y+y+d0######_d0y0y+y+y+y+y+y" \
                 "+d0y0y0y+y+y0d0######_#d0y0y+y+y0d0d0d0d0y0y0y0d0#######_##d0y0y+d0y0y+y+y+y0d0d0d0d0######_" \
                 "###d0d0d0d0d0y0y0d0d0d0g0g-d0#####_#######d0d0d0y0d0w0d0g0g-d0####_######d0y+y+y0d+d0d0d0d0g0g-d0" \
                 "###_#####d0y+d+d+d+y+d0y+y0y0d0g0d0###_###d0d0d0y+y+y+y+y+y0d0y+y+y0d0g0d0##_##d0y0y0d0d+y+y+y+y0d" \
                 "+d0d0y+y+y0d0d0##_#d0y0d+y+d0y+d+d+d+d+y+y0d0d0y+y+y0d0##_#d0y0y+y+y+d0y+y+y+y+y+y0d0y0y+y+y0d0##_" \
                 "##d0y0y0y0d0y+y+y+y+y0d0d0y0y0y+y0d0d0#_###d0d0d0#d0d+d+d+d0g-g-d0y0y0d0y+y0d0_#######d0d0d0d0g-g0g" \
                 "-d+d0d0d0d0d0#_######d0g-g-g-d0g-g0g0g-g-d0####_######d0g-g0g0d0d+y0y0g0g-d+d0###_######d0d+y0y0d" \
                 "+d0d+y0y0y0d+d0###_#######d0d0d0d0#d0d0d0d0d0####_"
        _goomba = "######d+d+d+d+######_####d+d+r0r0r0r-d+d+####_###d0d0d0d0r0r0d0d0d0d0###_####d+w0d0r0r0d0w0d+####_" \
                  "###d+r0w0w0d0d0w0w0r-d+###_#d+d+r0r-d0w0r0r-d0w0r0r-d+d+#_d+r0r0r0r-d0w0r0r-d0w0r0r0r-r-d+_d" \
                  "+r0r0r0r0r0r0r0r0r0r0r0r0r-r-d+_d+r-r0w0d0d0d0d0d0d0d0d0w0r-r-d+_#d+r-w0r-r-r-r-r-r-r-r-w0r-d+#_" \
                  "##d+d+d+d+d+d+d+d+d+d+d+d+##_####d+y+y+y+y+y+y0d+####_###d0d0y+y+y+y+y+y0d0d0###_#d0d0d0d0y0y+y" \
                  "+y0y0y0d0d0d0d0#_d0d0d0d0d0d0y0y0y0y0d0d0d0d0d0d0_d0d0d0d0d0d0####d0d0d0d0d0d0_"
        _pyranha = "#####d0d0d0d0d0###############_#d0d0d0d0r-w0w0w0r-d0d0#############_d0w-w0w0r-r-r-w0r-r0r-r-d0" \
                   "############_d0w0w0w0w-w-r-r-r+r-w0w0d0############_#d0d+d+w0w0w0r-r-r-w0w0w-d0###########_" \
                   "#d0w0d0d+d+w0w-r-r0r-w0w-d0d0d0d0d0#######_##d0d0w0d0d+w0r-r+r+r-r-r-d0g-g-g-d0######_" \
                   "##d0d0d0d0d0w0r-r+r+r+r0r0d0g0g0g-g-d0d0####_##d0w0d0d+d+w0r-r0r-r-r-d0d0d0d0g0g0g-g-d0###_##d0d" \
                   "+d+w0w0w-r-r-w0w-d0####d0d0g0g-d0###_#d0w0w0w0w0w-r-r-w0w0w-d0#####d0g0g-d0###_#d0w-w-w0w0d0r-r-w" \
                   "-d0d0#####d0d0g0g-d0###_##d0d0d0d0#d0d0d0#####d0d0g0g0g-g-d0###_##############d0g+g+g-g-d0d0####_" \
                   "#######d0d0#####d0g+g-d0d0######_######d0g+g+d0d0##d0g+g-g-d0#d0d0d0###_######d0g+d0g0g-d0#d0g0g" \
                   "-d0#d0d0d0g+d0d0#_######d0g-g+d0g0g-d0g0g-g-d0d0d0g0g0d0g-g-d0_#######d0d0g0d0g0d0g0g-g-g" \
                   "-d0g0d0d0g-g-g-d0_#########d0g0d0g-g0g-g-d0g-d0g-g-d0d0d0#_######d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0" \
                   "####_######d0g+g-g0g-g-g-g-g-g0g-g0g-g+d0####_######d0g+g+g-g-g-g-g-g-g0g-g0g-g+d0####_######d0g" \
                   "+g-g0g-g-g-g-g-g0g-g0g-g+d0####_######d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0####_########d0g+g-g0g-g-g" \
                   "-g0g-g+d0######_########d0g+g+g-g-g-g-g0g-g+d0######_########d0g+g-g0g-g-g-g0g-g+d0######_" \
                   "########d0g+g+g-g-g-g-g0g-g+d0######_########d0g+g-g0g-g-g-g0g-g+d0######_" \
                   "########d0d0d0d0d0d0d0d0d0d0d0######_"
        _chomp = "##########d0d0d0d0d0######################_#######d0d0d0d0d0d0d0d0d0d0d0###################_" \
                 "#####d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0#################_####d0d0d0d0d0d0d0d0d0d0w-w-w-w-d0d0d0" \
                 "################_###d0d0d0d0d0d0d0d0d0d0w0w0w0w0w0w-d0d0d0###############_" \
                 "##d0d0d0d0d0d0d0d0d0d0d0w0d0d0w0w0w-d0d0d0d0##############_##d0d0d0d0d0d0d0d0d0d0d0w0d0d0w0w0w" \
                 "-d0d0d0d0d0#############_#d0d0d0w-w-d0d0d0d0d0d0d0d0w0w0w0w-d0d0d0d0d0d0#############_#d0w-d0w0w0w" \
                 "-d0w-w-w-d0d0d0d0d0d0d0d0d0d0d0d0d0d0############_d0w-w0w0w0w0w-d0w0w0w-d0w-w" \
                 "-d0d0d0d0d0d0d0d0d0d0d0############_d0w0w0d0w0w0d0d0w0w0d0d0w-w0w-w-d0d0d0d0d0d0d0d0d0" \
                 "############_d0w-d0d0w0d0d0r-w0r-r-r-w0w0w0d0w0w-d0d0d0d0d0d0d0d0###########_#d0##d0r-r0r0r0r0r0r" \
                 "-w0r-r-r-w0w0w-d0d0d0d0d0d0d0###########_#####d0r+r0r0r0r0r0r0r-r-r-r-d0d0w0d0d0d0d0d0d0" \
                 "###########_#####d0r+r+r0r0r0r0r0r0r-r-r-r-d0w0d0d0d0d0d0d0###########_#####d0r+r+r0r0r0r0r0r0r-r" \
                 "-w0r-d0w0d0d0d0d0d0############_#####d0r+r0r0r0r0w0w-w0r-r-w0w0w-d0d0d0d0d0d0############_##d0d0d0r" \
                 "+r+r0w0r0r0w0w0w0w-d0w-w-d0d0d0d0d0d0d0############_##d0w-w0w0w0r0w-w0w0r-w-w0w0d0d0d0d0d0d0d0d0d0" \
                 "#############_###d0w-w0w0w-r-w0w0w0w-w-d0d0d0d0d0d0d0d0d0d+d+######d+d+d+d+##_####d0w-w0w-d0w-w" \
                 "-d0d0d0d0d0d0d0d0d0d0d0w-w-w-d+####d+w-w-w-w-d+#_#####d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0w-w-d+d+w-w-d" \
                 "+##d+w-w-d+d+w-w-d+_######d0d0d0d0d0d0d0d0d0d0d0d0#d+w-d+##d+w-d+d+d+d+w-d+##d+w-d+_" \
                 "##########d0d0d0d0d0####d+w-d+##d+w-d+w-w-w-d+d+##d+w-d+_###################d+w-w-d+d+w-w-d+d+d+w-w" \
                 "-d+d+d+w-w-d+_####################d+w-w-w-w-d+d+##d+w-d+w-w-w-d+#_#####################d+d+d+d+w-d" \
                 "+##d+w-d+d+d+d+##_########################d+w-w-d+d+w-w-d+#####_#########################d+w-w-w-w" \
                 "-d+######_##########################d+d+d+d+#######_"
        _thwomp = "d0d0d0d0d0##d0d0d0d0##d0d0d0d0##d0d0d0d0d0_d0w0w0w0w0d0d0w0w0w0w0d0d0w0w0w0w0d0d0w0w0w0w0d0_d0w0w" \
                  "-w-w-w0d0w0w-w-w0d0d0w0w-w-w0d0w0w-w-w-w0d0_d0w0w-w-w-w0d0w0d+w-w0d0d0w0w-d+w0d0w0w-w-w-w0d0_d0w0w" \
                  "-w-w-w0d0d0d0d+d+w0w0d+d+d0d0d0w0w-w-w-w0d0_#d0d+w-d+d0d0w0w0d0d0d0d0d0d0w0w0d0d0d+w-d+d0#_##d0d" \
                  "+d0w0w0d+w-w0w0w0w0w0w0w-d+w0w0d0d+d0##_#d0w0d0d0w0w-w-w-w-d+w-w-d+w-w-w-w-w0d0d0w0d0#_d0w0w-d0w0w" \
                  "-w-w-w-w-w-w-w-w-w-w-w-w-w-w0d0w-w0d0_d0w0w-d0w0w-w-w-w-w-w-w-w-w-w-w-w-w-w-w0d0w-w0d0_d0d+d+d0w-w" \
                  "-d0d+d+d+w-w-w-w-d+d+d+d0w-w-d0d+d+d0_#d0d+d0w0w-d+d0d0d0d+w-w-d+d0d0d0d+w-w0d0d+d0#_##d0d0#d+w" \
                  "-d0d0d0d0d+d+d0d0d0d0w-d+#d0d0##_#d0w0d0w0w-w-w0w0d0d0d0d0w0w0d0d0w-w-w0d0w0d0#_d0w0w-d0w-w-w" \
                  "-w0w0d0d0d0d0w0w0d0d0w-w-w-d0w-w0d0_d0w0w-d0w-w-w-w-d0d0d0w-w-d0d0d0w-w-w-w-d0w-w0d0_d0w0w-d0w-d+w" \
                  "-w-w-w-w-w-w-w-w-w-w-w-d+w-d0w-w0d0_d0d+d+d0w0w-w-d0d0d0w-w-w-w-d0d0d0w-w-w0d0d+d+d0_#d0d+d0w-w" \
                  "-d0w0w0d0d0d0d0d0d0w0w0d0w-w-d0d+d0#_##d0d0w-w-d0d0d0d0w0w0d0w0d0d0d0d0w-w-d0d0##_#d0w0d0w-d" \
                  "+d0d0d0d0d0d0d0d0d0d0d0d0d+w-d0w0d0#_d0w0w-d0d+d+d0d0d0d0w0w0d0w0w0d0d0d0d+d+d0w-w0d0_d0w0w-d0w-w" \
                  "-d0w0w0d0d0d0d0d0d0w0w0d0w-w-d0w-w0d0_d0d+d+d0d+w-w-d0d0w-w-w-w-w-w-d0d0w-w-d+d0d+d+d0_#d0d+d0d+d" \
                  "+w-w-w-w-w-w-w-w-w-w-w-w-d+d+d0d+d0#_##d0d0d+w0d+w-w-w-d+d+d+d+w-w-w-d+w0d+d0d0##_#d0w0d0d0d+d+d+d" \
                  "+d+d0d0d0d0d+d+d+d+d+d0d0w0d0#_d0w0w-d+d0d0d0d0d0d0d+d0d0d+d0d0d0d0d0d0d+w-w0d0_d0w0w-w-d+d+d0w0d" \
                  "+d+d+d0d0d+d+d+w0d0d+d+w-w-w0d0_d0w0w-w-w-d+d0w0w-w-d+d0d0d+w-w-w0d0d+w-w-w-w0d0_d0d+d+d+d+d0d0d+d" \
                  "+d+d+d0d0d+d+d+d+d0d0d+d+d+d+d0_d0d0d0d0d0##d0d0d0d0##d0d0d0d0##d0d0d0d0d0_"

    """
    Subclasses definition:
    
    Every creatures in the game is an extension of <Enemy> with their own caracteristics and data
    """

    class Bowser(Enemy):
        weight = .05
        level = 10

        target_size: entity.Entity.Property = entity.Entity.Property(8)

        @staticmethod
        def attack_funct(self, x):
            return 1 / (1 + abs(self.pos_x - x)) if abs(self.pos_x - x) <= self.size else 0

        @staticmethod
        def damage_funct(self, x):
            return 1 / (1 + max(abs(self.pos_x - x) - 2, 0)) if abs(self.pos_x - x) <= self.size else 0

        def __init__(self):
            super().__init__(**{
                "health": Enemy.Property(50),
                "attack": Enemy.Property(15),
                "drops": [Enemy.Property(25), Enemy.Property(300)],
                "texture": EnemyFactory._Design.get("bowser")
            })

    class BowserJr(Enemy):
        weight = .15
        level = 7

        def __init__(self):
            super().__init__(**{
                "health": Enemy.Property(25),
                "attack": Enemy.Property(12),
                "drops": [Enemy.Property(15), Enemy.Property(150)],
                "texture": EnemyFactory._Design.get("bowserjr")
            })

    class Kamek(Enemy):
        weight = .2
        level = 5

        def __init__(self):
            super().__init__(**{
                "health": Enemy.Property(10),
                "attack": Enemy.Property(7),
                "drops": [Enemy.Property(5), Enemy.Property(50)],
                "texture": EnemyFactory._Design.get("kamek")
            })

    class Pyranha(Enemy):
        weight = .25
        level = 4

        def __init__(self):
            super().__init__(**{
                "health": Enemy.Property(8),
                "attack": Enemy.Property(6),
                "drops": [Enemy.Property(4), Enemy.Property(30)],
                "texture": EnemyFactory._Design.get("pyranha")
            })

    class Chomp(Enemy):
        weight = .2
        level = 4

        def __init__(self):
            super().__init__(**{
                "health": Enemy.Property(8),
                "attack": Enemy.Property(12),
                "drops": [Enemy.Property(4), Enemy.Property(30)],
                "texture": EnemyFactory._Design.get("chomp")
            })

    class Thwomp(Enemy):
        weight = .2
        level = 4

        def __init__(self):
            super().__init__(**{
                "health": Enemy.Property(20),
                "attack": Enemy.Property(6),
                "drops": [Enemy.Property(4), Enemy.Property(30)],
                "texture": EnemyFactory._Design.get("thwomp")
            })

    class Koopa(Enemy):
        weight = .25
        level = 2

        def __init__(self):
            super().__init__(**{
                "health": Enemy.Property(7),
                "attack": Enemy.Property(3),
                "drops": [Enemy.Property(2), Enemy.Property(15)],
                "texture": EnemyFactory._Design.get("koopa")
            })

    class Goomba(Enemy):
        weight = .3
        level = 1

        def __init__(self):
            super().__init__(**{
                "health": Enemy.Property(3),
                "attack": Enemy.Property(1),
                "drops": [Enemy.Property(1), Enemy.Property(7)],
                "texture": EnemyFactory._Design.get("goomba")
            })


if __name__ == '__main__':
    @dep.Debug.add
    def createEnemy(**kwargs):
        """Return a created enemy

        :arguments:
        """
        return EnemyFactory.get("Bowser")()


    @dep.Debug.add
    def enemyCreation(**kwargs):
        """Test entity creation and display process

        :arguments:
        """
        objs: dep.List[Enemy] = [EnemyFactory.get(obj_name)() for obj_name in EnemyFactory.listAll()]
        for obj in objs:
            obj.printTexture()


    @dep.Debug.add
    def enemyFightDisplay(**kwargs):
        """Create a fight with enemies to test display

        :arguments:
        """

        def _colorAttack(self: fight.AccuracyBar.CreatureTarget):  # Used when player attacks as hitbox color reference
            if self.entity.life_percent == .0:
                return screen.colors.FG.black
            if 0 < self.entity.life_percent <= .2:
                return screen.colors.FG.light_red
            if .2 < self.entity.life_percent <= .5:
                return screen.colors.FG.light_yellow
            if .5 < self.entity.life_percent < 1.0:
                return screen.colors.FG.light_green
            if self.entity.life_percent == 1.0:
                return screen.colors.FG.light_blue
            return screen.colors.reset

        objs: dep.List[Enemy] = [EnemyFactory.Bowser() for obj_name in range(5)]
        for obj_i, pourcentage in enumerate([.0, .1, .6, .9, 1.0]):
            objs[obj_i].giveDamage(dep.math.ceil(objs[obj_i].prop("health") * pourcentage))
        fightBar = fight.AccuracyBar(100, len(objs), 15)
        fightBar.targets = [obj.makeAttackTarget() for obj in objs]
        fightBar.run(5)

        fightBar.targets = [obj.makeDamageTarget() for obj in objs]
        fightBar.run(5)


    dep.Debug()
    exit()
