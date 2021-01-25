# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.services.tests.test_access_rights import TestPortalservicesBase
from odoo.exceptions import AccessError
from odoo.tools import mute_logger


class TestPortalservices(TestPortalservicesBase):
    @mute_logger('odoo.addons.base.models.ir_model')
    def test_portal_services_access_rights(self):
        pigs = self.services_pigs
        pigs.write({'privacy_visibility': 'portal'})

        # Do: Alfred reads services -> ok (employee ok public)
        pigs.with_user(self.user_servicesuser).read(['user_id'])
        # Test: all services tasks visible
        tasks = self.env['services.task'].with_user(self.user_servicesuser).search([('services_id', '=', pigs.id)])
        self.assertEqual(tasks, self.task_1 | self.task_2 | self.task_3 | self.task_4 | self.task_5 | self.task_6,
                         'access rights: services user should see all tasks of a portal services')

        # Do: Bert reads services -> crash, no group
        self.assertRaises(AccessError, pigs.with_user(self.user_noone).read, ['user_id'])
        # Test: no services task searchable
        self.assertRaises(AccessError, self.env['services.task'].with_user(self.user_noone).search, [('services_id', '=', pigs.id)])

        # Data: task follower
        pigs.with_user(self.user_servicesmanager).message_subscribe(partner_ids=[self.user_portal.partner_id.id])
        self.task_1.with_user(self.user_servicesuser).message_subscribe(partner_ids=[self.user_portal.partner_id.id])
        self.task_3.with_user(self.user_servicesuser).message_subscribe(partner_ids=[self.user_portal.partner_id.id])
        # Do: Chell reads services -> ok (portal ok public)
        pigs.with_user(self.user_portal).read(['user_id'])
        # Do: Donovan reads services -> ko (public ko portal)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])
        # Test: no access right to services.task
        self.assertRaises(AccessError, self.env['services.task'].with_user(self.user_public).search, [])
        # Data: task follower cleaning
        self.task_1.with_user(self.user_servicesuser).message_unsubscribe(partner_ids=[self.user_portal.partner_id.id])
        self.task_3.with_user(self.user_servicesuser).message_unsubscribe(partner_ids=[self.user_portal.partner_id.id])
