
# Sistema de Controle de Estoque 📦

## 📌 Descrição do Projeto

O **Sistema de Controle de Estoque** é uma aplicação desktop desenvolvida com **Flet** e **Python**, voltada à gestão de produtos, movimentações e relatórios de estoque. Ela oferece uma interface intuitiva, CRUD completo, relatórios gerenciais e persistência dos dados via banco SQLite.

## 🎯 Objetivo

Desenvolver uma aplicação funcional que contemple um CRUD completo com persistência em banco de dados, utilizando Python e Flet, como parte da disciplina de **Tecnologias Emergentes**. O sistema é voltado para pequenos negócios, comércios e empresas que precisam gerenciar seu estoque de forma eficiente.

---

## 🛠️ Tecnologias Utilizadas

### Linguagem
- **Python 3.11**

### Framework
- **Flet** (interface gráfica em Python)

### Banco de Dados
- **SQLite 3** (banco relacional local via `sqlite3`)

### Bibliotecas Complementares
- `datetime`, `os`, `json`, `warnings`
---

## 📦 Funcionalidades da Aplicação

### ✅ CRUD Completo

- **Produtos**: cadastro, edição, listagem, exclusão lógica
- **Fornecedores**: cadastro e associação a produtos
- **Categorias**: pré-cadastradas e associadas aos produtos
- **Movimentações**: entrada e saída de estoque com histórico

### 📊 Relatórios
- Resumo do estoque
- Estatísticas de movimentações
- Exportação para JSON

### 🔔 Alertas
- Notificação de produtos com estoque baixo
- Validação automática de dados

### 🎯 Dashboard
- Visão geral com cards e métricas principais

---

## 📁 Estrutura do Projeto

```
controle_estoque/
├── data/                   # Banco de dados e exportações
├── avaliacao.py           # Arquivo principal do sistema
├── README.md              # Documentação do projeto
└── requirements.txt       # Dependências do projeto
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.11+
- Ambiente virtual (recomendado)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/Md-Reis/stock-control.git
cd controle_estoque

# Crie e ative o ambiente virtual
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python avaliacao.py
```

---

## 💻 Requisitos de Sistema

- Python 3.11+
- Ambiente Windows, macOS ou Linux
- Navegador moderno (para visualização web via Flet)

---

## 👩‍💻 Desenvolvimento

### Ambiente
- **IDE**: Visual Studio Code
- **Versão do Python**: 3.11
- **Banco**: SQLite (arquivos `.db`)
- **Modo de execução**: Flet Web Browser (`ft.WEB_BROWSER`)

---

## ✅ Código Limpo

O projeto aplica práticas de:
- Separação por responsabilidade (`DatabaseManager`, `ProductController`, `StockControlApp`)
- Docstrings explicativos
- Comentários claros
- Nomeação significativa de variáveis e funções
- Evita duplicação de lógica
- Trata exceções e exibe mensagens amigáveis ao usuário

---

## 🧪 Testes Automatizados

> Ainda **não foram implementados testes automatizados**. O sistema foi validado manualmente com entradas simuladas, verificações de consistência e testes de comportamento.

---

## 🧠 Padrões de Projeto

Foi aplicado o padrão **Singleton** no `DatabaseManager`, garantindo uma única instância da conexão com o banco de dados durante todo o ciclo de vida da aplicação.

---

## 📅 Cronograma de Desenvolvimento

### Checkpoint 01 ✅
- README inicial
- Definição da stack
- Estrutura de diretórios

### Checkpoint 02 ✅
- Banco de dados SQLite funcional
- Interface inicial com abas
- CRUD de produtos implementado

### Checkpoint 03 ✅
- CRUD de movimentações
- Relatórios em tempo real
- Validações e mensagens com `AlertDialog`

### Entrega Final ✅
- CRUD completo e funcional
- Exportações e relatórios finalizados
- Interface final estilizada
- README completo atualizado

---

## 🤝 Como Contribuir

Este projeto foi desenvolvido como atividade da disciplina **Tecnologias Emergentes (2025/01)**. Para sugestões ou melhorias:

1. Faça um fork
2. Crie uma branch com sua feature
3. Envie um pull request com a proposta

---

**Autor:** Marcelo dos Reis  
**Disciplina:** Tecnologias Emergentes  
**Ano:** 2025  
**Framework:** Flet  
