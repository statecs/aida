## happy path headache_form
* ask_about_headache
    - headache_form
    - form{"name": "headache_form"}
    - form{"name": null}

## happy path headache+cough_form
* ask_about_headache+ask_about_cough
    - action_symptoms
    - utter_ask_is_symptom
* deny
    - utter_ask_rephrase
    - action_listen
* affirm
    - headache_form
    - cough_form
    - form{"name": "headache_form"}
    - form{"name": "cough_form"}
    - form{"name": null} 

# happy path headache+fever_form
* ask_about_headache+ask_about_fever
    - action_symptoms
    - utter_ask_is_symptom
* deny
    - utter_ask_rephrase
    - action_listen
* affirm
    - headache_form
    - fever_form
    - form{"name": "fever_form"}
    - form{"name": "headache_form"}
    - form{"name": null} 
