# Estúdio de Vídeo com IA

Um estúdio de edição de vídeo completo para usar com uma **IA de programação**, como o **Claude Code** ou o **Codex**, no seu computador ou na nuvem. Você pede o vídeo em português. A IA escreve o roteiro, monta as animações, gera a narração, coloca trilha e efeitos, confere quadro a quadro e entrega o MP4.

Todas as ferramentas são gratuitas e de código aberto, e rodam na sua máquina. A IA só coordena o trabalho.

## O que ele faz

| | |
|---|---|
| 🎬 **Motion graphics** | Vídeos de lançamento e anúncios em HTML + GSAP com o [HyperFrames](https://github.com/heygen-com/hyperframes), deitados (1920×1080) ou em pé (1080×1920, para Reels, TikTok e Shorts). |
| 🎙️ **Narração com IA** | Voz em português com o Kokoro (`pf_dora`, `pm_alex`, `pm_santa`). Um comando gera, masteriza e confere cada frase com o Whisper, e avisa quando a IA pronunciou errado. |
| 🎵 **Trilha e efeitos** | Trilha original gerada no computador, sem direitos de terceiros, mais efeitos sonoros (whoosh, pop, impact...) no tempo da batida, com o volume no padrão das redes (−14 LUFS). |
| 📝 **Transcrição e legendas** | Transcrição com tempos pelo faster-whisper, para conferir falas e criar legendas. |
| 🖥️ **Gravação de tela** | Gravação de páginas reais com o Playwright, para tutoriais. |
| 🔍 **Melhorar vídeo ruim** | Ampliação 4× com IA (Real-ESRGAN) e remoção de legenda queimada. |
| ⚛️ **Remotion** (opcional) | Vídeos em React para modelos repetidos. |
| ✅ **Conferência** | Verificação automática (erros, layout, contraste), quadros de controle e folha de contato antes de entregar. |

## Como começar

**No seu computador**

1. Baixe esta pasta: botão verde **Code** → **Download ZIP**, ou `git clone`.
2. Abra a pasta no **Claude Code** ou no **Codex**.
3. Escreva: **"Leia o SETUP.md e instale o estúdio."**

O agente:
- descobre o seu sistema;
- pede permissão antes de instalar qualquer coisa (Node, Python, FFmpeg...);
- configura tudo e roda um teste de cada ferramenta;
- cria o `MEU-ESTUDIO.md` com os dados da sua máquina, que é o que faz os próximos chats já saberem trabalhar.

**Na nuvem**

Conecte este repositório a um ambiente de agente na nuvem (Claude Code na web, Codex na nuvem ou outro) e peça o mesmo: "Leia o SETUP.md e instale o estúdio". No Linux o agente instala tudo com `apt`. Sem placa de vídeo, o render e a IA de imagem ficam mais lentos. No fim, baixe os vídeos da pasta do projeto.

**Depois de instalado**, é só pedir. Exemplos:
- *"Faça um vídeo de 30 segundos em pé para Reels apresentando meu produto X. Me mostre o roteiro antes."*
- *"Narre este texto com voz feminina e me mostre onde a IA errou a pronúncia."*
- *"Melhore a qualidade deste vídeo do fornecedor e corte só os trechos de 0:12 a 0:20."*
- *"Grave um tutorial da página tal mostrando como fazer Y."*

## O que tem na pasta

| arquivo ou pasta | o que é |
|---|---|
| `SETUP.md` | o roteiro de instalação que o agente segue |
| `AGENTS.md` | o "cérebro" do estúdio: como trabalhar e tudo que já aprendemos (regras do HyperFrames, voz, áudio, formatos, Mercado Livre Clips, problemas conhecidos). O Codex lê este arquivo direto |
| `CLAUDE.md` | aponta para o `AGENTS.md`, para o Claude Code ler o mesmo conteúdo |
| `ferramentas/` | os scripts: novo projeto, narração, trilha, folha de contato, gravação de tela, upscale e mais (lista no `AGENTS.md`) |
| `modelo/` | projeto-modelo de motion graphics: título animado, números com contadores, fechamento, transição na batida da trilha e efeitos sonoros. Serve deitado ou em pé |
| `recursos/fontes/` | fonte Poppins (licença livre OFL) |
| `requirements.txt` / `package.json` | versões que foram testadas e funcionam |

Crie um vídeo novo a partir do modelo com:

```bash
node ferramentas/novo-projeto.mjs meu-video em-pe 30
```

## Créditos e licenças

- [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache 2.0). Os efeitos sonoros vêm dele e têm a licença Pixabay (uso comercial liberado).
- [Kokoro](https://github.com/thewh1teagle/kokoro-onnx), [faster-whisper](https://github.com/SYSTRAN/faster-whisper), [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN), [Playwright](https://playwright.dev) e [GSAP](https://gsap.com).
- [Remotion](https://remotion.dev): grátis para pessoa física e para empresa com até 3 funcionários. Acima disso, precisa de licença.
- Fonte Poppins: SIL Open Font License (`recursos/fontes/OFL.txt`).
