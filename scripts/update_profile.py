#!/usr/bin/env python3
"""Gera os dados do portfolio a partir da API do GitHub.

Saidas:
  data/profile.json  perfil, linguagens, highlights e links.
  data/repos.json    repositorios publicos autorais, prontos para o site.

Usa apenas a biblioteca padrao. Requer GH_TOKEN (ou GITHUB_TOKEN) para a
API autenticada; sem token funciona com limites menores da API anonima.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

API = "https://api.github.com"
USERNAME = "V1nic1us"
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

LANG_COLORS = {
    "JavaScript": "#f7df1e",
    "TypeScript": "#3178c6",
    "Kotlin": "#7f52ff",
    "Python": "#3776ab",
    "Go": "#00add8",
    "Rust": "#dea584",
    "C#": "#512bd4",
    "Java": "#ed8b00",
    "HTML": "#e34f26",
    "CSS": "#663399",
    "Shell": "#89e051",
    "Lua": "#000080",
    "Nix": "#7e7eff",
    "Assembly": "#6e4c13",
    "C": "#555555",
}

HIGHLIGHTS = [
    {
        "name": "go-explorer",
        "title": "GO EXPLORER",
        "icon": "▤",
        "description": "Explorador de arquivos no terminal, com arvore hierarquica e navegacao interativa via tview/tcell.",
        "tags": ["Go", "TUI", "tview", "Terminal"],
    },
    {
        "name": "music-streaming-app",
        "title": "MUSIC STREAMING APP",
        "icon": "♪",
        "description": "Aplicativo mobile de streaming de musica construido com Kotlin e Jetpack Compose.",
        "tags": ["Kotlin", "Jetpack Compose", "Android"],
    },
    {
        "name": "nix-config",
        "title": "NIX CONFIG",
        "icon": "❄",
        "description": "Configuracao Nix portatil com Home Manager e NixOS, versionada e reproduzivel em qualquer maquina.",
        "tags": ["Nix", "NixOS", "Home Manager"],
    },
    {
        "name": "calculadora-assembly",
        "title": "CALCULADORA ASSEMBLY",
        "icon": "▦",
        "description": "Calculadora de inteiros de 64 bits em Assembly x86-64 para Linux, escrita em sintaxe Intel.",
        "tags": ["Assembly", "x86-64", "Linux"],
    },
    {
        "name": "tauri-app",
        "title": "TAURI APP",
        "icon": "▣",
        "description": "Aplicacao desktop multiplataforma com Tauri, React e TypeScript empacotando um front-end com backend em Rust.",
        "tags": ["Rust", "React", "TypeScript", "Tauri"],
    },
    {
        "name": "rinha-de-backend-2024",
        "title": "RINHA DE BACKEND",
        "icon": "⚡",
        "description": "Participacao na Rinha de Backend 2024, desafio de alta performance e baixa latencia em Rust.",
        "tags": ["Rust", "Backend", "Performance"],
    },
    {
        "name": "rpg-legend-bot",
        "title": "RPG LEGEND BOT",
        "icon": "◈",
        "description": "Bot de Discord que auxilia jogadores de RPG de mesa a terem uma experiencia melhor nas aventuras.",
        "tags": ["Python", "Discord", "Bot"],
    },
    {
        "name": "demo-sdk-android",
        "title": "DEMO SDK ANDROID",
        "icon": "▤",
        "description": "Demonstracao da SDK v2 de pagamentos para Android, com integracao de leitura de codigo e transacoes.",
        "tags": ["Android", "SDK", "Pagamentos"],
    },
]

SOCIAL = [
    {"label": "GitHub", "handle": "@V1nic1us", "url": "https://github.com/V1nic1us", "glyph": "G"},
    {"label": "GitLab", "handle": "@V1nic1us", "url": "https://gitlab.com/V1nic1us", "glyph": "L"},
    {
        "label": "LinkedIn",
        "handle": "Marcus Vinícius",
        "url": "https://www.linkedin.com/in/marcus-vin%C3%ADcius-541a9b247/",
        "glyph": "in",
    },
    {"label": "Instagram", "handle": "@marcusmarques16", "url": "https://www.instagram.com/marcusmarques16/", "glyph": "I"},
    {
        "label": "Steam",
        "handle": "76561198978458942",
        "url": "https://steamcommunity.com/profiles/76561198978458942/",
        "glyph": "S",
    },
]


def request_json(url: str, token: str | None) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "v1nic1us-portfolio",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_all_repos(token: str | None) -> list[dict]:
    repos: list[dict] = []
    for page in range(1, 6):
        batch = request_json(
            f"{API}/users/{USERNAME}/repos?per_page=100&type=owner&sort=pushed&page={page}", token
        )
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
    return repos


def fetch_languages(repos: list[dict], token: str | None) -> dict[str, dict[str, int]]:
    """Busca as linguagens de cada repo em paralelo, com cache em disco."""
    cache_path = ROOT / "data" / ".languages-cache.json"
    cache: dict[str, dict[str, int]] = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            cache = {}

    pending = [repo for repo in repos if repo.get("languages_url") and repo["name"] not in cache]

    def fetch(repo: dict) -> tuple[str, dict[str, int]]:
        try:
            data = request_json(repo["languages_url"], token)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            return repo["name"], {}
        return repo["name"], data if isinstance(data, dict) else {}

    if pending:
        with ThreadPoolExecutor(max_workers=12) as pool:
            for name, languages in pool.map(fetch, pending):
                cache[name] = languages

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return cache


def collect_languages(repos: list[dict], cache: dict[str, dict[str, int]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        for name, size in cache.get(repo["name"], {}).items():
            totals[name] = totals.get(name, 0) + int(size)
    return totals


def build_repos(repos: list[dict], cache: dict[str, dict[str, int]]) -> list[dict]:
    own = [repo for repo in repos if not repo.get("fork")]
    own.sort(key=lambda repo: repo.get("pushed_at") or "", reverse=True)
    items = []
    for repo in own:
        languages_data = cache.get(repo["name"], {})
        languages = sorted(languages_data, key=lambda name: languages_data[name], reverse=True)
        items.append(
            {
                "name": repo["name"],
                "description": repo.get("description") or "",
                "language": repo.get("language") or (languages[0] if languages else ""),
                "languages": languages,
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "url": repo.get("html_url", ""),
                "pushedAt": repo.get("pushed_at", ""),
                "topics": repo.get("topics", []),
            }
        )
    return items


def build_profile(repos: list[dict], languages: dict[str, int], token: str | None) -> dict:
    user = request_json(f"{API}/users/{USERNAME}", token)
    own = [repo for repo in repos if not repo.get("fork")]

    total_bytes = sum(languages.values()) or 1
    ranked = sorted(languages.items(), key=lambda item: item[1], reverse=True)
    top = [
        {
            "name": name,
            "percent": round(size / total_bytes * 100, 1),
            "color": LANG_COLORS.get(name, "#a78bfa"),
        }
        for name, size in ranked[:6]
    ]
    others = ranked[6:]
    if others:
        top.append(
            {
                "name": "Outras",
                "percent": round(sum(size for _, size in others) / total_bytes * 100, 1),
                "color": "#77608e",
            }
        )

    return {
        "username": user.get("login", USERNAME),
        "name": user.get("name") or "Marcus Vinícius",
        "bio": user.get("bio") or "",
        "company": user.get("company") or "",
        "location": user.get("location") or "Brasil",
        "blog": user.get("blog") or "",
        "followers": user.get("followers", 0),
        "publicRepos": user.get("public_repos", 0),
        "ownRepos": len(own),
        "languages": top,
        "highlights": HIGHLIGHTS,
        "social": SOCIAL,
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"escrito: {path.relative_to(ROOT)}")


def main() -> None:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repos = fetch_all_repos(token)
    print(f"repositorios encontrados: {len(repos)}")

    cache = fetch_languages(repos, token)
    languages = collect_languages(repos, cache)
    profile = build_profile(repos, languages, token)
    write_json(DATA_DIR / "profile.json", profile)
    write_json(DATA_DIR / "repos.json", build_repos(repos, cache))


if __name__ == "__main__":
    main()
