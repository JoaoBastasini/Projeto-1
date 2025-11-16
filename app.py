from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import random
import os
from type_data import TYPE_CHART_OFFENSIVE, TYPE_CHART_DEFENSIVE

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

# -------- Funções Lógicas do Minigame --------

# Calcula o multiplicador de eficácia do tipo
def get_type_effectiveness(attack_type, defender_types):
    multiplier = 1.0
    for d_type in defender_types:
        # Primeiro .get retorna o dicionário do tipo de ataque
        # Segundo .get retorna o valor de eficácia contra o tipo defensor, no caso de dual type, entra nesse trecho duas vezes (for)
        # Se não tem nada no dicionário, o ataque é neutro, multiplicador 1.
        effectiveness = TYPE_CHART_OFFENSIVE.get(attack_type, {}).get(d_type, 1.0)
        multiplier *= effectiveness
    return multiplier

# Escolhe aleatoriamente o atacante, defensor, níveis e ataque.
def setup_battle(df):    
    
    # Escolhe os Pokémon
    # Faz um DF com um único elemento, aleatório
    # Reseta o índice, o original vira uma coluna chamada 'index' e o novo é 0.
    # Seleciona o primeiro e único elemento com iloc[0]
    attacker_data = df.sample(1).reset_index().iloc[0]
    defender_data = df.sample(1).reset_index().iloc[0]
    
    # Sorteia os níveis dos Pokémon
    level_att = random.randint(40, 60) # Níveis em uma faixa razoável
    # Garante que o nível do defensor fique entre 40 e 60 e a diferença seja no máximo 10
    # level_def = random.randint(max(40, level_att - 10), min(60, level_att + 10))
    # Aparentemente o nível do defensor não é usado no cálculo de dano, então foi comentado, mas caso venha a calhar, está aí.

    # Escolhe o poder do ataque (múltiplo de 10 de 40 a 120)
    base_power = random.choice(range(40, 121, 10))

    # Determina se é físico ou especial, por sorteio, e seleciona os stats correspondentes
    is_physical = random.choice([True, False])

    if is_physical:
        att_stat = attacker_data['Attack']
        def_stat = defender_data['Defense']
        att_stat_name = 'Attack'
        def_stat_name = 'Defense'
    else:
        att_stat = attacker_data['Special Attack']
        def_stat = defender_data['Special Defense']
        att_stat_name = 'Special Attack'
        def_stat_name = 'Special Defense'

    # Escolhe o tipo do ataque
    all_types = list(TYPE_CHART_OFFENSIVE.keys())

    attacker_types = [] # Lista vazia para armazenar os tipos válidos
    attacker_types.append(attacker_data['Primary Typing']) # Armazena o primeiro
    if pd.notna(attacker_data['Secondary Typing']):
        attacker_types.append(attacker_data['Secondary Typing']) # Armazena o segundo, se houver
    
    # 50% de chance de ser STAB (mesmo tipo, com bônus de 1.5 no dano), 50% de chance de ser outro tipo
    if random.random() < 0.5 and attacker_types:
        attack_type = random.choice(attacker_types)
    else:
        # Escolhe um tipo que não seja do atacante
        non_stab_types = []
        for t in all_types:
            if t not in attacker_types:
                non_stab_types.append(t)
        attack_type = random.choice(non_stab_types)

    # Calcula modificadores
    stab_mod = 1.5 if attack_type in attacker_types else 1.0
    
    defender_types = []
    defender_types.append(defender_data['Primary Typing'])
    if pd.notna(defender_data['Secondary Typing']):
        defender_types.append(defender_data['Secondary Typing'])

    type_effectiveness = get_type_effectiveness(attack_type, defender_types)

    # Cálculo de dano base (sem Fator Aleatório)
    # Dano Base = [ ( (2 * Nível / 5) + 2 ) * Poder * (Att / Def) / 50 ] + 2
    base_calc = (((2 * level_att / 5) + 2) * base_power * (att_stat / def_stat) / 50) + 2
    
    # Dano Final Mínimo e Máximo (inclui STAB e Eficácia)
    # A resposta correta para o usuário será o Dano Máximo (fator aleatório = 1.0)
    damage_max = np.floor(base_calc * stab_mod * type_effectiveness * 1.00)
    damage_min = np.floor(base_calc * stab_mod * type_effectiveness * 0.85)

    # Retorna todos os dados formatados para o frontend
    return {
        "attacker_name": attacker_data['Name'],
        "defender_name": defender_data['Name'],
        "attacker_types": attacker_types,
        "defender_types": defender_types,
        "level": level_att,
        "power": base_power,
        "att_stat_name": att_stat_name,
        "def_stat_name": def_stat_name,
        "att_value": int(att_stat),
        "def_value": int(def_stat),
        "attack_type": attack_type,
        "stab_mod": stab_mod,
        "type_effectiveness": type_effectiveness,
        "base_calc_no_random": base_calc,
        "answer": int(damage_max), # A resposta é com o valor com o fator aleatório máximo (1.0)
        "range_min": int(damage_min),
        "range_max": int(damage_max)
    }

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

    

# --- 4. Inicialização do Servidor ---

if __name__ == '__main__':
    app.run(debug=True)