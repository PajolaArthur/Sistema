from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import make_aware, datetime
from decimal import Decimal, InvalidOperation
from django.utils.decorators import method_decorator
from .models import Movimento, Caixa
from django.views.generic import ListView
from django.db.models import Sum, Case, When, DecimalField, Value as V
from django.db.models.functions import Coalesce
from collections import defaultdict
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.contrib.auth.decorators import login_required
import pprint
from io import BytesIO
from xhtml2pdf import pisa
from datetime import datetime
from .models import Caixa, Movimento
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.shortcuts import render
from .models import Movimento
from .forms import MovimentoConsultaForm
from django.db.models import Sum
from django.contrib.auth.models import User
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Formapagamento
from .forms import FormapagamentoForm
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import CreateView

from caixa.models import Movimento, Caixa, Formapagamento
from django.utils.timezone import localdate, make_aware
from datetime import datetime

@method_decorator(login_required, name="dispatch")
class MovimentoListView(ListView):
    model = Movimento
    template_name = 'caixa/caixa.html'
    paginate_by = 10
    context_object_name = 'movimentos'

    def get_queryset(self):
        filtros = Q()
        movimentos = self.request.GET.get('q', '').strip()
        tipo = self.request.GET.get('tipo', '')
        forma = self.request.GET.get('forma', '').strip()
    
        caixa = Caixa.objects.filter(usuario=self.request.user, fechamento_caixa__isnull=True).first()
        if not caixa:
            return Movimento.objects.none()

        queryset = super().get_queryset().filter(caixa=caixa)

        if movimentos:
            filtros &= (
                Q(observacao__icontains=movimentos) |
                Q(tipo__icontains=movimentos) |
                Q(forma__forma__icontains=movimentos) |
                Q(forma__sigla__icontains=movimentos)
            )

        if tipo:
            filtros &= Q(tipo=tipo)

        if forma:
            filtros &= Q(forma=forma)

        return queryset.filter(filtros)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Listas para filtros no template
        context['tipo_selecionado'] = Movimento.TIPO_MOVIMENTO
        context['forma_selecionada'] = Formapagamento.objects.all()

        # Manter os filtros preenchidos após submissão
        context['tipo'] = self.request.GET.get('tipo', '')
        context['forma'] = self.request.GET.get('forma', '')

        hoje = localdate()
        inicio_dia = make_aware(datetime.combine(hoje, datetime.min.time()))
        fim_dia = make_aware(datetime.combine(hoje, datetime.max.time()))

        caixa = Caixa.objects.filter(
            usuario=self.request.user,
            abertura_caixa__gte=inicio_dia,
            abertura_caixa__lte=fim_dia,
            fechamento_caixa__isnull=True
        ).first()

        movimentos = self.get_queryset().filter(caixa=caixa) if caixa else []

        total_suprimentos = sum(m.valor for m in movimentos if m.tipo == 'S')
        total_sangrias = sum(m.valor for m in movimentos if m.tipo == 'E')
        saldo = total_suprimentos - total_sangrias

        context['total_suprimentos'] = total_suprimentos
        context['total_sangrias'] = total_sangrias
        context['saldo'] = saldo
        context['caixa_aberto'] = caixa
        context['forma_selecionada'] = [(f.id, f.forma) for f in Formapagamento.objects.all()
]

        return context



@login_required
def abrir_caixa(request):
    hoje = timezone.localdate()  # Mais seguro que timezone.now().date()
    inicio_dia = timezone.make_aware(datetime.combine(hoje, datetime.min.time()))
    fim_dia = timezone.make_aware(datetime.combine(hoje, datetime.max.time()))

    caixa = Caixa.objects.filter(
        usuario=request.user,
        abertura_caixa__gte=inicio_dia,
        abertura_caixa__lte=fim_dia,
        fechamento_caixa__isnull=True
    ).first()

    if caixa:
        messages.warning(request, "Você já possui um caixa aberto!")
        return redirect('caixa')

    if request.method == 'POST':
        Caixa.objects.create(
            abertura_caixa=timezone.now(),
            usuario=request.user
        )
        messages.success(request, "Caixa aberto com sucesso!")
        return redirect('caixa')

    return render(request, 'caixa/caixa_abrir.html')

@login_required
def fechar_caixa(request):
    hoje = timezone.localdate()
    inicio_dia = timezone.make_aware(datetime.combine(hoje, datetime.min.time()))
    fim_dia = timezone.make_aware(datetime.combine(hoje, datetime.max.time()))

    caixa = Caixa.objects.filter(
        usuario=request.user,
        abertura_caixa__gte=inicio_dia,
        abertura_caixa__lte=fim_dia,
        fechamento_caixa__isnull=True
    ).first()

    if not caixa:
        messages.warning(request, "Você não abriu caixa para realizar o fechamento!")
        return redirect('caixa')

    movimentos = caixa.movimentos.all()
    totais_por_forma = movimentos.values('forma', 'tipo').annotate(total=Sum('valor'))

    formas_agrupadas = defaultdict(lambda: {'suprimento': 0, 'sangria': 0, 'saldo': 0})
    for item in totais_por_forma:
        forma_id = item['forma']
        tipo = item['tipo']
        valor = item['total']

        if tipo == 'S':
            formas_agrupadas[forma_id]['suprimento'] += valor
        elif tipo == 'E':
            formas_agrupadas[forma_id]['sangria'] += valor

    for valores in formas_agrupadas.values():
        valores['saldo'] = valores['suprimento'] - valores['sangria']

    # Obter objetos Formapagamento com os IDs usados
    ids_formas = formas_agrupadas.keys()
    formas_objetos = Formapagamento.objects.filter(id__in=ids_formas)
    mapa_formas = {fp.id: fp for fp in formas_objetos}

    if request.method == 'POST':
        caixa.fechamento_caixa = timezone.now()
        caixa.save()
        messages.success(request, "Caixa fechado com sucesso!")
        return redirect('caixa')

    return render(request, 'caixa/caixa_fechar.html', {
        'caixa': caixa,
        'formas_agrupadas': dict(formas_agrupadas),
        'mapa_formas': mapa_formas,  # dicionário de ID → objeto
    })


@login_required
def fechar_caixa_pdf(request):
    hoje = timezone.localdate()
    inicio_dia = timezone.make_aware(datetime.combine(hoje, datetime.min.time()))
    fim_dia = timezone.make_aware(datetime.combine(hoje, datetime.max.time()))

    caixa = Caixa.objects.filter(
        usuario=request.user,
        abertura_caixa__gte=inicio_dia,
        abertura_caixa__lte=fim_dia,
        fechamento_caixa__isnull=True
    ).first()

    if not caixa:
        return HttpResponse("Nenhum caixa aberto.", status=400)

    movimentos = caixa.movimentos.all()

    formas_agrupadas = defaultdict(lambda: {
        "suprimento": Decimal("0.00"),
        "sangria": Decimal("0.00"),
        "saldo": Decimal("0.00"),
    })

    for m in movimentos:
        forma_id = m.forma_id  # acessa diretamente o ID da FK
        if m.tipo == 'S':
            formas_agrupadas[forma_id]["suprimento"] += m.valor
        elif m.tipo == 'E':
            formas_agrupadas[forma_id]["sangria"] += m.valor
        formas_agrupadas[forma_id]["saldo"] = (
            formas_agrupadas[forma_id]["suprimento"] - formas_agrupadas[forma_id]["sangria"]
        )

    # Dicionário com objetos Formapagamento
    mapa_formas = {
        fp.id: fp for fp in Formapagamento.objects.filter(id__in=formas_agrupadas.keys())
    }

    # Renderizar HTML
    template = get_template("caixa/caixa_fechamento_pdf.html")
    html = template.render({
        "caixa": caixa,
        "formas_agrupadas": dict(formas_agrupadas),
        "mapa_formas": mapa_formas,
        "usuario": request.user,
        "data_hoje": hoje,
    })

    # Gerar PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="fechamento_caixa.pdf"'
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF", status=500)

    response.write(result.getvalue())
    return response


@login_required
def lancar_movimento(request):
    formas_pagamento = Formapagamento.objects.all()

    hoje = timezone.localdate()
    inicio_dia = timezone.make_aware(datetime.combine(hoje, datetime.min.time()))
    fim_dia = timezone.make_aware(datetime.combine(hoje, datetime.max.time()))

    caixa = Caixa.objects.filter(
        usuario=request.user,
        abertura_caixa__gte=inicio_dia,
        abertura_caixa__lte=fim_dia,
        fechamento_caixa__isnull=True
    ).first()

    if not caixa:
        messages.warning(request, "Você não abriu caixa para realizar o lançamento!")
        return redirect('caixa')

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        forma_id = request.POST.get('forma')
        observacao = request.POST.get('observacao', '').strip()
        valor_str = request.POST.get('valor', '').strip()

        # Validação da forma de pagamento
        try:
            forma_obj = Formapagamento.objects.get(id=forma_id)
        except Formapagamento.DoesNotExist:
            messages.error(request, "Forma de pagamento inválida.")
            return render(request, 'caixa/caixa_lancamento.html', {'formas': formas_pagamento})

        # Validação do valor
        try:
            valor_limpo = valor_str.replace('.', '').replace(',', '.')
            valor = Decimal(valor_limpo)
        except (InvalidOperation, ValueError):
            messages.error(request, "Valor inválido. Use o formato 1.234,56")
            return render(request, 'caixa/caixa_lancamento.html', {'formas': formas_pagamento})

        if tipo not in ['S', 'E'] or not observacao or valor <= 0:
            messages.error(request, "Preencha todos os campos corretamente.")
            return render(request, 'caixa/caixa_lancamento.html', {'formas': formas_pagamento})

        # Criação do movimento
        Movimento.objects.create(
            caixa=caixa,
            tipo=tipo,
            forma=forma_obj,
            observacao=observacao,
            valor=valor,
            usuario=request.user
        )

        messages.success(request, "Movimento registrado com sucesso!")
        return redirect('caixa')

    return render(request, 'caixa/caixa_lancamento.html', {'formas': formas_pagamento})

@login_required
def caixa_consulta(request):
    if not request.user.is_staff:
        messages.warning(request, "Você não tem permissão para realizar consultas!")
        return redirect('caixa')

    hoje = datetime.today()

    # Define valores iniciais (data de hoje) se não houver GET
    if not request.GET:
        initial = {'data_inicio': hoje, 'data_fim': hoje}
    else:
        initial = {}

    form = MovimentoConsultaForm(request.GET or None, initial=initial)
    movimentos = Movimento.objects.all()

    if form.is_valid():
        filtros = {}
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        tipo = form.cleaned_data.get('tipo')
        forma = form.cleaned_data.get('forma')
        usuario = form.cleaned_data.get('usuario')

        if data_inicio:
            filtros['criado_em__date__gte'] = data_inicio
        if data_fim:
            filtros['criado_em__date__lte'] = data_fim
        if tipo:
            filtros['tipo'] = tipo
        if forma:
            filtros['forma'] = forma
        if usuario:
            filtros['usuario'] = usuario

        movimentos = movimentos.filter(**filtros)
    else:
        # Se o formulário não é válido (ou na primeira carga), filtra pelo dia atual
        movimentos = movimentos.filter(criado_em__date=hoje)

    # Agrupamento por forma e tipo (S ou E)
    formas_agrupadas = movimentos.values('forma__forma', 'tipo').annotate(total=Sum('valor'))

    formas_totais_dict = defaultdict(lambda: {'suprimento': 0, 'sangria': 0})
    for item in formas_agrupadas:
        forma_nome = item['forma__forma'] or 'N/A'
        if item['tipo'] == 'S':
            formas_totais_dict[forma_nome]['suprimento'] += item['total'] or 0
        elif item['tipo'] == 'E':
            formas_totais_dict[forma_nome]['sangria'] += item['total'] or 0

    formas_totais_lista = []
    for forma, valores in formas_totais_dict.items():
        formas_totais_lista.append({
            'forma': forma,
            'suprimento': valores['suprimento'],
            'sangria': valores['sangria'],
            'saldo': valores['suprimento'] - valores['sangria'],
        })

    # Totais gerais
    total_suprimentos = movimentos.filter(tipo='S').aggregate(total=Sum('valor'))['total'] or 0
    total_sangrias = movimentos.filter(tipo='E').aggregate(total=Sum('valor'))['total'] or 0
    total_geral = total_suprimentos - total_sangrias

    context = {
        'form': form,
        'movimentos': movimentos.order_by('-criado_em'),
        'total_suprimentos': total_suprimentos,
        'total_sangrias': total_sangrias,
        'total_geral': total_geral,
        'formas_totais': formas_totais_lista,
        'hoje': hoje,  # usado no botão limpar
    }

    return render(request, 'caixa/caixa_consultas.html', context)


@login_required
def caixa_consulta_pdf(request):
    if not request.user.is_staff:
        messages.warning(request, "Você não tem permissão para gerar PDF!")
        return redirect('caixa')

    form = MovimentoConsultaForm(request.GET)
    movimentos = Movimento.objects.select_related('forma', 'usuario').all()

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        tipo = form.cleaned_data.get('tipo')
        forma = form.cleaned_data.get('forma')
        usuario = form.cleaned_data.get('usuario')

        if data_inicio:
            movimentos = movimentos.filter(criado_em__date__gte=data_inicio)
        if data_fim:
            movimentos = movimentos.filter(criado_em__date__lte=data_fim)
        if tipo:
            movimentos = movimentos.filter(tipo=tipo)
        if forma:
            movimentos = movimentos.filter(forma=forma)
        if usuario:
            movimentos = movimentos.filter(usuario=usuario)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="caixa_consulta.pdf"'

    buffer = response
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Consulta de Caixa", styles['Heading1']))
    elements.append(Spacer(1, 12))

    data = [["Data", "Tipo", "Forma", "Valor", "Usuário", "Observação"]]
    for m in movimentos.order_by('-criado_em'):
        usuario_nome = "-"
        if m.usuario:
            usuario_nome = m.usuario.get_full_name() or m.usuario.username

        forma_nome = m.forma.forma if m.forma else '-'

        data.append([
            m.criado_em.strftime('%d/%m/%Y'),
            "Suprimento" if m.tipo == 'S' else "Sangria",
            forma_nome,
            f"R$ {m.valor:.2f}",
            usuario_nome,
            m.observacao or "-"
        ])

    table = Table(data, colWidths=[70, 70, 80, 70, 100, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    elements.append(table)

    # Resumo de totais
    elements.append(Spacer(1, 12))
    total_suprimentos = movimentos.filter(tipo='S').aggregate(total=Sum('valor'))['total'] or 0
    total_sangrias = movimentos.filter(tipo='E').aggregate(total=Sum('valor'))['total'] or 0
    total_geral = total_suprimentos - total_sangrias

    resumo = f"""
    <b>Total de Suprimentos:</b> R$ {total_suprimentos:.2f}<br/>
    <b>Total de Sangrias:</b> R$ {total_sangrias:.2f}<br/>
    <b>Saldo Geral:</b> R$ {total_geral:.2f}
    """
    elements.append(Paragraph(resumo, styles['Normal']))

    doc.build(elements)
    return response


# FORMA DE PAGAMENTO
@method_decorator(login_required, name="dispatch")
class FormapagamentoListView(ListView):
    model = Formapagamento
    template_name = 'formapagamento/formapagamento_list.html'
    context_object_name = 'formapagamento'
    paginate_by = 10

    def get_queryset(self):
        queryset = Formapagamento.objects.filter(excluido_em__isnull=True).order_by('forma')

        busca_forma = self.request.GET.get('busca_forma')
        busca_sigla = self.request.GET.get('busca_sigla')

        if busca_forma:
            queryset = queryset.filter(forma__icontains=busca_forma)

        if busca_sigla:
            queryset = queryset.filter(sigla__icontains=busca_sigla)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['busca_forma'] = self.request.GET.get('busca_forma') or ''
        context['busca_sigla'] = self.request.GET.get('busca_sigla') or ''
        return context

    
@method_decorator(login_required, name="dispatch")
class FormapagamentoCreateView(CreateView):
    model = Formapagamento
    form_class = FormapagamentoForm
    template_name = 'formapagamento/formapagamento_form.html'
    success_url = reverse_lazy('formapagamento-list')
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        return super().form_valid(form)
    

@method_decorator(login_required, name="dispatch")
class FormapagamentoUpdateView(UpdateView):
    model = Formapagamento
    form_class = FormapagamentoForm
    template_name = 'formapagamento/formapagamento_form.html'
    success_url = reverse_lazy('formapagamento-list')
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.warning(request, "Você não tem permissão para atualizar uma forma de pagamento.")
            return redirect('formapagamento-list')
        return super().dispatch(request, *args, **kwargs)
    
@login_required
def formapagamento_excluir(request, pk):
    if not request.user.is_staff:
        messages.warning(request, "Você não tem permissão para excluir forma de pagamento!")
        return redirect('formapagamento-list')
    formapagamento = get_object_or_404(Formapagamento, pk=pk, excluido_em__isnull=True)
    formapagamento.excluido_por = request.user
    formapagamento.excluido_em = timezone.now()
    formapagamento.save()
    messages.success(request, "Categoria excluída com sucesso.")
    return redirect('formapagamento-list')