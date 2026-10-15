# Questionário — Bone Tribe

Respostas baseadas no código do jogo (versão 1.1.0). "Não sei" = informação que não está no repositório.

## Gerais

1. **Países liberados:** não sei (configurado na Play Console). O jogo está em pt-BR, inglês e espanhol.
2. **Vídeos por semana e redes:** não sei.
3. **Dados reais de Firebase/AdMob:** nenhum disponível. O Firebase só entrou no build de 13/10 (versão 1.1.0); não tenho acesso aos painéis. Retenção, eCPM e tempo de sessão: não sei.
4. **Mediação do AdMob:** pelo código, não (só AdMob, sem adaptadores de outras redes). Se houver mediação, é configuração do painel do AdMob, que não consigo ver.
5. **Data prevista de produção:** não sei.
6. **Verba:** decisão sua; sem informação.

## Bone Tribe

**7. Rewarded (por vontade própria): 5 pontos**

| Ponto | Limite |
|---|---|
| Reviver ao morrer | 1 por partida |
| Dobrar o pó de osso no fim da partida | 1 por partida |
| Trocar as opções de bônus ao subir de nível | 3 por partida |
| Baú extra | 3 por dia |
| Diamantes grátis na loja (5 cada) | 3 por dia |

Máximo: 5 por partida + 6 por dia.

**8. Intersticial:** a partir da 3ª partida, no máximo 1 a cada 3 minutos, sempre entre partidas (ao voltar para a tela inicial). Na prática, cerca de 1 por partida. **Sem banner.**

**9. Compras** (preços BRL de referência; os preços finais por país vêm da Play Console)

| Item | Preço | Conteúdo |
|---|---|---|
| Sem anúncios | R$ 9,90 | Remove os intersticiais (oferta aparece após 10 intersticiais) |
| Kit das primeiras 24h | R$ 4,90 | 300 diamantes, relíquia, skin e 1.000 de pó |
| Cartão do Coveiro (assinatura 30 dias) | R$ 9,90 | 30 diamantes + 300 de pó por dia, 1 reviver grátis por dia, 1 baú raro por semana |
| Apoiador | R$ 24,90 | Skin e nome nos créditos (só após vencer o Dragão) |
| 100 diamantes | R$ 2,90 | |
| 550 diamantes | R$ 9,90 | |
| 1.200 diamantes | R$ 19,90 | |
| 2.600 diamantes | R$ 39,90 | |
| Skins (Dourada, Neon, Pirata, Cristal) | R$ 4,90 a R$ 9,90 | |

Itens comprados com diamantes (sem dinheiro real): reviver extra, 1.000 de pó, osso inicial raro, baú, relíquia e a companheira Lumi. Todo dia há 3 ofertas com 20% a 50% de desconto.

**10. Conteúdo**
- 20 torres de 30 andares (600 andares) e 1 andar secreto.
- Cada partida dura poucos minutos.
- Na simulação (jogador que só melhora pelo Ossuário): Torre 10 por volta da partida 180; Torre 20 depois de 400 partidas. Quem usa relíquias e companheiros avança mais rápido.
- Em horas: não sei (depende do tempo real de cada partida, que virá do Firebase).

**11. Motivos para voltar**
- Calendários de login de 7 e de 28 dias.
- 3 ofertas diárias na loja.
- Baú e diamantes por anúncio, com limite diário.
- Recompensa diária da assinatura.
- O Caçador de Ossos rouba um osso quando o jogador morre, e dá para recuperá-lo.
- **Não tem:** missões, eventos com data, notificações push nem ganho offline.

**12. Tamanho e Android mínimo**
- APK universal: cerca de 68 MB. Pela Play (AAB), o download por aparelho deve ser menor (não medido).
- Android mínimo: API 24 (Android 7.0), padrão do Godot 4.7. Target: API 36.

**13. Títulos na loja** (fichas em `store/listing/`; se mudaram na Play Console, vale o de lá)

| Idioma | Título |
|---|---|
| pt-BR | Bone Tribe: RPG de Esqueleto |
| Inglês | Bone Tribe: Skeleton Roguelike |
| Espanhol | Bone Tribe: RPG de Esqueleto |

Dentro do jogo, o nome é só "Bone Tribe".
