initial_stats = {
    "hp": 100,
    "max_hp": 100,
    "gp": 50,
    "xp": 0,
    "level": 1,
    "str": 10,
    "con": 10,
    "spd": 10,
    "atk": 10,
    "inventory": ["sword", "herb", "magic_crystal"],
    "current_room": "village_square",
    "current_quest": None,
    "known_spells": ["fireball"],
    "game_state": "exploring",
    "npc": None,
    "game_time": "morning",
    "equipped_items": []
}

items = {
    "green_potion": {"type": "Consumable", "value": 50, "effect": "heal","heal_amount": 20, "description": "A magical potion that heals 20 HP."},
    "sword": {"type": "Weapon", "value": 100, "bonus": 5, "damage": 8, "description": "A sharp sword that increases attack by 5."},
    "armor": {"type": "Armor", "value": 150, "bonus": 3, "description": "Light armor that increases constitution by 3."},
    "mega_sword": {"type": "Weapon", "value": 300, "bonus": 10, "damage": 15, "description": "A powerful sword that greatly increases attack."},
    "health_amulet": {"type": "Accessory", "value": 200, "bonus": 20, "description": "An amulet that increases max HP by 20."},
    "trout": {"type": "Food", "value": 10, "heal_amount": 5, "description": "A common fish, useful for cooking or trading."},
    "salmon": {"type": "Food", "value": 20, "heal_amount": 7, "description": "A valuable fish, highly sought after for its taste."},
    "catfish": {"type": "Food", "value": 15, "heal_amount": 10, "description": "A bottom-dwelling fish, useful for trading."},
    "iron": {"type": "Ore", "value": 30, "description": "A basic crafting material, essential for weapons and armor."},
    "gold": {"type": "Ore", "value": 100, "description": "A precious metal, used for crafting and trading."},
    "diamond": {"type": "Ore", "value": 500, "description": "A rare and valuable gem, used for high-level crafting."},
    "wolf_pelt": {"type": "Material", "value": 50, "description": "The pelt of a wolf, useful for crafting armor."},
    "magic_crystal": {"type": "Material", "value": 200, "description": "A crystal infused with magical energy, used for crafting powerful items."},
    "ghost_essence": {"type": "Material", "value": 300, "description": "The essence of a ghost, a rare material used in dark magic."},
    "wood": {"type": "Material", "value": 5, "description": "A basic crafting material, essential for building and crafting."},
    "stone": {"type": "Material", "value": 8, "description": "A common material used in construction and crafting."},
    "herb": {"type": "Material", "value": 12, "description": "A medicinal herb used for crafting potions and remedies."},
    "rainbow_crystal": {"type": "Material", "value": 1000, "description": "A rare and mystical crystal that radiates with all the colors of the rainbow, used in high-level enchantments."},
    "climbing_gear": {"type": "Armor", "value": 250, "description": "Essential equipment for scaling steep cliffs and mountains, increases agility during climbs."},
    "magic_mushroom": {"type": "Item", "value": 40, "description": "A rare mushroom with magical properties, used in various potions and elixirs."},
    "ice_crystal": {"type": "Material", "value": 150, "description": "A crystal imbued with the essence of ice, used in crafting cold-based items and spells."},
    "fire_stone": {"type": "Material", "value": 150, "description": "A stone with fiery energy, used in crafting fire-based items and spells."},
    "spectral_essence": {"type": "Material", "value": 250, "description": "An ethereal substance, often used in crafting spectral and ghostly items."},
    "stolen_goods": {"type": "Item", "value": 60, "description": "Illicit items, likely taken from someone else. Can be traded or used for quests."},
    "frost_crystal": {"type": "Material", "value": 180, "description": "A crystal with a chilling aura, used in crafting frost-based items and spells."},
    "frozen_fang": {"type": "Material", "value": 80, "description": "A sharp fang covered in ice, often used in the crafting of cold-related weapons."},
    "ember_core": {"type": "Material", "value": 220, "description": "The fiery core of a powerful ember, used in crafting and fire-based enchantments."},
    "obsidian_shard": {"type": "Material", "value": 130, "description": "A sharp fragment of obsidian, used in crafting dark and deadly weapons."}
}

crafting_recipes = {
    "green_potion": {"herb": 1, "magic_crystal": 1},
    "sword": {"iron": 2, "wood": 1},
    "armor": {"iron": 3, "wolf_pelt": 1},
    "mega_sword": {"iron": 3, "gold": 1, "magic_crystal": 1},
    "health_amulet": {"gold": 1, "magic_crystal": 2},
    "climbing_gear": {"iron": 1, "wolf_pelt": 2},
    "ice_sword": {"iron": 2, "ice_crystal": 1, "frost_crystal": 1},
    "fire_staff": {"wood": 1, "fire_stone": 2, "ember_core": 1},
    "ghost_blade": {"obsidian_shard": 2, "ghost_essence": 1, "spectral_essence": 1},
    "rainbow_amulet": {"gold": 1, "rainbow_crystal": 1, "magic_crystal": 1}
}

trade_options = {
    "wolf_pelt": 15,
    "magic_crystal": 30,
    "ghost_essence": 50,
    "green_potion": 25
}

spells = {
    "fireball": {
        "damage": 20,
        "combat_only": True,
        "response": "utter_cast_fireball"
    }
}

rooms = {
    "village_square": {
        "description": "You're in the village square. There's a shop and a tavern here.",
        "items": [],
        "npcs": ["merchant", "villager"],
        "exits": {"north": "forest_entrance", "east": "blacksmith", "west": "tavern"},
        "shop": "village_shop"
    },
    "forest_entrance": {
        "description": "You're at the entrance of a dark forest. You can hear strange noises.",
        "items": [],
        "npcs": ["old_man"],
        "exits": {"south": "village_square", "north": "deep_forest"},
        "shop": None
    },
    "deep_forest": {
        "description": "You're in the depths of the forest. It's very dark and eerie.",
        "items": ["health_amulet"],
        "npcs": [],
        "exits": {"south": "forest_entrance", "east": "enchanted_grove"},
        "shop": None,
        "enemies": ["wolf", "ghost_dog"]
    },
    "blacksmith": {
        "description": "You're in the blacksmith's workshop. There are various weapons and armors.",
        "items": [],
        "npcs": ["blacksmith"],
        "exits": {"west": "village_square"},
        "shop": "blacksmith_shop"
    },
    "tavern": {
        "description": "You're in the tavern. It's filled with the chatter of adventurers.",
        "items": [],
        "npcs": ["innkeeper", "drunk_cat"],
        "exits": {"east": "village_square"},
        "shop": "tavern_shop"
    },
    "mountain_pass": {
        "description": "You're on a narrow mountain pass. The wind howls around you.",
        "items": ["climbing_gear"],
        "npcs": ["mountain_guide"],
        "exits": {"south": "village_square", "north": "snowy_peak"},
        "shop": None
    },
    "snowy_peak": {
        "description": "You've reached the snowy peak of the mountain. The view is breathtaking.",
        "items": ["ice_crystal"],
        "npcs": [],
        "exits": {"south": "mountain_pass"},
        "shop": None,
        "enemies": ["frost_giant", "ice_wolf"]
    },
    "enchanted_grove": {
        "description": "You're near a river in a magical grove filled with shimmering plants and glowing mushrooms.",
        "items": ["magic_mushroom"],
        "npcs": ["forest_spirit"],
        "exits": {"west": "deep_forest", "east": "crystal_cave"},
        "shop": None
    },
    "crystal_cave": {
        "description": "You're in a cave filled with glowing crystals of various colors.",
        "items": ["rainbow_crystal"],
        "npcs": ["crystal_miner"],
        "exits": {"west": "enchanted_grove", "down": "underground_city"},
        "shop": "crystal_shop"
    },
    "underground_city": {
        "description": "You've discovered a vast underground city carved into the rock.",
        "items": [],
        "npcs": ["dwarven_king", "gnome_inventor"],
        "exits": {"up": "crystal_cave", "east": "lava_fields"},
        "shop": "dwarven_market"
    },
    "lava_fields": {
        "description": "You're in a hellish landscape of bubbling lava and scorched earth.",
        "items": ["fire_stone"],
        "npcs": [],
        "exits": {"west": "underground_city"},
        "shop": None,
        "enemies": ["fire_elemental", "lava_golem"]
    }
}

enemies = {
    "ghost_dog": {"HP": 30, "STR": 8, "CON": 4, "SPD": 6, "XP": 20, "money": 50, "damage": 20, "drops": [{"item": "spectral_essence", "tries": 1, "chance": 0.5}]},
    "wolf": {"HP": 20, "STR": 5, "CON": 2, "SPD": 2, "XP": 10, "money": 20, "damage": 15, "drops": [{"item": "wolf_pelt", "tries": 3, "chance": 0.7}]},
    "bandit": {"HP": 50, "STR": 8, "CON": 6, "SPD": 5, "XP": 50, "money": 50, "damage": 10, "drops": [{"item": "stolen_goods", "tries": 1, "chance": 0.6}]},
    "frost_giant": {"HP": 100, "STR": 12, "CON": 10, "SPD": 4, "XP": 100, "money": 80, "damage": 15, "drops": [{"item": "frost_crystal", "tries": 1, "chance": 0.4}]},
    "ice_wolf": {"HP": 60, "STR": 8, "CON": 6, "SPD": 9, "XP": 60, "money": 40, "damage": 10, "drops": [{"item": "frozen_fang", "tries": 1, "chance": 0.5}]},
    "fire_elemental": {"HP": 80, "STR": 10, "CON": 8, "SPD": 7, "XP": 80, "money": 60, "damage": 12, "drops": [{"item": "ember_core", "tries": 1, "chance": 0.3}]},
    "lava_golem": {"HP": 120, "STR": 14, "CON": 12, "SPD": 3, "XP": 120, "money": 100, "damage": 18, "drops": [{"item": "obsidian_shard", "tries": 1, "chance": 0.2}]}
}

npcs = {
    "merchant": {
        "dialogue": "Welcome! I have a shop here. Show your face there sometime.",
        "quest": "Fetch me 3 wolf pelts from the deep forest, and I'll reward you handsomely."
    },
    "old_man": {
        "dialogue": "Beware of the dangers that lurk in the deep forest, young one.",
        "quest": "Find my lost amulet in the deep forest, and I'll teach you a powerful spell."
    },
    "blacksmith": {
        "dialogue": "Need any weapons or armor? I've got the best in town!",
        "quest": "Bring me some rare metal from the deep forest, and I'll forge you a legendary weapon."
    },
    "innkeeper": {
        "dialogue": "Welcome to the Purring Pint! Care for a drink or some gossip?",
        "quest": "Help me get rid of the ghost dog in the deep forest, it's scaring away my customers!"
    },
    "drunk_cat": {
        "dialogue": "Hic! Did I ever tell you about the treasure hidden in the deep forest? Hic!",
        "quest": None
    },
    "villager": {
        "dialogue": "It's a peaceful day in the village, isn't it?",
        "quest": None
    },
    "mountain_guide": {
        "dialogue": "Watch your step on the mountain pass. It's treacherous, but the view from the peak is worth it!",
        "quest": "Bring me an ice crystal from the snowy peak, and I'll teach you mountain climbing techniques."
    },
    "forest_spirit": {
        "dialogue": "Welcome to the enchanted grove, traveler. The magic here is ancient and powerful.",
        "quest": "Collect 5 magic mushrooms for me, and I'll grant you the ability to communicate with plants."
    },
    "crystal_miner": {
        "dialogue": "These caves are full of valuable crystals, but be careful. Some say they have a mind of their own.",
        "quest": "Find me a rainbow crystal, and I'll share my secret mining techniques with you."
    },
    "dwarven_king": {
        "dialogue": "Welcome to our underground kingdom, surface dweller. What brings you to the depths?",
        "quest": "Defeat the lava golem that's been threatening our eastern tunnels, and you'll have the gratitude of the dwarven kingdom."
    },
    "gnome_inventor": {
        "dialogue": "Ah, a new test subject! I mean, customer! Want to try my latest invention?",
        "quest": "Bring me 3 fire stones from the lava fields. I need them for my latest invention: fire-proof underwear!"
    }
}

shops = {
    "village_shop": {"items": ["green_potion", "sword"]},
    "blacksmith_shop": {"items": ["armor", "mega_sword"]},
    "tavern_shop": {"items": ["potion"]},
    "crystal_shop": {"items": ["rainbow_crystal", "ice_crystal"]},
    "dwarven_market": {"items": ["mega_sword", "fire_stone", "climbing_gear"]}
}

def update_known_spells(tracker):
    known_spells = tracker.get_slot("known_spells") or []
    return known_spells + ["fireball"]

quests = {
    "wolf pelt": {
        "required_items": {"wolf_pelt": 1},
        "xp_reward": 100,
        "gp_reward": 150,
        "utterance": "utter_completed_wolf_pelt_quest"
    },
    "lost amulet": {
        "required_items": {"old_man_amulet": 1},
        "xp_reward": 150,
        "gp_reward": 0,
        "utterance": "utter_completed_old_man_amulet_quest",
        "extra_slots": {"known_spells": update_known_spells}
    },
    "ghost dog": {
        "required_items": {},
        "xp_reward": 200,
        "gp_reward": 100,
        "utterance": "utter_completed_ghost_dog_quest",
        "condition": lambda: "ghost_dog" not in rooms["deep_forest"]["enemies"]
    }
}