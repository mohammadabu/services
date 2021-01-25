# -*- coding: utf-8 -*-

from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError

class TestservicesBase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestservicesBase, cls).setUpClass()

        user_group_employee = cls.env.ref('base.group_user')
        user_group_services_user = cls.env.ref('services.group_services_user')
        user_group_services_manager = cls.env.ref('services.group_services_manager')

        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Valid Lelitre',
            'email': 'valid.lelitre@agrolait.com'})
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Valid Poilvache',
            'email': 'valid.other@gmail.com'})

        # Test users to use through the various tests
        Users = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.user_public = Users.create({
            'name': 'Bert Tartignole',
            'login': 'bert',
            'email': 'b.t@example.com',
            'signature': 'SignBert',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.env.ref('base.group_public').id])]})
        cls.user_portal = Users.create({
            'name': 'Chell Gladys',
            'login': 'chell',
            'email': 'chell@gladys.portal',
            'signature': 'SignChell',
            'notification_type': 'email',
            'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])]})
        cls.user_servicesuser = Users.create({
            'name': 'Armande servicesUser',
            'login': 'Armande',
            'email': 'armande.servicesuser@example.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_services_user.id])]
        })
        cls.user_servicesmanager = Users.create({
            'name': 'Bastien servicesManager',
            'login': 'bastien',
            'email': 'bastien.servicesmanager@example.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_services_manager.id])]})

        # Test 'Pigs' services
        cls.services_pigs = cls.env['services.services'].with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs',
            'privacy_visibility': 'employees',
            'alias_name': 'services+pigs',
            'partner_id': cls.partner_1.id})
        # Already-existing tasks in Pigs
        cls.task_1 = cls.env['services.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs UserTask',
            'user_id': cls.user_servicesuser.id,
            'services_id': cls.services_pigs.id})
        cls.task_2 = cls.env['services.task'].with_context({'mail_create_nolog': True}).create({
            'name': 'Pigs ManagerTask',
            'user_id': cls.user_servicesmanager.id,
            'services_id': cls.services_pigs.id})

        # Test 'Goats' services, same as 'Pigs', but with 2 stages
        cls.services_goats = cls.env['services.services'].with_context({'mail_create_nolog': True}).create({
            'name': 'Goats',
            'privacy_visibility': 'followers',
            'alias_name': 'services+goats',
            'partner_id': cls.partner_1.id,
            'type_ids': [
                (0, 0, {
                    'name': 'New',
                    'sequence': 1,
                }),
                (0, 0, {
                    'name': 'Won',
                    'sequence': 10,
                })]
            })

    def format_and_process(self, template, to='groups@example.com, other@gmail.com', subject='Frogs',
                           extra='', email_from='Sylvie Lelitre <test.sylvie.lelitre@agrolait.com>',
                           cc='', msg_id='<1198923581.41972151344608186760.JavaMail@agrolait.com>',
                           model=None, target_model='services.task', target_field='name'):
        self.assertFalse(self.env[target_model].search([(target_field, '=', subject)]))
        mail = template.format(to=to, subject=subject, cc=cc, extra=extra, email_from=email_from, msg_id=msg_id)
        self.env['mail.thread'].with_context(mail_channel_noautofollow=True).message_process(model, mail)
        return self.env[target_model].search([(target_field, '=', subject)])

    def test_delete_services_with_tasks(self):
        """User should never be able to delete a services with tasks"""

        with self.assertRaises(UserError):
            self.services_pigs.unlink()

        # click on the archive button
        self.services_pigs.write({'active': False})

        with self.assertRaises(UserError):
            self.services_pigs.unlink()
