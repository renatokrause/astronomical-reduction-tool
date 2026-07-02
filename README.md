# Astronomical Image Reduction Tool

**Astronomical Image Reduction Tool**, ou **AIRT**, é uma aplicação desktop em Python para redução, composição e exportação de imagens astronômicas em formato FITS.

A versão atual do projeto usa uma interface gráfica moderna em **Qt / PySide6**, estruturada como um assistente passo a passo. O fluxo guia o usuário desde a escolha das pastas do projeto até a geração dos arquivos finais processados.

A versão antiga baseada em Tkinter foi removida do fluxo ativo de desenvolvimento. O código principal atual fica em src/airt.

---

## Status do projeto

O projeto está em fase final de desenvolvimento da nova interface e do novo fluxo de processamento.

Já existem:

- Interface Qt com wizard completo.
- Estrutura de projeto .airt.json.
- Detecção e organização de arquivos FITS.
- Seleção de frames por tipo e banda.
- Ordenação recomendada de bandas/filtros.
- Presets de processamento.
- Presets de mapeamento de cores.
- Alinhamento visual por banda.
- Correção de fundo/gradiente.
- Configuração de composição final e exportação.
- Processamento final automático.
- Exportação de arquivos finais.
- Configuração de qualidade, segurança e CI/CD.

Ainda em evolução:

- Qualidade final do pipeline de renderização.
- Refinamento científico da calibração, stacking, stretch e composição.
- Empacotamento final para Windows, Linux e macOS.
- Testes mais abrangentes cobrindo todos os fluxos da aplicação.

---

## Principais tecnologias

- Python
- PySide6 / Qt
- NumPy
- Astropy
- SciPy
- scikit-image
- astroalign
- Pillow
- Ruff
- Pytest
- Pyright
- Bandit
- pip-audit
- pre-commit
- GitHub Actions
- Dependabot

---

## Estrutura atual do projeto

`	ext
Astronomical-Image-Reduction-Tool/
+-- .github/
¦   +-- workflows/
¦   ¦   +-- ci.yml
¦   +-- dependabot.yml
+-- scripts/
¦   +-- run_qt_dev.ps1
¦   +-- check.ps1
¦   +-- test.ps1
¦   +-- build.ps1
+-- src/
¦   +-- airt/
¦       +-- __init__.py
¦       +-- __main__.py
¦       +-- app.py
¦       +-- core/
¦       ¦   +-- bands.py
¦       ¦   +-- color_mapping.py
¦       ¦   +-- file_scan.py
¦       ¦   +-- final_render.py
¦       +-- project/
¦       ¦   +-- io.py
¦       ¦   +-- model.py
¦       ¦   +-- recent.py
¦       +-- qt/
¦           +-- theme.py
¦           +-- widgets/
¦           +-- wizard/
+-- tests/
+-- requirements.txt
+-- requirements-dev.txt
+-- pyproject.toml
+-- .pre-commit-config.yaml
+-- README.md
+-- LICENSE
+-- AUTHORS.md
`

---

## Fluxo funcional da aplicação

O AIRT usa um wizard com nove etapas.

### 1. Welcome

Tela inicial da aplicação.

Permite:

- Criar um novo projeto.
- Abrir um projeto existente.
- Acessar projetos recentes.

Os projetos recentes são armazenados localmente e exibidos na tela inicial.

---

### 2. Project Folders

Define a estrutura principal do projeto.

O usuário informa:

- Pasta do objeto.
- Nome do objeto.
- Arquivo de projeto .airt.json.
- Pastas de calibração:
  - Bias
  - Dark
  - Flat
  - Focus

A pasta de saída é definida automaticamente como:

`	ext
<object_folder>\output
`

Exemplo:

`	ext
C:\Astro\M104\output
`

---

### 3. File Scan

Escaneia os arquivos FITS do projeto.

A aplicação identifica:

- Frames de objeto.
- Bias.
- Dark.
- Flat.
- Focus.
- Bandas/filtros.
- Exposição.
- Binagem.
- Dimensões.
- Problemas ou avisos básicos.

A detecção de banda usa cabeçalhos FITS e fallback por nome de arquivo quando aplicável.

Exemplos de chaves FITS consideradas:

`	ext
FILTER
FILTER1
FILTER2
FILT
BAND
FILTERID
FILTERID1
INSFLNAM
`

---

### 4. Frame Selection

Permite revisar e selecionar quais frames serão usados no processamento.

Recursos:

- Filtro por tipo.
- Filtro por banda.
- Seleção/deseleção de frames.
- Preview de arquivos FITS.
- Persistência da seleção no projeto.
- Separação entre arquivos selecionados e rejeitados.

A seleção feita nesta tela é usada nas etapas seguintes.

---

### 5. Preset & Color Mapping

Define o tipo de processamento e o mapeamento de cores.

Presets de processamento:

`	ext
Auto
Compact Galaxy
Extended Galaxy
Nebula
Star Field
Manual Advanced
`

Modos de mapeamento de cor:

`	ext
Photometric
Chromatic Order
SHO
HOO
Custom
`

No modo Custom, o usuário pode definir canal e cor por banda.

As configurações são salvas no arquivo .airt.json.

---

### 6. Alignment

Tela de alinhamento visual entre bandas.

Permite:

- Escolher banda de referência.
- Escolher banda a ajustar.
- Ajustar deslocamento X/Y.
- Usar alinhamento automático.
- Resetar uma banda.
- Resetar todos os offsets.
- Aplicar zoom.
- Arrastar/mover bandas visualmente.

Os offsets são salvos no projeto e usados na composição final.

---

### 7. Background Correction

Configura a correção de fundo/gradiente.

Modos disponíveis:

`	ext
Conservative
Standard
Aggressive
Custom
`

Também permite configurar:

- Ativar/desativar correção.
- Aplicar por banda ou preview.
- Nível de proteção do objeto.
- Strength.
- Background scale.
- Visualização:
  - Original
  - Corrected
  - Difference

A visualização desta tela é monocromática por decisão de projeto, para focar na inspeção do fundo e evitar confusão com a composição colorida final.

---

### 8. Final Composition & Export

Define como a imagem final será composta e quais arquivos serão gerados.

Configurações de composição:

- Rendering:
  - Color
  - Grayscale
- Stretch:
  - Linear
  - Auto
  - Soft
  - Strong
- Saturation.
- Brightness.
- Contrast.

Configurações de exportação:

- Nome base do arquivo.
- Formatos:
  - PNG
  - TIFF
  - FITS
  - JPEG
- Qualidade JPEG.
- Abrir pasta de saída ao final.

A tela 8 apenas salva as decisões de composição/exportação. Os arquivos finais são gerados na tela 9.

---

### 9. Process & Save

Executa o processamento final automaticamente ao entrar na tela.

A tela:

- Desabilita navegação enquanto processa.
- Mostra progresso.
- Gera os arquivos finais.
- Habilita o botão Finish ao concluir.
- Salva o projeto.
- Fecha a aplicação ao finalizar.

Os arquivos são gravados em:

`	ext
<object_folder>\output
`

---

## Estrutura recomendada de pastas do usuário

Exemplo recomendado:

`	ext
C:\Astro\
+-- calibration\
¦   +-- bias\
¦   +-- dark\
¦   +-- flat\
¦   +-- focus\
¦
+-- M104\
    +-- M104.airt.json
    +-- lights\
    ¦   +-- M104_L_001.fit
    ¦   +-- M104_R_001.fit
    ¦   +-- M104_G_001.fit
    ¦   +-- M104_B_001.fit
    +-- output\
        +-- M104.png
        +-- M104.tif
        +-- M104.jpg
        +-- M104_final.fits
`

A pasta lights é opcional. Se ela existir e contiver FITS, será usada como fonte dos frames de objeto. Caso contrário, a própria pasta do objeto será usada.

A aplicação aceita lat como padrão e também pode reconhecer lats como fallback.

---

## Ordenação de bandas/filtros

A aplicação usa ordenação recomendada por critério espectral, em vez de ordenação alfabética.

Ordem recomendada:

`	ext
L ? U ? B ? G ? V ? Hß ? OIII ? R ? Ha ? SII ? I ? desconhecidas/customizadas
`

Bandas desconhecidas ou customizadas são colocadas ao final, em ordem alfabética.

Exemplos de normalização:

`	ext
Luminance, Lum, Clear, C  ? L
Blue                      ? B
Green                     ? G
Red                       ? R
Ha, H-alpha, Ha           ? Ha
Hb, H-beta, Hß            ? Hß
OIII, O-III, [OIII]       ? OIII
SII, S-II, [SII]          ? SII
`

---

## Arquivo de projeto

Cada projeto é salvo como um arquivo:

`	ext
<object_name>.airt.json
`

Esse arquivo armazena:

- Pastas do projeto.
- Nome do objeto.
- Arquivos encontrados.
- Frames selecionados.
- Frames rejeitados.
- Preset escolhido.
- Mapeamento de cores.
- Offsets de alinhamento.
- Configurações de correção de fundo.
- Configurações de composição final.
- Configurações de exportação.

Os FITS originais não são modificados.

---

## Instalação para desenvolvimento

### Requisitos

- Python 3.11 ou superior recomendado.
- Windows PowerShell para os scripts atuais.
- Git.

### Criar ambiente virtual

`powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
`

### Instalar dependências de runtime

`powershell
pip install -r requirements.txt
`

### Instalar dependências de desenvolvimento

`powershell
pip install -r requirements-dev.txt
`

---

## Rodar a aplicação em modo desenvolvimento

Use o launcher Qt de desenvolvimento:

`powershell
.\scripts\run_qt_dev.ps1
`

Esse script configura o ambiente para usar o pacote em src e executa:

`powershell
python -m airt
`

---

## Comandos locais úteis

### Rodar testes

`powershell
.\scripts\test.ps1
`

Ou diretamente:

`powershell
pytest
`

### Rodar checks locais

`powershell
.\scripts\check.ps1
`

Ou manualmente:

`powershell
ruff format --check .
ruff check .
pytest
`

### Rodar formatação

`powershell
ruff format .
`

### Rodar lint

`powershell
ruff check .
`

### Rodar lint com correção automática segura

`powershell
ruff check . --fix
`

### Build local

`powershell
.\scripts\build.ps1
`

O build final ainda está em evolução. O objetivo é gerar no futuro:

- .exe para Windows.
- Binário/AppImage para Linux.
- .app para macOS.

---

## Qualidade e segurança

O projeto possui configuração para:

- Ruff formatter.
- Ruff lint.
- Pyright.
- Bandit.
- pip-audit.
- pytest.
- pytest-cov.
- pytest-qt.
- Vulture.
- Radon.
- pre-commit.
- Gitleaks.
- GitHub Actions.
- Dependabot.

### pre-commit

Instalar hooks locais:

`powershell
pre-commit install
`

Rodar manualmente:

`powershell
pre-commit run --all-files
`

Hooks configurados:

- trailing whitespace
- end-of-file-fixer
- check-yaml
- check-toml
- check-json
- check-merge-conflict
- debug-statements
- ruff
- ruff-format
- bandit
- gitleaks

---

## CI/CD

O workflow de CI roda em:

- push para main
- pull request para main

O CI executa:

1. Checkout.
2. Setup Python.
3. Instalação de dependências.
4. uff format --check.
5. uff check.
6. pyright.
7. andit.
8. gitleaks.
9. pip-audit.
10. pytest com coverage.
11. ulture informativo.
12. adon informativo.
13. Smoke test de build, quando aplicável.

Vulture e Radon começam como informativos para evitar bloqueios excessivos por falsos positivos nesta fase.

---

## Dependabot

O Dependabot está configurado para verificar semanalmente:

- Dependências Python/pip.
- GitHub Actions.

---

## Testes

A estrutura de testes fica em:

`	ext
tests/
`

Testes iniciais cobrem:

- Normalização de bandas.
- Ordenação recomendada de bandas.
- Labels de exibição.
- Mapeamento de cores.
- Normalização de arrays com NaN/infinito.
- Conversão de imagem final para QImage.

Áreas planejadas para ampliar cobertura:

- Identificação de filtros em headers FITS.
- Headers FITS incompletos.
- Arquivos FITS inválidos.
- Imagens com dimensões diferentes.
- Fluxo básico de projeto.
- Salvamento e abertura de .airt.json.
- Exportação final.
- Correção de fundo.
- Alinhamento.
- Renderização final.

---

## Saídas geradas

Os arquivos finais são gerados em:

`	ext
<object_folder>\output
`

Formatos suportados na configuração atual:

`	ext
PNG
TIFF
FITS
JPEG
`

A seleção dos formatos é feita na tela Final Composition & Export.

---

## Notas sobre FITS

O AIRT trabalha com arquivos FITS astronômicos e usa stropy para leitura e escrita.

Os dados originais não são modificados. Toda saída processada é gravada na pasta output.

A orientação visual para PNG/TIFF/JPEG é tratada separadamente da orientação científica dos dados FITS.

---

## Git workflow

O desenvolvimento atual segue diretamente na branch main.

Antes de commitar alterações relevantes:

`powershell
ruff format --check .
ruff check .
pytest
python -m py_compile src\airt\__main__.py
`

---

## Convenções atuais

- Código principal fica em src/airt.
- Não usar mais entrada antiga por python app.py.
- Não usar mais scripts antigos .bat/.sh da versão Tkinter.
- Projeto salvo em .airt.json.
- Saídas sempre em <object_folder>\output.
- FITS originais nunca são alterados.
- Telas devem salvar configurações ao avançar ou voltar.
- Listagens de bandas devem usar a ordenação recomendada centralizada em irt.core.bands.

---

## Roadmap técnico

Próximos pontos importantes:

- Melhorar qualidade final do pipeline de composição.
- Comparar masters intermediários com a versão 1.0 e com o Colab.
- Refinar calibração por bias/dark/flat.
- Melhorar alinhamento entre bandas com rotação/escala, não apenas offset X/Y.
- Adicionar histogramas e curvas em etapa avançada.
- Melhorar exportação FITS final.
- Adicionar empacotamento com PyInstaller.
- Adicionar mais testes unitários.
- Adicionar testes de integração do wizard.
- Melhorar documentação de uso com screenshots.
- Preparar release versionado.

---

## Licença

Este projeto é distribuído sob a licença **AGPL-3.0**.

Consulte o arquivo LICENSE.

---

## Autores

Consulte o arquivo AUTHORS.md.
