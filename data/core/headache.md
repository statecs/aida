## happy path headache_form
* ask_about_headache
    - headache_form
    - form{"name": "headache_form"}
    - utter_submit_headache
    - action_reset

## happy path headache+cough_form
* ask_about_headache+ask_about_cough
    - headache_form
    - cough_form
    - form{"name": "headache_form"}
    - form{"name": "cough_form"}
    - form{"name": null}
    - utter_submit_headache_cough
    - action_reset 

# happy path headache+fever_form
* ask_about_headache+ask_about_fever
    - headache_form
    - fever_form
    - form{"name": "headache_form"}
    - form{"name": "fever_form"}
    - form{"name": null}
    - utter_submit_headache_fever
    - action_reset

# happy path headache+soreThroat_form
* ask_about_headache+ask_about_soreThroat
    - headache_form
    - soreThroat_form
    - form{"name": "headache_form"}
    - form{"name": "soreThroat_form"}
    - form{"name": null}
    - utter_submit_headache_soreThroat
    - action_reset

# happy path headache+soreThroat_form+fever_form
* ask_about_headache+ask_about_soreThroat+ask_about_fever
    - headache_form
    - soreThroat_form
    - fever_form
    - form{"name": "headache_form"}
    - form{"name": "soreThroat_form"}
    - form{"name": "fever_form"}
    - form{"name": null}
    - utter_submit_headache_soreThroat_fever
    - action_reset

# happy path headache+soreThroat_form+cough_form
* ask_about_headache+ask_about_soreThroat+ask_about_cough
    - headache_form
    - soreThroat_form
    - cough_form
    - form{"name": "headache_form"}
    - form{"name": "soreThroat_form"}
    - form{"name": "cough_form"}
    - form{"name": null}
    - utter_submit_headache_soreThroat_cough
    - action_reset


# happy path headache+soreThroat_form+cough_form+fever_form
* ask_about_headache+ask_about_soreThroat+ask_about_cough+ask_about_fever
    - headache_form
    - soreThroat_form
    - cough_form
    - fever_form
    - form{"name": "headache_form"}
    - form{"name": "soreThroat_form"}
    - form{"name": "cough_form"}
    - form{"name": "fever_form"}
    - form{"name": null}
    - utter_submit_headache_soreThroat_cough_fever
    - action_reset
