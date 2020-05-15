## happy path headache_form
* ask_about_headache
    - headache_form
    - form{"name": "headache_form"}
    - form{"name": null}

## happy path headache+coughFever_form
* ask_about_headache+ask_about_coughFever 
    - action_symptoms
    - utter_ask_is_symptom
* deny
    - utter_ask_rephrase
    - action_listen
* affirm
    - headache_form
    - form{"name": "headache_form"}
    - form{"name": null}
