<div align="center">

# Portfolio · V1nic1us

Site pessoal de **Marcus Vinícius** — desenvolvedor front-end & mobile.

Identidade de terminal em roxo e rosa, a mesma dos gráficos e da cobrinha do
[repositório de perfil](https://github.com/V1nic1us/V1nic1us).

**→ [v1nic1us.github.io](https://v1nic1us.github.io/)**

</div>

---

### `~/portfolio $ ls`

```
.
├── index.html                              # site completo (HTML + CSS + JS inline)
├── data/
│   ├── profile.json                        # perfil, linguagens, destaques e links
│   └── repos.json                          # repositórios públicos autorais
├── scripts/
│   └── update_profile.py                   # gera os JSON a partir da API do GitHub
└── .github/workflows/
    └── update-profile-data.yml             # regenera os JSON a cada 12h
```

Site 100% estático: sem build, sem bundler, sem dependências. O GitHub Pages
serve o `main` na raiz.

### `~/portfolio $ cat README.md`

Os dados exibidos no site vêm de dois arquivos versionados no repositório:

- `data/profile.json` — nome, bio, seguidores, proporção de linguagens,
  projetos em destaque e links sociais.
- `data/repos.json` — todos os repositórios públicos próprios (sem forks),
  com linguagem, data do último push, stars e topics.

O site busca esses dois arquivos via `fetch` e monta a página em tempo de
execução. Se os arquivos não estiverem disponíveis, o layout permanece
funcional e a seção de repositórios mostra um aviso.

### `~/portfolio $ python3 scripts/update_profile.py`

Regenera os JSON consultando a API do GitHub. Requer `GH_TOKEN` (ou
`GITHUB_TOKEN`) para os limites maiores da API:

```sh
export GH_TOKEN=$(gh auth token)
python3 scripts/update_profile.py
```

O script usa apenas a biblioteca padrão do Python 3.10+ e mantém um cache em
`data/.languages-cache.json` (ignorado pelo git) para não repetir a mesma
consulta de linguagens a cada execução.

A coleta segue as mesmas regras do repositório de perfil: apenas repositórios
públicos próprios, sem forks, com linguagens detectadas. As porcentagens são
calculadas por soma de bytes de código.

### `~/portfolio $ cat .github/workflows/update-profile-data.yml`

Workflow agendado a cada 12 horas (`17 */12 * * *`) que regenera os JSON e
publica o commit automaticamente quando há mudanças. Também pode ser
disparado manualmente pela aba **Actions**.

---

<div align="center">

Construído com HTML, CSS e JavaScript puro. Sem dependências, sem rastreamento.

</div>
