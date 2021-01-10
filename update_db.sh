#!/bin/bash
source $PROJECT_PATH/env/bin/activate
python3 $PROJECT_PATH/manage.py add_off_data --settings=purbeurre.settings.production
