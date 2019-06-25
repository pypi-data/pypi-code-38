# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
#from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
#from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError
from django.db.models.fields import BooleanField, TextField, CharField

import re
from datetime import datetime, timedelta
import pytz