# -*- coding: utf-8 -*-

from contextlib import contextmanager

from odoo.tests.common import SavepointCase, Form
from odoo.exceptions import AccessError, UserError


class TestMultiCompanyCommon(SavepointCase):

    @classmethod
    def setUpMultiCompany(cls):

        # create companies
        cls.company_a = cls.env['res.company'].create({
            'name': 'Company A'
        })
        cls.company_b = cls.env['res.company'].create({
            'name': 'Company B'
        })

        # shared customers
        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Valid Lelitre',
            'email': 'valid.lelitre@agrolait.com',
            'company_id': False,
        })
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Valid Poilvache',
            'email': 'valid.other@gmail.com',
            'company_id': False,
        })

        # users to use through the various tests
        user_group_employee = cls.env.ref('base.group_user')
        Users = cls.env['res.users'].with_context({'no_reset_password': True})

        cls.user_employee_company_a = Users.create({
            'name': 'Employee Company A',
            'login': 'employee-a',
            'email': 'employee@companya.com',
            'company_id': cls.company_a.id,
            'company_ids': [(6, 0, [cls.company_a.id])],
            'groups_id': [(6, 0, [user_group_employee.id])]
        })
        cls.user_manager_company_a = Users.create({
            'name': 'Manager Company A',
            'login': 'manager-a',
            'email': 'manager@companya.com',
            'company_id': cls.company_a.id,
            'company_ids': [(6, 0, [cls.company_a.id])],
            'groups_id': [(6, 0, [user_group_employee.id])]
        })
        cls.user_employee_company_b = Users.create({
            'name': 'Employee Company B',
            'login': 'employee-b',
            'email': 'employee@companyb.com',
            'company_id': cls.company_b.id,
            'company_ids': [(6, 0, [cls.company_b.id])],
            'groups_id': [(6, 0, [user_group_employee.id])]
        })
        cls.user_manager_company_b = Users.create({
            'name': 'Manager Company B',
            'login': 'manager-b',
            'email': 'manager@companyb.com',
            'company_id': cls.company_b.id,
            'company_ids': [(6, 0, [cls.company_b.id])],
            'groups_id': [(6, 0, [user_group_employee.id])]
        })

    @contextmanager
    def sudo(self, login):
        old_uid = self.uid
        try:
            user = self.env['res.users'].sudo().search([('login', '=', login)])
            # switch user
            self.uid = user.id
            self.env = self.env(user=self.uid)
            yield
        finally:
            # back
            self.uid = old_uid
            self.env = self.env(user=self.uid)

    @contextmanager
    def allow_companies(self, company_ids):
        """ The current user will be allowed in each given companies (like he can sees all of them in the company switcher and they are all checked) """
        old_allow_company_ids = self.env.user.company_ids.ids
        current_user = self.env.user
        try:
            current_user.write({'company_ids': company_ids})
            context = dict(self.env.context, allowed_company_ids=company_ids)
            self.env = self.env(user=current_user, context=context)
            yield
        finally:
            # back
            current_user.write({'company_ids': old_allow_company_ids})
            context = dict(self.env.context, allowed_company_ids=old_allow_company_ids)
            self.env = self.env(user=current_user, context=context)

    @contextmanager
    def switch_company(self, company):
        """ Change the company in which the current user is logged """
        old_companies = self.env.context.get('allowed_company_ids', [])
        try:
            # switch company in context
            new_companies = list(old_companies)
            if company.id not in new_companies:
                new_companies = [company.id] + new_companies
            else:
                new_companies.insert(0, new_companies.pop(new_companies.index(company.id)))
            context = dict(self.env.context, allowed_company_ids=new_companies)
            self.env = self.env(context=context)
            yield
        finally:
            # back
            context = dict(self.env.context, allowed_company_ids=old_companies)
            self.env = self.env(context=context)


class TestMultiCompanyservices(TestMultiCompanyCommon):

    @classmethod
    def setUpClass(cls):
        super(TestMultiCompanyservices, cls).setUpClass()

        cls.setUpMultiCompany()

        user_group_services_user = cls.env.ref('services.group_services_user')
        user_group_services_manager = cls.env.ref('services.group_services_manager')

        # setup users
        cls.user_employee_company_a.write({
            'groups_id': [(4, user_group_services_user.id)]
        })
        cls.user_manager_company_a.write({
            'groups_id': [(4, user_group_services_manager.id)]
        })
        cls.user_employee_company_b.write({
            'groups_id': [(4, user_group_services_user.id)]
        })
        cls.user_manager_company_b.write({
            'groups_id': [(4, user_group_services_manager.id)]
        })

        # create services in both companies
        services = cls.env['services.services'].with_context({'mail_create_nolog': True, 'tracking_disable': True})
        cls.services_company_a = services.create({
            'name': 'services Company A',
            'alias_name': 'services+companya',
            'partner_id': cls.partner_1.id,
            'company_id': cls.company_a.id,
            'type_ids': [
                (0, 0, {
                    'name': 'New',
                    'sequence': 1,
                }),
                (0, 0, {
                    'name': 'Won',
                    'sequence': 10,
                })
            ]
        })
        cls.services_company_b = services.create({
            'name': 'services Company B',
            'alias_name': 'services+companyb',
            'partner_id': cls.partner_1.id,
            'company_id': cls.company_b.id,
            'type_ids': [
                (0, 0, {
                    'name': 'New',
                    'sequence': 1,
                }),
                (0, 0, {
                    'name': 'Won',
                    'sequence': 10,
                })
            ]
        })
        # already-existing tasks in company A and B
        Task = cls.env['services.task'].with_context({'mail_create_nolog': True, 'tracking_disable': True})
        cls.task_1 = Task.create({
            'name': 'Task 1 in services A',
            'user_id': cls.user_employee_company_a.id,
            'services_id': cls.services_company_a.id
        })
        cls.task_2 = Task.create({
            'name': 'Task 2 in services B',
            'user_id': cls.user_employee_company_b.id,
            'services_id': cls.services_company_b.id
        })

    def test_create_services(self):
        """ Check services creation in multiple companies """
        with self.sudo('manager-a'):
            services = self.env['services.services'].with_context({'tracking_disable': True}).create({
                'name': 'services Company A',
                'partner_id': self.partner_1.id,
            })
            self.assertEqual(services.company_id, self.env.user.company_id, "A newly created services should be in the current user company")

            with self.switch_company(self.company_b):
                with self.assertRaises(AccessError, msg="Manager can not create services in a company in which he is not allowed"):
                    services = self.env['services.services'].with_context({'tracking_disable': True}).create({
                        'name': 'services Company B',
                        'partner_id': self.partner_1.id,
                        'company_id': self.company_b.id
                    })

                # when allowed in other company, can create a services in another company (different from the one in which you are logged)
                with self.allow_companies([self.company_a.id, self.company_b.id]):
                    services = self.env['services.services'].with_context({'tracking_disable': True}).create({
                        'name': 'services Company B',
                        'partner_id': self.partner_1.id,
                        'company_id': self.company_b.id
                    })

    def test_generate_analytic_account(self):
        """ Check the analytic account generation, company propagation """
        with self.sudo('manager-b'):
            with self.allow_companies([self.company_a.id, self.company_b.id]):
                self.services_company_a._create_analytic_account()

                self.assertEqual(self.services_company_a.company_id, self.services_company_a.analytic_account_id.company_id, "The analytic account created from a services should be in the same company")

    def test_create_task(self):
        with self.sudo('employee-a'):
            # create task, set services; the onchange will set the correct company
            with Form(self.env['services.task'].with_context({'tracking_disable': True})) as task_form:
                task_form.name = 'Test Task in company A'
                task_form.services_id = self.services_company_a
            task = task_form.save()

            self.assertEqual(task.company_id, self.services_company_a.company_id, "The company of the task should be the one from its services.")

    def test_move_task(self):
        with self.sudo('employee-a'):
            with self.allow_companies([self.company_a.id, self.company_b.id]):
                with Form(self.task_1) as task_form:
                    task_form.services_id = self.services_company_b
                task = task_form.save()

                self.assertEqual(task.company_id, self.company_b, "The company of the task should be the one from its services.")

                with Form(self.task_1) as task_form:
                    task_form.services_id = self.env['services.services']  # False is not accepted by the form
                task = task_form.save()

                self.assertEqual(task.company_id, self.company_b, "Making a task orphan does not change its company.")

    def test_create_subtask(self):
        with self.sudo('employee-a'):
            with self.allow_companies([self.company_a.id, self.company_b.id]):
                # create subtask, set parent; the onchange will set the correct company and subtask services
                with Form(self.env['services.task'].with_context({'tracking_disable': True})) as task_form:
                    task_form.name = 'Test Subtask in company B'
                    task_form.parent_id = self.task_1
                    task_form.services_id = self.services_company_b

                task = task_form.save()

                self.assertEqual(task.company_id, self.services_company_b.company_id, "The company of the subtask should be the one from its services, and not from its parent.")

                # set parent on existing orphan task; the onchange will set the correct company and subtask services
                self.task_2.write({'services_id': False})
                with Form(self.task_2) as task_form:
                    task_form.name = 'Test Task 2 becomes child of Task 1 (other company)'
                    task_form.parent_id = self.task_1
                task = task_form.save()

                self.assertEqual(task.company_id, task.services_id.company_id, "The company of the orphan subtask should be the one from its services.")

    def test_cross_subtask_services(self):
        # set up default subtask services
        self.services_company_a.write({'subtask_services_id': self.services_company_b.id})

        with self.sudo('employee-a'):
            with self.allow_companies([self.company_a.id, self.company_b.id]):
                with Form(self.env['services.task'].with_context({'tracking_disable': True})) as task_form:
                    task_form.name = 'Test Subtask in company B'
                    task_form.parent_id = self.task_1

                task = task_form.save()

                self.assertEqual(task.services_id, self.task_1.services_id.subtask_services_id, "The default services of a subtask should be the default subtask services of the services from the mother task")
                self.assertEqual(task.company_id, task.services_id.subtask_services_id.company_id, "The company of the orphan subtask should be the one from its services.")
                self.assertEqual(self.task_1.child_ids.ids, [task.id])

        with self.sudo('employee-a'):
            with self.assertRaises(AccessError):
                with Form(task) as task_form:
                    task_form.name = "Testing changing name in a company I can not read/write"
