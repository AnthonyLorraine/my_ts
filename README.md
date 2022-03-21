# Overtime Tracking App

## Overview
### Purpose
Track any overtime performed during an on-call, change window or any similar timeframe scenarios.

## Installation
### Heroku for production use
1. Create new app on Heroku
2. Link to project on github
3. Wait for deployment
4. Apply the fixtures for auth_group and settings. `manage.py loaddata FIXTURE_NAME`
5. Create a superuser in the Heroku admin panel `manage.py createsuperuser`
6. Setup the teams, penalties and penalty types for time sheets to be entered.

### Local Installation for development
1. Run command `git clone https://github.com/AnthonyLorraine/my_ts.git`
2. Then create a virtual environment for the new project `python -m venv my_ts`
3. Activate the environment, Change to the directory `cd my_ts` and run the file `activate`
4. Install requirements `pip install -r requirements.txt`
5. Create the database `python manage.py migrate`
6. Install settings and auth_groups
   1. `python manage.py loaddata auth_group`
   2. `python manage.py loaddata settings`
7. Create the super user. `python manage.py createsuperuser`
8. Run the development server. `python manage.py runserver`
9. Open the project folder in whichever IDE you like.

## Features
### Teams
Allowing for a dedicated manager means tracking overtime for employees

### Penalty Types
Set up different penalty types with different reasons to allow for separation between payout types. 
For example, an on-call incident might accrue Paid overtime, whereas any time spent performing a change within an agreed change window may accrue Time off in Lieu (TOIL).

### Time tracking
Users can add a start time and a duration that they spent doing a task. The data can then be viewed by the user or a team manager.

