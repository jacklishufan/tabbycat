.. _starting-a-tournament:

=====================
Import Data Using API
=====================

It is possible to import data from third-party registration system using POST method. The APIs are as follows

Adding Institutions
========================
/<tournament code>/admin/participants/addspeaker/

- username
    Username of a staff account
- password:
    Password of the staff account
- inst_name:
    Institution name
- inst_code:
     Institution code

Adding Teams
==============================
/<tournament code>/admin/participants/addspeaker/

- username
    Username of a staff account
- password:
    Password of the staff account
- code_name:
    Team code name for identification, it must be unique
- reference
    Reference of the team
- institution
    The name of institution
- type (Optional)
    -N, S, C or B
- short_reference (Optional)
    A shorter version of reference

Adding Speakers
============================

/<tournament code>/admin/participants/addspeaker/

- username
    Username of a staff account
- password:
    Password of the staff account
- speaker_name:
    the name of the speaker
- team
    the name of the team this speaker belongs to
- gender(Optional)
    M, F, or O
- phone (Optional)
    this speaker's phone number
- email (Optional)
    this speaker's email address