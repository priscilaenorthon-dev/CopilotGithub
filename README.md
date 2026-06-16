# 🎮 TBH Task Bar Hero — Bot de Automação

Bot Python com visão computacional para **TBH: Task Bar Hero** (Steam). Navega mapas automaticamente, rastreia cooldowns de baús azuis em tempo real e clica nos baús quando aparecem na tela.

---

## ▶ Como Usar

**1. Abra o TBH no seu computador**

**2. Dê duplo clique em `INICIAR.bat`**

O sistema vai:
- Verificar Python instalado
- Instalar dependências automaticamente
- Detectar o jogo
- Baixar assets do jogo (ícones de baús, itens)
- Abrir o painel de automação

**3. Na primeira vez:** siga o assistente de configuração para ensinar o bot a reconhecer os elementos da sua tela.

---

## 🧠 O que é Automático vs Manual

| Elemento | Como é configurado |
|---|---|
| Ícones de baús, itens, soulstones | ✅ Baixado automaticamente do CDN do jogo |
| Ícone do Portal | 📷 Você captura uma vez (30 segundos) |
| Cabeçalhos Act 1 / Act 2 / Act 3 | 📷 Você captura uma vez por act |
| Botões de estágio (1-7, 2-8, etc.) | 📷 Você captura os estágios que for usar |
| Janela do jogo | ✅ Detectada automaticamente |
| Cooldowns de baús | ✅ Rastreados automaticamente (12 min) |

---

## 📋 Funcionalidades

### Passo 1 — Configuração Visual
O bot usa **template matching** (OpenCV) para reconhecer elementos na tela. Na primeira abertura:
- Assets do jogo são baixados automaticamente
- O bot verifica o que está faltando
- Você só precisa capturar os elementos que ele não encontrar sozinho

**Como capturar um template:**
1. Clique no botão `📷 Capturar` ao lado do elemento
2. O painel some temporariamente
3. Clique e arraste ao redor do elemento na tela do jogo
4. O template é salvo automaticamente

### Passo 2 — Automação de Mapas
Farm loop que navega automaticamente entre estágios:
- Selecione os mapas na lista ou use um **preset** (Exp, Gold, Pets)
- Escolha quantas repetições (ou infinito)
- Clique **▶ INICIAR FARM**

### 🔵 Tracker de Baús Azuis
Caçada automática de baús azuis com cooldown de 12 minutos por estágio:

```
Estágio  │ Último Farm │ Próximo em │ Status
  1-9    │  14:32:01   │   00:00    │ ✅ PRONTO!
  2-8    │  14:20:00   │   03:41    │ ████░░ 3m 41s
  3-8    │     —       │   00:00    │ ✅ PRONTO!
```

**Funciona assim:**
1. Bot navega ao estágio com cooldown expirado
2. Aguarda o combate terminar
3. **Detecta o baú azul na tela e clica automaticamente**
4. Aviso sonoro + animação na interface
5. Timer reinicia por 12 minutos
6. Segue para o próximo estágio disponível

**Melhores rotas (por dificuldade de build):**
- Iniciante: 1-7 / 1-8 / 1-9
- Intermediário: 1-9 / 2-7 / 2-8
- Avançado: 1-9 / 2-8 / 3-8
- Expert: 1-9 / 2-8 / 3-8 / 3-9

---

## 📁 Estrutura do Projeto

```
tbh_automation/
├── INICIAR.bat              ← Clique aqui para começar
├── launcher.py              ← Painel principal (gerado pelo INICIAR.bat)
├── main.py                  ← Uso via linha de comando
│
├── config/
│   ├── settings.toml        ← Configurações (delays, threshold, etc.)
│   └── maps.toml            ← Estágios e presets de farm
│
├── templates/               ← Imagens de referência (já incluídas!)
│   ├── ui/                  ← Ícones da interface (portal, baús, etc.)
│   │   ├── blue_chest_icon.png   ← Baú azul (Stage Boss)
│   │   ├── chest_act_boss.png    ← Baú do Act Boss
│   │   ├── soulstone_*.png       ← Soulstones por dificuldade
│   │   └── ...
│   ├── items/               ← Sprites de itens e materiais
│   ├── portal_menu/         ← Cabeçalhos "Act 1", "Act 2", "Act 3"
│   └── stages/              ← Botões de estágio no menu Portal
│
├── tbh/                     ← Módulos do bot
│   ├── window.py            ← Detecção da janela do jogo (pywin32)
│   ├── capture.py           ← Captura de tela (mss)
│   ├── vision.py            ← Reconhecimento visual (OpenCV)
│   ├── controller.py        ← Controle de mouse (PyAutoGUI)
│   ├── state.py             ← Estado do jogo (FSM)
│   ├── navigator.py         ← Navegação entre estágios
│   ├── tracker.py           ← Cooldowns e estatísticas de baús
│   └── config.py            ← Leitura de configuração
│
├── scripts/
│   ├── download_assets.py   ← Baixa sprites do CDN do jogo
│   ├── capture_templates.py ← Captura manual com hotkey F9
│   └── debug_vision.py      ← Debug visual dos templates
│
├── tracker_data.json        ← Dados persistentes dos cooldowns
└── requirements.txt         ← Dependências Python
```

---

## ⚙️ Configuração Avançada

### `config/settings.toml`
```toml
[vision]
match_threshold = 0.80    # Sensibilidade (0.7 = mais permissivo, 0.9 = mais exigente)

[timing]
portal_open_wait_ms = 600      # Espera após clicar no portal
stage_click_wait_ms = 800      # Espera após selecionar estágio
retry_attempts = 5             # Tentativas por navegação

[window]
process_name = "TBH.exe"
dpi_scale = 1.0                # Ajuste se usar DPI alto (ex: 1.25 para 125%)
```

### `config/maps.toml`
```toml
[chest_hunting]
default_route = ["1-9", "2-8", "3-8"]    # Rota padrão de baús
cooldown_minutes = 12                     # Cooldown por estágio
```

---

## 🔧 Linha de Comando

```bash
python main.py --list-stages          # Lista todos os estágios
python main.py --list-presets         # Lista presets de farm
python main.py --stage 2-4            # Navega uma vez para 2-4
python main.py --farm exp_farm        # Farm loop com preset
python main.py --farm 1-7,1-8 --loop  # Lista custom, infinito
python main.py --gui                  # Abre o painel gráfico
```

---

## 🐛 Solução de Problemas

| Problema | Solução |
|---|---|
| "Jogo não detectado" | Abra o TBH antes de iniciar o bot |
| Template não encontrado | Clique `📷 Capturar` e recapture o elemento |
| Bot clica no lugar errado | Ajuste `match_threshold` para 0.75 em `settings.toml` |
| Bot não encontra o baú | O baú pode não ter dropado; é chance-based |
| Erro de DPI | Ajuste `dpi_scale = 1.25` em `settings.toml` |
| Python não encontrado | Instale em python.org marcando "Add to PATH" |

---

## 📦 Assets Incluídos

Sprites baixados automaticamente do CDN oficial do jogo:

| Arquivo | Descrição |
|---|---|
| `blue_chest_icon.png` | Baú azul (Stage Boss Box) |
| `chest_act_boss.png` | Baú do chefe de ato (vermelho) |
| `soulstone_normal/nightmare/hell/torment.png` | Soulstones |
| `gold_icon.png` | Ícone de gold |
| `gem_ruby/sapphire/topaz/emerald/amethyst.png` | Gemas por raridade |
| `scroll_common/uncommon/rare.png` | Scrolls de inscrição |
| `wood/stone/leather/copper.png` | Materiais de craft |

---

## 📋 Requisitos

- Windows 10/11
- Python 3.10+
- TBH: Task Bar Hero (Steam, gratuito)
- Conexão com a internet (apenas para download inicial de assets)
