## happy path fever_form
* ask_about_fever
    - fever_form
    - form{"name": "fever_form"}
    - form{"name": null}
    
## happy path fever+cough
* ask_about_fever+ask_about_cough 
    - action_symptoms
    - utter_ask_is_symptom
* deny
    - utter_ask_rephrase
    - action_listen
* affirm
    - cough_form
    - fever_form
    - form{"name": "fever_form"}
    - form{"name": "cough_form"}
    - form{"name": null}
