from django.contrib import admin
from django import forms
from .services import registrar_movimentacao
from django.core.exceptions import ValidationError


from .models import (
    Empresa,
    Filial,
    Categoria,
    UnidadeMedida,
    Marca,
    Produto,
    Estoque,
    MovimentacaoEstoque,
)


class MovimentacaoEstoqueForm(forms.ModelForm):
    
    tipo = forms.ChoiceField(
        choices=[
            ('ENTRADA', 'Entrada'),
            ('SAIDA', 'Saída'),
        ],
        label='Tipo',
    )

    class Meta:
        model = MovimentacaoEstoque
        fields = (
            'estoque',
            'tipo',
            'quantidade',
            'motivo',
            'observacao',
        )
    
    
    def clean(self):
        cleaned_data = super().clean()

        estoque = cleaned_data.get('estoque')
        tipo = cleaned_data.get('tipo')
        quantidade = cleaned_data.get('quantidade')

        if quantidade is not None and quantidade <= 0:
            self.add_error(
                'quantidade',
                'A quantidade deve ser maior que zero.'
            )

        if (
            tipo == 'SAIDA'
            and estoque is not None
            and quantidade is not None
            and quantidade > estoque.quantidade
        ):
            self.add_error(
                'quantidade',
                'Saldo insuficiente para realizar a saída.'
            )

        return cleaned_data


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'ativa')
    search_fields = ('nome', 'cnpj')
    list_filter = ('ativa',)


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ('nome', 'codigo', 'empresa', 'ativa')
    search_fields = ('nome', 'codigo', 'empresa__nome')
    list_filter = ('ativa', 'empresa')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa')
    search_fields = ('nome',)
    list_filter = ('ativa',)


@admin.register(UnidadeMedida)
class UnidadeMedidaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sigla', 'ativa')
    search_fields = ('nome', 'sigla')
    list_filter = ('ativa',)
    
@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa')
    search_fields = ('nome',)
    list_filter = ('ativa',)
    
    
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'marca',
        'embalagem',
        'unidade_medida',
        'codigo',
        'categoria',
        'tipo',
        'ativo',
    )
    search_fields = ('nome', 'marca__nome', 'codigo')
    list_filter = (
        'tipo',
        'categoria',
        'unidade_medida',
        'ativo',
    )


@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = (
        'produto',
        'filial',
        'quantidade',
        'estoque_minimo',
        'atualizado_em',
    )
    search_fields = ('produto__nome', 'filial__nome')
    list_filter = ('filial',)


@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):
    form = MovimentacaoEstoqueForm

    list_display = (
        'data_movimentacao',
        'estoque',
        'tipo',
        'quantidade',
        'motivo',
        'usuario',
    )
    search_fields = ('motivo', 'estoque__produto__nome','usuario__username',)
    list_filter = ('tipo', 'data_movimentacao')
    readonly_fields = ('data_movimentacao',)

    def save_model(self, request, obj, form, change):
        if change:
            raise ValidationError(
                'Não é permitido alterar uma movimentação já registrada.'
            )

        movimentacao = registrar_movimentacao(
            estoque_id=obj.estoque_id,
            tipo=obj.tipo,
            quantidade=obj.quantidade,
            motivo=obj.motivo,
            usuario=request.user,
            observacao=obj.observacao,
        )
        obj.pk = movimentacao.pk
        obj.usuario = request.user

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False
