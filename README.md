# Simulação Monte Carlo no ciclo de podas das árvores críticas

## Parâmetros da Simulação
- ( $N$ ): Número de árvores ($N = 1000$).
- ( $T$ ): Número de meses na simulação ( $T = 12$).
- ( $\text{critical_distance}$): Distância crítica de toque em metros ($ \text{critical_distance} = 1.0 $).
- ( $\text{n_simulation} $): Quantidade de eventos ($ \text{n_simulation} = 500 $).
- ($ \text{growth_rate} $): Crescimento mensal em metros ($ \text{growth_rate} = 0.2 $).
- ($ \text{total_tree} $): Total de árvores podadas por mês ( $\text{total_tree} = 400 $).

## Passos da Simulação

1. **Gerar a Matriz de Confusão:**
   - Dado a precisão ( $\text{PRECISION}$ ) e o recall ($ \text{RECALL}$), calcular Verdadeiros Positivos ($ VP$ ), Falsos Positivos ($ FP$)), e Falsos Negativos ($ FN $):
     
     \begin{align*}
     VP &= \lceil \text{RECALL} \times N \rceil, \\
     FP &= \lceil \frac{VP \times (1 - \text{PRECISION})}{\text{PRECISION}} \rceil, \\
     FN &= \lceil \frac{VP \times (1 - \text{RECALL})}{\text{RECALL}} \rceil.
     \end{align*}
     

2. **Simulação dos Eventos:**
   - Para cada uma das ($ \text{n_simulation} $) simulações:
     - Gerar distâncias aleatórias para $VP$, $FP$ e $FN$.
     - Adicionar erro ($\text{MAE}$) às distâncias detectadas de $VP$.
     - Ordenar e filtrar distâncias detectadas menores que a distância crítica.
     - Calcular o número de árvores críticas de cada mês para os $VP$, $FP$ e $FN$.
     - Aplicar o crescimento mensal às distâncias detectadas após a poda.
     - Selecionar aleatoriamente árvores não mapeadas e adicioná-las ao conjunto de árvores mapeadas.

3. **Cálculo dos Resultados:**
   - Para cada mês, calcular:
     - O número de podas reais ($t_{\text{VP}}$), chamadas falsas ($t_{\text{FP}}$) e árvores não mapeadas ($t_{\text{FN}}$).
     - O número de árvores críticas não podadas.
     - Crescimento das árvores.
     - Repetir o processo para todos os meses ($T$).

## Formulação Matemática

## Inicialização
Calcula-se a distância de toque dos $VP$, $FP$ e $FN$.

\begin{align*}
     \text{dist_VP} \sim \mathcal{U}(0, \text{dist_max}) \\
     \text{dist_FP} \sim \mathcal{U}(0, \text{dist_max}) \\
     \text{dist_FN} \sim \mathcal{U}(0, \text{dist_max})
\end{align*}

Onde $\text{dist_max}$ é a distância máxima dentro da faixa de risco e $ \mathcal{U}(a, b) $ é a distribuição uniforme entre $ a $ e $ b $.

## Para cada simulação:
1. **Adicionar erro às distâncias detectadas:**

\begin{align*}
     \text{dist_det_VP} = \text{dist_VP} + \mathcal{N}(0, \text{MAE})
\end{align*}

Onde  $\mathcal{N}(\mu, \sigma)$ é a distribuição normal com média $ \mu $ e desvio padrão $ \sigma $.

2. **Filtrar e quantificar as árvores críticas:**

Árvores mapeadas corretamente e críticas ($t_{\text{VP}}$):
\begin{align*}
     \text{mask_VP} &= \text{dist_det_VP} < \text{critical_distance} \\
     t_{\text{VP}} &= \sum \text{mask_VP}
\end{align*}

Árvores inexistentes e dita crítica ($t_{\text{FP}}$):
\begin{align*}
     \text{mask_FP} &= \text{dist_det_FP} < \text{critical_distance} \\
     t_{\text{FP}} &= \sum \text{mask_FP}
\end{align*}

Árvores não mapeadas e crítica ($t_{\text{FN}}$):
\begin{align*}
     \text{mask_FN} &= \text{dist_det_FN} < \text{critical_distance} \\
     t_{\text{FN}} &= \sum \text{mask_FN}
\end{align*}
   

3. **Quantidade de chamados de podas:**

Consideramos que a equipe não seja eficiente ou que exista problemas no qual não seja possível realizar todo o planejamento de podas no mês.

Inicialmente é feito a seleção do quantitativo de chamados de árvores críticas a serem podadas.
\begin{align*}
   \text{size} &= \min(\text{total_tree}, t_{\text{VP}} + t_{\text{FP}})
\end{align*}

Em seguida estimamos a eficiência da equipe no mês, a fim de chegar no quantitativo final
\begin{align*}   
   \text{prob} &\sim \mathcal{U}(\text{prob_min}, 1.0) \\
   \text{size} &= \lfloor \text{prob} \times \text{size} \rfloor
\end{align*}

Onde $ \text{prob_min} $ corresponde a probabilidade mínima de eficiência do atendimento dos chamados de poda.

Por exemplo se a meta é de atender 400 chamados de podas no mês, e considerando $ \text{prob_min} = 0.75$, então o quantitativo final pode está entre 300 e 400 chamados a serem atendidos.

4. **Selecionar árvores para poda:**
   
\begin{align*}
   \text{select_VP} = \mathcal{B}(p = \frac{t_{\text{VP}}}{t_{\text{VP}} + t_{\text{FP}}}, \text{size})
\end{align*}

   
Onde $ \mathcal{B}(p, n) $ é a distribuição binomial com probabilidade $ p$ e $ n $ tentativas.

5. **Crescimento das árvores:**
   
\begin{align*}
      \text{dist_det_VP} &= \text{dist_det_VP} - \text{growth_rate} \\
      \text{dist_det_FP} &= \text{dist_det_FP} - \text{growth_rate} \\
      \text{dist_det_FN} &= \text{dist_det_FN} - \text{growth_rate}
\end{align*}

6. **Atualização dos resultados:**

\begin{align*}
    \text{count_vp}[m] &= \text{select_VP} \\
    \text{count_fp}[m] &= \text{size} - \text{select_VP} \\   
    \text{count_fn}[m] &= t_{\text{FN}} \\   
   \text{critical_trees_not_pruned}[m] &= \max(0, (t_{\text{VP}} + t_{\text{FN}}) - \text{select_VP})
\end{align*}
