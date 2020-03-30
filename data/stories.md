## story_greet <!--- The name of the story. It is not mandatory, but useful for debugging. -->
* greet <!--- User input expressed as intent. In this case it represents users message 'Hello'. -->
  - utter_greet <!--- The response of the chatbot expressed as an action. In this case it represents chatbot's response 'Hello, how can I help?' -->

## happy path headache_form
* ask_about_headache
    - headache_form
    - form{"name": "headache_form"}
    - form{"name": null}

## happy path soreThroat_form
* ask_about_soreThroat
    - soreThroat_form
    - form{"name": "soreThroat_form"}
    - form{"name": null}

## happy path coughFever_form
* ask_about_coughFever
    - coughFever_form
    - form{"name": "coughFever_form"}
    - form{"name": null}

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

## Corona
* ask_about_corona_symptom
  - utter_corona_symptom

## Corona Virus
* ask_about_corona_virus
  - utter_corona_virus

## Corona Death
* ask_about_corona_death
  - utter_corona_death

## clear
* clear
  - utter_greet
  - action_restart