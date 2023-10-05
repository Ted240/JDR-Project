"""
Creator: Teddy Barthelemy
25/09/2022 - 07:11

main.sub
Chest, Loot, LootData classes
"""
import data.dependancies as dep
import data.screen as screen


class LootData:
    effects_icons = {
        "base_health": "❤",
        "health": "❤",
        "attack": "⚔️",
        "toughness": "🛡️",
        "luck": "🍀",
        "speed": "⏱️", #⋙️
        "loot": "📈",
        "coin": "💰"
    }
    tiers = [
        { "name": "Common",     "coef": 1,      "color": screen.colors.FG.white             },
        { "name": "Uncommon",   "coef": 1.1,    "color": screen.colors.FG.light_green       },
        { "name": "Rare",       "coef": 1.3,    "color": screen.colors.FG.light_blue        },
        { "name": "Epic",       "coef": 1.7,    "color": screen.colors.FG.magenta           },
        { "name": "Legendary",  "coef": 2.2,    "color": screen.colors.FG.light_yellow      },
        { "name": "Mytical",    "coef": 3,      "color": screen.colors.FG.light_red         }
    ]
    items = {
        "red_mushroom":     {   "type": "active" , "name": "Mushroom",          "targets": [
            ["health",      "+",    5  ]
        ]},
        "green_mushroom":   {   "type": "active" , "name": "1UP Mushroom",      "targets": [
            ["health",      "+",    15 ]]},
        "giant_mushroom":   {   "type": "passive", "name": "Giant Mushroom",    "targets": [
            ["attack",      "*",    1.2],
            ["toughness",   "*",    0.9],
            ["speed",       "*",    0.9]]},
        "hammer":           {   "type": "passive", "name": "Hammer",            "targets": [
            ["attack",      "*",    1.2]]},
        "koopa_shell":      {   "type": "passive", "name": "Koopa Shell",       "targets": [
            ["toughness",   "*",    0.7],
            ["speed",       "*",    0.85]]},
        "lucky_block":      {   "type": "passive", "name": "Lucky Block",       "targets": [
            ["luck",        "*",    1.5]
        ]},
        "gold_coin":        {   "type": "passive", "name": "Golden Coin",       "targets": [
            ["coin",        "*",    1.3]
        ]},
        "coin":             {   "type": "passive", "name": "Coin",              "targets": [
            ["coin",        "+",    10 ]
        ]},
        "wings_cap":        {   "type": "passive", "name": "Wings Cap",         "targets": [
            ["speed",       "*",    1.3]
        ]},
        "_unknown":         {   "type": "passive", "name": "NaN",               "targets": [

        ]}
    }


class Loot:
    def __init__(self, item, tier=0):
        self._item = item
        self._tier = min(tier, len(LootData.tiers)-1)
        self._type = None
        self._effects = {}
        self._name = "NaN"
        self._generate()

    type = property(fget=lambda self: self._type)
    tier = property(fget=lambda self: self._tier)

    def _generate(self):
        self._type = LootData.items.get(self._item, LootData.items["_unknown"])\
            .get("type", "passive")
        self._name = LootData.items.get(self._item, LootData.items["_unknown"])\
            .get("name", "NaN")
        self._effects = {
            spec[0]: [spec[1], spec[2]]
            for spec in LootData.items.get(self._item, LootData.items["_unknown"]).get("targets", [])
        }

    @property
    def effects(self):
        return {
            k: [v[0], v[1]**LootData.tiers[self._tier].get("coef", 1)] for k, v in self._effects.items()
        }

    @property
    def display_name(self) -> str:
        return "{color}{_c.bold}[ {tier_name} ] {name}{_c.reset}".format(
            color = LootData.tiers[self._tier].get('color', ''),
            tier_name = LootData.tiers[self._tier].get('name', 'Unclassified'),
            name = self._name,
            _c = screen.colors
        )


    def format(self, formater:str) -> str:
        """
        Return a formated string

        Args:
         - display_name : name with tier color, tier name and item name
         - tier_name    : tier name value
         - tier_id      : tier order index
         - tier_color   : tier color char
         - name         : item name

         - effects      : all effects
           ~.base_health     : health boost value
           ~.health     : health boost value
           ~.attack     : attack boost value
           ~.toughness  : toughness boost value
           ~.luck       : luck boost value
           ~.speed      : speed boost value
           ~.loot       : loot boost value
           ~.coin       : coin boost value
           ~.~.value    : return value (ex: '+15' / '+10%')
           ~.~.icon     : return value as icon (ex: '❤')
           ~.~.full     : return value as icon (ex: 'health')

         - _c           : [Optional] access to colored chars (<screen.colors>)

        :param str formater: Format order string
        :return str: Formated string
        """
        def _effectFormat():
            return dep.Return(
                **{
                    k: dep.Return(
                        value = (f"{'-' if self.effects[k][1] < 1 else '+'}{round(abs(self.effects[k][1]-1)*100)}%" if self.effects[k][0] == "*" else f"{round(self.effects[k][1], 2)}pts") if k in self.effects.keys() else '+0%',
                        icon = LootData.effects_icons.get(k, ""),
                        full = k.replace("_", " "),
                    )
                    for k in ["base_health", "health", "attack", "toughness", "luck", "speed", "loot", "coin"]
                }
            )

        return formater.format(
            display_name = self.display_name,
            tier_name = LootData.tiers[self._tier].get('name', 'Unclassified'),
            tier_id = self._tier,
            tier_color = LootData.tiers[self._tier].get('color', ''),
            name = self._name,
            effects = _effectFormat(),
            _c = screen.colors
        )

    def use(self, player) -> None:
        """
        Make item function (equip / disequip / apply )

        :param player.Player player: Player to apply on
        """
        if player.hasItem(self):
            if self._type == "active":
                player.apply(self)
            elif self._type == "passive":
                if self in player.equiped:
                    player.disequip(self)
                else:
                    player.equip(self)

    def __repr__(self):
        return self.format("<Loot: {name} ({tier_name})>")


class Chest:
    __slots__ = ("_content", "_room", "_static_cost", "_static_base", "_tier_cost")

    def __init__(self, room):
        """
        Chest constructor

        :param room.LeveledRoom room: Room containing the chest
        """
        self._static_cost = 1.9
        self._static_base = 5
        self._tier_cost = [self._static_base+dep.math.ceil(self._static_cost**t) for t in range(len(LootData.tiers))]

        self._content: dep.List[Loot] = []
        self._room = room

    @property
    def content(self):
        return self._content
    # content = property(fget=lambda self: self._content) Litteraly bugged wtf (skip 1/2 items when len(items) > 3)

    @property
    def cost(self):
        return sum([self._tier_cost[i.tier] for i in self._content])
    # cost = property(fget=lambda self: sum([self._tier_cost[i.tier] for i in self._content]))

    def generate(self) -> None:
        """
        Generate a chest with items
        """
        price = self._room.level
        while len(self._content) < 5 and price >= self._static_base+1 and dep.rnd.randint(0, 10):
            self._content.append(
                Loot(
                    dep.rnd.choice([i for i in LootData.items.keys() if not i.startswith("_")]),
                    dep.rnd.choice([i for i in range(len(LootData.tiers)) if self._tier_cost[i] <= price])
                )
            )

    def pop(self, item: Loot):
        self._content.remove(item)
