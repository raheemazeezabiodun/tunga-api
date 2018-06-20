import datetime

from copy import copy
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tunga_tasks.models import Task, ProgressEvent
from tunga_utils.constants import USER_TYPE_DEVELOPER, USER_TYPE_PROJECT_OWNER, STATUS_ACCEPTED, TASK_TYPE_WEB, \
    TASK_SCOPE_TASK, USER_TYPE_PROJECT_MANAGER, STATUS_REJECTED, TASK_SCOPE_PROJECT, PROGRESS_EVENT_TYPE_PERIODIC, \
    PROGRESS_REPORT_STATUS_ON_SCHEDULE, PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK, PROGRESS_REPORT_STUCK_REASON_ERROR, \
    PROGRESS_EVENT_TYPE_CLIENT, PROGRESS_EVENT_TYPE_PM


class APITaskTestCase(APITestCase):

    def setUp(self):
        self.project_owner = get_user_model().objects.create_user(
            'project_owner', 'po@example.com', 'secret',
            **dict(type=USER_TYPE_PROJECT_OWNER)
        )
        self.developer = get_user_model().objects.create_user(
            'developer', 'developer@example.com', 'secret',
            **dict(type=USER_TYPE_DEVELOPER)
        )
        self.project_manager = get_user_model().objects.create_user(
            'project_manager', 'pm@example.com', 'secret',
            **dict(type=USER_TYPE_PROJECT_MANAGER)
        )
        self.admin = get_user_model().objects.create_superuser(
            'admin', 'admin@example.com', 'secret'
        )

        self.factory = RequestFactory()

    def test_create_task(self):
        """
        Only clients, PMs and admins can create tasks
        """
        url = reverse('task-list')
        data_outer = dict(
            first_name='David', last_name='Semakula', email='guest@example.com',
            type=TASK_TYPE_WEB, scope=TASK_SCOPE_PROJECT
        )
        data_inner = dict(
            title='Task 1', skills='Django, React.js',
            type=TASK_TYPE_WEB, scope=TASK_SCOPE_TASK,
            description='This is a sample task'
        )

        # Guests can fill the wizard
        self.__auth_guest()
        response = self.client.post(url, data_outer)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Developer's can't create tasks
        self.__auth_developer()
        response = self.client.post(url, data_inner)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admins can create tasks
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, data_inner)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # PMs can create tasks
        self.__auth_project_manager()
        response = self.client.post(url, data_inner)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Clients can create tasks
        self.__auth_project_owner()
        response = self.client.post(url, data_inner)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Clients can invite developers to tasks when creating the task
        data_inner['title'] = 'Task 2'
        data_inner['participation'] = [{'user': self.developer.id}]
        response = self.client.post(url, data_inner)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['participation']), 1)
        self.assertEqual(response.data['participation'][0]['user'], self.developer.id)

        # Clients can create milestone on tasks when creating the task
        data_inner['title'] = 'Task 3'
        data_inner['milestones'] = [
            {
                'due_at': datetime.datetime.now(), 'title': 'Milestone 1',
                'description': 'Milestone 1 description'
            }
        ]
        response = self.client.post(url, data_inner)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['milestones']), 1)
        self.assertEqual(response.data['milestones'][0]['title'], 'Milestone 1')

    def test_update_task(self):
        """
        Only the task creator or an admin can update a task
        """
        task = self.__create_task()

        url = reverse('task-detail', args=[task.id])
        data = dict(title='Task 1 Edit', fee=20)

        # Guests can't edit tasks
        self.__auth_guest()
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Devs can't edit tasks
        self.__auth_developer()
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admins can edit tasks
        self.__auth_admin()
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Clients can edit tasks
        self.__auth_project_owner()
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Clients can invite developers tasks
        participation_data = dict(participation=[dict(user=self.developer.id)])
        response = self.client.patch(url, participation_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['participation']), 1)
        self.assertEqual(response.data['participation'][0]['user'], self.developer.id)

        self.__auth_developer()
        # Dev accepting task invitations
        response = self.client.patch(
            url, {
                'participation': [
                    {'user': self.developer.id, 'status': STATUS_ACCEPTED}
                ]
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['participation']), 1)
        self.assertEqual(response.data['participation'][0]['user'], self.developer.id)
        self.assertTrue(response.data['participation'][0]['status'] == STATUS_ACCEPTED)

        # Dev rejecting task invitations
        response = self.client.patch(
            url, {
                'participation': [
                    {'user': self.developer.id, 'status': STATUS_REJECTED}
                ]
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['details']['participation']), 0)

        self.__auth_project_owner()
        # Clients can create milestones for tasks
        milestone_data = {
            'milestones': [
                {
                    'due_at': datetime.datetime.now(),
                    'title': 'Milestone 1',
                    'description': 'Milestone 1 description'
                }
            ]
        }
        response = self.client.patch(url, milestone_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['milestones']), 1)
        self.assertEqual(response.data['milestones'][0]['title'], 'Milestone 1')

        # Client's can't reduce the task fee
        data = {'fee': 15}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Change task owner to admin
        task.user = self.admin
        task.save()

        # Client's can't edit the task fee
        data = {'title': 'Task 1 Edit 2'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_developer_progress_report(self):
        """
        Developer can share progress reports
        """
        task = self.__create_task()
        progress_event = self.__create_progress_event(task, PROGRESS_EVENT_TYPE_PERIODIC)

        url = reverse('progressreport-list')

        # Guests can't create developer reports
        self.__auth_guest()
        response = self.client.post(url, dict(event=progress_event.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.__auth_developer()
        # Devs can't create empty reports
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Devs can create reports
        dev_report = dict(
            event=progress_event.id,
            status=PROGRESS_REPORT_STATUS_ON_SCHEDULE,
            started_at=datetime.datetime.utcnow() - relativedelta(days=2),
            percentage=50,
            accomplished='Finished',
            todo='Next steps',
            rate_deliverables=5,
            next_deadline=datetime.datetime.utcnow() + relativedelta(days=3),
            next_deadline_meet=True
        )
        response = self.client.post(url, dev_report)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Devs can create reports with percentage completed as zero
        dev_report_zero = copy(dev_report)
        dev_report_zero['percentage'] = 0
        response = self.client.post(url, dev_report_zero)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Devs can't create reports with missing conditional values
        dev_report_conditionals_missing = copy(dev_report)
        dev_report_conditionals_missing.update(
            dict(
                status=PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK,
                next_deadline_meet=False
            )
        )
        response = self.client.post(url, dev_report_conditionals_missing)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('stuck_reason' in response.data)
        self.assertTrue('next_deadline_fail_reason' in response.data)

        # Devs can create reports with correct conditional values
        dev_report_conditionals = copy(dev_report)
        dev_report_conditionals.update(
            dict(
                status=PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK,
                stuck_reason=PROGRESS_REPORT_STUCK_REASON_ERROR,
                next_deadline_meet=False,
                next_deadline_fail_reason="It's complicated"
            )
        )
        response = self.client.post(url, dev_report_conditionals)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Devs can't create reports with invalid values
        dev_report_invalid = copy(dev_report)
        dev_report_invalid.update(dict(status='bad_status', percentage=101, rate_deliverables=6))
        response = self.client.post(url, dev_report_invalid)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('status' in response.data)
        self.assertTrue('percentage' in response.data)
        self.assertTrue('rate_deliverables' in response.data)

    def test_create_pm_progress_report(self):
        """
        PM can share progress reports
        """
        task = self.__create_task()
        progress_event = self.__create_progress_event(task, PROGRESS_EVENT_TYPE_PM)

        url = reverse('progressreport-list')

        # Guests can't create PM reports
        self.__auth_guest()
        response = self.client.post(url, dict(event=progress_event.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.__auth_project_manager()
        # PMs can't create empty reports
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # PMs can create reports
        pm_report = dict(
            event=progress_event.id,
            status=PROGRESS_REPORT_STATUS_ON_SCHEDULE,
            last_deadline_met=True,
            percentage=75,
            accomplished='Finished',
            todo='Next steps',
            next_deadline=datetime.datetime.utcnow() + relativedelta(days=3),
            next_deadline_meet=True,
            team_appraisal='Good devs'
        )
        response = self.client.post(url, pm_report)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # PMs can't create reports with missing conditional values
        pm_report_conditionals_missing = copy(pm_report)
        pm_report_conditionals_missing.update(
            dict(
                status=PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK,
                last_deadline_met=False,
                next_deadline_meet=False
            )
        )
        response = self.client.post(url, pm_report_conditionals_missing)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('stuck_reason' in response.data)
        self.assertTrue('deadline_miss_communicated' in response.data)
        self.assertTrue('deadline_report' in response.data)
        self.assertTrue('next_deadline_fail_reason' in response.data)

        # PMs can create reports with correct conditional values
        pm_report_conditionals = copy(pm_report)
        pm_report_conditionals.update(
            dict(
                status=PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK,
                stuck_reason=PROGRESS_REPORT_STUCK_REASON_ERROR,
                last_deadline_met=False,
                deadline_miss_communicated=False,
                deadline_report="The was nasty AF",
                next_deadline_meet=False,
                next_deadline_fail_reason="It's complicated"
            )
        )
        response = self.client.post(url, pm_report_conditionals)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # PMs can't create reports with invalid values
        pm_report_invalid = copy(pm_report)
        pm_report_invalid.update(dict(status='bad_status', percentage=101))
        response = self.client.post(url, pm_report_invalid)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('status' in response.data)
        self.assertTrue('percentage' in response.data)

    def test_create_client_surveys(self):
        """
        Clients can fill survsys
        """
        task = self.__create_task()
        progress_event = self.__create_progress_event(task, PROGRESS_EVENT_TYPE_CLIENT)

        url = reverse('progressreport-list')

        # Guests can't create client surveys
        self.__auth_guest()
        response = self.client.post(url, dict(event=progress_event.id))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.__auth_project_owner()
        # Clients can't create empty surveys
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Clients can create reports
        client_report = dict(
            event=progress_event.id,
            last_deadline_met=True,
            deliverable_satisfaction=False,
            rate_deliverables=3
        )
        response = self.client.post(url, client_report)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Clients can't create reports with missing conditional values
        client_report_conditionals_missing = copy(client_report)
        client_report_conditionals_missing.update(dict(last_deadline_met=False))
        response = self.client.post(url, client_report_conditionals_missing)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('deadline_miss_communicated' in response.data)

        # Clients can create reports with correct conditional values
        client_report_conditionals = copy(client_report)
        client_report_conditionals.update(
            dict(
                last_deadline_met=False,
                deadline_miss_communicated=False,
            )
        )
        response = self.client.post(url, client_report_conditionals)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Clients can't create reports with invalid values
        client_report_invalid = copy(client_report)
        client_report_invalid.update(dict(rate_deliverables=6))
        response = self.client.post(url, client_report_invalid)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('rate_deliverables' in response.data)

    # Utility methods
    def __auth_guest(self):
        self.client.force_authenticate(user=None)

    def __auth_admin(self):
        self.client.force_authenticate(user=self.admin)

    def __auth_project_owner(self):
        self.client.force_authenticate(user=self.project_owner)

    def __auth_project_manager(self):
        self.client.force_authenticate(user=self.project_manager)

    def __auth_developer(self):
        self.client.force_authenticate(user=self.developer)

    def __create_task(self):
        return Task.objects.create(
            title='Task 1', description='Task 1 description',
            skills='Django, React.js', fee=15, user=self.project_owner
        )

    def __create_progress_event(self, task, event_type=PROGRESS_EVENT_TYPE_PERIODIC):
        if not task:
            task = self.__create_task()
        return ProgressEvent.objects.create(
            task=task, type=event_type, due_at=datetime.datetime.utcnow()
        )
