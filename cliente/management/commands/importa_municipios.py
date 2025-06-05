import requests
from django.core.management.base import BaseCommand
from cliente.models import UF, Municipio


class Command(BaseCommand):
    help = 'Importa ou atualiza UFs e Municípios do IBGE'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🔸 Iniciando importação de UFs...'))

        # Importa UFs
        uf_url = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados'
        ufs = requests.get(uf_url).json()

        for uf_data in ufs:
            uf, created = UF.objects.update_or_create(
                sigla=uf_data['sigla'],
                defaults={
                    'nome': uf_data['nome'],
                    'ibge_id': uf_data['id'],
                }
            )
            status = '✅ Criado' if created else '♻️ Atualizado'
            self.stdout.write(self.style.SUCCESS(f'{status} UF: {uf.nome} ({uf.sigla})'))

        self.stdout.write(self.style.WARNING('🔸 Importando Municípios...'))

        # Para cada UF, importa seus municípios corretamente
        for uf in UF.objects.all():
            municipios_url = f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf.ibge_id}/municipios'
            response = requests.get(municipios_url)

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'❌ Erro ao buscar municípios de {uf.sigla}'))
                continue

            municipios = response.json()

            for municipio_data in municipios:
                municipio, created = Municipio.objects.update_or_create(
                    nome=municipio_data['nome'],
                    uf=uf
                )
                status = '✅ Criado' if created else '♻️ Atualizado'
                self.stdout.write(self.style.SUCCESS(
                    f'{status} Município: {municipio.nome} - {uf.sigla}'
                ))

        self.stdout.write(self.style.SUCCESS('🎉 Importação concluída com sucesso!'))
