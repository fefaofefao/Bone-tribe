# Publicação na Google Play

Checklist para levar o Bone Tribe (com.bonetribe.game) do repositório até a loja. Dividido entre o que só o dono da conta pode fazer e o que o Claude Code faz no código.

## Como gerar o APK e o AAB

Sempre pelo GitHub Actions (workflow **Android AAB e APK**):

- **Teste:** qualquer push no repositório gera os artefatos `BoneTribe-apk` (instalar no celular) e `BoneTribe-aab` (enviar à Play Console). Ficam na aba *Actions* → execução → *Artifacts*.
- **Versão:** crie a tag `vX.Y.Z` (ex.: `v1.0.0`). O workflow usa esse número como `version/name`, gera os dois arquivos e anexa no *Release* da tag.
- O `version/code` sobe sozinho a cada execução (número da execução + 100), então nunca repete na Play Console.
- Sem a keystore de release nos *secrets*, o workflow assina com uma chave temporária nova a cada execução: serve para testar, mas o celular recusa instalar por cima da versão anterior (desinstale antes) e a Play Console recusa o AAB.

## Do seu lado (só você pode fazer)

### Contas e cadastros
- [ ] Criar a conta de desenvolvedor na Google Play Console (taxa única de US$ 25) e verificar identidade.
- [ ] Conferir se "Bone Tribe" está livre: busca na Google Play, domínio, INPI e USPTO (GDD, seção Visão geral).
- [ ] Criar o app na Play Console com o pacote **com.bonetribe.game** (não muda depois).

### Assinatura
- [ ] Gerar a chave de upload uma única vez e guardar em local seguro (perdeu = não atualiza o app):
  `keytool -genkeypair -v -keystore bonetribe-upload.keystore -alias bonetribe -keyalg RSA -keysize 2048 -validity 10000`
- [ ] Cadastrar no GitHub (*Settings → Secrets and variables → Actions*):
  - `ANDROID_RELEASE_KEYSTORE_BASE64` = saída de `base64 -w0 bonetribe-upload.keystore`
  - `ANDROID_RELEASE_KEYSTORE_USER` = `bonetribe` (o alias)
  - `ANDROID_RELEASE_KEYSTORE_PASSWORD` = a senha
- [ ] Ativar a *Assinatura de apps do Google Play* ao enviar o primeiro AAB.

### Privacidade e contato
- [ ] Revisar o rascunho `docs/privacy.html` (trocar `CONTATO_EMAIL`/`CONTACT_EMAIL` e `DATA`/`DATE`/`FECHA`).
- [ ] Hospedar a página num endereço público. Opção simples: GitHub Pages servindo a pasta `docs/` (repositório público, ou plano pago para repositório privado), ficando em `https://fefaofefao.github.io/bone-tribe/privacy.html`.
- [ ] Me passar o endereço e o e-mail de suporte para eu preencher `privacy_url` e `support_email` em `data/app.json` (o item "Privacidade" aparece no menu de Configurações assim que o endereço existir).

### Serviços reais (anúncios, compras, Firebase)
- [ ] AdMob: criar conta, o app e os blocos de anúncio (recompensado e intersticial). Me passar os IDs.
- [ ] Play Console → Produtos no app: cadastrar os produtos com **os mesmos IDs** de `data/shop.json` (`iap_kit24`, `iap_remove_ads`, `iap_gravedigger_card`, `iap_supporter`, `iap_diamonds_handful`, `iap_diamonds_sack`, `iap_diamonds_chest`, `iap_diamonds_vault`, `iap_skin_golden`, `iap_skin_neon`, `iap_skin_pirate`, `iap_skin_crystal`) e preços por país.
- [ ] Firebase: criar o projeto, registrar o app Android e baixar o `google-services.json` (**não** commitar; vai para um *secret*, que eu configuro no workflow).
- [ ] Conta de pagamentos (perfil de comerciante) na Play Console para receber as compras.

### Ficha da loja e políticas
- [ ] Colar os textos de `store/listing/` (pt-BR, en-US, es-419) na ficha da loja.
- [ ] Enviar ícone `store/icon_512.png`, gráfico de destaque `store/feature_graphic.png` e as capturas de `store/screenshots/` (no mínimo 2 por idioma; as de `es_ES_*` servem para es-419).
- [ ] Questionário de classificação de conteúdo (violência cartunesca leve, compras no app, anúncios).
- [ ] Seção *Segurança dos dados*: declarar ID de publicidade e dados de uso (AdMob/Firebase), compras (Play Billing), sem dados pessoais diretos, criptografia em trânsito, pedido de exclusão por e-mail.
- [ ] Público-alvo: 13+ (evita as regras do programa Famílias). Declarar que o app contém anúncios.
- [ ] Países e preço (gratuito).

### Testes
- [ ] Teste fechado: 12 testadores por 14 dias (exigência para contas pessoais novas) antes de pedir acesso à produção.
- [ ] Ler os 60 eventos nos 3 idiomas no celular (tom e humor).
- [ ] Teste de equilíbrio com 5 pessoas jogando 3 partidas cada.
- [ ] Arte final: ícone, Ossinho e chefes (os placeholders atuais têm o tamanho e o pivô finais; basta trocar os PNGs com o mesmo nome).
- [ ] Lançamento suave no Brasil e no México, depois global (GDD, Ordem de lançamento).

## Do meu lado (Claude Code)

### Feito
- [x] Versão automática (`version/code` e `version/name`) e Release com APK + AAB ao criar tag `v*`.
- [x] Ganchos de teste (`BT_*`) desligados em build de release (`Dev.env`).
- [x] Tela de créditos (autor, Godot MIT, fontes SIL OFL, apoiadores) e item de política de privacidade ligado a `data/app.json`.
- [x] Pasta `store/` fora do jogo exportado (`.gdignore` e filtro de exportação).
- [x] Textos da ficha nos 3 idiomas (`store/listing/`), ícone 512, gráfico de destaque 1024x500 e 24 capturas 1080x1920 (8 por idioma).
- [x] Rascunho da política de privacidade em 3 idiomas (`docs/privacy.html`).
- [x] Painel de combate refeito: cartões de inimigo com retrato, vida, estados e próxima habilidade; status do Ossinho; registro do combate; painel que se ajusta ao conteúdo.

### Quando você me passar os dados
- [ ] Preencher `privacy_url` e `support_email` em `data/app.json`.
- [ ] Trocar os serviços simulados (`scripts/services/`) pelos plugins reais: AdMob, Google Play Billing (plugin oficial Godot) e Firebase; ativar a permissão `INTERNET` no `export_presets.cfg` (hoje desligada, porque nada acessa a rede) e `AD_ID`.
- [ ] Ligar o `google-services.json` e os IDs do AdMob pelo workflow, a partir de *secrets*, sem commitar credenciais.
- [ ] Plugin Android de compartilhamento nativo e vídeo de 8 s do Cartão da Criatura (hoje a imagem é salva no aparelho).
- [ ] Validação de compras e horário do servidor no backend real (hoje simulados em `Backend`).
- [ ] Integrar a arte final quando chegar e regenerar as capturas (`tools/store_shots.sh`).
- [ ] Ajustar equilíbrio com base nos testes (`data/balance.json`).
