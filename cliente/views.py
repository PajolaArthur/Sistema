from django.views.generic import ListView
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView
from .forms import ClienteForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Municipio, UF, Cliente
from django.utils import timezone

@method_decorator(login_required, name='dispatch')
class ClienteListView(ListView):
    model = Cliente
    template_name = 'cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 20

    def get_queryset(self):
        queryset = Cliente.objects.filter(excluido_em__isnull=True)

        filtro_geral = self.request.GET.get('q', '')
        nome_razao = self.request.GET.get('nome_razao', '')
        tipo_pessoa = self.request.GET.get('tipo_pessoa', '')
        cpf_cnpj = self.request.GET.get('cpf_cnpj', '')
        cidade = self.request.GET.get('cidade', '')
        uf = self.request.GET.get('uf', '')

        # Checkbox "Mostrar inativos"
        mostrar_inativos = self.request.GET.get('mostrar_inativos', '')

        # 🔸 Filtros dinâmicos
        if filtro_geral:
            queryset = queryset.filter(nome_razao__icontains=filtro_geral)

        if nome_razao:
            queryset = queryset.filter(nome_razao__icontains=nome_razao)

        if tipo_pessoa:
            queryset = queryset.filter(tipo_pessoa=tipo_pessoa)

        if cpf_cnpj:
            queryset = queryset.filter(cpf_cnpj__icontains=cpf_cnpj)

        if cidade:
            queryset = queryset.filter(municipio__nome__icontains=cidade)

        if uf:
            queryset = queryset.filter(municipio__uf__sigla__iexact=uf)

        # 🔸 Filtrar ativos por padrão (se checkbox não marcado)
        if not mostrar_inativos:
            queryset = queryset.filter(ativo=True)

        return queryset.order_by('nome_razao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['filtro_geral'] = self.request.GET.get('q', '')
        context['nome_razao'] = self.request.GET.get('nome_razao', '')
        context['tipo_pessoa'] = self.request.GET.get('tipo_pessoa', '')
        context['cpf_cnpj'] = self.request.GET.get('cpf_cnpj', '')
        context['cidade'] = self.request.GET.get('cidade', '')
        context['uf'] = self.request.GET.get('uf', '')
        context['mostrar_inativos'] = self.request.GET.get('mostrar_inativos', '')

        context['municipios_com_clientes'] = (
            Cliente.objects
            .filter(municipio__isnull=False, excluido_em__isnull=True)
            .values('municipio__id', 'municipio__nome', 'municipio__uf__sigla')
            .distinct()
            .order_by('municipio__nome')
        )

        context['ufs_com_clientes'] = (
            Cliente.objects
            .filter(municipio__uf__isnull=False, excluido_em__isnull=True)
            .values('municipio__uf__sigla')
            .distinct()
            .order_by('municipio__uf__sigla')
        )

        return context





@method_decorator(login_required, name='dispatch')
class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente_edit.html'
    success_url = reverse_lazy('cliente-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ufs'] = UF.objects.all().order_by('nome')
        return context

    def form_valid(self, form):
        form.instance.alterado_por = self.request.user
        form.instance.atualizado_em = timezone.now()
        return super().form_valid(form)

    
@method_decorator(login_required, name='dispatch')
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente_create.html'
    success_url = reverse_lazy('cliente-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ufs'] = UF.objects.all().order_by('nome')
        context['titulo'] = 'Novo Cliente'  # Padrão extra
        return context

    def form_valid(self, form):
        form.instance.ativo = True
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        print("❌ Formulário INVÁLIDO")
        print("POST recebido:", self.request.POST)
        print("Erros do form:", form.errors)
        return super().form_invalid(form)


def carregar_municipios(request):
    uf_id = request.GET.get('uf')
    municipios = Municipio.objects.filter(uf_id=uf_id).order_by('nome')
    municipios_list = [{'id': m.id, 'nome': m.nome} for m in municipios]
    return JsonResponse({'municipios': municipios_list})



@method_decorator(login_required, name='dispatch')
class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'cliente_delete.html'
    success_url = reverse_lazy('cliente-list')

    def get_queryset(self):
        return Cliente.objects.all()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.warning(request, "Você não tem permissão para excluir permanentemente um cliente.")
            return redirect('cliente-list')
        return super().dispatch(request, *args, **kwargs)

    

@login_required
def cliente_excluir(request, pk):
    if not request.user.is_staff:
        messages.warning(request, "Você não tem permissão para excluir clientes!")
        return redirect('cliente-list')
    
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if cliente.excluido_em is None:
        cliente.excluido_por = request.user
        cliente.excluido_em = timezone.now()
        cliente.save()
        messages.success(request, f"Cliente '{cliente.nome_razao}' foi excluído com sucesso.")
    else:
        messages.warning(request, f"Cliente '{cliente.nome_razao}' já estava excluído.")
    
    return redirect('cliente-list')
