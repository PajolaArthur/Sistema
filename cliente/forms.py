from django import forms
from .models import Cliente, Municipio, UF

class ClienteForm(forms.ModelForm):
    uf = forms.ModelChoiceField(
        queryset=UF.objects.all().order_by('nome'),
        required=True,
        label='Estado (UF)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Cliente
        exclude = ['criado_por', 'excluido_por', 'excluido_em', 'criado_em', 'atualizado_em']
        widgets = {
            'nome_razao': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'ie_rg': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Inicializa queryset do UF (já definido acima)
        # Inicializa queryset de municipios vazio por padrão
        self.fields['municipio'].queryset = Municipio.objects.none()
        self.fields['municipio'].widget.attrs.update({'class': 'form-select'})

        # Se houver dados POST, carrega municípios conforme UF
        if 'uf' in self.data:
            try:
                uf_id = int(self.data.get('uf'))
                self.fields['municipio'].queryset = Municipio.objects.filter(uf_id=uf_id).order_by('nome')
            except (ValueError, TypeError):
                self.fields['municipio'].queryset = Municipio.objects.none()

        # Se instancia já existir (edição), popula uf e municípios correspondentes
        elif self.instance.pk:
            self.fields['uf'].initial = self.instance.uf
            self.fields['municipio'].queryset = Municipio.objects.filter(uf=self.instance.uf).order_by('nome')
            self.fields['municipio'].initial = self.instance.municipio

    def clean(self):
        cleaned_data = super().clean()
        uf = cleaned_data.get('uf')
        municipio = cleaned_data.get('municipio')

        # Validação para garantir município dentro do UF selecionado
        if uf and municipio and municipio.uf != uf:
            self.add_error('municipio', 'O município não pertence ao estado (UF) selecionado.')
