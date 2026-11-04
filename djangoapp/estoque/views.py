from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F
from django.core.exceptions import ValidationError

from .models import Estoque
from .forms import MovimentacaoEstoqueForm
from .services import registrar_movimentacao as executar_movimentacao


@staff_member_required
def lista_estoque(request):

    estoques = (
        Estoque.objects
        .select_related(
            'produto',
            'produto__categoria',
            'produto__marca',
            'produto__unidade_medida',
            'filial',
        )
        .filter(produto__ativo=True)
        .order_by('produto__nome')
    )

    total_produtos = estoques.values('produto').distinct().count()

    total_estoques_baixos = estoques.filter(
        quantidade__lte=F('estoque_minimo')
    ).count()

    contexto = {
        'estoques': estoques,
        'total_produtos': total_produtos,
        'total_estoques_baixos': total_estoques_baixos,
    }

    return render(
        request,
        'estoque/lista_estoque.html',
        contexto
    )


    """
    O decorador @staff_member_required restringe essas páginas aos usuários 
    autenticados que possuem permissão de acesso à área administrativa 
    (is_staff=True).
    """

@staff_member_required
def registrar_movimentacao(request):

    if request.method == 'POST':
        form = MovimentacaoEstoqueForm(request.POST)

        if form.is_valid():
            dados = form.cleaned_data

            try:
                executar_movimentacao(
                    estoque_id=dados['estoque'].pk,
                    tipo=dados['tipo'],
                    quantidade=dados['quantidade'],
                    motivo=dados['motivo'],
                    usuario=request.user,
                    observacao=dados['observacao'],
                )

                messages.success(
                    request,
                    'Movimentação registrada com sucesso!'
                )

                return redirect('estoque:registrar_movimentacao')
                #return redirect('estoque:lista_estoque')
                

            except ValidationError as erro:
                form.add_error(None, erro)

    else:
        form = MovimentacaoEstoqueForm()

    return render(
        request,
        'estoque/movimentacao_form.html',
        {'form': form}
    )