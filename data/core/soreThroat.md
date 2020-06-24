## happy path soreThroat_form
* ask_about_soreThroat
    - soreThroat_form
    - form{"name": "soreThroat_form"}
    - utter_submit_soreThroat
    - action_reset


# happy path soreThroat_form+cough_form+fever_form
*ask_about_soreThroat+ask_about_cough+ask_about_fever
    - soreThroat_form
    - form{"name": "soreThroat_form"}
    - cough_form
    - form{"name": "cough_form"}
    - fever_form
    - form{"name": "fever_form"}
    - form{"name": null}
    - utter_submit_soreThroat_cough_fever
    - action_reset