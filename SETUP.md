# Instalação do estúdio (roteiro para o agente)

> **Para a pessoa:** abra esta pasta no Claude Code ou no Codex e escreva: **"Leia o SETUP.md e instale o estúdio."** O agente faz o resto e pede sua permissão antes de instalar qualquer coisa no sistema.

---

**Agente, siga estes passos em ordem.** Fale com a pessoa em português simples. Depois de cada etapa, diga em uma linha o que foi feito. Confira o comando de instalação atual no site oficial antes de rodar, porque as versões mudam. **Peça permissão antes de instalar qualquer coisa fora desta pasta.**

## 1. Conheça a pessoa e a máquina

- Pergunte:
  - o nome da pessoa e como ela prefere ser chamada;
  - que tipo de vídeo ela faz (anúncios, lançamentos, tutoriais, Reels...);
  - se ela é programadora ou prefere explicações sem jargão.
- Descubra:
  - o sistema (Windows, macOS ou Linux) e se é uma máquina local ou um ambiente de nuvem;
  - a placa de vídeo (`nvidia-smi`, ou Apple Silicon);
  - a memória e o disco livre (são precisos uns 10 GB).
- No Windows, verifique se o **Controle Inteligente de Aplicativos** está ligado, no registro `HKLM\SYSTEM\CurrentControlSet\Control\CI\Policy`, valor `VerifiedAndReputablePolicyState` (1 = ligado). Se estiver, aplique desde já as soluções da seção "Problemas conhecidos" do `AGENTS.md`.

## 2. Base do sistema (peça permissão)

| ferramenta | para quê |
|---|---|
| Node.js 22+ | HyperFrames, Remotion e Playwright |
| Git | versões e repositórios |
| Python 3.11 | voz, transcrição e IA de imagem |
| FFmpeg (com ffprobe) | cortar, juntar, converter, mixar e normalizar áudio |
| Google Chrome | render (no Windows com bloqueio de apps) e gravação de tela |

- **Windows:** `winget` (`OpenJS.NodeJS.LTS`, `Git.Git`, `Python.Python.3.11`, `Gyan.FFmpeg`, `Google.Chrome`).
- **macOS:** `brew` (`node`, `git`, `python@3.11`, `ffmpeg`).
- **Linux e nuvem:** `apt` (`nodejs`, `git`, `python3.11-venv`, `ffmpeg`).

Pule o que já estiver instalado. Depois de instalar, recarregue o PATH da sessão.

## 3. Dentro da pasta do estúdio

```bash
npm install                                  # HyperFrames 0.8.143, GSAP, Playwright
npx playwright install chromium              # no Linux: npx playwright install --with-deps chromium
python -m venv .venv                         # use o Python 3.11
.venv/bin/pip install -r requirements.txt    # Windows: .venv\Scripts\pip install -r requirements.txt
```

- **PyTorch** (para o Real-ESRGAN), conforme pytorch.org:
  - com NVIDIA, a versão com CUDA;
  - no Mac com chip Apple, o `pip install torch` normal (dispositivo `mps`);
  - sem placa, a versão CPU: `pip install torch --index-url https://download.pytorch.org/whl/cpu`.
- Teste os imports: `python -c "import torch, kokoro_onnx, faster_whisper, ctranslate2, cv2, spandrel"`. Se algum for bloqueado no Windows, veja os "Problemas conhecidos" do `AGENTS.md`.

## 4. Modelos de IA (para `modelos/`)

- `realesr-general-x4v3.pth`: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth (padrão, rápido).
- `RealESRGAN_x4plus.pth`: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth (pesado, só para imagem isolada).
- A voz do Kokoro é baixada sozinha no primeiro uso do `ferramentas/narrar.py` ou do `npx hyperframes tts`.
- O Whisper `small` também é baixado no primeiro uso.

## 5. Ligue as ferramentas ao agente

- Crie a variável de ambiente do usuário **`HYPERFRAMES_PYTHON`** apontando para o Python da `.venv`, com o caminho completo.
- **Skills do HyperFrames:**
  - no Claude Code: `claude plugin marketplace add heygen-com/hyperframes` e `claude plugin install hyperframes@hyperframes`;
  - no Codex ou em outro agente: `npx skills add heygen-com/hyperframes` (escolha o agente na lista) ou `npx hyperframes skills update`.
- Rode `npx hyperframes doctor` e resolva o que ele apontar.
- **Windows com bloqueio de apps:** crie também `HYPERFRAMES_BROWSER_PATH` apontando para o `chrome.exe` instalado.

## 6. Opcionais (pergunte se a pessoa quer)

- **Remotion**, vídeo em React para modelos repetidos:
  - `npx create-video@latest --yes --hello-world remotion` e `npx skills add remotion-dev/skills`;
  - **avise sobre a licença:** é grátis só para pessoa física e para empresa com até 3 funcionários.
- **Chatterbox**, voz mais expressiva (~4 GB):
  - numa venv separada, `.venv-chatterbox`, com `pip install chatterbox-tts`;
  - nunca na mesma venv do Real-ESRGAN, porque as versões do torch brigam.
- **ImageMagick**, só se a pessoa quiser montagens além do `folha.py`.

## 7. Crie o `MEU-ESTUDIO.md`

O `MEU-ESTUDIO.md` fica na raiz da pasta e não vai para o git. O `AGENTS.md` manda ler este arquivo antes de tudo. Inclua:
- **Quem usa:** nome, como chamar, que vídeos faz, nível técnico e preferências de voz e visual que surgirem.
- **A máquina:** sistema, processador, memória, placa de vídeo, nuvem ou local, e bloqueios encontrados com a solução aplicada.
- **Uma tabela das ferramentas instaladas:** versão, onde ficou e o comando para usar.
- **O desempenho medido nos testes:** segundos por quadro do Real-ESRGAN, tempo de render de 10 s de vídeo e tempo de uma narração.

## 8. Testes de fumaça (salve em `testes/`)

1. **Motion graphics:** `node ferramentas/novo-projeto.mjs teste deitado 10`, depois `npx hyperframes check` (0 erros) e o render do vídeo. Copie o MP4 para `testes/hyperframes.mp4` e faça a folha com `folha.py`. Olhe a folha.
2. **Narração com IA:** crie um roteiro de duas frases (uma delas: "Olá, [nome], o estúdio está pronto.") e rode `narrar.py`. As duas frases precisam conferir no Whisper.
3. **Trilha:** `music.py testes/trilha.wav 15 2.4 13`.
4. **Gravação de tela:** `gravar_tela.mjs https://example.com testes/tela.mp4 1280 720 6`.
5. **Real-ESRGAN:** gere um quadro 360×640 (`ffmpeg -f lavfi -i testsrc2=size=360x640 -frames:v 1 ...`), amplie 4× e anote o tempo por quadro.
6. **Remotion**, se foi instalado: renderize o exemplo para `testes/remotion.mp4`.

## 9. Relatório final

Diga, em linguagem simples:
- o que ficou instalado e o que falhou, com o motivo e o que fazer;
- quanto tempo o Real-ESRGAN leva por quadro nesta máquina;
- como começar: "me peça um vídeo, por exemplo: *faça um vídeo de 30 segundos em pé para Reels apresentando meu produto X*".
