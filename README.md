# Chuva de Meteoros

Jogo 2D de nave feito com **Python 3** e **Pygame** (Projeto Avaliativo de Computação Gráfica).
Pilote a nave, destrua asteroides, colete power-ups e sobreviva o máximo possível.
Todo o visual é gerado por código: não há imagens nem sons externos.

## Requisitos e instalação
- Python 3.9 ou superior (testado com Pygame 2.6.1)

```bash
python -m venv venv
source venv/bin/activate       
pip install -r requirements.txt
python main.py
```

## Controles
| Tecla | Ação |
|---|---|
| Setas ou WASD | Mover a nave |
| Espaço (segurar) | Atirar |
| P ou ESC | Pausar / continuar |
| Enter | Iniciar / jogar de novo |
| R / M (na pausa) | Reiniciar / voltar ao menu |

## Regras
- Você começa com 3 vidas. Bater em um asteroide tira 1 vida (e dá 2 s de invulnerabilidade).
- Asteroides grandes se dividem em dois menores ao serem destruídos.
- A cada 500 pontos sobe o nível: asteroides ficam mais rápidos e mais frequentes.
- Power-ups (12% de chance ao destruir um asteroide): **E** escudo (8 s) e **T** tiro triplo (8 s).
- O recorde é salvo em `recorde.json`.

## Estados do jogo
`MENU -> JOGANDO <-> PAUSADO` e `JOGANDO -> FIM -> (JOGANDO | MENU)`

## Técnicas de Computação Gráfica
1. **Parallax** em 3 camadas de estrelas (`CampoEstrelas`).
2. **Sistema de partículas** com fade-out (`Particulas`).
3. **Animação por quadros** da chama da nave (`criar_frames_nave`).
4. **Transformações**: rotação dos asteroides e inclinação da nave (`pygame.transform.rotate`), escala do ícone de vida (`smoothscale`), vetores rotacionados no tiro triplo.
5. **Geração procedural** do formato dos asteroides (`Asteroide._gerar_sprite`).
6. **Câmera com tremor** e **composição por camadas** (cena separada do HUD em `Jogo.desenhar`).

## Colisões
Círculo x círculo: colidem quando `distância² < (r1 + r2)²` (função `colidem`).
Limites da tela: a nave é limitada por `max/min`; asteroides rebatem nas laterais.

## Estrutura
```
chuva_de_meteoros/
├── main.py            # todo o código (efeitos, entidades, jogo)
├── requirements.txt
├── README.md
├── CREDITOS.md
└── recorde.json       # criado automaticamente
```

## Problemas conhecidos
- Sem áudio. Sem suporte a controle (gamepad).
