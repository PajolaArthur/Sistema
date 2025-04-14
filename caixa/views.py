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



@method_decorator(login_required, name="dispatch")
class MovimentoListView(ListView):
    model = Movimento
    template_name = 'caixa.html'
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
                Q(forma__icontains=movimentos)
            )

        if tipo:
            filtros &= Q(tipo=tipo)

        if forma:
            filtros &= Q(forma=forma)

        return queryset.filter(filtros)
    
    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)

            context['tipo_selecionado'] = Movimento.TIPO_MOVIMENTO
            context['forma_selecionada'] = Movimento.FORMAS_PAGAMENTO

            # Adiciona os filtros atuais para manter seleção no template
            context['tipo'] = self.request.GET.get('tipo', '')
            context['forma'] = self.request.GET.get('forma', '')

             # lógica para identificar o caixa aberto do usuário
            hoje = timezone.localdate()
            inicio_dia = timezone.make_aware(datetime.combine(hoje, datetime.min.time()))
            fim_dia = timezone.make_aware(datetime.combine(hoje, datetime.max.time()))

            caixa = Caixa.objects.filter(
                usuario=self.request.user,
                abertura_caixa__gte=inicio_dia,
                abertura_caixa__lte=fim_dia,
                fechamento_caixa__isnull=True
            ).first()

            # usa o mesmo queryset da tela, mas filtrado por caixa aberto
            movimentos = self.get_queryset().filter(caixa=caixa) if caixa else []

            total_suprimentos = sum(m.valor for m in movimentos if m.tipo == 'S')
            total_sangrias = sum(m.valor for m in movimentos if m.tipo == 'E')
            saldo = total_suprimentos - total_sangrias

            context['total_suprimentos'] = total_suprimentos
            context['total_sangrias'] = total_sangrias
            context['saldo'] = saldo
            context['caixa_aberto'] = caixa

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

    return render(request, 'caixa_abrir.html')

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

    # Agrupamento de totais por forma de pagamento
    movimentos = caixa.movimentos.all()
    totais_por_forma = movimentos.values('forma', 'tipo').annotate(total=Sum('valor'))

    formas_agrupadas = defaultdict(lambda: {'suprimento': 0, 'sangria': 0, 'saldo': 0})
    for item in totais_por_forma:
        forma = item['forma']
        tipo = item['tipo']
        valor = item['total']

        if tipo == 'S':
            formas_agrupadas[forma]['suprimento'] += valor
        elif tipo == 'E':
            formas_agrupadas[forma]['sangria'] += valor

    # Calcula saldo por forma
    for forma, valores in formas_agrupadas.items():
        valores['saldo'] = valores['suprimento'] - valores['sangria']

    if request.method == 'POST':
        caixa.fechamento_caixa = timezone.now()
        caixa.save()
        messages.success(request, "Caixa fechado com sucesso!")
        return redirect('caixa')

    return render(request, 'caixa_fechar.html', {
        'caixa': caixa,
        'formas_agrupadas': dict(formas_agrupadas),
        'formato': dict(Movimento.FORMAS_PAGAMENTO)  # Para exibir nomes legíveis no template
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

    # Agrupamento por forma
    formas_agrupadas = defaultdict(lambda: {
        "suprimento": Decimal("0.00"),
        "sangria": Decimal("0.00"),
        "saldo": Decimal("0.00"),
    })
    formato = dict(Movimento.FORMAS_PAGAMENTO)

    for m in movimentos:
        forma = m.forma
        if m.tipo == 'S':
            formas_agrupadas[forma]["suprimento"] += m.valor
        elif m.tipo == 'E':
            formas_agrupadas[forma]["sangria"] += m.valor
        formas_agrupadas[forma]["saldo"] = (
            formas_agrupadas[forma]["suprimento"] - formas_agrupadas[forma]["sangria"]
        )

    # Renderizar HTML do template
    template = get_template("caixa_fechamento_pdf.html")
    html = template.render({
        "caixa": caixa,
        "formas_agrupadas": dict(formas_agrupadas),
        "formato": formato,
        "usuario": request.user,
        "data_hoje": hoje,
    })

    # Gerar o PDF
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
    FORMAS_PAGAMENTO = Movimento.FORMAS_PAGAMENTO

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
        forma = request.POST.get('forma')
        observacao = request.POST.get('observacao', '').strip()
        valor_str = request.POST.get('valor', '').strip()

        # Validação da forma de pagamento
        codigos_formas_validas = [codigo for codigo, _ in FORMAS_PAGAMENTO]
        if forma not in codigos_formas_validas:
            messages.error(request, "Forma de pagamento inválida.")
            return render(request, 'caixa_lancamento.html', {'formas': FORMAS_PAGAMENTO})

        try:
            valor_limpo = valor_str.replace('.', '').replace(',', '.')
            valor = Decimal(valor_limpo)
        except (InvalidOperation, ValueError):
            messages.error(request, "Valor inválido. Use o formato 1.234,56")
            return render(request, 'caixa_lancamento.html', {'formas': FORMAS_PAGAMENTO})

        if tipo not in ['S', 'E'] or not observacao or valor <= 0:
            messages.error(request, "Preencha todos os campos corretamente.")
            return render(request, 'caixa_lancamento.html', {'formas': FORMAS_PAGAMENTO})

        # Criação do movimento
        Movimento.objects.create(
            caixa=caixa,
            tipo=tipo,
            forma=forma,
            observacao=observacao,
            valor=valor,
            usuario=request.user
        )

        messages.success(request, "Movimento registrado com sucesso!")
        return redirect('caixa')

    return render(request, 'caixa_lancamento.html', {'formas': FORMAS_PAGAMENTO})

@login_required
def caixa_consulta(request):
    if not request.user.is_staff:
        messages.warning(request, "Você não tem permissão para realizar consultas!")
        return redirect('caixa')
    if request.GET and any(param for param in request.GET.values()):
        form = MovimentoConsultaForm(request.GET)
    else:
        form = MovimentoConsultaForm()

    movimentos = Movimento.objects.all()

    # Aplicar filtros se forem passados
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

    # Totais por forma de pagamento (com separação S/E e saldo)
    formas_agrupadas = movimentos.values('forma', 'tipo').annotate(total=Sum('valor'))

    formas_totais_dict = defaultdict(lambda: {'suprimento': 0, 'sangria': 0})
    for item in formas_agrupadas:
        forma = item['forma']
        tipo = item['tipo']
        if tipo == 'S':
            formas_totais_dict[forma]['suprimento'] += item['total']
        elif tipo == 'E':
            formas_totais_dict[forma]['sangria'] += item['total']

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

    # Contexto final
    context = {
        'form': form,
        'movimentos': movimentos,
        'total_suprimentos': total_suprimentos,
        'total_sangrias': total_sangrias,
        'total_geral': total_geral,
        'formas_totais': formas_totais_lista,
    }

    return render(request, 'caixa_consultas.html', context)