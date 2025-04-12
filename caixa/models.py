from django.db import models
from django.contrib.auth.models import User

class Caixa(models.Model):
    abertura_caixa = models.DateTimeField()
    fechamento_caixa = models.DateTimeField(null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Caixa aberto por {self.usuario} em {self.abertura_caixa.strftime('%d/%m/%Y %H:%M')}"


class Movimento(models.Model):
    TIPO_MOVIMENTO = (
        ('S', 'Suprimento'),
        ('E', 'Sangria'),
    )

    FORMAS_PAGAMENTO = (
        ('DNH', 'DINHEIRO'),
        ('PIX', 'PIX'),
        ('CRC', 'CARTÃO DE CRÉDITO'),
        ('CRD', 'CARTÃO DE DÉBITO'),
        ('CHA', 'CHEQUE PRÉ'),
        ('CHP', 'CHEQUE PÓS'),
    )

    caixa = models.ForeignKey(Caixa, on_delete=models.CASCADE, related_name='movimentos')
    observacao = models.CharField(max_length=60)
    tipo = models.CharField(max_length=1, choices=TIPO_MOVIMENTO)
    forma = models.CharField(max_length=3, choices=FORMAS_PAGAMENTO, null=True, blank=True)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor} em {self.get_forma_display()} ({self.criado_em.strftime('%d/%m/%Y %H:%M')})"
