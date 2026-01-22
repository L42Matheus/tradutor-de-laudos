# Contribuindo para o Traduz Saude

Obrigado pelo interesse em contribuir!

## Como contribuir

### 1. Fork e Clone
```bash
git clone https://github.com/SEU-USUARIO/tradutor-de-laudos.git
cd tradutor-de-laudos
```

### 2. Crie uma branch
```bash
git checkout -b feature/minha-feature
```

Padroes de nome:
- `feature/` - novas funcionalidades
- `fix/` - correcoes de bugs
- `docs/` - documentacao
- `refactor/` - refatoracao

### 3. Faca suas mudancas
- Siga o padrao de codigo existente
- Teste localmente com `python -m streamlit run app.py`
- Nao commite dados sensiveis (API keys, .env, etc)

### 4. Commit
```bash
git add .
git commit -m "Descricao clara da mudanca"
```

### 5. Push e Pull Request
```bash
git push origin feature/minha-feature
```

Abra um Pull Request no GitHub e aguarde a revisao.

## Regras

- Todo PR precisa de aprovacao do Code Owner (@L42Matheus)
- PRs direto na `master` nao sao permitidos
- Mantenha o codigo limpo e documentado

## Ambiente de desenvolvimento

```bash
# Instalar dependencias
pip install -r requirements.txt

# Criar arquivo .env
cp .env.example .env
# Adicione sua ANTHROPIC_API_KEY

# Rodar
python -m streamlit run app.py
```

## Duvidas?

Abra uma issue ou entre em contato com @L42Matheus.
