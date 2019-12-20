.. _starting-a-tournament:

=====================
Import Data Using API
=====================

It is possible to import data from third-party registration system using POST method. The APIs are as follows

Adding Institutions, Teams and Speakers
=========================================================================
/<tournament code>/admin/participants/addimportdata/

Header

- apiusername
    Username of a staff account
- password:
    Password of the staff account

Body (JSON)

- adjudicators(List):

    name : the name of an adjudicator

    gender : the gender of an adjudicator

    email : contact information

    institution: the institution an adjudicator belongs to


- institutions(List):

    name : the name of an institution

    code : the identification codename of an institution
- teams(List):

    name : the reference of the team

    code : team codename

    institution : the codename of the institution a team belongs to

    uses_institution_prefix(bool) : whether the institution name will show up as a prefix in interface

    speakers(List):
        name : the name of a speaker

        gender : the gender of a speaker

        email : contact information

