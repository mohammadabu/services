# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'

    services_ids = fields.One2many('services.services', 'analytic_account_id', string='servicess')
    services_count = fields.Integer("services Count", compute='_compute_services_count')

    @api.depends('services_ids')
    def _compute_services_count(self):
        services_data = self.env['services.services'].read_group([('analytic_account_id', 'in', self.ids)], ['analytic_account_id'], ['analytic_account_id'])
        mapping = {m['analytic_account_id'][0]: m['analytic_account_id_count'] for m in services_data}
        for account in self:
            account.services_count = mapping.get(account.id, 0)

    @api.constrains('company_id')
    def _check_company_id(self):
        for record in self:
            if record.company_id and not all(record.company_id == c for c in record.services_ids.mapped('company_id')):
                raise UserError(_('You cannot change the company of an analytical account if it is related to a services.'))

    def unlink(self):
        servicess = self.env['services.services'].search([('analytic_account_id', 'in', self.ids)])
        has_tasks = self.env['services.task'].search_count([('services_id', 'in', servicess.ids)])
        if has_tasks:
            raise UserError(_('Please remove existing tasks in the services linked to the accounts you want to delete.'))
        return super(AccountAnalyticAccount, self).unlink()

    def action_view_servicess(self):
        kanban_view_id = self.env.ref('services.view_services_kanban').id
        result = {
            "type": "ir.actions.act_window",
            "res_model": "services.services",
            "views": [[kanban_view_id, "kanban"], [False, "form"]],
            "domain": [['analytic_account_id', '=', self.id]],
            "context": {"create": False},
            "name": "servicess",
        }
        if len(self.services_ids) == 1:
            result['views'] = [(False, "form")]
            result['res_id'] = self.services_ids.id
        return result
