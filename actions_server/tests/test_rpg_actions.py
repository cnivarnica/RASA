import unittest
from unittest.mock import MagicMock
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction

from rasa_actions.rpg_actions import (
    ActionStartGame, ActionMove, ActionLook, ActionExplore, ActionStatus,
    ActionHelp, ActionGetItem, ActionUseItem, ActionInventory, ActionShop,
    ActionBuyItem, ActionTrade, ActionExecuteTrade, ActionAttack, ActionRunAway,
    ActionCheckLevelUp, ActionLevelUp, ActionIncreaseStat, ActionQuestInfo,
    ActionTalkToNPC, ActionCompleteQuest, ActionCastSpell, ActionCraft,
    ActionFish, ActionMine, ActionRest, ActionPassTime, ActionCheckGameOver
)

class TestRPGActions(unittest.TestCase):

    def setUp(self):
        self.dispatcher = CollectingDispatcher()
        self.tracker = Tracker.from_dict({
            "sender_id": "test_user",
            "slots": {},
            "latest_message": {},
            "events": []
        })
        self.domain = {}

    def test_action_start_game(self):
        action = ActionStartGame()
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertEqual(len(events), 16)
        self.assertIn(SlotSet("hp", 100), events)
        self.assertIn(SlotSet("max_hp", 100), events)
        self.assertIn(SlotSet("gp", 50), events)
        self.assertIn(SlotSet("current_room", "village_square"), events)

    def test_action_move(self):
        action = ActionMove()
        
        self.tracker.slots["current_room"] = "village_square"
        self.tracker.slots["game_state"] = "exploring"
        self.tracker.slots["direction"] = "north"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("current_room", "forest_path"), events)
        self.assertIn(SlotSet("direction", None), events)
        self.assertIn(FollowupAction("action_look"), events)

    def test_action_look(self):
        action = ActionLook()
        
        self.tracker.slots["current_room"] = "village_square"
        self.tracker.slots["game_time"] = "morning"
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn("village square", self.dispatcher.messages[0]['text'].lower())
        self.assertIn("morning", self.dispatcher.messages[0]['text'].lower())

    def test_action_explore(self):
        action = ActionExplore()
        
        self.tracker.slots["game_state"] = "exploring"
        self.tracker.slots["current_room"] = "forest_path"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertTrue(len(events) > 0)  # Should return at least one event

    def test_action_status(self):
        action = ActionStatus()
        
        self.tracker.slots["hp"] = 80
        self.tracker.slots["max_hp"] = 100
        self.tracker.slots["gp"] = 100
        self.tracker.slots["xp"] = 50
        self.tracker.slots["level"] = 2
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn("80/100", self.dispatcher.messages[0]['text'])
        self.assertIn("Level: 2", self.dispatcher.messages[0]['text'])

    def test_action_help(self):
        action = ActionHelp()
        
        self.tracker.slots["game_state"] = "exploring"
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn("actions you can take", self.dispatcher.messages[0]['text'].lower())

    def test_action_get_item(self):
        action = ActionGetItem()
        
        self.tracker.slots["game_state"] = "exploring"
        self.tracker.slots["current_room"] = "forest_path"
        self.tracker.slots["item"] = "potion"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("item", None), events)

    def test_action_use_item(self):
        action = ActionUseItem()
        
        self.tracker.slots["game_state"] = "exploring"
        self.tracker.slots["item"] = "potion"
        self.tracker.slots["inventory"] = ["potion"]
        self.tracker.slots["hp"] = 80
        self.tracker.slots["max_hp"] = 100
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("hp", 100), events)
        self.assertIn(SlotSet("inventory", []), events)

    def test_action_inventory(self):
        action = ActionInventory()
        
        self.tracker.slots["inventory"] = ["potion", "sword"]
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn("potion", self.dispatcher.messages[0]['text'])
        self.assertIn("sword", self.dispatcher.messages[0]['text'])

    def test_action_shop(self):
        action = ActionShop()
        
        self.tracker.slots["game_state"] = "exploring"
        self.tracker.slots["current_room"] = "village_square"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("game_state", "shopping"), events)

    def test_action_buy_item(self):
        action = ActionBuyItem()
        
        self.tracker.slots["game_state"] = "shopping"
        self.tracker.slots["item"] = "potion"
        self.tracker.slots["gp"] = 100
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("gp", 75), events)  # Assuming potion costs 25 gp
        self.assertIn(SlotSet("item", None), events)

    def test_action_trade(self):
        action = ActionTrade()
        
        self.tracker.slots["game_state"] = "exploring"
        self.tracker.slots["current_room"] = "village_square"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("game_state", "shopping"), events)

    def test_action_execute_trade(self):
        action = ActionExecuteTrade()
        
        self.tracker.slots["game_state"] = "shopping"
        self.tracker.slots["trade_item"] = "wolf_pelt"
        self.tracker.slots["inventory"] = ["wolf_pelt"]
        self.tracker.slots["gp"] = 50
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("gp", 65), events)  # Assuming wolf_pelt sells for 15 gp
        self.assertIn(SlotSet("inventory", []), events)

    def test_action_attack(self):
        action = ActionAttack()
        
        self.tracker.slots["game_state"] = "in_combat"
        self.tracker.slots["enemy"] = "wolf"
        self.tracker.slots["hp"] = 100
        self.tracker.slots["atk"] = 15
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("hp", 90), events)  # Assuming wolf does 10 damage
        self.assertIn(SlotSet("game_state", "in_combat"), events)

    def test_action_run_away(self):
        action = ActionRunAway()
        
        self.tracker.slots["game_state"] = "in_combat"
        self.tracker.slots["enemy"] = "wolf"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertTrue(SlotSet("game_state", "exploring") in events or FollowupAction("action_attack") in events)

    def test_action_check_level_up(self):
        action = ActionCheckLevelUp()
        
        self.tracker.slots["xp"] = 150
        self.tracker.slots["level"] = 1
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("game_state", "leveling_up"), events)
        self.assertIn(FollowupAction("action_level_up"), events)

    def test_action_level_up(self):
        action = ActionLevelUp()
        
        self.tracker.slots["game_state"] = "leveling_up"
        self.tracker.slots["level"] = 1
        self.tracker.slots["xp"] = 150
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("level", 2), events)
        self.assertIn(SlotSet("xp", 50), events)

    def test_action_increase_stat(self):
        action = ActionIncreaseStat()
        
        self.tracker.slots["game_state"] = "leveling_up"
        self.tracker.slots["stat"] = "str"
        self.tracker.slots["str"] = 10
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("str", 11), events)
        self.assertIn(SlotSet("game_state", "exploring"), events)

    def test_action_quest_info(self):
        action = ActionQuestInfo()
        
        self.tracker.slots["current_quest"] = "Collect 3 wolf pelts"
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn("Collect 3 wolf pelts", self.dispatcher.messages[0]['text'])

    def test_action_talk_to_npc(self):
        action = ActionTalkToNPC()
        
        self.tracker.slots["npc"] = "old_man"
        self.tracker.slots["current_room"] = "village_square"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("npc", None), events)

    def test_action_complete_quest(self):
        action = ActionCompleteQuest()
        
        self.tracker.slots["current_quest"] = "Collect 3 wolf pelts"
        self.tracker.slots["inventory"] = ["wolf_pelt", "wolf_pelt", "wolf_pelt"]
        self.tracker.slots["xp"] = 50
        self.tracker.slots["gp"] = 100
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("xp", 150), events)
        self.assertIn(SlotSet("gp", 150), events)
        self.assertIn(SlotSet("current_quest", None), events)

    def test_action_cast_spell(self):
        action = ActionCastSpell()
        
        self.tracker.slots["spell"] = "fireball"
        self.tracker.slots["known_spells"] = ["fireball"]
        self.tracker.slots["in_combat"] = True
        self.tracker.slots["enemy"] = "wolf"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("spell", None), events)

    def test_action_craft(self):
        action = ActionCraft()
        
        self.tracker.slots["game_state"] = "exploring"
        self.tracker.slots["crafting_materials"] = ["wood", "stone", "herb"]
        self.tracker.slots["inventory"] = []
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("inventory", ["potion"]), events)

    def test_action_fish(self):
        action = ActionFish()
        
        self.tracker.slots["current_room"] = "river_bank"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertTrue(len(events) == 0 or SlotSet("inventory", ["trout"]) in events)

    def test_action_mine(self):
        action = ActionMine()
        
        self.tracker.slots["current_room"] = "cave"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertTrue(len(events) == 0 or SlotSet("inventory", ["iron"]) in events)

    def test_action_rest(self):
        action = ActionRest()
        
        self.tracker.slots["game_state"] = "exploring"
        self.tracker.slots["hp"] = 80
        self.tracker.slots["max_hp"] = 100
        self.tracker.slots["current_room"] = "forest_path"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("hp", 100), events)
        self.assertIn(FollowupAction("action_pass_time"), events)

    def test_action_pass_time(self):
        action = ActionPassTime()
        
        self.tracker.slots["game_time"] = "morning"
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("game_time", "afternoon"), events)

    def test_action_check_game_over(self):
        action = ActionCheckGameOver()
        
        self.tracker.slots["hp"] = 0
        
        events = action.run(self.dispatcher, self.tracker, self.domain)
        
        self.assertIn(SlotSet("game_state", "game_over"), events)

if __name__ == '__main__':
    unittest.main()