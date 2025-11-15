from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

'''
Para rodar o servidor Flask:
1. Certifique-se de que você tem o Flask e o Pandas instalados: pip install Flask pandas
2. Execute este arquivo: python app.py
3. Acesse no navegador: http://127.0.0.1:5000/
'''

app = Flask(__name__)

# -------- Carregar Dados --------

# Carrega os dados do .csv de forma relativa tanto ao diretório atual quanto ao sistema operacional
# os.path.dirname(__file__) pega o diretório
# os.path.join monta o caminho corretamente independentemente do SO
try:
    caminho_csv = os.path.join(os.path.dirname(__file__), 'dados', 'all_pokemon_data.csv')
    dados_pokemon = pd.read_csv(caminho_csv)
except FileNotFoundError:
    print("ERRO: O arquivo all_pokemon_data.csv não foi encontrado. Verifique o caminho.")
    dados_pokemon = pd.DataFrame() # Cria um DataFrame vazio para evitar erros

# -------- Rotas de Navegação --------

@app.route('/')
def pagina_inicial():
    # O Flask procura o template em 'templates/'
    return render_template('pagina_inicial.html')

@app.route('/calculo_dano')
def calculo_dano_page():
    # O Flask procura o template em 'templates/minijogos/'
    return render_template('minijogos/calculo_dano.html')

@app.route('/calculo_xp')
def calculo_xp_page():
    return render_template('minijogos/calculo_xp.html')

# -------- Rota do Minigame (API) --------

