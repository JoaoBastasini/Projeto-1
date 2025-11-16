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
    caminho_csv = os.path.join(os.path.dirname(__file__), 'all_pokemon_data.csv')
    dados_pokemon = pd.read_csv(caminho_csv)
    print("Dados de Pokémon carregados com sucesso.")
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

#Recebe os dados do front para calcular o dano
@app.route('/api/calcular_dano', methods=['POST'])
def calcular_dano():
    dados = request.get_json() # Recebe os dados JSON enviados pelo frontend

    if dados_pokemon.empty:
        return jsonify({'erro': 'Dados de Pokémon não carregados'}), 500

    ataque = dados.get('ataque')
    defesa = dados.get('defesa')
    potencia = dados.get('potencia', 80) # Valor padrão 80, se não for enviado
    modificador = dados.get('modificador', 2) # Valor padrão 2, se não for enviado

    try:
        # A Fórmula de Dano Simplificada de Pokémon é:
        # Dano = ((((2 * Level / 5 + 2) * Potência * (Ataque/Defesa)) / 50) + 2) * Modificador
        # Assumindo Level 50 para simplificação no minigame:
        # Garante que os valores são numéricos
        ataque = float(ataque)
        defesa = float(defesa)
        potencia = float(potencia)
        modificador = float(modificador)
        
        if defesa == 0:
            return jsonify({'sucesso': False, 'erro': 'Defesa do Pokémon não pode ser zero para o cálculo de dano. Por favor, insira um valor positivo.'}), 400

        level = 50
        dano_bruto = (((2 * level / 5 + 2) * potencia * (ataque / defesa)) / 50) + 2
        dano_final = int(dano_bruto * modificador) # Arredonda para baixo, como no jogo

        # Retorna o resultado como JSON para o frontend
        return jsonify({
            'dano_calculado': dano_final,
            'sucesso': True
        })

    except Exception as e:
        return jsonify({'erro': str(e), 'sucesso': False}), 400

# --- 4. Inicialização do Servidor ---

if __name__ == '__main__':
    app.run(debug=True)