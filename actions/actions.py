# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import requests


class ActionChitchat(Action):
    """Returns the chitchat utterance dependent on the intent"""

    def name(self):
        return "action_chitchat"

    def run(self, dispatcher, tracker, domain):
        intent = tracker.latest_message["intent"].get("name")

        # retrieve the correct chitchat utterance dependent on the intent
        if intent in [
            "ask_builder",
            "ask_weather",
            "ask_howdoing",
            "ask_whatspossible",
            "ask_whatisrasa",
            "ask_isbot",
            "ask_howold",
            "ask_languagesbot",
            "ask_restaurant",
            "ask_time",
            "ask_wherefrom",
            "ask_whoami",
            "handleinsult",
            "nicetomeeyou",
            "telljoke",
            "ask_whatismyname",
            "ask_howbuilt",
            "ask_whoisit",
        ]:
            dispatcher.utter_template("utter_" + intent, tracker)
        return []


class ActionExplainConcept(Action):
    """Returns the chitchat utterance dependent on the intent"""

    def name(self):
        return "action_explain_chatbot"

    def run(self, dispatcher, tracker, domain):
        intent = tracker.latest_message["intent"].get("name")

        # retrieve the correct chitchat utterance dependent on the intent
        if intent in [
            "why_make_a_bot",
            "why_did_you_make_a_bot",
            "why_machine_learning",
            "dialogue_tools",
            "explain_dialogue_machines",
            "types_of_chatbots",
            "explain_generative_chatbot",
            "explain_retrieval_chatbot",
            "explain_deep_learning",
            "explain_entities",
            "explain_intents",
            "explain_nlp",
            "explain_nlu",
            "explain_nltk",
            "explain_spacy",
            "explain_tensorflow",
            "explain_pytorch",
            "explain_keras",
            "explain_turing_test",
            "when_will_you_beat_turing_test",

        ]:
            dispatcher.utter_template("utter_" + intent, tracker)
        return []


class ActionStoreUnknownConcept(Action):
    """Stores unknown concepts people are asking about in a slot"""

    def name(self):
        return "action_store_unknown_concept"

    def run(self, dispatcher, tracker, domain):
        # if we dont know the concept the user is talking about,
        # store his last message in a slot.
        return [SlotSet("unknown_product", tracker.latest_message.get("text"))]


class ActionVisitWebsite(Action):
    """Stores unknown concepts people are asking about in a slot"""

    def name(self):
        return "action_visit_website"

    def run(self, dispatcher, tracker, domain):
        # if we dont know the concept the user is talking about,
        # store his last message in a slot.
        dispatcher.utter_message(text="https://shenoy-anurag.github.io/")
        return []


class ActionToolFrontend(Action):
    """Stores unknown concepts people are asking about in a slot"""

    def name(self):
        return "action_which_tool_for_bot_frontend"

    def run(self, dispatcher, tracker, domain):
        # if we dont know the concept the user is talking about,
        # store his last message in a slot.
        url = "https://my-json-server.typicode.com/shenoy-anurag/temp-json/projects/1"
        resp = requests.get(url=url)
        if resp.status_code == 200:
            tool = resp.json()['answer']
        else:
            tool = "I used the tool named {} as a frontend to the chatbot.".format("chat-bubble")
        dispatcher.utter_message(text=tool)
        return []
