import numpy as np
import pandas as pd

# Gerar características iniciais das árvores
np.random.seed(42)

# Funções
def ConfusionMatrix(precision, recall, n):
    VP = int(np.ceil(recall * n))
    FP = int(np.ceil(VP*(1-precision)/precision))
    FN = int(np.ceil(VP*(1-recall)/recall))

    while VP + FN != n:
        FN = FN - 1

    return VP, FP, FN

def random_tree_distances(vp, fp, fn, distance_MAE, dist_max=2.5):
    distances_VP = np.random.uniform(low=0, high=dist_max, size=vp)
    distances_FP = np.random.uniform(low=0, high=dist_max, size=fp)
    distances_FN = np.random.uniform(low=0, high=dist_max, size=fn)

    detect_distances_VP = distances_VP + np.random.randn(vp)*distance_MAE
    detect_distances_VP = np.clip(detect_distances_VP, 0, dist_max)

    detect_distances_FP = distances_FP.copy()
    detect_distances_FN = distances_FN.copy()

    detect_distances_VP.sort()
    detect_distances_FP.sort()
    detect_distances_FN.sort()

    return detect_distances_VP, detect_distances_FP, detect_distances_FN

# Função para aplicar crescimento das árvores
def apply_tree_growth(distances, growth_rate, months=1):
    grown_distances = distances - (growth_rate * months)
    return grown_distances

# Função de probabilidade de não atingir a meta de podas
def not_reaching_the_pruning_target(prob_min=0.7):
    prob = np.random.uniform(low=prob_min, high=1.05, size=1)[0]
    prob = np.clip(prob, 0, 1)
    return prob
    # return int(prob * size)

# Função para selecionar algumas árvores não mapeadas e cadastrá-las
def unregistered_trees_found(trees, size):
    # Selecionando aleatoriamente sem repetição
    selected_trees = np.random.choice(trees, size=min(size, len(trees)), replace=False)

    # Criando a máscara para os elementos não selecionados
    mask = np.isin(trees, selected_trees, invert=True)

    # Filtrando o array original para remover os elementos selecionados
    trees_remove = trees[mask]

    # Elementos selecionados
    trees_found = trees[~mask]

    return trees_found, trees_remove

def create_dataframe_simulation(data, T):
    df = pd.DataFrame(data['count_vp'])
    df['Estimativa'] = 'Podas Reais'

    df0 = pd.DataFrame(data['count_fp'])
    df0['Estimativa'] = 'Chamadas Falsas'

    df = pd.concat([df, df0])

    df0 = pd.DataFrame(data['critical_trees_not_pruned'])
    df0['Estimativa'] = 'Árvores criticas não podadas'

    df = pd.concat([df, df0])
    df.columns = [f'Mês {i+1}' for i in range(T)] + ['Estimativa']

    # Reorganize o dataframe usando o método melt do pandas
    df_melted = pd.melt(df, id_vars=['Estimativa'], value_vars=[f'Mês {i+1}' for i in range(T)])

    return df_melted

def create_table(df):
    #  Calcular a média dos valores por mês e por estimativa
    df_mean = df.groupby(['variable', 'Estimativa'], as_index=False)['value'].mean()

    table = {'Mês': [], 'Chamadas Falsas':[], 'Podas Reais':[], 
         'Árvores criticas não podadas':[]}

    for i in [1, 6, 12, 18, 24, 30, 36]:
        arr = df_mean.loc[df_mean['variable'] == f'Mês {i}', ['Estimativa', 'value']].values
        table['Mês'].append(i)
        for col, val in arr:
            table[col].append(int(round(val,0)))
            
    return pd.DataFrame(table)    

def simulation(METRICS, N, n_simulation, T, critical_distance, growth_rate, total_tree, prob_min):
    data = {
        'count_vp': list(),
        'count_fp': list(),
        'count_fn': list(),
        'critical_trees_not_pruned': list()
    }

    PRECISION = METRICS['PRECISION']
    RECALL = METRICS['RECALL']
    MAE_DISTANCE = METRICS['MAE_DISTANCE']

    VP, FP, FN = ConfusionMatrix(PRECISION, RECALL, N)

    for _ in range(n_simulation):

        detect_distances_VP, detect_distances_FP, detect_distances_FN = random_tree_distances(vp=VP,
                                                                                              fp=FP,
                                                                                              fn=FN,
                                                                                              distance_MAE=MAE_DISTANCE,
                                                                                              dist_max=2.5)

        count_vp = list()
        count_fp = list()
        count_fn = list()
        critical_trees_not_pruned = list()

        for month in range(T):

            # Filtro da seleção das árvores críticas
            mask_VP = detect_distances_VP < critical_distance
            mask_FP = detect_distances_FP < critical_distance
            mask_FN = detect_distances_FN < critical_distance

            # Quantificando os vp, fp e fn
            t_vp, t_fp, t_fn = np.sum(mask_VP), np.sum(mask_FP), np.sum(mask_FN)
            t_vpfp = t_vp + t_fp

            # Selecionando aleatoriamente quais árvores serão podadas no mês dentro dos VP e FP
            size = min(total_tree, t_vpfp)
            prob = not_reaching_the_pruning_target(prob_min=prob_min)
            size = int(prob * size)

            select_vp = np.random.choice([1,0], p=[t_vp/t_vpfp, t_fp/t_vpfp], size=size).sum()
            select_fp = size - select_vp

            # Ajustanto quantitativo
            while select_vp > t_vp:
                select_vp -= 1

            while select_fp > t_fp:
                select_fp -= 1

            # Apende na lista de podas por mês
            count_vp.append(select_vp)
            count_fp.append(select_fp)
            count_fn.append(t_fn)

            # Total de árvores críticas
            unpruned_critical_trees = (t_vp + t_fn) - select_vp
            critical_trees_not_pruned.append(max(0, unpruned_critical_trees))

            # Encontrando Árvores não mapeadas durante as podas
            trees_found, trees_remove = unregistered_trees_found(trees=detect_distances_FN, size=int(prob * 50))
            detect_distances_FN = trees_remove

            # Verdadeiros Positivos (VP)
            ## Gerando aleatoriamente a distância de toque após a poda entre 2.0 e 2.5 metros
            detect_distances_VP[:select_vp] = np.random.uniform(low=2.0, high=2.5, size=select_vp)
            ## Adicionando as novas árvores mapeadas durante as podas
            detect_distances_VP = np.append(detect_distances_VP, trees_found)
            ## Aplicando a taxa de crescimento
            detect_distances_VP = apply_tree_growth(distances=detect_distances_VP,
                                                    growth_rate=growth_rate,
                                                    months=1)
            ## Ordenando pelas árvores mais críticas
            detect_distances_VP.sort()

            # Falsos Positivos (FP)
            ## Excluindo as árvores que foram visitadas
            detect_distances_FP = detect_distances_FP[select_fp:]
            ## Aplicando a taxa de crescimento
            detect_distances_FP = apply_tree_growth(distances=detect_distances_FP,
                                                    growth_rate=growth_rate,
                                                    months=1)
            ## Ordenando pelas árvores mais críticas
            detect_distances_FP.sort()

            # Falsos Negativos (FN)
            ## Aplicando a taxa de crescimento
            detect_distances_FN = apply_tree_growth(distances=detect_distances_FN,
                                                    growth_rate=growth_rate,
                                                    months=1)


        data['count_vp'].append(count_vp)
        data['count_fp'].append(count_fp)
        data['count_fn'].append(count_fn)
        data['critical_trees_not_pruned'].append(critical_trees_not_pruned)

    data['count_vp'] = np.array(data['count_vp'])
    data['count_fp'] = np.array(data['count_fp'])
    data['count_fn'] = np.array(data['count_fn'])
    data['critical_trees_not_pruned'] = np.array(data['critical_trees_not_pruned'])

    return data    
