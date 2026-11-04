from django import forms

from .models import Estoque


class MovimentacaoEstoqueForm(forms.Form):

    estoque = forms.ModelChoiceField(
        queryset=Estoque.objects.select_related(
            'produto',
            'filial'
        ).all(),
        label='Produto / Filial',
        empty_label='Selecione o produto e a filial'
    )

    tipo = forms.ChoiceField(
        choices=[
            ('ENTRADA', 'Entrada'),
            ('SAIDA', 'Saída'),
        ],
        label='Tipo de movimentação'
    )

    quantidade = forms.DecimalField(
        max_digits=10,
        decimal_places=3,
        min_value=0.001,
        label='Quantidade'
    )

    motivo = forms.CharField(
        max_length=200,
        label='Motivo'
    )

    observacao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Observação'
    )