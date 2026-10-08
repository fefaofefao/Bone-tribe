# Decisões de implementação

Registro das escolhas feitas onde o GDD (docs/GDD.md) é ambíguo ou silencioso.
Regra geral: a opção mais simples que siga o GDD.

## Projeto e build

- **Godot 4.7.2 estável** (versão estável mais recente disponível em 08/10/2026), renderizador
  *Compatibility* (OpenGL ES 3), que tem luz 2D e roda nos Android mais simples.
- **Resolução base 720x1280** em retrato, `stretch = canvas_items`, `aspect = expand`.
  As texturas são produzidas em 2x e desenhadas com escala 0,5.
- **Build do AAB**: GitHub Actions baixa o Godot e os templates oficiais, instala o
  template de build Android (gradle) e exporta `build/BoneTribe.aab`. Sem keystore de
  release nos secrets, o CI assina com uma chave temporária (o AAB serve para teste,
  não para a Play Store). Secrets esperados: `ANDROID_RELEASE_KEYSTORE_BASE64`,
  `ANDROID_RELEASE_KEYSTORE_USER`, `ANDROID_RELEASE_KEYSTORE_PASSWORD`.
- **Locale es_419**: o Godot normaliza `es_419` para `es`. O arquivo continua sendo
  `res://i18n/es_419.csv`, e a tradução gerada é registrada com o locale `es`
  (vale para toda a América Latina e para outros espanhóis como fallback).
- **i18n**: os três CSV em `res://i18n/` são a fonte da verdade. `tools/i18n.py`
  apenas insere linhas nos três de uma vez e valida chaves faltando ou vazias.
- **Fontes**: Fredoka (texto) e Pirata One (títulos), ambas SIL OFL, em `res://art/fonts/`.
- **Interface montada por código** a partir de um tema único (`Style`), com cenas
  `.tscn` enxutas. Isso evita arquivos de cena gigantes escritos à mão e mantém todos
  os textos vindo das chaves de tradução.

## Protótipo (Passo 2)

### Estrutura da partida
- **Andar = um evento.** O índice `n` das fórmulas é o número do evento na partida. Assim
  "inimigo do andar 1 com vida 34" e "chefes nos andares 10, 20 e 30" ficam coerentes:
  cada bloco de 10 andares termina num chefe. O protótipo tem 10 andares e o Rei Rato no 10º
  (`balance.json -> run.prototype_mode`).
- **Pesos do protótipo**: combate 60%, escolha 20%, baú 20% (`prototype_event_weights`).

### Equilíbrio (validado com `tests/BalanceSim.tscn`)
O GDD manda ajustar primeiro os multiplicadores 1,12 e 1,10. Valores atuais:

| Parâmetro | GDD | Atual | Motivo |
| --- | --- | --- | --- |
| Vida do inimigo | 30 × 1,12^n | 32 × 1,05^n | Andar 1 continua com 33,6 (34) de vida |
| Ataque do inimigo | 5 × 1,10^n | 5,238 × 1,05^n | Andar 1 continua com 5,5 de ataque |
| Chefe | 8× vida, 1,5× ataque | 5× vida, 1,2× ataque | Com 8× ninguém vencia o Rei Rato |
| XP por abate | — | 14 + 4n | O GDD não define; ~4 níveis por partida |
| Osso comum / raro | 25% / 5% | 35% / 8% | Mais ossos = o corpo muda mais por partida |
| Cura ao subir de nível | — | 25% da vida | Sem cura, as partidas acabavam no andar 7 |
| Rato-Esqueleto (lacaio) | — | 30% vida, 35% ataque | Invocados em grupo pelo Rei Rato |

Resultado da simulação (60 jogadores novos, gastando o pó no Ossuário entre partidas):
1ª vitória sobre o Rei Rato em média na **partida 2,5**; 16% vencem na 1ª partida e
80% até a 4ª. Meta do GDD: vencer o Rei Rato até a 3ª partida.

### Regras
- **Ossos têm atributos de base** além do efeito do GDD (braços dão ataque, pernas dão
  velocidade etc.), seguindo a tabela "O que define" de cada encaixe.
- **Defesa em %**: "+30% de defesa" vira +30 pontos de defesa (a defesa base é 0, então
  porcentagem sobre zero não faria nada). A redução segue o GDD: defesa ÷ (defesa + 50).
- **Sinergia Construto "+15% de escudo"**: escudo de 15% da vida no início do combate.
- **Trocar** um osso tritura automaticamente o antigo em pó de osso.
- **Braços**: o osso entra no primeiro braço vazio; com os dois ocupados, o jogador escolhe
  qual trocar ou tritura.
- **Opções ligadas ao corpo** só aparecem quando o osso está equipado e ganham destaque
  (botão cor de vela com o ícone do osso).
- **Alvo**: o Ossinho ataca o primeiro inimigo; tocar num inimigo muda o foco.
- **Golem Esquecido**: o escudo reduz o dano em 75% e quebra com 3 golpes no mesmo turno.
- **Dragão Ancião**: "defesa contra fogo" = ter qualquer osso Dragão ou Marinho.
- **Sem pernas** o Ossinho fica mais baixo e anda aos pulinhos; as pernas o erguem.
- **Nome da criatura**: os campos `name_part` e `adjective` do `bones.json` guardam *chaves*
  de tradução (a regra "todo texto visível em res://i18n/" vale sobre o prompt). Ossos básicos
  contam como encaixe vazio ("Osso"). A cauda vazia usa o adjetivo "Ossudo" (Bony/Huesudo).
  A ordem das palavras vem da chave `creature_name_format` (em inglês o adjetivo vem antes:
  "Venomous Wolf-Spider").
- **Compartilhar** salva o PNG 1080x1920 em `user://cards/`. O envio nativo para outros apps
  exige um plugin Android, que fica para quando os SDKs reais entrarem.
- **Modo demonstração**: sequência fixa em `balance.json -> demo`, escolhas automáticas,
  Ossinho reforçado e revive garantido, para gravar vídeos sem falhas.
