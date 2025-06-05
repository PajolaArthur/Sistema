from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import CreateView
from .models import Compra
from .forms import CompraForm
from .forms import CompraFormCreate
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
import datetime
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Fabricante
from .forms import FabricanteForm
from .models import Categoria
from .forms import CategoriaForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

@method_decorator(login_required, name="dispatch")
class CompraListView(ListView):
    model = Compra
    template_name = 'compra/compra_list.html'
    paginate_by = 10
    context_object_name = 'compras'

    def get_queryset(self):
        queryset = super().get_queryset().filter(excluido_em__isnull=True)
        filtros = Q()

        # Parâmetros
        compras = self.request.GET.get('q', '').strip()
        codigoproduto = self.request.GET.get('codigoproduto', '').strip()
        situacao = self.request.GET.get('situacao', '')
        fabricante = self.request.GET.get('fabricante', '').strip()
        categoria = self.request.GET.get('categoria', '')
        data_inicial = self.request.GET.get('data_inicial')
        data_final = self.request.GET.get('data_final')

        # Filtro geral (busca livre)
        if compras:
            filtros &= (
                Q(descricao_produto__icontains=compras) |
                Q(codigo_produto__icontains=compras) |
                Q(fabricante_produto__nome__icontains=compras) |
                Q(categoria_produto__icontains=compras) |
                Q(situacao__icontains=compras)
            )

        if codigoproduto:
            filtros &= Q(codigo_produto__icontains=codigoproduto)

        if situacao:
            filtros &= Q(situacao=situacao)

        if categoria:
            filtros &= Q(categoria_produto=categoria)

        if fabricante:
            queryset = queryset.filter(fabricante_produto__id=fabricante)

        try:
            if data_inicial:
                data_ini = datetime.datetime.strptime(data_inicial, '%Y-%m-%d').date()
                filtros &= Q(criado_em__date__gte=data_ini)
            if data_final:
                data_fim = datetime.datetime.strptime(data_final, '%Y-%m-%d').date()
                filtros &= Q(criado_em__date__lte=data_fim)
        except ValueError:
            pass

        return queryset.filter(filtros).order_by('-criado_em')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['status_choices'] = Compra.COMPRA_STATUS
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        context['fabricantes'] = Fabricante.objects.filter(excluido_em__isnull=True).order_by('nome')
        context['categorias'] = Categoria.objects.filter(excluido_em__isnull=True).order_by('nome')  # ✅ Adicione esta linha
        context['compra'] = Compra  # Para acessar enums no template
        return context

@method_decorator(login_required, name='dispatch')   
class CompraUpdateView(UpdateView):
    model = Compra
    form_class = CompraForm
    template_name = 'compra/compra_edit.html'
    success_url = reverse_lazy('compra-list')
    def form_valid(self,form):
        #adicionar lógica no que o usuário escreveu no formulário
        return super().form_valid(form)

   
@method_decorator(login_required, name='dispatch')
class CompraDeleteView(DeleteView):
    model = Compra
    template_name = 'compra/compra_delete.html'
    success_url = reverse_lazy('compra-list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.warning(request, "Você não tem permissão para excluir permanentemente uma solicitação de compra.")
            return redirect('compra-list')
        return super().dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class CompraCreateView(CreateView):
    model = Compra
    form_class = CompraFormCreate
    template_name = 'compra/compra_create.html'
    success_url = reverse_lazy('compra-list')
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)

@login_required
def aprovar_compra(request, pk):
    if not request.user.is_staff:
        messages.warning(request, "Você não tem permissão para aprovar as solicitações de compras!")
        return redirect('caixa')
    compra = get_object_or_404(Compra, pk=pk)
    compra.situacao = 'A'  # 'A' de Aprovado
    compra.save()
    return redirect('compra-list')  # redireciona de volta para a listagem

@login_required
def recusar_compra(request, pk):
    if not request.user.is_staff:
        messages.warning(request, "Você não tem permissão para recusar as solicitações de compras!")
        return redirect('caixa')
    compra = get_object_or_404(Compra, pk=pk)
    compra.situacao = 'R'  # 'R' de Recusado
    compra.save()
    return redirect('compra-list')  # redireciona de volta para a listagem

@login_required
def compra_excluir(request, pk):
    if not request.user.is_staff:
        messages.warning(request, "Você não tem permissão para excluir solicitações de compras!")
        return redirect('compra-list')
    compra = get_object_or_404(Compra, pk=pk)
    compra.excluido_por = request.user
    compra.excluido_em = timezone.now()
    compra.save()
    return redirect('compra-list')


@login_required
def gerar_pdf_compras(request):
    queryset = Compra.objects.filter(excluido_em__isnull=True)
    filtros = Q()

    compras = request.GET.get('q', '').strip()
    codigoproduto = request.GET.get('codigoproduto', '').strip()
    situacao = request.GET.get('situacao', '')
    fabricante = request.GET.get('fabricante', '').strip()
    categoria = request.GET.get('categoria', '')
    data_inicial = request.GET.get('data_inicial')
    data_final = request.GET.get('data_final')

    if compras:
        filtros &= (
            Q(descricao_produto__icontains=compras) |
            Q(codigo_produto__icontains=compras) |
            Q(fabricante_produto__nome__icontains=compras) |
            Q(categoria_produto__nome__icontains=compras) |
            Q(situacao__icontains=compras)
        )
    if codigoproduto:
        filtros &= Q(codigo_produto__icontains=codigoproduto)
    if situacao:
        filtros &= Q(situacao=situacao)
    if categoria:
        filtros &= Q(categoria_produto=categoria)
    if fabricante:
        queryset = queryset.filter(fabricante_produto__id=fabricante)
    try:
        if data_inicial:
            data_ini = datetime.datetime.strptime(data_inicial, '%Y-%m-%d').date()
            filtros &= Q(criado_em__date__gte=data_ini)
        if data_final:
            data_fim = datetime.datetime.strptime(data_final, '%Y-%m-%d').date()
            filtros &= Q(criado_em__date__lte=data_fim)
    except ValueError:
        pass

    compras_filtradas = queryset.filter(filtros).order_by('-criado_em')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio_compras.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elementos = []

    styles = getSampleStyleSheet()
    titulo = Paragraph("Relatório de Compras", styles['Heading1'])
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))

    dados = [['Código', 'Descrição', 'Fabricante', 'Categoria', 'Situação', 'Data']]

    for compra in compras_filtradas:
        dados.append([
            compra.codigo_produto,
            compra.descricao_produto,
            compra.fabricante_produto.sigla if compra.fabricante_produto else '',
            compra.categoria_produto.nome if compra.categoria_produto else '',
            compra.get_situacao_display(),
            compra.criado_em.strftime('%d/%m/%Y'),
        ])

    tabela = Table(dados, repeatRows=1)

    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
    ])

    # Cores alternadas nas linhas (zebra)
    for i in range(1, len(dados)):
        if i % 2 == 0:
            estilo.add('BACKGROUND', (0, i), (-1, i), colors.whitesmoke)
        else:
            estilo.add('BACKGROUND', (0, i), (-1, i), colors.lightgrey)

    # Cores para a coluna 'Situação' (coluna 4 → índice 4)
    for i, linha in enumerate(dados[1:], start=1):
        situacao = linha[4].lower()
        if situacao == 'pendente':
            cor = colors.HexColor("#4da6ff")  # Azul
        elif situacao == 'aprovado':
            cor = colors.HexColor("#66cc66")  # Verde
        elif situacao == 'cancelado':
            cor = colors.HexColor("#ff6666")  # Vermelho
        elif situacao == 'concluído':
            cor = colors.HexColor("#ffcc66")  # Amarelo
        else:
            cor = colors.white

        estilo.add('BACKGROUND', (4, i), (4, i), cor)

    tabela.setStyle(estilo)
    elementos.append(tabela)

    doc.build(elementos)
    return response


# FABRICANTE
@method_decorator(login_required, name="dispatch")
class FabricanteListView(ListView):
    model = Fabricante
    template_name = 'fabricante/fabricante_list.html'
    context_object_name = 'fabricantes'
    paginate_by = 10

    def get_queryset(self):
        queryset = Fabricante.objects.filter(excluido_em__isnull=True).order_by('nome')

        busca_nome = self.request.GET.get('busca_nome')
        busca_sigla = self.request.GET.get('busca_sigla')

        if busca_nome:
            queryset = queryset.filter(nome__icontains=busca_nome)

        if busca_sigla:
            queryset = queryset.filter(sigla__icontains=busca_sigla)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busca_nome'] = self.request.GET.get('busca_nome') or ''
        context['busca_sigla'] = self.request.GET.get('busca_sigla') or ''
        return context


@method_decorator(login_required, name="dispatch")
class FabricanteCreateView(CreateView):
    model = Fabricante
    form_class = FabricanteForm
    template_name = 'fabricante/fabricante_form.html'
    success_url = reverse_lazy('fabricante-list')
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)
    

@method_decorator(login_required, name="dispatch")
class FabricanteUpdateView(UpdateView):
    model = Fabricante
    form_class = FabricanteForm
    template_name = 'fabricante/fabricante_form.html'
    success_url = reverse_lazy('fabricante-list')
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.warning(request, "Você não tem permissão para excluir um fabricante.")
            return redirect('fabricante-list')
        return super().dispatch(request, *args, **kwargs)
    
@login_required
def excluir_fabricante(request, pk):
    if not request.user.is_staff:
        messages.warning(request, "Você não tem permissão para excluir fabricantes!")
        return redirect('fabricante-list')
    fabricante = get_object_or_404(Fabricante, pk=pk, excluido_em__isnull=True)
    fabricante.excluido_por = request.user
    fabricante.excluido_em = timezone.now()
    fabricante.save()
    messages.success(request, "Fabricante excluído com sucesso.")
    return redirect('fabricante-list')

# CATEGORIA
@method_decorator(login_required, name="dispatch")
class CategoriaListView(ListView):
    model = Categoria
    template_name = 'categoria/categoria_list.html'
    context_object_name = 'categorias'
    paginate_by = 10

    def get_queryset(self):
        queryset = Categoria.objects.filter(excluido_em__isnull=True).order_by('nome')

        busca_nome = self.request.GET.get('busca_nome')
        busca_sigla = self.request.GET.get('busca_sigla')

        if busca_nome:
            queryset = queryset.filter(nome__icontains=busca_nome)

        if busca_sigla:
            queryset = queryset.filter(sigla__icontains=busca_sigla)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busca_nome'] = self.request.GET.get('busca_nome') or ''
        context['busca_sigla'] = self.request.GET.get('busca_sigla') or ''
        return context


    
@method_decorator(login_required, name="dispatch")
class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categoria/categoria_form.html'
    success_url = reverse_lazy('categoria-list')
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)
    

@method_decorator(login_required, name="dispatch")
class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categoria/categoria_form.html'
    success_url = reverse_lazy('categoria-list')
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.warning(request, "Você não tem permissão para excluir uma categoria.")
            return redirect('categoria-list')
        return super().dispatch(request, *args, **kwargs)
    
@login_required
def excluir_categoria(request, pk):
    if not request.user.is_staff:
        messages.warning(request, "Você não tem permissão para excluir categorias!")
        return redirect('categoria-list')
    categoria = get_object_or_404(Categoria, pk=pk, excluido_em__isnull=True)
    categoria.excluido_por = request.user
    categoria.excluido_em = timezone.now()
    categoria.save()
    messages.success(request, "Categoria excluída com sucesso.")
    return redirect('categoria-list')