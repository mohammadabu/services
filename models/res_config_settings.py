# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_services_forecast = fields.Boolean(string="Forecasts")
    module_hr_timesheet = fields.Boolean(string="Task Logs")
    group_subtask_services = fields.Boolean("Sub-tasks", implied_group="services.group_subtask_services")
    group_services_rating = fields.Boolean("Use Rating on services", implied_group='services.group_services_rating')
