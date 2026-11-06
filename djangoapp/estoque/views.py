from django.shortcuts import render, redirect
from django.contrib import messages
#from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.db.models import F
from django.core.exceptions import ValidationError

from .models import Estoque, Filial
from .forms import MovimentacaoEstoqueForm
from .services import registrar_movimentacao as executar_movimentacao


@login_required
def lista_estoque(request):
    # NOVO TRECHO: busca as filiais ativas
    filiais = Filial.objects.filter(
        ativa=True
    ).order_by('nome')

    # NOVO TRECHO: verifica se alguma filial foi selecionada
    filial_selecionada = request.GET.get('filial', '')

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
    # Aplica o filtro por filial, quando houver seleção
    if filial_selecionada.isdigit():
        filial_id = int(filial_selecionada)

        if filiais.filter(pk=filial_id).exists():
            estoques = estoques.filter(filial_id=filial_id)
        else:
            filial_selecionada = ''
    else:
        filial_selecionada = ''
    
    #-------------------------------------------------------
    filiais_com_selecao = [
        {
            'id': filial.id,
            'nome': filial.nome,
            'selecionada': str(filial.id) == filial_selecionada,
        }
        for filial in filiais
    ]
    #-------------------------------------------------------

    total_produtos = estoques.values('produto').distinct().count()

    total_estoques_baixos = estoques.filter(
        quantidade__lte=F('estoque_minimo')
    ).count()

    contexto = {
        'estoques': estoques,
        'total_produtos': total_produtos,
        'total_estoques_baixos': total_estoques_baixos,
        'filiais': filiais_com_selecao,
        'filial_selecionada': filial_selecionada,
    }

    return render(
        request,
        'estoque/lista_estoque.html',
        contexto
    )


def login_estoque(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(
            request,
            username=username,
            password=password
        )

        if usuario is not None:
            login(request, usuario)

            return redirect('estoque:lista_estoque')

        messages.error(
            request,
            'Usuário ou senha incorretos.'
        )

    return render(
        request,
        'estoque/login.html'
    )
    

@login_required
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