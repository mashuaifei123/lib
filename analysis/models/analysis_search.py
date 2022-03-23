import datetime
from inspect import isasyncgenfunction
from uuid import NAMESPACE_OID
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import pandas as pd
import numpy as np

