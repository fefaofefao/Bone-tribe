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

### AdMob (IDs reais)
- [ ] No AdMob: criar o app Android (pacote com.bonetribe.game) e 2 blocos: **Premiado** (recompensado) e **Intersticial**.
- [ ] No GitHub: *Settings → Secrets and variables → Actions → aba Variables → New repository variable*, criar:
  - `ADMOB_APP_ID` = ID do app (formato `ca-app-pub-XXXXXXXXXXXXXXXX~YYYYYYYYYY`, com **til**)
  - `ADMOB_REWARDED_ID` = bloco premiado (`ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY`, com **barra**)
  - `ADMOB_INTERSTITIAL_ID` = bloco intersticial (mesmo formato)
- [ ] Rodar o workflow de novo (*Actions → Android AAB e APK → Run workflow*, ou criar a tag `v1.0.0`). Sem essas variáveis o build sai com os IDs de **teste** do Google (anúncios de teste, sem receita), e o log do workflow avisa.
- [ ] No AdMob, em *Privacidade e mensagens*, criar a mensagem de consentimento GDPR (o jogo já mostra o formulário quando o país exige) e publicar o `app-ads.txt` no site de desenvolvedor informado na Play Console.
- [ ] Não clicar nos próprios anúncios reais. Para testar no seu celular, use o APK com IDs de teste ou cadastre o aparelho como dispositivo de teste no AdMob.

### Firebase (Analytics + Remote Config)
O código já está pronto e desligado; ele liga sozinho quando o secret existir.
- [ ] Em https://console.firebase.google.com: **Adicionar projeto** (pode usar o mesmo projeto do Google Analytics; ative o Google Analytics quando perguntar).
- [ ] No projeto: **Adicionar app → Android**, pacote `com.bonetribe.game`, apelido "Bone Tribe".
- [ ] Ainda no cadastro do app, informe o **SHA-1** da chave de upload: `keytool -list -v -keystore bonetribe-upload.keystore -alias bonetribe` (e, depois de publicar, também o SHA-1 da "chave de assinatura do app" que aparece na Play Console em *Integridade do app*).
- [ ] Baixe o `google-services.json` e cole **o conteúdo inteiro** num secret do GitHub chamado `FIREBASE_GOOGLE_SERVICES_JSON` (*Settings → Secrets and variables → Actions → Secrets*). Não coloque o arquivo no repositório.
- [ ] Rode o workflow de novo. No log, o passo "Firebase" mostra o nome do projeto; sem o secret aparece um aviso.
- [ ] Vincule o Firebase ao **AdMob** (AdMob → Configurações do app → Vincular ao Firebase) e à **Play Console** (Firebase → Configurações do projeto → Integrações → Google Play). Assim a receita de anúncios e compras aparece no Firebase sem código extra.
- [ ] Teste com o celular no **DebugView**: `adb shell setprop debug.firebase.analytics.app com.bonetribe.game` e abra o jogo; os eventos aparecem em segundos (sem isso, demoram algumas horas para aparecer nos relatórios).
- [ ] Atualize a seção *Segurança dos dados* da Play Console: o app passa a coletar "Atividade no app", "Identificadores do dispositivo" e "Diagnóstico" (finalidade: análise), criptografados em trânsito.

### Produtos no app (Play Console → Monetizar → Produtos → Produtos no app)
Cadastrar **todos como produtos únicos (in-app), nenhum como assinatura**, com os mesmos IDs de `data/shop.json` e ativá-los:
- Consumíveis (podem ser comprados de novo; o jogo consome): `iap_diamonds_handful`, `iap_diamonds_sack`, `iap_diamonds_chest`, `iap_diamonds_vault` e `iap_gravedigger_card` (Cartão do Coveiro = passe de 30 dias, comprado de novo quando acaba).
- Permanentes (comprados uma vez; restaurados ao reinstalar): `iap_kit24`, `iap_remove_ads`, `iap_supporter`, `iap_skin_golden`, `iap_skin_neon`, `iap_skin_pirate`, `iap_skin_crystal`.
- [ ] Os preços exibidos no jogo passam a vir da Play Store, na moeda do jogador.
- [ ] Compras só funcionam em versões instaladas pela Play Store (faixa de teste interno/fechado). Adicione seu e-mail em *Configuração → Teste de licença* para comprar sem ser cobrado.
- [ ] Conta de pagamentos (perfil de comerciante) na Play Console para receber as compras.

### Ficha da loja e políticas
- [ ] Colar os textos de `store/listing/` (pt-BR, en-US, es-419) na ficha da loja.
- [ ] Enviar ícone `store/icon_512.png`, gráfico de destaque `store/feature_graphic.png` e as capturas de `store/screenshots/` (no mínimo 2 por idioma; as de `es_ES_*` servem para es-419).
- [ ] Questionário de classificação de conteúdo (violência cartunesca leve, compras no app, anúncios).
- [ ] Seção *Segurança dos dados*: declarar ID de publicidade, interações com anúncios e diagnóstico (AdMob), compras (Play Billing), sem dados pessoais diretos, criptografia em trânsito, pedido de exclusão por e-mail.
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
- [x] AdMob real (plugin Poing AdMob 5.1.0): consentimento UMP/GDPR, recompensado e intersticial pré-carregados, item "Privacidade dos anúncios" nas Configurações quando o país exige. IDs pelas variáveis `ADMOB_*`.
- [x] Google Play Billing real (plugin oficial 3.3.0): preços da loja, consumo/reconhecimento antes de entregar, compras pendentes e restauração de compras permanentes.
- [x] Horário pela rede (cabeçalho `Date` de um servidor do Google) e proteção contra voltar o relógio: calendários de login, ofertas do dia e Kit 24h não liberam antes da hora.
- [x] Compartilhamento nativo do Cartão da Criatura (menu "Compartilhar" do Android com imagem, texto e link da loja).
- [x] Permissões de internet e estado da rede; APK e AAB gerados com Gradle (exigência dos plugins).

### Quando você me passar os dados
- [ ] Preencher `privacy_url` e `support_email` em `data/app.json`.
- [x] Firebase Analytics + Remote Config prontos no código (plugin `addons/bonetribe_firebase`, provedor `scripts/services/firebase_backend_provider.gd`); ligam quando o secret `FIREBASE_GOOGLE_SERVICES_JSON` existir.
- [ ] Vídeo de 8 s do Cartão da Criatura (exige codificador nativo).
- [ ] Validação de compras num servidor próprio (hoje a confirmação é a da Google Play no aparelho).
- [ ] Integrar a arte final quando chegar e regenerar as capturas (`tools/store_shots.sh`).
- [ ] Ajustar equilíbrio com base nos testes (`data/balance.json`).
