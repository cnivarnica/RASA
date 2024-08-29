from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from .custom_actions_packages.rpg_entities import (
    items, rooms, enemies, npcs, shops, quests,
    initial_stats, trade_options, spells, crafting_recipes)
import random
import datetime
from dateutil import parser

class ActionStartGame(Action):
    def name(self) -> Text:
        return "action_start_game"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(response="utter_greet_rpg")
        return [SlotSet(slot, value) for slot, value in initial_stats.items()] + [SlotSet("rooms", rooms)]

class ActionMove(Action):
    def name(self) -> Text:
        return "action_move"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "exploring":
            dispatcher.utter_message(response="utter_cannot_move")
            return [SlotSet("direction", None)]

        direction = tracker.get_slot("direction")
        current_room = tracker.get_slot("current_room")
        rooms = tracker.get_slot("rooms")

        if not rooms:
            dispatcher.utter_message(text="There seems to be an issue with the room data.")
            return []

        if current_room not in rooms:
            dispatcher.utter_message(response="utter_lost")
            return [SlotSet("current_room", "village_square"),
                    SlotSet("direction", None)]

        exits = rooms[current_room].get("exits", {})

        if not direction:
            if exits:
                buttons = [{"title": exit_dir.capitalize(),
                            "payload": f'/move{{"direction":"{exit_dir}"}}'}
                            for exit_dir in exits]
                dispatcher.utter_message(response="utter_which_direction", buttons=buttons)
            else:
                dispatcher.utter_message(response="utter_no_exit")
            return []

        new_room = exits.get(direction)
        if new_room:
            dispatcher.utter_message(text=f"You move {direction} to {new_room}.")
            return [SlotSet("current_room", new_room),
                    SlotSet("direction", None),
                    FollowupAction("action_look")]
        else:
            dispatcher.utter_message(response="utter_invalid_move")
            return [SlotSet("direction", None)]

class ActionLook(Action):
    def name(self) -> Text:
        return "action_look"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_room = tracker.get_slot("current_room")
        rooms = tracker.get_slot("rooms")

        if not rooms:
            dispatcher.utter_message(text="There seems to be an issue with the room data.")
            return []

        room_info = rooms.get(current_room)
        if room_info:
            message_parts = [room_info.get("description", "")]

            items = room_info.get("items")
            npcs = room_info.get("npcs")
            enemies = room_info.get("enemies")
            exits = room_info.get("exits")

            if items:
                message_parts.append(f"You see: {', '.join(items)}.")
            if npcs:
                message_parts.append(f"NPCs present: {', '.join(npcs)}.")
            if enemies:
                message_parts.append(f"Enemies lurking: {', '.join(enemies)}.")
            if exits:
                exit_directions = ', '.join(exits.keys())
                message_parts.append(f"Exits: {exit_directions}.")

            time_of_day = tracker.get_slot("game_time") or "morning"
            message_parts.append(f"It is currently {time_of_day}.")

            dispatcher.utter_message(text="\n".join(message_parts))
        else:
            dispatcher.utter_message(response="utter_lost")
            return [SlotSet("current_room", "village_square")]
        
        return []

class ActionExplore(Action):
    def name(self) -> Text:
        return "action_explore"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "exploring":
            dispatcher.utter_message(response="utter_cannot_explore")
            return []

        current_room = tracker.get_slot("current_room")
        rooms = tracker.get_slot("rooms")
        
        if not rooms or not current_room:
            dispatcher.utter_message(response="utter_room_data_err")
            return []

        room_info = rooms.get(current_room, {})
        
        outcome_probability = random.random()
        if outcome_probability < 0.4:
            return self._find_material(room_info, tracker, dispatcher)
        elif outcome_probability < 0.6:
            return self._encounter_enemy(room_info, tracker, dispatcher)
        elif outcome_probability < 0.8:
            return self._find_item(room_info, tracker, dispatcher)
        else:
            return self._explore_nothing(dispatcher)

    def _find_item(self, room_info: Dict[str, Any], tracker: Tracker, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        items = room_info.get("items", ["green_potion"])
        if not items:
            return self._explore_nothing(dispatcher)
        
        found_item = random.choice(items)
        inventory = tracker.get_slot("inventory") or []
        inventory.append(found_item)
        dispatcher.utter_message(response="utter_explore_item", item=found_item)
        return [SlotSet("inventory", inventory)]

    def _encounter_enemy(self, room_info: Dict[str, Any], tracker: Tracker, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        enemies = room_info.get("enemies", ["wolf"])
        if not enemies:
            return self._explore_nothing(dispatcher)
        
        enemy = random.choice(enemies)
        dispatcher.utter_message(response="utter_explore_enemy", enemy=enemy)
        
        # Update room info
        if "enemies" not in room_info:
            room_info["enemies"] = []
        if isinstance(room_info["enemies"], list):
            room_info["enemies"].append(enemy)
        else:
            room_info["enemies"] = [enemy]
        
        rooms = tracker.get_slot("rooms")
        current_room = tracker.get_slot("current_room")
        rooms[current_room] = room_info
        
        return [
            SlotSet("enemy", enemy),
            SlotSet("game_state", "in_combat"),
            SlotSet("rooms", rooms),
            FollowupAction("action_attack")
        ]

    def _find_material(self, room_info: Dict[str, Any], tracker: Tracker, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        materials = room_info.get("materials", ["wood", "stone", "herb"])
        material = random.choice(materials)
        inventory = tracker.get_slot("inventory") or []
        inventory.append(material)
        dispatcher.utter_message(response="utter_explore_material", material=material)
        return [SlotSet("inventory", inventory)]

    def _explore_nothing(self, dispatcher: CollectingDispatcher) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_explore_nothing")
        return []

class ActionStatus(Action):
    def name(self) -> Text:
        return "action_status"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        hp = tracker.get_slot("hp") or 0
        max_hp = tracker.get_slot("max_hp") or 0
        gp = tracker.get_slot("gp") or 0
        xp = tracker.get_slot("xp") or 0
        level = tracker.get_slot("level") or 1
        next_level_xp = level * 100
        str_stat = tracker.get_slot("str") or 0
        con_stat = tracker.get_slot("con") or 0
        spd_stat = tracker.get_slot("spd") or 0
        atk_stat = tracker.get_slot("atk") or 0
        game_state = tracker.get_slot("game_state")
        enemy = tracker.get_slot("enemy")

        message_data = {
            "game_state": game_state,
            "level": level,
            "hp": hp,
            "max_hp": max_hp,
            "gp": gp,
            "xp": xp,
            "str_stat": str_stat,
            "con_stat": con_stat,
            "spd_stat": spd_stat,
            "atk_stat": atk_stat,
            "progress": f"{(xp / next_level_xp) * 100:.1f}%"
        }

        # Add enemy status if in combat
        if game_state == "in_combat" and enemy:
            enemy_info = enemies.get(enemy, {})
            if enemy_info:
                message_data.update({
                    "enemy": enemy,
                    "enemy_hp": enemy_info.get("HP", "Unknown"),
                    "enemy_atk": enemy_info.get("damage", "Unknown"),
                    "enemy_str": enemy_info.get("STR", "Unknown"),
                    "enemy_con": enemy_info.get("CON", "Unknown"),
                    "enemy_spd": enemy_info.get("SPD", "Unknown"),
                    "enemy_xp": enemy_info.get("XP", "Unknown"),
                    "enemy_gp": enemy_info.get("money", "Unknown")
                })
                dispatcher.utter_message(response="utter_combat_status", **message_data)
            else:
                dispatcher.utter_message(response="utter_no_enemy_info")
        else:
            dispatcher.utter_message(response="utter_character_status", **message_data)

        return []

class ActionHelp(Action):
    def name(self) -> Text:
        return "action_help"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        available_actions = self.get_available_actions(dispatcher, tracker)

        message = "Here are the actions you can take right now:\n\n"
        message += "\n".join(f"- {action}" for action in available_actions)
        message += "\n\nTo perform an action, simply type the action name (e.g., 'look', 'move north', 'attack wolf').\n"
        message += self.get_additional_tips()

        dispatcher.utter_message(text=message)
        return []

    def get_available_actions(self, dispatcher: CollectingDispatcher, tracker: Tracker) -> List[Text]:
        game_state = tracker.get_slot("game_state")
        current_room = tracker.get_slot("current_room")
        rooms = tracker.get_slot("rooms")
        room_info = rooms.get(current_room, {})

        if not rooms:
            dispatcher.utter_message(response="utter_room_data_err")
            return []

        actions = {
            "exploring": [
                "look - Examine your surroundings",
                "inventory - Check the items in your inventory",
                "character info - View your character's stats",
                "quest info - See your current quests",
                "move [direction] - Move in the specified direction",
                "shop - Visit the local shop",
                "talk to [npc] - Interact with a non-player character",
                "explore - Search the area for items and enemies",
                "rest - Take a nap to restore health",
                "fish - Try your hand at fishing",
                "mine - Search for rare minerals",
                "craft - Create useful items from materials"
            ],
            "in_combat": [
                "look - Assess the battlefield",
                "inventory - Use an item from your inventory",
                "character info - Check your current status",
                "attack [enemy] - Strike an enemy",
                "use [item] - Consume a usable item",
                "cast [spell] - Unleash a magical spell",
                "run away - Attempt to flee the combat"
            ],
            "shopping": [
                "look - Inspect the shop's wares",
                "inventory - Review your current items",
                "character info - View your character details",
                "buy [item] - Purchase an item from the shop"
            ],
            "crafting": [
                "look - Examine your crafting materials",
                "inventory - Check your available items",
                "character info - Review your character stats",
                "craft [item] - Create a new item from your materials"
            ]
        }


        available_actions = actions.get(game_state, [])
        if game_state == "exploring":
            if room_info.get("shop"):
                available_actions.append("buy [item] - Purchase an item from the shop")
            if room_info.get("npcs"):
                available_actions.append(f"talk to [{', '.join(room_info['npcs'])}] - Speak with a specific NPC")

        return available_actions

    def get_additional_tips(self) -> str:
        return (
            "\nHere are some additional tips:\n"
            "- Explore different areas to find new items, enemies, and NPCs.\n"
            "- Complete quests from NPCs to gain rewards and progress the story.\n"
            "- Use items and spells wisely to defeat enemies and survive.\n"
            "- Rest at the tavern to fully restore your health.\n"
            "- Check your character info to see your current stats and level progress.\n"
            "- Craft items from materials you find in the world.\n"
            "- Pay attention to your surroundings and the time of day, as they may affect your actions."
        )

class ActionGetItem(Action):
    def name(self) -> Text:
        return "action_get_item"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, 
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not self.is_exploring(tracker):
            dispatcher.utter_message(response="utter_cannot_get_item")
            return [SlotSet("item", None)]

        rooms = tracker.get_slot("rooms") or {}
        if not rooms:
            dispatcher.utter_message(response="utter_room_data_err")
            return []

        current_room = tracker.get_slot("current_room")
        room_info = rooms.get(current_room, {"items": []})
        
        item = tracker.get_slot("item")
        if not item:
            return self.prompt_for_item(dispatcher, room_info)
        
        if item in room_info["items"]:
            return self.add_item_to_inventory(dispatcher, item, tracker, room_info, rooms, current_room)

        dispatcher.utter_message(response="utter_no_item_to_get", item=item)
        return [SlotSet("item", None)]

    def is_exploring(self, tracker: Tracker) -> bool:
        return tracker.get_slot("game_state") == "exploring"

    def prompt_for_item(self, dispatcher: CollectingDispatcher,
                        room_info: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if room_info["items"]:
            buttons = [{"title": item_name.capitalize(),
                        "payload": f'/get_item{{\"item\":\"{item_name}\"}}'}
                        for item_name in room_info["items"]]
            dispatcher.utter_message(response="utter_get_which_item", buttons=buttons)
        else:
            dispatcher.utter_message(response="utter_no_items_to_get")
        return []

    def add_item_to_inventory(self, dispatcher: CollectingDispatcher, item: Text, tracker: Tracker, 
        room_info: Dict[Text, Any], rooms: Dict[Text, Any], current_room: Text) -> List[Dict[Text, Any]]:
        inventory = tracker.get_slot("inventory") or []
        inventory.append(item)
        room_info["items"].remove(item)
        rooms[current_room] = room_info

        dispatcher.utter_message(response="utter_item_got", item=item, description=items[item]['description'])
        return [SlotSet("inventory", inventory),
                SlotSet("item", None),
                SlotSet("rooms", rooms)]

class ActionUseItem(Action):
    def name(self) -> Text:
        return "action_use_item"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state not in ["exploring", "in_combat"]:
            dispatcher.utter_message(response="utter_cannot_use_items")
            return [SlotSet("item", None)]

        item = tracker.get_slot("item")
        inventory = tracker.get_slot("inventory") or []

        if not item:
            return self.prompt_for_item(dispatcher, inventory)

        if item in inventory:
            return self.use_item(dispatcher, item, tracker, inventory)
        else:
            dispatcher.utter_message(response="utter_item_not_in_inventory", item=item)
            return [SlotSet("item", None)]

    def prompt_for_item(self, dispatcher: CollectingDispatcher, inventory: List[Text]) -> List[Dict[Text, Any]]:
        allowed_types = ["Armor", "Weapon", "Accessory", "Consumable", "Food"]
        filtered_inventory = [item_name for item_name in inventory
                              if items[item_name]["type"] in allowed_types]

        if filtered_inventory:
            buttons = [{"title": item_name,
                        "payload": f'/use_item{{"item":"{item_name}"}}'}
                        for item_name in filtered_inventory]
            dispatcher.utter_message(response="utter_use_which_item", buttons=buttons)
        else:
            dispatcher.utter_message(response="utter_no_items_to_use")
        return []

    def use_item(self, dispatcher: CollectingDispatcher, item: Text,
                 tracker: Tracker, inventory: List[Text]) -> List[Dict[Text, Any]]:
        item_type = items[item]["type"]

        if item_type in ["Weapon", "Armor", "Accessory"]:
            return self.equip_item(dispatcher, item, item_type, tracker, inventory)
        elif item_type in ["Consumable", "Food"]:
            return self.consume_item(dispatcher, item, tracker, inventory)
        else:
            dispatcher.utter_message(response="utter_cannot_use_item", item=item)
            return [SlotSet("item", None)]

    def equip_item(self, dispatcher: CollectingDispatcher, item: Text, item_type: Text,
                tracker: Tracker, inventory: List[Text]) -> List[Dict[Text, Any]]:
        try:
            equipped_items = tracker.get_slot("equipped_items") or []
            
            # Assuming the first (and only) dictionary in the list contains all the equipped items
            equipped_items_dict = equipped_items[0] if equipped_items else {}

            stat_map = {"Weapon": "atk", "Armor": "con", "Accessory": "max_hp"}
            stat = stat_map[item_type]
            bonus = items[item]["bonus"]

            # Initialize events list
            events = []

            # Check if an item of the same type is already equipped
            currently_equipped = equipped_items_dict.get(item_type)
            if currently_equipped:
                current_bonus = items[currently_equipped]["bonus"]
                inventory.append(currently_equipped)
                equipped_items_dict[item_type] = None

                # Remove current item's bonus
                current_stat = tracker.get_slot(stat) or 0
                new_stat = current_stat - current_bonus
                events.append(SlotSet(stat, new_stat))

                dispatcher.utter_message(text=f"You unequipped the {currently_equipped}, losing {current_bonus} {stat.upper()} points.")

            # Equip new item
            inventory.remove(item)
            equipped_items_dict[item_type] = item
            current_stat = tracker.get_slot(stat) or 0
            new_stat = current_stat + bonus

            # Update the list with the modified dictionary
            equipped_items = [equipped_items_dict]
            events.extend([SlotSet(stat, new_stat),
                        SlotSet("inventory", inventory),
                        SlotSet("equipped_items", equipped_items),
                        SlotSet("item", None)])

            dispatcher.utter_message(text=f"You equipped the {item}, gaining {bonus} {stat.upper()} points.")

            return events

        except Exception as e:
            dispatcher.utter_message(text=f"Error: {str(e)}")
            return [SlotSet("item", None)]


    def consume_item(self, dispatcher: CollectingDispatcher, item: Text,
                     tracker: Tracker, inventory: List[Text]) -> List[Dict[Text, Any]]:
        effect = items[item].get("effect")
        if effect == "heal":
            hp = tracker.get_slot("hp") or 0
            max_hp = tracker.get_slot("max_hp") or 0
            heal_amount = items[item].get("heal_amount", 0)
            new_hp = min(hp + heal_amount, max_hp)
            inventory.remove(item)

            dispatcher.utter_message(text=f"You consumed {item} and restored {heal_amount} HP.")

            return [SlotSet("hp", new_hp),
                    SlotSet("inventory", inventory),
                    SlotSet("item", None)]
        else:
            dispatcher.utter_message(text=f"You consumed {item}, but nothing happened.")
            return [SlotSet("item", None)]

class ActionInventory(Action):
    def name(self) -> Text:
        return "action_inventory"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        inventory = tracker.get_slot("inventory") or []
        
        if inventory:
            item_descriptions = [f"- {item}: {items[item]['description']}" for item in inventory]
            message = "Your inventory:\n" + "\n".join(item_descriptions)
        else:
            message = "Your inventory is empty."
            
        dispatcher.utter_message(text=message)
        return []

class ActionShop(Action):
    def name(self) -> Text:
        return "action_shop"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("game_state") != "exploring":
            dispatcher.utter_message(response="utter_cannot_shop")
            return []
        
        shop_name = rooms.get(tracker.get_slot("current_room"), {}).get("shop")
        if not shop_name:
            dispatcher.utter_message(response="utter_no_shop")
            return []

        shop_info = shops.get(shop_name, {"items": []})
        items_message = "\n".join(
            [f"- {item}: {items[item]['value']} GP - {items[item]['description']}" for item in shop_info['items']]
        )
        dispatcher.utter_message(text=f"Welcome to the shop! Items for sale:\n{items_message}")
        
        return [SlotSet("game_state", "shopping")]

class ActionBuyItem(Action):
    def name(self) -> Text:
        return "action_buy_item"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("game_state") != "shopping":
            dispatcher.utter_message(response="utter_not_in_shop")
            return []

        item = tracker.get_slot("item")
        current_room = tracker.get_slot("current_room")
        shop_name = rooms.get(current_room, {}).get("shop")
        shop_info = shops.get(shop_name, {"items": []})
        gp = tracker.get_slot("gp") or 0

        if not item:  # No item entity provided
            if shop_info["items"]:
                buttons = [{"title": f"{item_name} ({items[item_name]['value']} GP)",
                            "payload": f'/buy_item{{"item":"{item_name}"}}'}
                            for item_name in shop_info["items"]]
                dispatcher.utter_message(response="utter_what_to_buy", buttons=buttons)
            else:
                dispatcher.utter_message(response="utter_nothing_to_buy")
            return []

        if item not in shop_info["items"]:
            dispatcher.utter_message(response="utter_shop_no_such_item", item=item)
            return [SlotSet("item", None),
                    SlotSet("game_state", "exploring")]

        item_cost = items[item]["value"]
        if gp < item_cost:
            dispatcher.utter_message(response="utter_not_enough_money", item=item, cost=item_cost, gp=gp)
            return [SlotSet("item", None),
                    SlotSet("game_state", "exploring")]

        # Successful purchase
        gp -= item_cost
        inventory = tracker.get_slot("inventory") or []
        inventory.append(item)
        dispatcher.utter_message(response="utter_shop_buy_success", item=item, cost=item_cost)
        
        return [SlotSet("gp", gp),
                SlotSet("inventory", inventory),
                SlotSet("item", None),
                SlotSet("game_state", "exploring")]

class ActionTrade(Action):
    def name(self) -> Text:
        return "action_trade"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("game_state") != "exploring":
            dispatcher.utter_message(response="utter_cannot_trade")
            return []

        current_room = tracker.get_slot("current_room")
        if "merchant" not in rooms.get(current_room, {}).get("npcs", []):
            dispatcher.utter_message(response="utter_no_trade")
            return []

        inventory = tracker.get_slot("inventory") or []
        if not inventory:
            dispatcher.utter_message(response="utter_no_items_to_trade")
            return []

        trades_message = "\n".join([f"{item}: {value} GP" for item, value in trade_options.items()])
        dispatcher.utter_message(text=f"Available trades:\n{trades_message}")

        return [SlotSet("game_state", "trading")]

class ActionSellItem(Action):
    def name(self) -> Text:
        return "action_sell_item"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("game_state") != "trading":
            dispatcher.utter_message(response="utter_not_in_trade")
            return []

        item = tracker.get_slot("item")
        inventory = tracker.get_slot("inventory") or []
        gp = tracker.get_slot("gp") or 0

        if not item:  # No item entity provided
            tradeable_items = [item for item in inventory if item in trade_options]
            if tradeable_items:
                buttons = [{"title": f"{item} ({trade_options[item]} GP)",
                            "payload": f'/sell_item{{"item":"{item}"}}'}
                            for item in tradeable_items]
                dispatcher.utter_message(response="utter_trade_which_item", buttons=buttons)
            else:
                dispatcher.utter_message(response="utter_no_items_to_trade")
            return []

        if item not in inventory:
            dispatcher.utter_message(response="utter_item_not_found", item=item)
            return [SlotSet("item", None),
                    SlotSet("game_state", "exploring")]

        # Successful trade
        value = trade_options[item]
        inventory.remove(item)
        gp += value
        dispatcher.utter_message(text=f"You traded {item} for {value} GP.")

        return [SlotSet("inventory", inventory),
                SlotSet("gp", gp),
                SlotSet("game_state", "exploring"),
                SlotSet("item", None)]

class ActionAttack(Action):
    def name(self) -> Text:
        return "action_attack"

    def process_drops(self, enemy_info, tracker):
        inventory = tracker.get_slot("inventory") or []
        drops_message = ""

        for drop in enemy_info.get("drops", []):            
            item = drop.get("item")
            tries = drop.get("tries", 0)
            chance = drop.get("chance", 0)

            dropped_quantity = 0
            for _ in range(tries):
                if random.random() < chance:
                    dropped_quantity += 1

            if dropped_quantity > 0:
                # Add item to inventory
                for _ in range(dropped_quantity):
                    inventory.append(item)
                drops_message += f"You found {dropped_quantity} {item}. "

        return inventory, drops_message

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        game_state = tracker.get_slot("game_state")
        enemy = tracker.get_slot("enemy")
        current_room = tracker.get_slot("current_room")
        rooms = tracker.get_slot("rooms") or {}


        if not rooms:
            dispatcher.utter_message(response="utter_room_data_err")
            return []

        room_info = rooms.get(current_room, {"enemies": []})
        enemies_in_room = room_info.get("enemies", [])

        # Start a new combat if not already in combat
        if game_state != "in_combat":
            if not enemy:  # No enemy entity provided
                if enemies_in_room:
                    buttons = [{"title": enemy_name,
                                "payload": f'/attack{{"enemy":"{enemy_name}"}}'}
                                for enemy_name in enemies_in_room]
                    dispatcher.utter_message(response="utter_attack_which_enemy", buttons=buttons)
                else:
                    dispatcher.utter_message(response="utter_no_enemies")
                return []

            if enemy in enemies_in_room:
                dispatcher.utter_message(response="utter_start_combat", enemy=enemy)
                return [SlotSet("game_state", "in_combat"),
                        SlotSet("enemy", enemy)]
            else:
                dispatcher.utter_message(response="utter_no_such_enemy", enemy=enemy)
                return []

        # Continue combat
        if enemy not in enemies_in_room:
            dispatcher.utter_message(response="utter_no_such_enemy", enemy=enemy)
            return [SlotSet("game_state", "exploring"),
                    SlotSet("enemy", None)]

        enemy_info = enemies.get(enemy)
        if not enemy_info:
            dispatcher.utter_message(response="utter_no_enemy_data")
            return [SlotSet("game_state", "exploring"),
                    SlotSet("enemy", None)]

        player_at = tracker.get_slot("atk") or 0
        player_hp = tracker.get_slot("hp") or 0
        enemy_hp = enemy_info.get("HP", 0)
        damage = max(1, player_at - enemy_info.get("CON", 0))
        enemy_hp -= damage

        message = f"You hit the {enemy} for {damage} damage. "
        if enemy_hp <= 0:
            xp = tracker.get_slot("xp") or 0
            gp = tracker.get_slot("gp") or 0
            xp += enemy_info.get("XP", 0)
            gp += enemy_info.get("money", 0)

            new_inventory, drops_message = self.process_drops(enemy_info, tracker)

            message += (
                f"The {enemy} has been defeated! You gained {enemy_info.get('XP', 0)} XP and {enemy_info.get('money', 0)} GP. "
                f"{drops_message}"
            )
            room_info["enemies"].remove(enemy)
            rooms[current_room] = room_info

            dispatcher.utter_message(text=message)
            return [SlotSet("xp", xp),
                    SlotSet("gp", gp),
                    SlotSet("inventory", new_inventory),
                    SlotSet("game_state", "exploring"),
                    SlotSet("enemy", None),
                    SlotSet("rooms", rooms),
                    FollowupAction("action_check_level_up"),]

        enemy_info["HP"] = enemy_hp
        message += f"The {enemy} has {enemy_hp} HP remaining.\n"

        enemy_damage = max(1, enemy_info.get("damage", 0) - (tracker.get_slot("con") or 0))
        player_hp -= enemy_damage
        message += f"The {enemy} hits you for {enemy_damage} damage. You have {player_hp} HP left."

        if player_hp <= 0:
            message += "\nYou have been defeated! Game over."
            dispatcher.utter_message(text=message)
            return [SlotSet("hp", 0),
                    SlotSet("game_state", "game_over"),
                    SlotSet("enemy", None)]

        dispatcher.utter_message(text=message)
        return [SlotSet("hp", player_hp),
                SlotSet("game_state", "in_combat"),
                SlotSet("enemy", enemy),
                SlotSet("rooms", rooms)]

class ActionRunAway(Action):
    def name(self) -> Text:
        return "action_run_away"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("game_state") != "in_combat":
            dispatcher.utter_message(response="utter_not_in_combat")
            return []

        enemy = tracker.get_slot("enemy")
        success_chance = 0.7

        if random.random() < success_chance:
            dispatcher.utter_message(response="utter_run_success", enemy=enemy)
            return [SlotSet("game_state", "exploring"),
                    SlotSet("enemy", None)]
        else:
            dispatcher.utter_message(response="utter_run_fail", enemy=enemy)
            return [FollowupAction("action_attack")]

class ActionCheckLevelUp(Action):
    def name(self) -> Text:
        return "action_check_level_up"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        xp = tracker.get_slot("xp") or 0
        level = tracker.get_slot("level") or 1
        if xp >= level * 100:
            dispatcher.utter_message(response="utter_enough_xp")
            return [SlotSet("game_state", "leveling_up"),
                    FollowupAction("action_level_up")]
        dispatcher.utter_message(response="utter_xp_to_next_level" , xp_to_next_level=level * 100 - xp)
        return []

class ActionLevelUp(Action):
    def name(self) -> Text:
        return "action_level_up"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("game_state") != "leveling_up":
            dispatcher.utter_message(response="utter_not_leveling_up")
            return []

        xp = tracker.get_slot("xp") or 0
        level = tracker.get_slot("level") or 1
        max_hp = tracker.get_slot("max_hp") or 0
        next_level_xp = level * 100

        # Level up
        level += 1
        xp -= next_level_xp

        dispatcher.utter_message(response="utter_level_up", level=level)
        dispatcher.utter_message(response="utter_choose_stat")

        return [SlotSet("level", level),
                SlotSet("xp", xp),
                SlotSet("hp", max_hp)]

class ActionIncreaseStat(Action):
    def name(self) -> Text:
        return "action_increase_stat"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("game_state") != "leveling_up":
            dispatcher.utter_message(response="utter_not_leveling_up")
            return [SlotSet("stat", None)]

        stat = tracker.get_slot("stat")
        valid_stats = ["str", "con", "spd", "atk"]

        if not stat:
            # No stat selected, present options to the user
            buttons = [{"title": stat.upper(),
                        "payload": f'/increase_stat{{"stat":"{stat}"}}'}
                        for stat in valid_stats]
            dispatcher.utter_message(response="utter_choose_stat", buttons=buttons)
            return []

        if stat.lower() not in valid_stats:
            dispatcher.utter_message(response="utter_invalid_stat", stat=stat)
            return [SlotSet("stat", None)]

        # Increase the stat
        current_value = tracker.get_slot(stat.lower()) or 0
        current_value += 1

        dispatcher.utter_message(response="utter_stat_increased", stat=stat, value=current_value)
        return [SlotSet(stat.lower(), current_value),
                SlotSet("game_state", "exploring"),
                SlotSet("stat", None),
                FollowupAction("action_check_level_up")]

class ActionQuestInfo(Action):
    def name(self) -> Text:
        return "action_quest_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_quest = tracker.get_slot("current_quest")
        
        if current_quest:
            dispatcher.utter_message(response="utter_quest_info", current_quest=current_quest)
        else:
            dispatcher.utter_message(response="utter_no_quest")
        
        return []

class ActionTalkToNPC(Action):
    def name(self) -> Text:
        return "action_talk_to_npc"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        npc = tracker.get_slot("npc")
        current_room = tracker.get_slot("current_room")
        rooms = tracker.get_slot("rooms")
        room_info = rooms.get(current_room, {"npcs": []})

        # Check if rooms data is available
        if not rooms:
            dispatcher.utter_message(response="utter_room_data_err")
            return []

        # Handle the case where no NPC is provided
        if not npc:
            if room_info["npcs"]:
                buttons = [{"title": npc_name,
                            "payload": f'/talk_to_npc{{"npc":"{npc_name}"}}'}
                            for npc_name in room_info["npcs"]]
                dispatcher.utter_message(response="utter_talk_to_who", buttons=buttons)
            else:
                dispatcher.utter_message(response="utter_no_npcs")
            return []

        # Handle the case where the NPC exists in the room
        if npc in room_info["npcs"]:
            npc_info = npcs[npc]
            dispatcher.utter_message(text=f"You talk to {npc}.")
            dispatcher.utter_message(response="utter_talk_to_npc", npc_dialogue=npc_info["dialogue"])

            # Assign a quest if the NPC offers one and the player doesn't already have a quest
            if npc_info.get("quest") and not tracker.get_slot("current_quest"):
                dispatcher.utter_message(response="utter_npc_gives_quest", npc=npc, quest=npc_info["quest"])
                return [SlotSet("current_quest", npc_info["quest"]),
                        SlotSet("npc", None)]

        else:
            dispatcher.utter_message(response="utter_no_such_npc", npc=npc)
        
        return [SlotSet("npc", None)]

class ActionCompleteQuest(Action):
    def name(self) -> Text:
        return "action_complete_quest"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_quest = tracker.get_slot("current_quest")
        inventory = tracker.get_slot("inventory") or []
        xp = tracker.get_slot("xp") or 0
        gp = tracker.get_slot("gp") or 0

        if not current_quest:
            dispatcher.utter_message(response="utter_no_done_quests")
            return []

        for quest, data in quests.items():
            if quest in current_quest.lower():
                # Check if additional conditions for the quest are met
                if "condition" in data and not data["condition"]():
                    break
                
                # Check if the player has required items
                if all(inventory.count(item) >= amount for item, amount in data["required_items"].items()):
                    # Update inventory
                    for item, amount in data["required_items"].items():
                        for _ in range(amount):
                            inventory.remove(item)
                    
                    # Calculate rewards
                    xp += data["xp_reward"]
                    gp += data["gp_reward"]
                    
                    # Update slots
                    slots = [SlotSet("xp", xp),
                            SlotSet("gp", gp),
                            SlotSet("inventory", inventory),
                            SlotSet("current_quest", None)]

                    if "extra_slots" in data:
                        slots.extend([SlotSet(k, v) for k, v in data["extra_slots"].items()])

                    dispatcher.utter_message(response=data["utterance"])
                    return slots
        
        # If no quest was completed
        dispatcher.utter_message(response="utter_quest_not_completed")
        return []

class ActionCastSpell(Action):
    def name(self) -> Text:
        return "action_cast_spell"

    def process_drops(self, enemy_info, tracker):
        inventory = tracker.get_slot("inventory") or []
        drops_message = ""

        for drop in enemy_info.get("drops", []):
            item = drop.get("item")
            tries = drop.get("tries", 0)
            chance = drop.get("chance", 0)

            dropped_quantity = 0
            for _ in range(tries):
                if random.random() < chance:
                    dropped_quantity += 1

            if dropped_quantity > 0:
                # Add item to inventory
                for _ in range(dropped_quantity):
                    inventory.append(item)
                drops_message += f"You found {dropped_quantity} {item}. "

        return inventory, drops_message

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        spell = tracker.get_slot("spell")
        known_spells = tracker.get_slot("known_spells") or []
        game_state = tracker.get_slot("game_state")
        current_room = tracker.get_slot("current_room")
        rooms = tracker.get_slot("rooms") or {}
        enemy = tracker.get_slot("enemy")
        
        if not spell:  # If no spell is selected, show available spells
            if known_spells:
                buttons = [{"title": spell_name,
                            "payload": f'/cast_spell{{"spell":"{spell_name}"}}'}
                            for spell_name in known_spells]
                dispatcher.utter_message(response="utter_cast_which", buttons=buttons)
            else:
                dispatcher.utter_message(response="utter_no_spells")
            return []
        
        if spell not in known_spells:
            dispatcher.utter_message(response="utter_no_such_spell", spell=spell)
            return [SlotSet("spell", None)]
        
        if spell in spells:
            spell_info = spells[spell]
            
            if spell_info.get("combat_only") and game_state != "in_combat":
                dispatcher.utter_message(response="utter_spell_requires_combat", spell=spell)
                return [SlotSet("spell", None)]
            
            if spell == "fireball" and enemy:
                enemy_info = enemies.get(enemy)
                if not enemy_info:
                    dispatcher.utter_message(response="utter_no_enemy_data")
                    return [SlotSet("game_state", "exploring"),
                            SlotSet("spell", None),
                            SlotSet("enemy", None)]
                
                damage = spell_info["damage"]
                enemy_hp = enemy_info.get("HP", 0) - damage
                message = f"You cast {spell} and hit the {enemy} for {damage} damage. "
                
                if enemy_hp <= 0:
                    xp = tracker.get_slot("xp") or 0
                    gp = tracker.get_slot("gp") or 0
                    xp += enemy_info.get("XP", 0)
                    gp += enemy_info.get("money", 0)

                    new_inventory, drops_message = self.process_drops(enemy_info, tracker)
                    message += (
                        f"The {enemy} has been defeated! You gained {enemy_info.get('XP', 0)} XP and {enemy_info.get('money', 0)} GP. "
                        f"{drops_message}"
                    )
                    room_info = rooms.get(current_room, {"enemies": []})
                    room_info["enemies"].remove(enemy)
                    rooms[current_room] = room_info

                    dispatcher.utter_message(text=message)
                    return [SlotSet("xp", xp),
                            SlotSet("gp", gp),
                            SlotSet("inventory", new_inventory),
                            SlotSet("game_state", "exploring"),
                            SlotSet("enemy", None),
                            SlotSet("rooms", rooms),
                            SlotSet("spell", None),
                            FollowupAction("action_check_level_up"),]

                # If enemy is not defeated
                enemy_info["HP"] = enemy_hp
                message += f"The {enemy} has {enemy_hp} HP remaining.\n"
                enemy_damage = max(1, enemy_info.get("damage", 0) - (tracker.get_slot("con") or 0))
                player_hp = (tracker.get_slot("hp") or 0) - enemy_damage
                message += f"The {enemy} hits you for {enemy_damage} damage. You have {player_hp} HP left."

                if player_hp <= 0:
                    message += "\nYou have been defeated! Game over."
                    dispatcher.utter_message(text=message)
                    return [SlotSet("hp", 0),
                            SlotSet("game_state", "game_over"),
                            SlotSet("enemy", None),
                            SlotSet("spell", None)]

                dispatcher.utter_message(text=message)
                return [SlotSet("hp", player_hp),
                        SlotSet("game_state", "in_combat"),
                        SlotSet("enemy", enemy),
                        SlotSet("rooms", rooms),
                        SlotSet("spell", None)]
        
        # Default case, spell is not handled
        dispatcher.utter_message(response="utter_spell_not_recognized")
        return [SlotSet("spell", None)]

class ActionCraft(Action):
    def name(self) -> Text:
        return "action_craft"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        if game_state != "exploring":
            dispatcher.utter_message(response="utter_cannot_craft")
            return []

        inventory = tracker.get_slot("inventory") or []
        craftable_item = next(tracker.get_latest_entity_values("craftable_item"), None)

        # Determine craftable items based on available materials in the inventory
        craftable_items = [item for item, recipe in crafting_recipes.items()
                           if self.can_craft(recipe, inventory)]

        if not craftable_items:
            dispatcher.utter_message(text="You don't have enough materials to craft anything.")
            return []

        if not craftable_item or craftable_item not in craftable_items:
            buttons = [{"title": item,
                        "payload": f'/craft{{"craftable_item":"{item}"}}'} 
                        for item in craftable_items]
            dispatcher.utter_message(text="What would you like to craft?", buttons=buttons)
            return []

        # Craft the chosen item
        recipe = crafting_recipes[craftable_item]
        for material, amount in recipe.items():
            for _ in range(amount):
                inventory.remove(material)

        inventory.append(craftable_item)

        dispatcher.utter_message(text=f"You have crafted a {craftable_item}!")
        return [SlotSet("inventory", inventory)]

    def can_craft(self, recipe: Dict[str, int], inventory: List[Text]) -> bool:
        """Check if the recipe can be crafted based on the current inventory."""
        temp_inventory = inventory.copy()  # Create a temporary inventory to check availability
        for material, amount in recipe.items():
            if temp_inventory.count(material) < amount:
                return False
            for _ in range(amount):
                temp_inventory.remove(material)
        return True

class ActionFish(Action):
    def name(self) -> Text:
        return "action_fish"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_room = tracker.get_slot("current_room")
        room_description = rooms.get(current_room, {}).get("description", "").lower()

        if "river" in room_description:
            success_chance = 0.5  # Chance to successfully catch a fish
            if random.random() < success_chance:
                fish = random.choice(["trout", "salmon", "catfish"])
                inventory = tracker.get_slot("inventory") or []
                inventory.append(fish)
                dispatcher.utter_message(response="utter_fish_success", fish=fish)
                return [SlotSet("inventory", inventory)]
            else:
                dispatcher.utter_message(response="utter_fish_fail")
        else:
            dispatcher.utter_message(response="utter_cannot_fish")

        return []

class ActionMine(Action):
    def name(self) -> Text:
        return "action_mine"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_room = tracker.get_slot("current_room")
        room_description = rooms.get(current_room, {}).get("description", "").lower()

        # Check if mining is possible in the current room
        if "cave" in room_description:
            if random.random() < 0.4:  # 40% chance of finding ore
                ore = random.choice(["iron", "gold", "diamond"])
                inventory = tracker.get_slot("inventory") or []
                inventory.append(ore)

                dispatcher.utter_message(response="utter_mine_success", ore=ore)
                return [SlotSet("inventory", inventory)]
            else:
                dispatcher.utter_message(response="utter_mine_fail")
        else:
            dispatcher.utter_message(response="utter_cannot_mine")

        return []

class ActionRest(Action):
    def name(self) -> Text:
        return "action_rest"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        game_state = tracker.get_slot("game_state")
        current_room = tracker.get_slot("current_room")
        max_hp = tracker.get_slot("max_hp") or 0
        current_hp = tracker.get_slot("hp") or 0

        # Prevent resting if the player is in combat
        if game_state == "in_combat":
            dispatcher.utter_message(response="utter_cannot_rest_in_combat")
            return []

        # Resting in the tavern fully restores HP
        if current_room == "tavern":
            dispatcher.utter_message(response="utter_rest_in_tavern")
            return [SlotSet("hp", max_hp),
                    FollowupAction("action_pass_time")]
        
        # Resting elsewhere restores up to 20 HP
        heal_amount = min(max_hp - current_hp, 20)
        if heal_amount > 0:
            new_hp = min(max_hp, current_hp + heal_amount)
            dispatcher.utter_message(response="utter_rest", hp=heal_amount)
            return [SlotSet("hp", new_hp),
                    FollowupAction("action_pass_time")]

        # In case no healing is needed (already at max HP)
        dispatcher.utter_message(response="utter_rest_at_full_health")
        return [FollowupAction("action_pass_time")]

class ActionPassTime(Action):
    def name(self) -> Text:
        return "action_pass_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        time_sequence = ["morning", "afternoon", "evening", "night"]
        current_time = tracker.get_slot("game_time") or "morning"

        # Safely handle cases where current_time is not in the sequence
        if current_time not in time_sequence:
            current_time = "morning"

        # Calculate the next time of day
        new_time = time_sequence[(time_sequence.index(current_time) + 1) % len(time_sequence)]

        # Announce the passage of time
        dispatcher.utter_message(response="utter_pass_time", time=new_time)

        # Additional messages for specific times of day
        if new_time == "night":
            dispatcher.utter_message(response="utter_night_dawns")
        elif new_time == "morning":
            dispatcher.utter_message(response="utter_new_day")

        return [SlotSet("game_time", new_time)]

class ActionCheckGameOver(Action):
    def name(self) -> Text:
        return "action_check_game_over"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        hp = tracker.get_slot("hp")

        if hp is not None and hp <= 0:
            dispatcher.utter_message(response="utter_game_over")
            return [SlotSet("game_state", "game_over")]

        return []
