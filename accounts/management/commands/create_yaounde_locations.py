"""
Management command to create Yaoundé coverage areas and streets
"""
from django.core.management.base import BaseCommand
from accounts.location_models import CoverageArea, Street


class Command(BaseCommand):
    help = 'Creates Yaoundé coverage areas and streets/neighborhoods'

    def handle(self, *args, **options):
        """Create coverage areas and streets."""
        
        # Define all coverage areas and their streets
        coverage_data = {
            'YAOUNDE_1': {
                'name': 'Yaoundé 1',
                'streets': [
                    'Centre Commercial', 'Elig Essono', 'Etoa Meki 1', 'Etoa Meki 2',
                    'Nlongkak', 'Elig Edzoa', 'Bastos', 'Manguier', 'Tongolo',
                    'Mballa 1', 'Mballa 2', 'Mballa 3', 'Nkolondom', 'Etoudi',
                    'Messassi', 'Okolo', 'Olembe', 'Nyom', 'Emana', 'Nkoleton'
                ]
            },
            'YAOUNDE_2': {
                'name': 'Yaoundé 2',
                'streets': [
                    'Cité Verte', 'Madagascar', 'Mokolo', 'Grand Messa', 'Ekoudou',
                    'Tsinga', 'Nkomkana', 'Oliga', 'Messa Carrière', 'Febe', 'Ntoungou'
                ]
            },
            'YAOUNDE_3': {
                'name': 'Yaoundé 3',
                'streets': [
                    'Obili', 'Ngoaekele 1', 'Nlong Mvolye', 'Ahala 1', 'Ahala 2',
                    'Efoulan', 'Obobogo', 'Nsam', 'Melen 2', 'Etoa', 'Nkolmesseng 1',
                    'Afanoya 1', 'Afanoya 2', 'Afanoya 3', 'Afanoya 4', 'Nkolfon',
                    'Mekoumbou 1', 'Mekoumbou 2', 'Ntouessong', 'Nsimeyong 1',
                    'Nsimeyong 2', 'Nsimeyong 3', 'Olezoa', 'Dakar', 'Ngoaekele 2'
                ]
            },
            'YAOUNDE_4': {
                'name': 'Yaoundé 4',
                'streets': [
                    'Mvogada', 'Mvogmbi', 'Mimboman', 'Kondengui', 'Nkolndongo',
                    'Emombo', 'Nkolebogo', 'Quartier Fouda', 'Etambafia', 'Nkolbikok'
                ]
            },
            'YAOUNDE_5': {
                'name': 'Yaoundé 5',
                'streets': [
                    'Biyemassi', 'Essos', 'Nkolbisson', 'Nkolebogo 2', 'Mvogbetsi',
                    'Mvogatsa', 'Nkolmesseng 2', 'Etougebe'
                ]
            },
            'YAOUNDE_6': {
                'name': 'Yaoundé 6',
                'streets': [
                    'Mvogada 2', 'Mvogbetsi 2', 'Nkolbisson 2', 'Nkoleton 2'
                ]
            },
            'YAOUNDE_7': {
                'name': 'Yaoundé 7',
                'streets': [
                    'Nkolbisson 3', 'Nkolebogo 4', 'Mvogbetsi 3', 'Mvogatsa 2', 'Nkoleton 3'
                ]
            },
        }
        
        total_areas = 0
        total_streets = 0
        
        for code, data in coverage_data.items():
            # Create or get coverage area
            area, created = CoverageArea.objects.get_or_create(
                code=code,
                defaults={'name': data['name']}
            )
            if created:
                total_areas += 1
                self.stdout.write(self.style.SUCCESS(f'Created coverage area: {data["name"]}'))
            else:
                self.stdout.write(self.style.WARNING(f'Coverage area already exists: {data["name"]}'))
            
            # Create streets for this area
            for street_name in data['streets']:
                street, created = Street.objects.get_or_create(
                    name=street_name,
                    coverage_area=area,
                    defaults={}
                )
                if created:
                    total_streets += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully processed {len(coverage_data)} coverage areas and {total_streets} streets. '
                f'{total_areas} new areas created.'
            )
        )


