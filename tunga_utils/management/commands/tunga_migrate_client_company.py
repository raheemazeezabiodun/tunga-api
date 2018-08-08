from django.core.management.base import BaseCommand

from tunga_auth.models import TungaUser
from tunga_profiles.models import Company
from tunga_utils.constants import USER_TYPE_PROJECT_OWNER


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Fix payment rates based on task status
        """
        # command to run: python manage.py tunga_migrate_client_company

        clients = TungaUser.objects.filter(type=USER_TYPE_PROJECT_OWNER)
        for client in clients:
            if client.profile and not client.company:
                print('client: ', client.id, client.display_name)

                field_map = [
                    ['name', 'company'],
                    ['bio', 'company_bio'],
                    ['website', 'website'],
                    ['vat_number', 'vat_number'],
                    ['reg_no', 'company_reg_no'],
                    ['ref_no', 'reference_number'],
                    ['street', 'street'],
                    ['plot_number', 'plot_number'],
                    ['postal_code', 'postal_code'],
                    ['postal_address', 'postal_address'],
                    ['tel_number', 'phone_number']
                ]

                str_field_map = [
                    ['skills', 'skills'],
                    ['city', 'city'],
                ]

                company = Company(user=client)

                for item in field_map:
                    field_value = getattr(client.profile, item[1], None)
                    if field_value:
                        setattr(company, item[0], field_value)

                if client.profile.country:
                    setattr(company, 'country', client.profile.country.code)

                for item in str_field_map:
                    field_value = str(getattr(client.profile, item[1], None))
                    if field_value:
                        setattr(company, item[0], field_value)

                company.save()
