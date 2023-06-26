import kivy.uix.screenmanager
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen
from kivy_garden.graph import Graph
import requests
import json
from kivymd_extensions.akivymd.uix.charts import AKBarChart, AKPieChart, AKLineChart
from kivy.metrics import dp


Window.size = (1280 / 3.5, 2220 / 3.5)


class Cadastros(Screen):
    pass


class Pesquisa(Screen):
    pass

class Grafico(Screen):
    pass


def show_message(text, dispensar=True):
    from kivymd.uix.snackbar import Snackbar
    snackbar = Snackbar(text=str(text), duration=1)
    buttons = []
    if dispensar:
        from kivymd.uix.button import MDFlatButton
        buttons.append(MDFlatButton(text='DISPENSAR', theme_text_color='Custom', text_color='#ffffff',
                                    on_release=snackbar.dismiss))
    snackbar.buttons = buttons

    return snackbar


class MainApp(MDApp):
    dados = {}

    url = 'https://finansee-8a974-default-rtdb.firebaseio.com/'
    dado = requests.get(url + '.json')
    dict_dados = dado.json()

    grafico = 0
    # requests.patch(url, data=json.dumps(dict_dados))

    def build(self):
        self.theme_cls.primary_palette = 'Blue'
        self.theme_cls.device_orientation = 'vertical'
        self.theme_cls.theme_style = 'Dark'
        return Builder.load_file('main.kv')

    def cadastrar(self, nome, nascimento, cidade, cpf, salario, alterar=False):
        cpf = cpf.replace('.', '').replace('-', '')

        if len(nome) == 0:
            show_message('Digite o nome!').open()
            return
        if len(nascimento) == 0:
            show_message('Digite o nascimento!').open()
            return
        if len(cidade) == 0:
            show_message('Digite a cidade!').open()
            return
        if len(cpf) == 0:
            show_message('Digite o cpf!').open()
            return
        if self.existe_cpf(cpf) and alterar is False:
            show_message('CPF já cadastrado!').open()
            return
        if len(cpf) != 11:
            show_message('CPF deve conter 11 caracteres').open()
            return
        if len(salario) == 0:
            show_message('Digite o salario!').open()
            return

        self.dados[cpf] = {'nome': nome, 'nascimento': nascimento, 'cidade': cidade, 'salario': salario}
        requests.patch(self.url + '.json', data=json.dumps(self.dados))

        if alterar:
            show_message('Cadastro alterado com sucesso').open()
        else:
            tela_cadastro = self.root.ids.screen_manager.get_screen('cadastros')
            tela_cadastro.ids.inp_nome.text, tela_cadastro.ids.inp_nascimento.text, tela_cadastro.ids.inp_cidade.text, tela_cadastro.ids.inp_cpf.text, tela_cadastro.ids.inp_salario.text = '', '', '', '', ''
            show_message('Cadastro realizado com sucesso').open()

    def pesquisar(self, cpf):
        cpf = cpf.replace('.', '').replace('-', '')
        if len(cpf) == 0:
            show_message('Digite um CPF!').open()
        elif len(cpf) != 11:
            show_message('CPF deve ter 11 caracteres!').open()

        if self.existe_cpf(cpf):
            tela_pesquisa = self.root.ids.screen_manager.get_screen('pesquisa')
            tela_pesquisa.ids.inp_cpf.disabled = True
            tela_pesquisa.ids.btn_pesquisar.pos_hint = {'x': 2, 'y': 2}
            tela_pesquisa.ids.btn_alterar.pos_hint = {}
            tela_pesquisa.ids.btn_remover.pos_hint = {}
            tela_pesquisa.ids.inp_nome.text = self.dict_dados[cpf]['nome']
            tela_pesquisa.ids.inp_nome.pos_hint = {}
            tela_pesquisa.ids.inp_nascimento.text = self.dict_dados[cpf]['nascimento']
            tela_pesquisa.ids.inp_nascimento.pos_hint = {}
            tela_pesquisa.ids.inp_cidade.text = self.dict_dados[cpf]['cidade']
            tela_pesquisa.ids.inp_cidade.pos_hint = {}
            tela_pesquisa.ids.inp_salario.text = self.dict_dados[cpf]['salario']
            tela_pesquisa.ids.inp_salario.pos_hint = {}
            show_message('Dados carregados!').open()
        else:
            show_message('CPF não registrado!').open()

    def existe_cpf(self, cpf):
        dado = requests.get(self.url + '.json')
        self.dict_dados = dado.json()
        return cpf in self.dict_dados

    def limpar_pesquisa(self):
        tela_pesquisa = self.root.ids.screen_manager.get_screen('pesquisa')
        tela_pesquisa.ids.inp_cpf.disabled = False
        tela_pesquisa.ids.btn_pesquisar.pos_hint = {}
        tela_pesquisa.ids.btn_alterar.pos_hint = {'x': 2, 'y': 2}
        tela_pesquisa.ids.btn_remover.pos_hint = {'x': 2, 'y': 2}
        tela_pesquisa.ids.inp_cpf.text = ''
        tela_pesquisa.ids.inp_nome.text = ''
        tela_pesquisa.ids.inp_nome.pos_hint = {'x': 2, 'y': 2}
        tela_pesquisa.ids.inp_nascimento.text = ''
        tela_pesquisa.ids.inp_nascimento.pos_hint = {'x': 2, 'y': 2}
        tela_pesquisa.ids.inp_cidade.text = ''
        tela_pesquisa.ids.inp_cidade.pos_hint = {'x': 2, 'y': 2}
        tela_pesquisa.ids.inp_salario.text = ''
        tela_pesquisa.ids.inp_salario.pos_hint = {'x': 2, 'y': 2}

    def alterar(self, nome, nascimento, cidade, cpf, salario):
        self.cadastrar(nome, nascimento, cidade, cpf, salario, alterar=True)

    def remover(self, cpf):
        requests.delete(self.url + '/'+cpf+'/.json')
        if self.existe_cpf(cpf):
            show_message('Dados deletados com sucesso!').open()
        self.limpar_pesquisa()

    def remove_marks_all_chips(self, selected_chip):
        tela_grafico = self.root.ids.screen_manager.get_screen('grafico')
        g = tela_grafico.ids.scrollview.children[0].children
        for instance_chip in g[2].children:
            if instance_chip != {} and instance_chip != selected_chip:
                instance_chip.active = False

    def draw_graphic(self):
        gerenciador = self.root.ids.screen_manager
        self.dados = requests.get(self.url + '.json')
        self.dados = self.dados.json()
        salarios = []
        for chave in self.dados.keys():
            salarios.append(self.dados[chave]['salario'])
        salarios.sort()
        print('salarios', salarios)
        n = 5
        min_value = float(salarios[0])
        max_value = float(salarios[-1])
        passo = (max_value-min_value)/n

        x = []
        aux = min_value + passo
        for i in range(n):
            x.append(round(aux, 2))
            aux = aux+passo
        print('x', x)

        hist = [0]*n
        for value in salarios:
            j = int((float(value)-min_value)/passo)
            if j >= n:
                j = n-1
            hist[j] += 1
        print('hist', hist)

        if self.grafico != 0:
            gerenciador.get_screen('grafico').ids.graph.remove_widget(self.grafico)

        for instance_chip in gerenciador.get_screen('grafico').ids.chips_grafico.children:
            if instance_chip.active:
                if instance_chip.text == 'Barras':
                    self.grafico = self.monta_grafico_barras(x, hist)
                    break
                if instance_chip.text == 'Retas':
                    self.grafico = self.monta_grafico_linha(x, hist)
                    break
                if instance_chip.text == 'Pizza':
                    self.grafico = self.monta_grafico_pizza(x, hist)
                    break

    def monta_grafico_barras(self, x, hist):
        gerenciador = self.root.ids.screen_manager
        barchart = AKBarChart(
            x_values=x,
            y_values=hist,
            bars_color='#AE4646',
            lines_color='#000000',
            bg_color='#FFFFFF',
            size_hint_y=None,
            height=dp(280),
            label_size=dp(12),
            size=(dp(100), dp(300)),
            labels=True,
            bars_radius=0,
            labels_color='#000000',

        )
        gerenciador.get_screen('grafico').ids.graph.add_widget(barchart)
        return barchart

    def monta_grafico_linha(self, x, hist):
        gerenciador = self.root.ids.screen_manager
        linechart = AKLineChart(
            x_values=x,
            y_values=hist,
            bg_color='#ffffff',
            size_hint_y=None,
            height=dp(20),
            label_size=dp(12),
            size=(dp(100), dp(300)),
            circles_color='#4646FF',
            lines_color='#000000',
            labels_color='#000000',
        )
        gerenciador.get_screen('grafico').ids.graph.add_widget(linechart)
        return linechart

    def monta_grafico_pizza(self, x, hist):
        gerenciador = self.root.ids.screen_manager
        total = sum(hist)
        porc_hist = []
        for item in hist:
            porc_hist.append((item/total)*100)
        chaves = []
        for v in x:
            chaves.append('R$ '+str(v))
        item = {}
        for i in range(len(porc_hist)):
            item[chaves[i]] = porc_hist[i]
        items = [item]

        piechart = AKPieChart(
            items=items,
            size_hint=[None, None],
            size=(dp(300),dp(300)),
            pos_hint={'center_x': None, 'center_y': None},
            pos=(dp(50), dp(50))
        )
        gerenciador.get_screen('grafico').ids.graph.add_widget(piechart)
        return piechart

MainApp().run()
