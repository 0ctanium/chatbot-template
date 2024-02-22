import requests
import os
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List, Union
from rasa_sdk.events import SlotSet, UserUttered

api_url = os.environ.get('API_URL', 'http://localhost:3000')

def return_fallback_suggestions(self,
                         dispatcher: CollectingDispatcher,
                         tracker: Tracker,
                         domain: Dict[Text, Any]):

    if not tracker.get_slot('return_suggestions'):
        return []

    banned_intents = ['nlu_fallback', 'phrase_presentation', 'phrase_feedback']
    intents_not_bad = [intent for intent in tracker.latest_message['intent_ranking'] if intent['confidence'] >= 0.2 and intent['name'] not in banned_intents]
    if len(intents_not_bad) <= 0:
        return []

    buttons_to_send = []
    intents_ids = []
    for i in intents_not_bad:
        intents_ids.append(i['name'])

    response = requests.post(api_url + '/api/public/intents', json = intents_ids)
    for i in response.json():
        buttons_to_send.append({"payload": "/" + i['id'], "title": i['mainQuestion']})

    if len(buttons_to_send) <= 0:
        return []

    dispatcher.utter_message(text = "J'ai trouvé des propositions qui pourraient correspondre à votre recherche", buttons = buttons_to_send)
