# E-commerce Image CDN

Repositório de imagens públicas para e-commerce, servido via GitHub Pages.

## URLs Públicas

Após deploy, as imagens ficam disponíveis em:

```
https://kiwi-kaktu-corp.github.io/e-commecer-img/
```

Exemplo de URL de imagem:
```
https://kiwi-kaktu-corp.github.io/e-commecer-img/assets/vinho/pack-01/uva-01.webp
```

## Catálogo Visual

Acesse o catálogo interativo em:
```
https://kiwi-kaktu-corp.github.io/e-commecer-img/
```

### Navegação Hierárquica

1. **Página inicial** → Lista de categorias (ex: vinho) com preview
2. **Categoria** → Lista de packs com miniaturas
3. **Pack** → Todas as imagens com botão "Copiar URL"

## Estrutura de Pastas

```
e-commecer-img/
├── assets/
│   └── vinho/
│       ├── index.html         # Lista de packs
│       └── pack-01/
│           ├── index.html     # Imagens do pack
│           ├── *.png          # Originais
│           └── *.webp         # Otimizados
├── tools/
│   ├── optimize.py            # Converte PNG/JPG → WebP
│   └── generate_index.py      # Gera catálogos HTML
├── index.html                 # Página inicial (categorias)
└── requirements.txt           # Dependências Python
```

## Como Adicionar Novas Imagens

1. Crie uma pasta para a categoria e pack (ex: `assets/vinho/pack-02/`)
2. Adicione as imagens PNG ou JPG na pasta
3. Faça commit e push para a branch `main`
4. O GitHub Actions irá automaticamente:
   - Converter as imagens para WebP
   - Gerar os arquivos `index.html` em cada nível
   - Fazer deploy no GitHub Pages

## Rodar Localmente

### Pré-requisitos

```bash
pip install -r requirements.txt
```

### Converter Imagens

```bash
# Converter todas as imagens
python tools/optimize.py

# Com qualidade customizada
python tools/optimize.py --quality 90

# Com largura máxima
python tools/optimize.py --max-width 1200

# Forçar reconversão de imagens existentes
python tools/optimize.py --force
```

### Gerar Catálogo

```bash
python tools/generate_index.py
```

### Visualizar Catálogo

Abra `index.html` no navegador ou use um servidor local:

```bash
python -m http.server 8000
# Acesse http://localhost:8000
```

## Configuração do GitHub Pages

1. Vá em **Settings > Pages**
2. Em **Source**, selecione **GitHub Actions**
3. O deploy será automático a cada push na branch `main`

## Formato WebP

As imagens são convertidas para WebP com:
- Qualidade: 85%
- Suporte a transparência (PNG com alpha)
- Tamanho reduzido em ~60-80% comparado ao PNG
