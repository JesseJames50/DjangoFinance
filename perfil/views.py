from django.shortcuts import render, redirect
from django.http import HttpResponse

from extrato.models import Valores
from .models import Categoria, Conta
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models import Sum
from .utils import calcula_total, calcula_equilibrio_financeiro
from datetime import datetime

# Create your views here.
def home(request): 
    valores = Valores.objects.filter(data__month=datetime.now().month)
    
    #Utiliza a função em perfil utils
    entradas = valores.filter(tipo='E')
    saidas = valores.filter(tipo='S')
    
    contas = Conta.objects.all()
    
    total_entradas = calcula_total(entradas, 'valor')
    total_saidas = calcula_total(saidas, 'valor')
    
    #Utiliza uma função utils para calcular total - exemplo Clean Architecture
    #As demais formas de calcular seguem para efeito didático 
        
    total_contas = calcula_total(contas, 'valor')
    
    percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()
    
    
    return render(request, 'home.html', {'contas': contas,
                                         'total_contas':  total_contas,
                                         'total_entradas': total_entradas,
                                         'total_saidas': total_saidas,
                                         'total_livre': total_entradas - total_saidas,
                                         'percentual_gastos_essenciais': int(percentual_gastos_essenciais),
                                         'percentual_gastos_nao_essenciais': int(percentual_gastos_nao_essenciais)})

def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    total_contas = 0
    #Outra forma de calcular a soma total
    total_contas = contas.aggregate(Sum('valor'))
    #verificar o valor impresso
    #print("O valor do total é:", total_contas['valor__sum'])
    '''for conta in contas:
        total_conta +=  conta.valor '''   
    return render(request, 'gerenciar.html', {'contas': contas, 'total_contas':  total_contas['valor__sum'], 'categorias': categorias})

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')
    
    if len(apelido.strip()) == 0 or len(apelido.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')
    
    if len(banco.strip()) == 0 or len(banco.strip()) == 0:
        return redirect('/perfil/gerenciar/')
    
    if len(tipo.strip()) == 0 or len(tipo.strip()) == 0:
        return redirect('/perfil/gerenciar/')
    
    if len(valor.strip()) == 0 or len(valor.strip()) == 0:
        return redirect('/perfil/gerenciar/')   
         
    conta = Conta(
        apelido=apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )
    
    conta.save()
    
    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso!')
    
    return redirect('/perfil/gerenciar/')

def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()
    
    messages.add_message(request, constants.SUCCESS, 'Registro deletado com sucesso!')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.essencial = not categoria.essencial
    categoria.save()
    
    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}
    categorias = Categoria.objects.all()

    for categoria in categorias:
        dados[categoria.categoria] = Valores.objects.filter(categoria=categoria).aggregate(Sum('valor'))['valor__sum']
        '''
          #Outra forma de fazer os cálculos
          if dados[categoria.categoria] is None:
            dados[categoria.categoria] = 0
            print(dados)
        '''
        for categoria in categorias:
            total = 0
            valores = Valores.objects.filter(categoria=categoria)
            for v in valores:
                total = total + v.valor
                
            dados[categoria.categoria] = total
      
        
    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})
    