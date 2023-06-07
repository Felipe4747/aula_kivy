import kivy.uix.screenmanager
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import Screen

import requests
import json

Window.size = (1280 / 3.5, 2220 / 3.5)


class Cadastros(Screen):
    pass


class Pesquisa(Screen):
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

    requests.delete(url + '/RA/aebf/.json')

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


MainApp().run()
