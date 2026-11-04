from django.db import models
from django.conf import settings

# Create your models here.

class Empresa(models.Model):
    nome = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Filial(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name='filiais'
    )
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20)
    endereco = models.CharField(max_length=200, blank=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        unique_together = ('empresa', 'codigo')

    def __str__(self):
        return f'{self.nome} - {self.empresa.nome}'


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    

class UnidadeMedida(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    sigla = models.CharField(max_length=10, unique=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nome} ({self.sigla})'


class Marca(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    TIPO_PRODUTO = [
        ('USO_INTERNO', 'Uso interno'),
        ('REVENDA', 'Revenda'),
    ]

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='produtos'
    )
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_PRODUTO
    )
    codigo = models.CharField(max_length=30, unique=True)
    unidade_medida = models.ForeignKey(
        UnidadeMedida,
        on_delete=models.PROTECT,
        related_name='produtos'       
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name='produtos',
        null=True,
        blank=True
    )
    embalagem = models.CharField(max_length=100, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
    
    
class Estoque(models.Model):
    filial = models.ForeignKey(
        Filial,
        on_delete=models.PROTECT,
        related_name='estoques'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='estoques'
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0
    )
    estoque_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=0
    )
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['filial', 'produto'],
                name='estoque_unico_por_filial_produto'
            )
        ]

    def __str__(self):
        return f'{self.produto.nome} - {self.filial.nome}'    
    


class MovimentacaoEstoque(models.Model):
    TIPO_MOVIMENTACAO = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
        ('TRANSFERENCIA', 'Transferência'),
    ]

    estoque = models.ForeignKey(
        Estoque,
        on_delete=models.PROTECT,
        related_name='movimentacoes'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='movimentacoes_estoque',
        
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_MOVIMENTACAO
    )
    quantidade = models.DecimalField(
        max_digits=10,
        decimal_places=3
    )
    data_movimentacao = models.DateTimeField(
        auto_now_add=True
    )
    motivo = models.CharField(max_length=200)
    observacao = models.TextField(blank=True)

    def __str__(self):
        return (
            f'{self.get_tipo_display()} - '
            f'{self.estoque.produto.nome} - '
            f'{self.quantidade}'
        )
