import datetime

from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from django_rq.workers import get_worker
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from tunga_utils.constants import USER_TYPE_DEVELOPER, USER_TYPE_PROJECT_OWNER, STATUS_ACCEPTED, TASK_TYPE_WEB, \
    TASK_SCOPE_TASK, USER_TYPE_PROJECT_MANAGER, STATUS_REJECTED
from tunga_tasks.models import Task


class APITaskTestCase(APITestCase):

    def setUp(self):
        self.project_owner = get_user_model().objects.create_user(
            'project_owner', 'po@example.com', 'secret', **{'type': USER_TYPE_PROJECT_OWNER})
        self.developer = get_user_model().objects.create_user(
            'developer', 'developer@example.com', 'secret', **{'type': USER_TYPE_DEVELOPER})
        self.project_manager = get_user_model().objects.create_user(
            'project_manager', 'pm@example.com', 'secret', **{'type': USER_TYPE_PROJECT_MANAGER})
        self.admin = get_user_model().objects.create_superuser('admin', 'admin@example.com', 'secret')

        self.factory = RequestFactory()

    def __process_jobs(self):
        get_worker().work(burst=True)

    def test_create_task(self):
        """
        Only project owners and admins can create tasks
        """
        url = reverse('task-list')
        data_outer = {'first_name': 'David', 'last_name': 'Semakula', 'email': 'guest@example.com', 'type': TASK_TYPE_WEB}
        data_inner = {'title': 'Task 1', 'skills': 'Django, React.js', 'type': TASK_TYPE_WEB, 'scope': TASK_SCOPE_TASK}

        # Guests can fill the wizard
        self.client.force_authenticate(user=None)
        response = self.client.post(url, data_outer)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Developer's can't create tasks
        self.client.force_authenticate(user=self.developer)
        response = self.client.post(url, data_inner)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admins can create tasks
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, data_inner)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # PMs can create tasks
        self.client.force_authenticate(user=self.project_manager)
        response = self.client.post(url, data_inner)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Clients can create tasks
        self.client.force_authenticate(user=self.project_owner)
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
        data_inner['title'] = 'Task 4'
        data_inner['milestones'] = [{'due_at': datetime.datetime.now(), 'title': 'Milestone 1', 'description': 'Do some stuff'}]
        response = self.client.post(url, data_inner)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['milestones']), 1)
        self.assertEqual(response.data['milestones'][0]['title'], 'Milestone 1')

    def test_update_task(self):
        """
        Only the task creator or admin can update tasks
        """
        task = Task.objects.create(
            **{'title': 'Task 1', 'skills': 'Django, React.js', 'fee': 15, 'user': self.project_owner}
        )

        url = reverse('task-detail', args=[task.id])
        data = {'title': 'Task 1 Edit', 'fee': 20}

        # Guests can't edit tasks
        self.client.force_authenticate(user=None)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Devs can't edit tasks
        self.client.force_authenticate(user=self.developer)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Admins can edit tasks
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Clients can edit tasks
        self.client.force_authenticate(user=self.project_owner)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Clients can invite developers tasks
        participation_data = {'participation': [{'user': self.developer.id}]}
        response = self.client.patch(url, participation_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['participation']), 1)
        self.assertEqual(response.data['participation'][0]['user'], self.developer.id)

        # Clients can create milestones for tasks
        milestone_data = {
            'milestones': [
                {'due_at': datetime.datetime.now(), 'title': 'Milestone 1', 'description': 'Do some stuff'}
            ]
        }
        response = self.client.patch(url, milestone_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['milestones']), 1)
        self.assertEqual(response.data['milestones'][0]['title'], 'Milestone 1')

        self.client.force_authenticate(user=self.developer)
        # Dev accepting task invitations
        response = self.client.patch(
            url, {'participation': [{'user': self.developer.id, 'status': STATUS_ACCEPTED}]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['participation']), 1)
        self.assertEqual(response.data['participation'][0]['user'], self.developer.id)
        self.assertTrue(response.data['participation'][0]['status'] == STATUS_ACCEPTED)

        # Dev rejecting task invitations
        response = self.client.patch(
            url, {'participation': [{'user': self.developer.id, 'status': STATUS_REJECTED}]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['details']['participation']), 1)
        self.assertEqual(response.data['details']['participation'][0]['user']['id'], self.developer.id)
        self.assertFalse(response.data['details']['participation'][0]['status'] == STATUS_REJECTED)

        task.user = self.admin
        task.save()

        # Client's can't reduce the task fee
        data = {'title': 'Task 1 Edit 2', 'fee': 15}
        self.client.force_authenticate(user=self.project_owner)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def tearDown(self):
        self.__process_jobs()
