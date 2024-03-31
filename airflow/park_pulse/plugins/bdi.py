# -*- coding: utf-8 -*-

from airflow.plugins_manager import AirflowPlugin
from operators.check_db import *

# Defining the plugin class
class ExporoPlugin(AirflowPlugin):
    name = "bdi"
    operators = [
        CheckDbOperator,
    ]
