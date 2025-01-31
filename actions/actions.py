# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from typing import Dict, Text, Any, List, Union, Type, Optional

import typing
import logging
import requests
import json
import csv

from rasa_sdk import Action, Tracker, ActionExecutionRejection
from rasa_sdk.events import SlotSet, AllSlotsReset, EventType, FollowupAction, UserUtteranceReverted, Restarted, Form
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.executor import CollectingDispatcher

from datetime import datetime, date, time, timedelta

logger = logging.getLogger(__name__)
vers = 'Vers: 0.7.0, Date: Mar 11, 2020'

#INTENT_DESCRIPTION_MAPPING_PATH = "actions/intent_description_mapping.csv"


class ActionDefaultAskAffirmation(Action):
    """Asks for an affirmation of the intent if NLU threshold is not met."""

    def name(self) -> Text:
        return "action_default_ask_affirmation"

    # def __init__(self) -> None:
       # import pandas as pd

        # self.intent_mappings = pd.read_csv(INTENT_DESCRIPTION_MAPPING_PATH)
        # self.intent_mappings = "intent,button,entities affirm,Ja"
        # self.intent_mappings.fillna("", inplace=True)
        # self.intent_mappings.entities = self.intent_mappings.entities.map(
        #    lambda entities: {e.strip() for e in entities.split(",")}
        # )

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        intent_ranking = tracker.latest_message.get("intent_ranking", [])
        if len(intent_ranking) > 1:
            diff_intent_confidence = intent_ranking[0].get(
                "confidence"
            ) - intent_ranking[1].get("confidence")
            if diff_intent_confidence < 0.2:
                intent_ranking = intent_ranking[:2]
            else:
                intent_ranking = intent_ranking[:1]
        first_intent_names = [
            intent.get("name", "")
            for intent in intent_ranking
            if intent.get("name", "") != "out_of_scope"
        ]

        message_title = (
            "Ledsen, men jag är osäker om jag förstod din fråga. Du kan fråga mig om huvudvärk, halsont och hosta och feber "
        )

        entities = tracker.latest_message.get("entities", [])
        entities = {e["entity"]: e["value"] for e in entities}

        entities_json = json.dumps(entities)

        buttons = []
        for intent in first_intent_names:
            logger.debug(intent)
            logger.debug(entities)
            # buttons.append(
            #    {
            #        "title": self.get_button_title(intent, entities),
            #        "payload": "/{}{}".format(intent, entities_json),
            #    }
            # )

        # /out_of_scope is a retrieval intent
        # you cannot send rasa the '/out_of_scope' intent
        # instead, you can send one of the sentences that it will map onto the response
        buttons.append(
            {
                "title": "Starta om",
                "payload": "Hej",
            }
        )

        dispatcher.utter_message(text=message_title, buttons=buttons)

        return []

    # def get_button_title(self, intent: Text, entities: Dict[Text, Text]) -> Text:
    #    default_utterance_query = self.intent_mappings.intent == intent
    #    utterance_query = (self.intent_mappings.entities == entities.keys()) & (
    #        default_utterance_query
    #    )

    #    utterances = self.intent_mappings[utterance_query].button.tolist()

    #    if len(utterances) > 0:
    #        button_title = utterances[0]
    #    else:
    #        utterances = self.intent_mappings[default_utterance_query].button.tolist(
    #        )
    #        button_title = utterances[0] if len(utterances) > 0 else intent
    #
    #    return button_title.format(**entities)


class ActionReset(Action):
    def name(self):
        return "action_reset"

    def run(self, dispatcher, tracker, domain):
        return [AllSlotsReset()]


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[EventType]:

        # Fallback caused by TwoStageFallbackPolicy
        if (
            len(tracker.events) >= 4
            and tracker.events[-4].get("name") == "action_default_ask_affirmation"
        ):

            dispatcher.utter_message(template="utter_restart_with_button")

            return [SlotSet("feedback_value", "negative")]

        # Fallback caused by Core
        else:
            dispatcher.utter_message(template="utter_default")
            return [UserUtteranceReverted()]


class ActionRewind(Action):
    def name(self):
        logger.info("actionrewind self called")
        # define the name of the action which can then be included in training stories
        return "action_rewind"

    def run(self, dispatcher, tracker, domain):
        # only utter the template if it is available
        dispatcher.utter_template("utter_back", tracker,
                                  silent_fail=True)
        return [UserUtteranceReverted(), UserUtteranceReverted()]


class ActionVersion(Action):
    def name(self):
        logger.info("ActionVersion self called")
        # define the name of the action which can then be included in training stories
        return "action_version"

    def run(self, dispatcher, tracker, domain):
        request = json.loads(requests.get(
            'http://185.157.221.183:5002/api/version').text)
        logger.info(">> rasa x version response: {}".format(request['rasa-x']))
        logger.info(">> rasa version response: {}".format(
            request['rasa']['production']))
        dispatcher.utter_message(
            f"Rasa X: {request['rasa-x']}\nRasa:  {request['rasa']['production']}")
        return []


class HeadacheForm(FormAction):
    """headache form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "headache_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["state_of_health", "headache_utter", "headache_when", "headache_pain", "symptoms_changed", "headache_where", "other_symptoms", "medication", "length_weight", "other", "expectation"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "state_of_health": [self.from_text()],
            "headache_utter": [self.from_text()],
            "headache_when": [self.from_text()],
            "headache_pain": [self.from_text()],
            "symptoms_changed": [self.from_text()],
            "headache_where": [self.from_text()],
            "other_symptoms": [self.from_text()],
            "medication": [self.from_text()],
            "length_weight": [self.from_text()],
            "other": [self.from_text()],
            "expectation": [self.from_text()],
        }

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        # track intent of the input
        msg = tracker.latest_message.get('text')
        # classify deacitvate intent
        if msg == "/restart":
            dispatcher.utter_template(
                "utter_restart", tracker, silent_fail=True)
            return [Form(None), AllSlotsReset(None), Restarted(None)]
        if msg == "/back":
            dispatcher.utter_template(
                "utter_back", tracker, silent_fail=True)
            return [UserUtteranceReverted(), UserUtteranceReverted()]
        if msg == "/Nej":
            dispatcher.utter_template(
                "utter_ask_rephrase", tracker, silent_fail=True)

            return [Form(None), AllSlotsReset(None), Restarted(None), FollowupAction("action_reset")]
        else:
            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if tracker.latest_message['intent'].get('name') == "ask_about_headache":

                        numb_user_list = []

                        slot = tracker.get_slot("headache_utter")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_utter")[:])
                        slot = tracker.get_slot("headache_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_pain")[:])
                        slot = tracker.get_slot("headache_when")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_when")[:])
                        slot = tracker.get_slot("headache_where")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_where")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, " + numb_user_string)
                            return [SlotSet("search_reasons", "huvudvärk, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk")
                            return [SlotSet("search_reasons", "huvudvärk"), SlotSet(REQUESTED_SLOT, slot)]

                    if tracker.latest_message['intent'].get('name') == "ask_about_headache+ask_about_cough":

                        numb_user_list = []

                        slot = tracker.get_slot("headache_utter")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_utter")[:])
                        slot = tracker.get_slot("headache_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_pain")[:])
                        slot = tracker.get_slot("headache_when")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_when")[:])
                        slot = tracker.get_slot("headache_where")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_where")[:])

                        slot = tracker.get_slot("cough_chronic")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_chronic")[:])
                        slot = tracker.get_slot("cough_cold")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_cold")[:])
                        slot = tracker.get_slot("cough_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_length")[:])
                        slot = tracker.get_slot("cough_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_pain")[:])
                        slot = tracker.get_slot("cough_shape")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_shape")[:])
                        slot = tracker.get_slot("cough_smoke")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_smoke")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, hosta, " + numb_user_string)
                            return [SlotSet("search_reasons", "huvudvärk, hosta,  " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk och hosta")
                            return [SlotSet("search_reasons", "huvudvärk och hosta"), SlotSet(REQUESTED_SLOT, slot)]

                    if tracker.latest_message['intent'].get('name') == "ask_about_headache+ask_about_fever":

                        numb_user_list = []

                        slot = tracker.get_slot("headache_utter")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_utter")[:])
                        slot = tracker.get_slot("headache_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_pain")[:])
                        slot = tracker.get_slot("headache_when")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_when")[:])
                        slot = tracker.get_slot("headache_where")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_where")[:])

                        slot = tracker.get_slot("fever_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_length")[:])
                        slot = tracker.get_slot("fever_temperature")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_temperature")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, feber, " + numb_user_string)
                            return [SlotSet("search_reasons", "huvudvärk, feber, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, och feber")
                            return [SlotSet("search_reasons", "huvudvärk och feber"), SlotSet(REQUESTED_SLOT, slot)]

                    if tracker.latest_message['intent'].get('name') == "ask_about_headache+ask_about_soreThroat":

                        numb_user_list = []

                        slot = tracker.get_slot("headache_utter")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_utter")[:])
                        slot = tracker.get_slot("headache_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_pain")[:])
                        slot = tracker.get_slot("headache_when")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_when")[:])
                        slot = tracker.get_slot("headache_where")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_where")[:])

                        slot = tracker.get_slot("soreThroat_duration")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_duration")[:])
                        slot = tracker.get_slot("soreThroat_location")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_location")[:])
                        slot = tracker.get_slot("soreThroat_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_pain")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, halsont, " + numb_user_string)
                            return [SlotSet("search_reasons", "huvudvärk, halsont, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk och halsont")
                            return [SlotSet("search_reasons", "huvudvärk och halsont"), SlotSet(REQUESTED_SLOT, slot)]

                    if tracker.latest_message['intent'].get('name') == "ask_about_headache+ask_about_soreThroat+ask_about_fever":

                        numb_user_list = []

                        slot = tracker.get_slot("headache_utter")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_utter")[:])
                        slot = tracker.get_slot("headache_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_pain")[:])
                        slot = tracker.get_slot("headache_when")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_when")[:])
                        slot = tracker.get_slot("headache_where")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_where")[:])

                        slot = tracker.get_slot("soreThroat_duration")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_duration")[:])
                        slot = tracker.get_slot("soreThroat_location")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_location")[:])
                        slot = tracker.get_slot("soreThroat_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_pain")[:])

                        slot = tracker.get_slot("fever_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_length")[:])
                        slot = tracker.get_slot("fever_temperature")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_temperature")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, halsont, feber, " + numb_user_string)
                            return [SlotSet("search_reasons", "huvudvärk, halsont, feber, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, halsont och feber")
                            return [SlotSet("search_reasons", "huvudvärk, halsont och feber"), SlotSet(REQUESTED_SLOT, slot)]

                    if tracker.latest_message['intent'].get('name') == "ask_about_headache+ask_about_soreThroat+ask_about_cough":

                        numb_user_list = []

                        slot = tracker.get_slot("headache_utter")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_utter")[:])
                        slot = tracker.get_slot("headache_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_pain")[:])
                        slot = tracker.get_slot("headache_when")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_when")[:])
                        slot = tracker.get_slot("headache_where")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_where")[:])

                        slot = tracker.get_slot("soreThroat_duration")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_duration")[:])
                        slot = tracker.get_slot("soreThroat_location")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_location")[:])
                        slot = tracker.get_slot("soreThroat_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_pain")[:])

                        slot = tracker.get_slot("cough_chronic")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_chronic")[:])
                        slot = tracker.get_slot("cough_cold")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_cold")[:])
                        slot = tracker.get_slot("cough_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_length")[:])
                        slot = tracker.get_slot("cough_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_pain")[:])
                        slot = tracker.get_slot("cough_shape")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_shape")[:])
                        slot = tracker.get_slot("cough_smoke")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_smoke")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, halsont, hosta, " + numb_user_string)
                            return [SlotSet("search_reasons", "huvudvärk, halsont, hosta, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, halsont och hosta")
                            return [SlotSet("search_reasons", "huvudvärk, halsont och hosta"), SlotSet(REQUESTED_SLOT, slot)]

                    if tracker.latest_message['intent'].get('name') == "ask_about_headache+ask_about_soreThroat+ask_about_cough+ask_about_fever":

                        numb_user_list = []

                        slot = tracker.get_slot("headache_utter")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_utter")[:])
                        slot = tracker.get_slot("headache_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_pain")[:])
                        slot = tracker.get_slot("headache_when")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_when")[:])
                        slot = tracker.get_slot("headache_where")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("headache_where")[:])

                        slot = tracker.get_slot("soreThroat_duration")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_duration")[:])
                        slot = tracker.get_slot("soreThroat_location")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_location")[:])
                        slot = tracker.get_slot("soreThroat_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_pain")[:])

                        slot = tracker.get_slot("cough_chronic")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_chronic")[:])
                        slot = tracker.get_slot("cough_cold")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_cold")[:])
                        slot = tracker.get_slot("cough_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_length")[:])
                        slot = tracker.get_slot("cough_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_pain")[:])
                        slot = tracker.get_slot("cough_shape")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_shape")[:])
                        slot = tracker.get_slot("cough_smoke")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_smoke")[:])

                        slot = tracker.get_slot("fever_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_length")[:])
                        slot = tracker.get_slot("fever_temperature")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_temperature")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, halsont, hosta, feber, " + numb_user_string)

                            return [SlotSet("search_reasons", "huvudvärk, halsont, hosta, feber, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="huvudvärk, halsont, hosta och feber")
                            return [SlotSet("search_reasons", "huvudvärk, halsont, hosta och feber"), SlotSet(REQUESTED_SLOT, slot)]

                if self._should_request_slot(tracker, slot):
                    logger.debug("Request next slot '{}'".format(slot))
                    dispatcher.utter_template("utter_ask_{}".format(slot),
                                              tracker,
                                              silent_fail=False,
                                              **tracker.slots)
                    return [SlotSet(REQUESTED_SLOT, slot)]

    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot else reject the execution of the form action"""
        # extract other slots that were not requested
        # but set by corresponding entity

        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(
                dispatcher, tracker, domain))

         # we'll check when validation failed in order
         # to add appropriate utterances
        for slot, value in slot_values.items():

            msg = tracker.latest_message.get('text')

            if msg == "/restart":
                dispatcher.utter_template(
                    "utter_restart", tracker, silent_fail=True)
                return [Form(None), AllSlotsReset(None), Restarted(None)]

            if slot == "state_of_health":
                if value <= '10':
                    dispatcher.utter_message(template="utter_urgent")
                    return [Form(None), AllSlotsReset(None), Restarted(None)]

        # validation succeed, set the slots values to the extracted values
        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        return []


class soreThroatForm(FormAction):
    """soreThroatForm form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "soreThroat_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["state_of_health", "soreThroat_duration", "soreThroat_pain", "soreThroat_location", "other_symptoms", "other", "expectation"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "state_of_health": [self.from_text()],
            "soreThroat_duration": [self.from_text()],
            "soreThroat_pain": [self.from_text()],
            "soreThroat_location": [self.from_text()],
            "other_symptoms": [self.from_text()],
            "other": [self.from_text()],
            "expectation": [self.from_text()],
        }

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        # track intent of the input
        msg = tracker.latest_message.get('text')
        # classify deacitvate intent
        if msg == "/back":
            dispatcher.utter_template(
                "utter_back", tracker, silent_fail=True)
            return [UserUtteranceReverted(), UserUtteranceReverted()]
        if msg == "/restart":
            dispatcher.utter_template(
                "utter_restart", tracker, silent_fail=True)
            return [Form(None), AllSlotsReset(None), Restarted(None)]
        if msg == "/Nej":
            dispatcher.utter_template(
                "utter_ask_rephrase", tracker, silent_fail=True)

            return [Form(None), AllSlotsReset(None), Restarted(None), FollowupAction("action_reset")]
        else:
            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if tracker.latest_message['intent'].get('name') == "ask_about_soreThroat":

                        numb_user_list = []

                        slot = tracker.get_slot("soreThroat_duration")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_duration")[:])
                        slot = tracker.get_slot("soreThroat_location")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_location")[:])
                        slot = tracker.get_slot("soreThroat_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_pain")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="halsont, " + numb_user_string)
                            return [SlotSet("search_reasons", "halsont, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="halsont")
                            return [SlotSet("search_reasons", "halsont"), SlotSet(REQUESTED_SLOT, slot)]

                    if tracker.latest_message['intent'].get('name') == "ask_about_soreThroat+ask_about_cough+ask_about_fever":

                        numb_user_list = []

                        slot = tracker.get_slot("soreThroat_duration")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_duration")[:])
                        slot = tracker.get_slot("soreThroat_location")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_location")[:])
                        slot = tracker.get_slot("soreThroat_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_pain")[:])

                        slot = tracker.get_slot("cough_chronic")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_chronic")[:])
                        slot = tracker.get_slot("cough_cold")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_cold")[:])
                        slot = tracker.get_slot("cough_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_length")[:])
                        slot = tracker.get_slot("cough_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_pain")[:])
                        slot = tracker.get_slot("cough_shape")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_shape")[:])
                        slot = tracker.get_slot("cough_smoke")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_smoke")[:])

                        slot = tracker.get_slot("fever_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_length")[:])
                        slot = tracker.get_slot("fever_temperature")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_temperature")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="halsont, hosta, feber, " + numb_user_string)
                            return [SlotSet("search_reasons", "halsont, hosta, feber, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="halsont, hosta och feber")
                            return [SlotSet("search_reasons", "halsont, hosta och feber"), SlotSet(REQUESTED_SLOT, slot)]

                if self._should_request_slot(tracker, slot):
                    logger.debug("Request next slot '{}'".format(slot))
                    dispatcher.utter_template("utter_ask_{}".format(slot),
                                              tracker,
                                              silent_fail=False,
                                              **tracker.slots)
                    return [SlotSet(REQUESTED_SLOT, slot)]

    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot else reject the execution of the form action"""
        # extract other slots that were not requested
        # but set by corresponding entity

        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(
                dispatcher, tracker, domain))

         # we'll check when validation failed in order
         # to add appropriate utterances
        for slot, value in slot_values.items():

            msg = tracker.latest_message.get('text')
            if msg == "/back":
                dispatcher.utter_template(
                    "utter_back", tracker, silent_fail=True)
                # return [FollowupAction('action_listen')]
                return [FollowupAction("action_rewind")]

            if msg == "/restart":
                dispatcher.utter_template(
                    "utter_restart", tracker, silent_fail=True)
                # return [FollowupAction('action_listen')]
                return [Form(None), AllSlotsReset(None), Restarted(None)]

            if slot == "state_of_health":
                if value <= '10':
                    dispatcher.utter_message(template="utter_urgent")
                    return [Form(None), AllSlotsReset(None), Restarted(None)]

        # validation succeed, set the slots values to the extracted values
        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        return []


class coughForm(FormAction):
    """coughForm form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "cough_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["state_of_health", "cough_length", "cough_pain", "cough_shape", "other_symptoms", "cough_chronic", "cough_cold", "medication", "cough_smoke", "length_weight", "other", "expectation"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "state_of_health": [self.from_text()],
            "cough_length": [self.from_text()],
            "cough_pain": [self.from_text()],
            "cough_shape": [self.from_text()],
            "other_symptoms": [self.from_text()],
            "cough_chronic": [self.from_text()],
            "cough_cold": [self.from_text()],
            "medication": [self.from_text()],
            "cough_smoke": [self.from_text()],
            "length_weight": [self.from_text()],
            "other": [self.from_text()],
            "expectation": [self.from_text()],
        }

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        # track intent of the input
        msg = tracker.latest_message.get('text')
        # classify deacitvate intent
        if msg == "/restart":
            dispatcher.utter_template(
                "utter_restart", tracker, silent_fail=True)
            return [Form(None), AllSlotsReset(None), Restarted(None)]
        if msg == "/back":
            dispatcher.utter_template(
                "utter_back", tracker, silent_fail=True)
            return [UserUtteranceReverted(), UserUtteranceReverted()]
        if msg == "/Nej":
            dispatcher.utter_template(
                "utter_ask_rephrase", tracker, silent_fail=True)

            return [Form(None), AllSlotsReset(None), Restarted(None), FollowupAction("action_reset")]
        else:
            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if tracker.latest_message['intent'].get('name') == "ask_about_cough":
                        numb_user_list = []

                        slot = tracker.get_slot("cough_chronic")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_chronic")[:])
                        slot = tracker.get_slot("cough_cold")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_cold")[:])
                        slot = tracker.get_slot("cough_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_length")[:])
                        slot = tracker.get_slot("cough_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_pain")[:])
                        slot = tracker.get_slot("cough_shape")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_shape")[:])
                        slot = tracker.get_slot("cough_smoke")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_smoke")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="hosta, " + numb_user_string)
                            return [SlotSet("search_reasons", "hosta, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="hosta")
                            return [SlotSet("search_reasons", "hosta"), SlotSet(REQUESTED_SLOT, slot)]

                    if tracker.latest_message['intent'].get('name') == "ask_about_cough+ask_about_soreThroat":

                        numb_user_list = []

                        slot = tracker.get_slot("cough_chronic")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_chronic")[:])
                        slot = tracker.get_slot("cough_cold")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_cold")[:])
                        slot = tracker.get_slot("cough_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_length")[:])
                        slot = tracker.get_slot("cough_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_pain")[:])
                        slot = tracker.get_slot("cough_shape")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_shape")[:])
                        slot = tracker.get_slot("cough_smoke")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_smoke")[:])

                        slot = tracker.get_slot("soreThroat_duration")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_duration")[:])
                        slot = tracker.get_slot("soreThroat_location")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_location")[:])
                        slot = tracker.get_slot("soreThroat_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_pain")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="hosta, halsont, " + numb_user_string)
                            return [SlotSet("search_reasons", "hosta, halsont, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="hosta och halsont")
                            return [SlotSet("search_reasons", "hosta och halsont"), SlotSet(REQUESTED_SLOT, slot)]

                if self._should_request_slot(tracker, slot):
                    logger.debug("Request next slot '{}'".format(slot))
                    dispatcher.utter_template("utter_ask_{}".format(slot),
                                              tracker,
                                              silent_fail=False,
                                              **tracker.slots)
                    return [SlotSet(REQUESTED_SLOT, slot)]

    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot else reject the execution of the form action"""
        # extract other slots that were not requested
        # but set by corresponding entity

        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(
                dispatcher, tracker, domain))

         # we'll check when validation failed in order
         # to add appropriate utterances
        for slot, value in slot_values.items():

            msg = tracker.latest_message.get('text')
            if msg == "/back":
                dispatcher.utter_template(
                    "utter_back", tracker, silent_fail=True)
                # return [FollowupAction('action_listen')]
                return [FollowupAction("action_rewind")]

            if msg == "/restart":
                dispatcher.utter_template(
                    "utter_restart", tracker, silent_fail=True)
                # return [FollowupAction('action_listen')]
                return [Form(None), AllSlotsReset(None), Restarted(None)]

            if slot == "state_of_health":
                if value <= '10':
                    dispatcher.utter_message(template="utter_urgent")
                    return [Form(None), AllSlotsReset(None), Restarted(None)]

        # validation succeed, set the slots values to the extracted values
        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        return []


class feverForm(FormAction):
    """feverForm form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "fever_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["state_of_health", "other_symptoms", "fever_length", "fever_temperature", "symptoms_changed", "other", "expectation"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "state_of_health": [self.from_text()],
            "other_symptoms": [self.from_text()],
            "fever_length": [self.from_text()],
            "fever_temperature": [self.from_text()],
            "symptoms_changed": [self.from_text()],
            "other": [self.from_text()],
            "expectation": [self.from_text()],
        }

    def request_next_slot(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict[Text, Any],
    ) -> Optional[List[EventType]]:

        # track intent of the input
        msg = tracker.latest_message.get('text')
        # classify deacitvate intent
        if msg == "/restart":
            dispatcher.utter_template(
                "utter_restart", tracker, silent_fail=True)
            return [Form(None), AllSlotsReset(None), Restarted(None)]
        if msg == "/back":
            dispatcher.utter_template(
                "utter_back", tracker, silent_fail=True)
            return [UserUtteranceReverted(), UserUtteranceReverted()]
        if msg == "/Nej":
            dispatcher.utter_template(
                "utter_ask_rephrase", tracker, silent_fail=True)

            return [Form(None), AllSlotsReset(None), Restarted(None), FollowupAction("action_reset")]
        else:
            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    if tracker.latest_message['intent'].get('name') == "ask_about_fever":
                        numb_user_list = []

                        slot = tracker.get_slot("fever_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_length")[:])
                        slot = tracker.get_slot("fever_temperature")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_temperature")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="feber, " + numb_user_string)
                            return [SlotSet("search_reasons", "feber, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="feber")
                            return [SlotSet("search_reasons", "feber"), SlotSet(REQUESTED_SLOT, slot)]

                    if tracker.latest_message['intent'].get('name') == "ask_about_fever+ask_about_cough":

                        numb_user_list = []

                        slot = tracker.get_slot("fever_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_length")[:])
                        slot = tracker.get_slot("fever_temperature")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_temperature")[:])

                        slot = tracker.get_slot("cough_chronic")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_chronic")[:])
                        slot = tracker.get_slot("cough_cold")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_cold")[:])
                        slot = tracker.get_slot("cough_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_length")[:])
                        slot = tracker.get_slot("cough_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_pain")[:])
                        slot = tracker.get_slot("cough_shape")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_shape")[:])
                        slot = tracker.get_slot("cough_smoke")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("cough_smoke")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="feber, hosta, " + numb_user_string)
                            return [SlotSet("search_reasons", "feber, hosta, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="feber och hosta")
                            return [SlotSet("search_reasons", "feber och hosta"), SlotSet(REQUESTED_SLOT, slot)]

                    if tracker.latest_message['intent'].get('name') == "ask_about_fever+ask_about_soreThroat":
                        numb_user_list = []

                        slot = tracker.get_slot("fever_length")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_length")[:])
                        slot = tracker.get_slot("fever_temperature")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("fever_temperature")[:])

                        slot = tracker.get_slot("soreThroat_duration")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_duration")[:])
                        slot = tracker.get_slot("soreThroat_location")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_location")[:])
                        slot = tracker.get_slot("soreThroat_pain")
                        if slot:
                            numb_user_list.append(
                                tracker.get_slot("soreThroat_pain")[:])

                        if numb_user_list:
                            numb_user_string = ', '.join(numb_user_list)
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="feber, halsont, " + numb_user_string)
                            return [SlotSet("search_reasons", "feber, halsont, " + numb_user_string),  SlotSet(REQUESTED_SLOT, slot)]
                        else:
                            dispatcher.utter_template(
                                "utter_ask_about_cause", tracker, search_reasons="feber och halsont")
                            return [SlotSet("search_reasons", "feber och halsont"), SlotSet(REQUESTED_SLOT, slot)]

                if self._should_request_slot(tracker, slot):
                    logger.debug("Request next slot '{}'".format(slot))
                    dispatcher.utter_template("utter_ask_{}".format(slot),
                                              tracker,
                                              silent_fail=False,
                                              **tracker.slots)
                    return [SlotSet(REQUESTED_SLOT, slot)]

    def validate(self,
                 dispatcher: CollectingDispatcher,
                 tracker: Tracker,
                 domain: Dict[Text, Any]) -> List[Dict]:
        """Validate extracted requested slot else reject the execution of the form action"""
        # extract other slots that were not requested
        # but set by corresponding entity

        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        # extract requested slot
        slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
        if slot_to_fill:
            slot_values.update(self.extract_requested_slot(
                dispatcher, tracker, domain))

         # we'll check when validation failed in order
         # to add appropriate utterances
        for slot, value in slot_values.items():

            msg = tracker.latest_message.get('text')
            if msg == "/back":
                dispatcher.utter_template(
                    "utter_back", tracker, silent_fail=True)
                # return [FollowupAction('action_listen')]
                return [FollowupAction("action_rewind")]

            if msg == "/restart":
                dispatcher.utter_template(
                    "utter_restart", tracker, silent_fail=True)
                # return [FollowupAction('action_listen')]
                return [Form(None), AllSlotsReset(None), Restarted(None)]

            if slot == "state_of_health":
                if value <= '10':
                    dispatcher.utter_message(template="utter_urgent")

            if slot == "fever_temperature":
                if value == 'Över 41,0 grader':
                    dispatcher.utter_message(template="utter_urgent")
                    return [Form(None), AllSlotsReset(None), Restarted(None)]
                    # validation succeed, set the slots values to the extracted values
        return [SlotSet(slot, value) for slot, value in slot_values.items()]

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        return []
