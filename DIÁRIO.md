# Diário de Desenvolvimento — Chuva de Meteoros

Gustavo Henrique Alves Costa · Luis Otavio Garcia Santos / Disciplina de Computação Gráfica · Professor Pedro Cândido

## 1. Visão geral

O projeto é um jogo 2D de nave feito em Python 3 com a biblioteca Pygame. O jogador pilota uma nave, destrói asteroides, coleta power-ups e sobrevive enquanto a dificuldade aumenta. Todo o visual é gerado por código, sem arquivos de imagem ou som externos.

A construção foi feita em passos pequenos. Em cada passo o jogo já rodava sozinho, e só então avançávamos para o seguinte. Assim, cada novo conceito de Computação Gráfica entrou isolado e pôde ser testado e compreendido antes de somar complexidade.

| Marco | Passos | Resultado |
| --- | --- | --- |
| Etapa 1 · Concepção | Planejamento | Tema, regras, estados e escopo definidos |
| Etapa 2 · Protótipo jogável | 1 a 6 | Nave, tiros, asteroides e colisões funcionando |
| Etapa 3 · Versão intermediária | 7 a 11 | Efeitos visuais, power-ups, estados, HUD e progressão |
| Etapa 4 · Versão final | 12 | Testes, documentação, apresentação e pacote de entrega |

## 2. Etapa 1 · Concepção


**O que foi feito.** Escolhemos o gênero arcade de nave por permitir aplicar, em um escopo pequeno, vários conceitos da disciplina: movimento, animação, colisões, partículas, parallax e interface. Definimos o objetivo (fazer o maior número de pontos antes de perder as 3 vidas), a mecânica principal (desviar e atirar nos asteroides) e os quatro estados do jogo: menu, jogando, pausado e fim.

**Referências estudadas.** Documentação oficial do Pygame (superfícies, eventos, tempo, `draw` e `transform`) e os repositórios indicados no enunciado. 

**Decisões.** Não usar nenhum recurso externo: sprites e efeitos seriam desenhados por código. Isso simplifica a instalação e elimina dúvidas de licença. Também decidimos separar o código em classes pequenas (nave, tiro, asteroide, partículas, estrelas) e uma classe `Jogo` para o laço e os estados.


## 3. Etapa 2 · Protótipo jogável

### Passo 1 · Janela e laço principal


Criamos a janela de 800 x 600 e o laço que se repete 60 vezes por segundo, com três fases: ler eventos, atualizar o estado e desenhar. Usamos `relogio.tick(FPS)` para limitar a taxa de quadros e calcular o `dt` (tempo do quadro em segundos). Para testar, movemos uma bolinha com `posição += velocidade * dt`.

*Conceitos:* ciclo do jogo, sistema de coordenadas (origem no canto superior esquerdo, y cresce para baixo), movimento independente da taxa de quadros.

### Passo 2 · Constantes e função de colisão



Organizamos os imports, as constantes (tamanho da tela, cores, nomes dos estados) e escrevemos `colidem()`: dois círculos colidem quando o quadrado da distância entre os centros é menor que o quadrado da soma dos raios. Comparar os quadrados evita a raiz quadrada. Testamos com um círculo seguindo o mouse, que mudava de cor ao encostar em outro.

*Conceitos:* vetores com `Vector2`, colisão círculo x círculo.

### Passo 3 · A nave


Desenhamos a nave com polígonos e um círculo numa `Surface` transparente, uma única vez, e passamos a apenas copiá-la com `blit` a cada quadro. O movimento usa setas ou WASD, com o vetor de direção normalizado para que a diagonal não seja mais rápida. Os limites da tela foram aplicados com `max` e `min`. Desenhamos também o círculo de colisão para visualizar a hitbox, deliberadamente menor que o sprite.

*Conceitos:* sprites por primitivas, composição por camadas, normalização de vetores, limites de tela.

### Passo 4 · Tiros

Criamos a classe `Tiro` e o disparo com a barra de espaço. Um tempo de recarga de 0,22 s controla a cadência. Cada tiro tem um marcador `viva`, que vira falso quando sai da tela, e uma lista nova só com os tiros vivos é montada a cada quadro. Isso evita remover itens de uma lista enquanto ela é percorrida.

### Passo 5 · Asteroides

Cada asteroide é um polígono de 9 a 12 pontos a distâncias aleatórias do centro, com três crateras, gerado proceduralmente. O sprite é desenhado uma vez e girado a cada quadro com `transform.rotate`. Os asteroides nascem acima da tela em intervalos aleatórios, rebatem nas laterais e são descartados ao sair embaixo. O tamanho define a resistência (1 a 3 de vida).

*Conceitos:* geração procedural, transformação de rotação, uso de `cos` e `sin` para posicionar vértices.

### Passo 6 · Colisões

Aplicamos `colidem()` em três situações: tiro contra asteroide, nave contra asteroide e nave contra power-up. Asteroides grandes se dividem em dois menores ao serem destruídos. Ao ser atingida, a nave perde uma vida e ganha 2 s de invulnerabilidade, durante os quais pisca.

## 4. Etapa 3 · Versão intermediária

### Passo 7 · Estrelas com parallax

Criamos três camadas de estrelas com velocidades diferentes. Também deslocamos as estrelas no eixo X em sentido contrário ao movimento da nave, o que reforça a sensação de profundidade.

### Passo 8 · Partículas


Cada partícula tem posição, velocidade e tempo de vida. Ao envelhecer, ela diminui e escurece, produzindo o efeito de explosão se dissipando. Usamos o sistema nas explosões, nos impactos dos tiros e no rastro do motor da nave.

### Passo 9 · Animação, inclinação e power-ups


A chama da nave ganhou três quadros, trocados 15 vezes por segundo. A nave se inclina levemente ao virar, com interpolação suave até o ângulo alvo. Adicionamos dois power-ups: escudo (E) e tiro triplo (T), cada um com duração de 8 s.

### Passo 10 · Estados e menu

Implementamos os quatro estados (menu, jogando, pausado e fim). O tratamento de teclas depende do estado atual, o que permite pausar, reiniciar, voltar ao menu e jogar de novo sem editar o código.

### Passo 11 · HUD, progressão, recorde e câmera

O HUD mostra pontos, recorde, nível, vidas e o tempo dos power-ups. A cada 500 pontos o nível sobe: os asteroides ficam mais rápidos e nascem com mais frequência. O recorde é salvo em `recorde.json`, com tratamento de erro caso não haja permissão de escrita. Para dar peso aos impactos, a cena é desenhada numa superfície à parte e copiada para a tela com um pequeno deslocamento aleatório (tremor de câmera), enquanto o HUD permanece fixo por cima.

## 5. Etapa 4 · Versão final

### Passo 12 · Testes, documentação e entrega

Revisamos o jogo com o checklist do enunciado, escrevemos o README com instruções de instalação, execução, controles e estrutura, criamos o `requirements.txt`, listamos os créditos e a declaração de uso de IA, preparamos a apresentação e gravamos um vídeo curto de segurança.

## 6. Registro de testes

| Teste
| --- | 
| Controles (setas, WASD, espaço, P, Esc, Enter) 
| Limites da tela (nave e asteroides)
| Colisões (tiro, nave, power-up) 
| Pausa e retomada
| Fim de jogo e reinício 
| Recorde salvo e carregado 
| Subida de nível 
| Instalação em ambiente limpo 

## 7. Decisões técnicas e problemas resolvidos

- **Velocidade dependente do FPS.** O movimento passou a usar `dt`, limitado a 0,05 s para evitar saltos após travadas.
- **Diagonal mais rápida.** O vetor de direção é normalizado antes de multiplicar pela velocidade.
- **Colisão injusta.** Os círculos de colisão são menores que os desenhos, para que encostões nas pontas não tirem vida.
- **Remoção durante a iteração.** Cada objeto tem um marcador `viva`, e as listas são refeitas só com os vivos.
- **Desempenho de desenho.** Sprites são gerados uma vez e apenas copiados ou girados a cada quadro.
- **Estados.** Os estados são constantes, o que evita erros de digitação em textos soltos.
- **Caminhos.** O recorde é gravado em um caminho relativo à pasta do jogo, e não há arquivos externos a carregar.

## 8. Uso de ferramentas de IA

Usamos o Claude (Anthropic) para gerar o código-base e os comentários explicativos, e para orientar a explicação passo a passo da construção. Reconstruímos o código em etapas no VS Code, estudando cada trecho. Validamos o resultado executando o jogo e realizando os testes da seção 6. 