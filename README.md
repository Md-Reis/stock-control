# Sistema de Controle de Estoque 📦

## Descrição do Projeto

O **Sistema de Controle de Estoque** é uma aplicação desktop desenvolvida com Flet para gerenciar produtos de uso e consumo em empresas, estabelecimentos comerciais ou pequenos negócios. A aplicação oferece controle completo sobre entrada e saída de produtos, níveis de estoque, alertas de reposição e relatórios gerenciais.

## Objetivo da Aplicação

O objetivo principal desta aplicação é automatizar e modernizar o controle de estoque, proporcionando:

- **Gestão de Produtos**: Cadastro completo de produtos com categorização
- **Controle de Movimentação**: Registro de entradas e saídas de produtos
- **Alertas de Estoque**: Notificações automáticas para produtos com estoque baixo
- **Relatórios Gerenciais**: Análise de movimentação e situação do estoque
- **Interface Intuitiva**: Sistema desktop fácil de usar e responsivo
- **Controle de Fornecedores**: Gestão de fornecedores e relacionamento com produtos

## Tecnologias Utilizadas

### Framework Principal
- **Flet** - Framework Python para criação de aplicações desktop, web e mobile
- **Python 3.11+** - Linguagem principal de desenvolvimento

### Banco de Dados
- **SQLite** - Banco de dados relacional local
- **SQLAlchemy** - ORM para manipulação do banco de dados

### Bibliotecas Complementares
- **Pandas** - Manipulação e análise de dados para relatórios
- **Matplotlib** - Geração de gráficos e visualizações
- **DateTime** - Manipulação de datas e horários
- **UUID** - Geração de identificadores únicos
- **Openpyxl** - Exportação de relatórios para Excel

### Ferramentas de Desenvolvimento
- **Visual Studio Code** - IDE principal de desenvolvimento
- **Git** - Controle de versão
- **Python Virtual Environment** - Isolamento de dependências
- **DB Browser for SQLite** - Visualização do banco de dados

## Funcionalidades Principais

### CRUD Completo

1. **Produtos**
   - Cadastrar produtos com código, nome, descrição, categoria, unidade de medida
   - Consultar produtos por diversos filtros
   - Atualizar informações dos produtos
   - Remover produtos do sistema
   - Definir estoque mínimo e máximo

2. **Movimentações de Estoque**
   - Registrar entradas de produtos (compras/recebimentos)
   - Registrar saídas de produtos (vendas/consumo)
   - Consultar histórico de movimentações
   - Atualizar movimentações (quando permitido)
   - Cancelar movimentações

3. **Fornecedores**
   - Cadastrar fornecedores com dados completos
   - Visualizar fornecedores cadastrados
   - Atualizar informações de fornecedores
   - Gerenciar relacionamento produto-fornecedor

4. **Categorias**
   - Criar categorias de produtos
   - Organizar produtos por categoria
   - Atualizar e remover categorias

### Funcionalidades Especiais
- **Dashboard**: Visão geral do estoque com indicadores
- **Alertas**: Produtos com estoque baixo ou vencimento próximo
- **Relatórios**: Exportação de dados para PDF e Excel
- **Busca Avançada**: Pesquisa por múltiplos critérios
- **Backup**: Sistema de backup automático dos dados

## Estrutura do Projeto

```
controle-estoque-flet/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── product.py
│   │   ├── movement.py
│   │   ├── supplier.py
│   │   └── category.py
│   ├── views/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── products_view.py
│   │   ├── movements_view.py
│   │   ├── suppliers_view.py
│   │   └── reports_view.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── product_controller.py
│   │   ├── movement_controller.py
│   │   └── supplier_controller.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── migrations.py
│   └── utils/
│       ├── __init__.py
│       ├── validators.py
│       ├── formatters.py
│       └── exporters.py
├── assets/
│   ├── icons/
│   └── images/
├── backups/
├── reports/
├── tests/
├── venv/
├── requirements.txt
├── config.py
├── run.py
└── README.md
```

## Configuração do Ambiente de Desenvolvimento

### Pré-requisitos
- Python 3.11 ou superior
- Visual Studio Code
- Git

### Instalação e Configuração

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/controle-estoque-flet.git
cd controle-estoque-flet
```

2. **Crie e ative o ambiente virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o arquivo de configuração**
```bash
# Crie um arquivo config.py com as configurações necessárias
cp config.py.example config.py
```

5. **Execute a aplicação**
```bash
python run.py
```

## Dependências do Projeto (requirements.txt)

```
flet>=0.21.0
sqlalchemy>=2.0.0
pandas>=2.0.0
matplotlib>=3.7.0
openpyxl>=3.1.0
reportlab>=4.0.0
python-dateutil>=2.8.0
```

## Interface da Aplicação

### Tela Principal (Dashboard)
- Resumo geral do estoque
- Produtos com estoque baixo
- Movimentações recentes
- Gráficos de análise

### Módulo de Produtos
- Lista de produtos cadastrados
- Formulário de cadastro/edição
- Busca e filtros avançados
- Visualização de detalhes

### Módulo de Movimentações
- Registro de entradas e saídas
- Histórico de movimentações
- Filtros por período e tipo
- Detalhamento de movimentações

### Módulo de Relatórios
- Relatório de estoque atual
- Relatório de movimentações
- Análise de consumo
- Exportação para Excel/PDF

## Extensões Recomendadas para VS Code

- **Python** - Suporte completo para Python
- **Python Docstring Generator** - Geração automática de docstrings
- **SQLite Viewer** - Visualização do banco SQLite
- **GitLens** - Melhorias para Git
- **Prettier** - Formatação de código
- **Error Lens** - Visualização de erros inline

## Vantagens do Flet

- **Multiplataforma**: Executa em Windows, macOS, Linux, Web e Mobile
- **Interface Moderna**: Baseado no Flutter, oferece interfaces nativas
- **Python Puro**: Desenvolvimento 100% em Python
- **Responsivo**: Interface adaptável a diferentes tamanhos de tela
- **Performance**: Aplicações rápidas e eficientes

## Fluxo de Desenvolvimento

### Checkpoint 01 ✅
- [x] README completo com descrição do projeto
- [x] Definição das tecnologias utilizadas
- [x] Estrutura do projeto planejada

### Checkpoint 02 (Planejado)
- [ ] Implementação dos modelos de dados
- [ ] Configuração do banco de dados
- [ ] Interface básica com Flet
- [ ] CRUD de produtos

### Checkpoint 03 (Planejado)
- [ ] CRUD de movimentações
- [ ] Sistema de alertas
- [ ] Relatórios básicos
- [ ] Validações e tratamento de erros

### Entrega Final (Planejado)
- [ ] Interface completa e polida
- [ ] Todos os CRUDs funcionais
- [ ] Sistema de relatórios avançado
- [ ] Testes e documentação final

## Casos de Uso Práticos

- **Pequenos Comércios**: Controle de produtos para venda
- **Escritórios**: Gestão de materiais de escritório e consumo
- **Oficinas**: Controle de peças e ferramentas
- **Restaurantes**: Gestão de ingredientes e insumos
- **Farmácias**: Controle de medicamentos e produtos

## Contribuição

Este projeto está sendo desenvolvido como parte da disciplina de Tecnologias Emergentes. Contribuições e sugestões são bem-vindas através de issues e pull requests.

**Desenvolvido por:** Marcelo dos Reis
**Disciplina:** Tecnologias Emergentes  
**Período:** 2025/01  
**Framework:** Flet (Python)
