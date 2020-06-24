## happy path fever_form
* ask_about_fever
    - fever_form
    - form{"name": "fever_form"}
    - utter_submit_fever
    - action_reset
    
## happy path fever+cough
* ask_about_fever+ask_about_cough 
    - fever_form
    - form{"name": "fever_form"}
    - cough_form
    - form{"name": "cough_form"}
    - form{"name": null}
    - utter_submit_fever_cough
    - action_reset

## happy path fever+soreThroat
* ask_about_fever+ask_about_soreThroat
    - fever_form
    - form{"name": "fever_form"}
    - soreThroat_form
    - form{"name": "soreThroat_form"}
    - form{"name": null}
    - utter_submit_fever_soreThroat
    - action_reset