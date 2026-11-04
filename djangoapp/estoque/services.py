
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Estoque, MovimentacaoEstoque


@transaction.atomic
def registrar_movimentacao(
    estoque_id,
    tipo,
    quantidade,
    motivo,
    usuario,
    observacao=''
):
    quantidade = Decimal(str(quantidade))

    if quantidade <= 0:
        raise ValidationError(
            'A quantidade deve ser maior que zero.'
        )

    if tipo not in ('ENTRADA', 'SAIDA'):
        raise ValidationError(
            'Tipo inválido. Utilize ENTRADA ou SAIDA.'
        )

    estoque = Estoque.objects.select_for_update().get(
        pk=estoque_id
    )

    if tipo == 'ENTRADA':
        estoque.quantidade += quantidade

    elif tipo == 'SAIDA':
        if quantidade > estoque.quantidade:
            raise ValidationError(
                'Saldo insuficiente para realizar a saída.'
            )

        estoque.quantidade -= quantidade

    estoque.save(update_fields=['quantidade', 'atualizado_em'])

    movimentacao = MovimentacaoEstoque.objects.create(
        estoque=estoque,
        usuario=usuario,
        tipo=tipo,
        quantidade=quantidade,
        motivo=motivo,
        observacao=observacao
    )

    return movimentacao
