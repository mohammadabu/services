# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.services.tests.test_services_base import TestservicesBase
from odoo.exceptions import AccessError
from odoo.tools import mute_logger


class TestPortalservicesBase(TestservicesBase):

    def setUp(self):
        super(TestPortalservicesBase, self).setUp()

        user_group_employee = self.env.ref('base.group_user')
        user_group_services_user = self.env.ref('services.group_services_user')

        self.user_noone = self.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True}).create({
            'name': 'Noemie NoOne',
            'login': 'noemie',
            'email': 'n.n@example.com',
            'signature': '--\nNoemie',
            'notification_type': 'email',
            'groups_id': [(6, 0, [])]})

        self.user_follower = self.env['res.users'].with_context({'no_reset_password': True, 'mail_create_nosubscribe': True}).create({
            'name': 'Jack Follow',
            'login': 'jack',
            'email': 'n.n@example.com',
            'signature': '--\nJack',
            'notification_type': 'email',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_services_user.id])]
        })

        self.task_3 = self.env['services.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test3', 'user_id': self.user_portal.id, 'services_id': self.services_pigs.id})
        self.task_4 = self.env['services.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test4', 'user_id': self.user_public.id, 'services_id': self.services_pigs.id})
        self.task_5 = self.env['services.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test5', 'user_id': False, 'services_id': self.services_pigs.id})
        self.task_6 = self.env['services.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Test5', 'user_id': False, 'services_id': self.services_pigs.id})

        self.task_6.message_subscribe(partner_ids=[self.user_follower.partner_id.id])


class TestPortalservices(TestPortalservicesBase):

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_employee_services_access_rights(self):
        pigs = self.services_pigs

        pigs.write({'privacy_visibility': 'employees'})
        # Do: Alfred reads services -> ok (employee ok employee)
        pigs.with_user(self.user_servicesuser).read(['user_id'])
        # Test: all services tasks visible
        tasks = self.env['services.task'].with_user(self.user_servicesuser).search([('services_id', '=', pigs.id)])
        test_task_ids = set([self.task_1.id, self.task_2.id, self.task_3.id, self.task_4.id, self.task_5.id, self.task_6.id])
        self.assertEqual(set(tasks.ids), test_task_ids,
                        'access rights: services user cannot see all tasks of an employees services')
        # Do: Bert reads services -> crash, no group
        self.assertRaises(AccessError, pigs.with_user(self.user_noone).read, ['user_id'])
        # Do: Donovan reads services -> ko (public ko employee)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])
        # Do: services user is employee and can create a task
        tmp_task = self.env['services.task'].with_user(self.user_servicesuser).with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs task',
            'services_id': pigs.id})
        tmp_task.with_user(self.user_servicesuser).unlink()

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_favorite_services_access_rights(self):
        pigs = self.services_pigs.with_user(self.user_servicesuser)

        # we can't write on services name
        self.assertRaises(AccessError, pigs.write, {'name': 'False Pigs'})
        # we can write on is_favorite
        pigs.write({'is_favorite': True})

    @mute_logger('odoo.addons.base.ir.ir_model')
    def test_followers_services_access_rights(self):
        pigs = self.services_pigs
        pigs.write({'privacy_visibility': 'followers'})
        pigs.flush(['privacy_visibility'])

        # Do: Jack reads services -> ok (task follower ok followers)
        pigs.with_user(self.user_follower).read(['user_id'])
        # Do: Jack edit services -> ko (task follower ko followers)
        self.assertRaises(AccessError, pigs.with_user(self.user_follower).write, {'name': 'Test Follow not ok'})
        # Do: Jack edit task not followed -> ko (task follower ko followers)
        self.assertRaises(AccessError, self.task_5.with_user(self.user_follower).write, {'name': 'Test Follow not ok'})
        # Do: Jack edit task followed-> ok (task follower ok followers)
        self.task_6.with_user(self.user_follower).write({'name': 'Test Follow ok'})

        # Do: Alfred reads services -> ko (employee ko followers)
        pigs.task_ids.message_unsubscribe(partner_ids=[self.user_servicesuser.partner_id.id])
        self.assertRaises(AccessError, pigs.with_user(self.user_servicesuser).read, ['user_id'])

        # Test: no services task visible
        tasks = self.env['services.task'].with_user(self.user_servicesuser).search([('services_id', '=', pigs.id)])
        self.assertEqual(tasks, self.task_1,
                         'access rights: employee user should not see tasks of a not-followed followers services, only assigned')

        # Do: Bert reads services -> crash, no group
        self.assertRaises(AccessError, pigs.with_user(self.user_noone).read, ['user_id'])

        # Do: Donovan reads services -> ko (public ko employee)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])

        pigs.message_subscribe(partner_ids=[self.user_servicesuser.partner_id.id])

        # Do: Alfred reads services -> ok (follower ok followers)
        donkey = pigs.with_user(self.user_servicesuser)
        donkey.invalidate_cache()
        donkey.read(['user_id'])

        # Do: Donovan reads services -> ko (public ko follower even if follower)
        self.assertRaises(AccessError, pigs.with_user(self.user_public).read, ['user_id'])
        # Do: services user is follower of the services and can create a task
        self.env['services.task'].with_user(self.user_servicesuser).with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs task', 'services_id': pigs.id
        })
        # not follower user should not be able to create a task
        pigs.with_user(self.user_servicesuser).message_unsubscribe(partner_ids=[self.user_servicesuser.partner_id.id])
        self.assertRaises(AccessError, self.env['services.task'].with_user(self.user_servicesuser).with_context({
            'mail_create_nolog': True}).create, {'name': 'Pigs task', 'services_id': pigs.id})

        # Do: services user can create a task without services
        self.assertRaises(AccessError, self.env['services.task'].with_user(self.user_servicesuser).with_context({
            'mail_create_nolog': True}).create, {'name': 'Pigs task', 'services_id': pigs.id})
