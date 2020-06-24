## happy path cough_form
* ask_about_cough
    - cough_form
    - form{"name": "cough_form"}
    - utter_submit_cough
    - action_reset

# happy path cough+soreThroat
* ask_about_cough+ask_about_soreThroat
    - cough_form
    - form{"name": "cough_form"}
    - soreThroat_form
    - form{"name": "soreThroat_form"}
    - form{"name": null}
    - utter_submit_cough_soreThroat
    - action_reset