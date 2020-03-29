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

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, AllSlotsReset, EventType
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.executor import CollectingDispatcher

from datetime import datetime, date, time, timedelta

logger = logging.getLogger(__name__)
vers = 'Vers: 0.7.0, Date: Mar 11, 2020'


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

        return ["headache_utter", "headache_when", "headache_pain", "headache_changed", "headache_where", "headache_other_symptoms",  "headache_meds", "headache_length_weight", "headache_other", "headache_expectation"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "headache_utter": [self.from_entity(entity="headache_utter"), self.from_text()],
            "headache_when": [self.from_entity(entity="headache_when"), self.from_text()],
            "headache_pain": [self.from_entity(entity="headache_pain"), self.from_text()],
            "headache_changed": [self.from_entity(entity="headache_changed"), self.from_text()],
            "headache_where": [self.from_entity(entity="headache_where"), self.from_text()],
            "headache_other_symptoms": [self.from_entity(entity="headache_other_symptoms"), self.from_text()],
            "headache_meds": [self.from_entity(entity="headache_meds"), self.from_text()],
            "headache_length_weight": [self.from_entity(entity="headache_length_weight"), self.from_text()],
            "headache_other": [self.from_entity(entity="headache_other"), self.from_text()],
            "headache_expectation": [self.from_entity(entity="headache_expectation"), self.from_text()],
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        dispatcher.utter_message(template="utter_submit_headache")
        return [AllSlotsReset()]
