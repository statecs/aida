## story_greet <!--- The name of the story. It is not mandatory, but useful for debugging. -->
* greet <!--- User input expressed as intent. In this case it represents users message 'Hello'. -->
  - utter_greet <!--- The response of the chatbot expressed as an action. In this case it represents chatbot's response 'Hello, how can I help?' -->

## Huvudvärk
* greet
  - utter_greet
* huvudvärk
  - utter_headache

## Huvudvärk
* huvudvärk
  - utter_headache

## greet
* greet
  - utter_greet
* goodbye
  - utter_goodbye
  - action_restart

## handle_insult
* handleinsult
  - utter_handleinsult

## story_thanks
* thankyou
  - utter_thanks

## howdoing
* ask_howdoing
  - utter_ask_howdoing

## telljoke
* telljoke
  - utter_telljoke

## chitchat
* chitchat
  - utter_chitchat

## story_goodbye
* goodbye
  - utter_goodbye
  - action_restart

## goback
* goback
  - action_back

## clear
* clear
  - utter_clear
  - action_restart

## New Story

* goback
    - action_back

## New Story

* goback
    - action_back

## New Story
* utter_headache
    - utter_headache
