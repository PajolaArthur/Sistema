from django.db import models
from django.contrib.auth.models import User


class Formapagamento(models.Model):
    forma = models.CharField(max_length=50, unique=True)
    sigla = models.CharField(max_length=10, unique=True)
    icone = models.CharField(max_length=10, blank=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    excluido_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='formapagamento_excluidas')
    excluido_em = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.forma}"


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


    caixa = models.ForeignKey(Caixa, on_delete=models.CASCADE, related_name='movimentos')
    observacao = models.CharField(max_length=60)
    tipo = models.CharField(max_length=1, choices=TIPO_MOVIMENTO)
    forma = models.ForeignKey(Formapagamento, on_delete=models.SET_NULL, null=True, blank=True)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - R$ {self.valor} em {self.get_forma_display()} ({self.criado_em.strftime('%d/%m/%Y %H:%M')})"
