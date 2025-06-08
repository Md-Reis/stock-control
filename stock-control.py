#!/usr/bin/env python3
"""
Sistema de Controle de Estoque
Desenvolvido com Flet (Python)
Autor: Marcelo dos Reis
Disciplina: Tecnologias Emergentes
"""

import flet as ft
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
import os
import json
import warnings

class DatabaseManager:
    """Gerencia todo o nosso banco de Dados"""
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._connection is None:
            self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados e cria as tabelas"""
        try:
            # Cria o diretório data se não existir
            os.makedirs('data', exist_ok=True)
            
            self._connection = sqlite3.connect('data/estoque.db', check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            
            # Criar tabelas
            self.create_tables()
            print("✅ Banco de dados inicializado com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco: {e}")
            raise
    
    def create_tables(self):
        """Cria as tabelas necessárias para que o sistema funcione corretamente"""
        cursor = self._connection.cursor()
        
        # Tabela de Categorias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                descricao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de Fornecedores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT UNIQUE,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de Produtos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                categoria_id INTEGER,
                fornecedor_id INTEGER,
                preco_compra REAL DEFAULT 0.0,
                preco_venda REAL DEFAULT 0.0,
                estoque_atual INTEGER DEFAULT 0,
                estoque_minimo INTEGER DEFAULT 0,
                estoque_maximo INTEGER DEFAULT 100,
                unidade_medida TEXT DEFAULT 'UN',
                ativo BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES categorias (id),
                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id)
            )
        ''')
        
        # Tabela de Movimentações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimentacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
                quantidade INTEGER NOT NULL,
                valor_unitario REAL DEFAULT 0.0,
                valor_total REAL DEFAULT 0.0,
                observacao TEXT,
                data_movimentacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario TEXT DEFAULT 'Sistema',
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
        ''')
        
        # Inserir dados iniciais
        self.insert_initial_data()
        
        self._connection.commit()
        print("✅ Tabelas criadas com sucesso")
    
    def insert_initial_data(self):
        """Insere dados iniciais para as validações"""
        cursor = self._connection.cursor()
        
        # Categorias iniciais
        categorias_iniciais = [
            ('Eletrônicos', 'Produtos eletrônicos e tecnológicos'),
            ('Alimentícios', 'Produtos alimentícios e bebidas'),
            ('Limpeza', 'Produtos de limpeza e higiene'),
            ('Escritório', 'Materiais de escritório'),
            ('Ferramentas', 'Ferramentas e equipamentos')
        ]
        
        for nome, desc in categorias_iniciais:
            cursor.execute('''
                INSERT OR IGNORE INTO categorias (nome, descricao) 
                VALUES (?, ?)
            ''', (nome, desc))
        
        # Fornecedores iniciais
        fornecedores_iniciais = [
            ('Fornecedor Geral', '00.000.000/0001-00', '(11) 9999-9999', 'contato@fornecedor.com', 'Rua A, 123'),
            ('Tech Solutions', '11.111.111/0001-11', '(11) 8888-8888', 'vendas@tech.com', 'Av. Tecnologia, 456')
        ]
        
        for nome, cnpj, tel, email, end in fornecedores_iniciais:
            cursor.execute('''
                INSERT OR IGNORE INTO fornecedores (nome, cnpj, telefone, email, endereco) 
                VALUES (?, ?, ?, ?, ?)
            ''', (nome, cnpj, tel, email, end))
    
    def get_connection(self):
        """Retorna a conexão com o banco"""
        return self._connection
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Executa uma query SELECT e retorna os resultados"""
        cursor = self._connection.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def execute_command(self, command: str, params: tuple = ()) -> int:
        """Executa um comando INSERT/UPDATE/DELETE e retorna o ID ou linhas afetadas"""
        cursor = self._connection.cursor()
        cursor.execute(command, params)
        self._connection.commit()
        return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

class ProductController:
    """Funções de controle dos produtos (criação/edição/remoção)"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_product(self, product_data: Dict[str, Any]) -> bool:
        """Cadastra um novo produto"""
        try:
            command = '''
                INSERT INTO produtos (
                    nome, descricao, categoria_id, fornecedor_id, 
                    preco_compra, preco_venda, estoque_atual, 
                    estoque_minimo, estoque_maximo, unidade_medida
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            params = (
            product_data['nome'],
            product_data.get('descricao', ''),
            product_data.get('categoria_id'),
            product_data.get('fornecedor_id'),
            product_data.get('preco_compra', 0.0),
            product_data.get('preco_venda', 0.0),
            0,  #Novos produtos sempre iniciam com qtdade 0 no estoque
            product_data.get('estoque_minimo', 0),
            product_data.get('estoque_maximo', 100),
            product_data.get('unidade_medida', 'UN')
        )
            
            product_id = self.db.execute_command(command, params)
            # Registrar movimentação de entrada inicial se houver estoque

            if product_data.get('estoque_atual', 0) > 0:
                self.register_movement(
                    product_id, 
                    'ENTRADA', 
                    product_data.get('estoque_atual', 0),
                    product_data.get('preco_compra', 0.0),
                    'Estoque inicial do produto'
                )
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao criar produto: {e}")
            return False
    
    def get_products(self, filter_active: bool = True) -> List[sqlite3.Row]:
        """Lista todos os produtos"""
        try:
            query = '''
                SELECT 
                    p.*,
                    c.nome as categoria_nome,
                    f.nome as fornecedor_nome,
                    CASE 
                        WHEN p.estoque_atual <= p.estoque_minimo THEN 'BAIXO'
                        WHEN p.estoque_atual >= p.estoque_maximo THEN 'ALTO'
                        ELSE 'NORMAL'
                    END as status_estoque
                FROM produtos p
                LEFT JOIN categorias c ON p.categoria_id = c.id
                LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
            '''
            
            if filter_active:
                query += ' WHERE p.ativo = 1'
            
            query += ' ORDER BY p.nome'
            
            return self.db.execute_query(query)
            
        except Exception as e:
            print(f"❌ Erro ao listar produtos: {e}")
            return []
    
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> bool:
        """Atualiza um produto existente"""
        try:
            command = '''
                UPDATE produtos SET
                    nome = ?, descricao = ?, categoria_id = ?, fornecedor_id = ?,
                    preco_compra = ?, preco_venda = ?, estoque_minimo = ?,
                    estoque_maximo = ?, unidade_medida = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            '''
            
            params = (
                product_data['nome'],
                product_data.get('descricao', ''),
                product_data.get('categoria_id'),
                product_data.get('fornecedor_id'),
                product_data.get('preco_compra', 0.0),
                product_data.get('preco_venda', 0.0),
                product_data.get('estoque_minimo', 0),
                product_data.get('estoque_maximo', 100),
                product_data.get('unidade_medida', 'UN'),
                product_id
            )
            
            rows_affected = self.db.execute_command(command, params)
            return rows_affected > 0
            
        except Exception as e:
            print(f"❌ Erro ao atualizar produto: {e}")
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """Remove um produto (soft delete)"""
        try:
            # Primeiro: verificar se o produto tem estoque > 0
            product = self.db.execute_query(
                'SELECT estoque_atual FROM produtos WHERE id = ?',
                (product_id,)
            )
            
            if not product:
                return False
                
            if product[0]['estoque_atual'] > 0:
                # Produto com estoque não pode ser excluído
                return False
            
            # Segundo: verificar se há movimentações
            movements = self.db.execute_query(
                'SELECT COUNT(*) as count FROM movimentacoes WHERE produto_id = ?',
                (product_id,)
            )
            
            if movements[0]['count'] > 0: #faz a validação de movimento do produto para exclui-lo
                # Soft delete - apenas marca como inativo se ja houver movimentação do produto
                command = 'UPDATE produtos SET ativo = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
            else:
                # Hard delete - remove completamente se o produto nunca teve uma movimentação
                command = 'DELETE FROM produtos WHERE id = ?'
            
            rows_affected = self.db.execute_command(command, (product_id,))
            return rows_affected > 0
            
        except Exception as e:
            print(f"❌ Erro ao deletar produto: {e}")
            return False
    
    def register_movement(self, product_id: int, tipo: str, quantidade: int, 
                         valor_unitario: float = 0.0, observacao: str = '') -> bool:
        """Registra uma movimentação de estoque"""
        try:
            valor_total = quantidade * valor_unitario
            
            # Inserir movimentação
            command = '''
                INSERT INTO movimentacoes (
                    produto_id, tipo, quantidade, valor_unitario, 
                    valor_total, observacao
                ) VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            params = (product_id, tipo, quantidade, valor_unitario, valor_total, observacao)
            self.db.execute_command(command, params)
            
            # Atualizar estoque do produto
            if tipo == 'ENTRADA':
                update_command = '''
                    UPDATE produtos SET 
                        estoque_atual = estoque_atual + ?,
                        updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                '''
            else:  # SAIDA
                update_command = '''
                    UPDATE produtos SET 
                        estoque_atual = estoque_atual - ?,
                        updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                '''
            
            self.db.execute_command(update_command, (quantidade, product_id))
            return True
            
        except Exception as e:
            print(f"❌ Erro ao registrar movimentação: {e}")
            return False
    
    def get_categories(self) -> List[sqlite3.Row]:
        """Lista todas as categorias"""
        return self.db.execute_query('SELECT * FROM categorias ORDER BY nome')
    
    def get_suppliers(self) -> List[sqlite3.Row]:
        """Lista todos os fornecedores"""
        return self.db.execute_query('SELECT * FROM fornecedores ORDER BY nome')
    
    def get_movements(self, product_id: int = None) -> List[sqlite3.Row]:
        """Lista movimentações de estoque"""
        if product_id:
            query = '''
                SELECT m.*, p.nome as produto_nome
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                WHERE m.produto_id = ?
                ORDER BY m.data_movimentacao DESC
            '''
            return self.db.execute_query(query, (product_id,))
        else:
            query = '''
                SELECT m.*, p.nome as produto_nome
                FROM movimentacoes m
                JOIN produtos p ON m.produto_id = p.id
                ORDER BY m.data_movimentacao DESC
                LIMIT 100
            '''
            return self.db.execute_query(query)

class StockControlApp:
    """Aplicação principal do Sistema de Controle de Estoque"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.controller = ProductController()
        self.setup_page()
        self.selected_product_id = None
        
    def setup_page(self):
        """Configura as propriedades da página"""
        self.page.title = "Sistema de Controle de Estoque"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.CYAN_ACCENT
        )
        self.page.bgcolor = ft.Colors.BLACK
        self.page.scroll = "auto"
        self.page.window_width = 1200
        self.page.window_height = 900
        self.page.window_resizable = True
        
        self.build_interface()
    
    def build_interface(self):
        """Constrói a interface principal"""
        title = ft.Text(
            "📦 Sistema de Controle de Estoque",
            size=28,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_800
        )

        self.tabs = ft.Tabs(
            selected_index=0,
            on_change=self.on_tab_change,
            expand=True,
            tabs=[
                ft.Tab(text="Dashboard", icon=ft.Icons.DASHBOARD, content=self.build_dashboard()),
                ft.Tab(text="Produtos", icon=ft.Icons.INVENTORY, content=self.build_products_tab()),
                ft.Tab(text="Movimentações", icon=ft.Icons.SWAP_HORIZ, content=self.build_movements_tab()),
                ft.Tab(text="Relatórios", icon=ft.Icons.ANALYTICS, content=self.build_reports_tab())
            ]
        )

        main_content = ft.Column([
            ft.Container(
                content=title,
                padding=20,
                alignment=ft.alignment.center
            ),
            ft.Divider(),
            self.tabs
        ], expand=True) 

        self.page.add(
            ft.Container(
                content=main_content,
                expand=True,
                padding=0
            )
        )

    def build_dashboard(self) -> ft.Container:
        """Constrói o dashboard principal"""
        # Métricas principais
        products = self.controller.get_products()
        total_products = len(products)
        low_stock = len([p for p in products if p['estoque_atual'] <= p['estoque_minimo']])
        
        valor_total_estoque = sum(p['estoque_atual'] * p['preco_venda'] for p in products)
        
        metrics_row = ft.Row([
            self.create_metric_card("Total de Produtos", str(total_products), ft.Icons.INVENTORY, ft.Colors.BLUE),
            self.create_metric_card("Estoque Baixo", str(low_stock), ft.Icons.WARNING, ft.Colors.ORANGE),
            self.create_metric_card("Valor Total", f"R$ {valor_total_estoque:,.2f}", ft.Icons.ATTACH_MONEY, ft.Colors.GREEN),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        
        # Produtos com estoque baixo
        low_stock_products = [p for p in products if p['estoque_atual'] <= p['estoque_minimo']]
        
        low_stock_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Produto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estoque Atual", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estoque Mínimo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(product['nome'])),
                    ft.DataCell(ft.Text(str(product['estoque_atual']))),
                    ft.DataCell(ft.Text(str(product['estoque_minimo']))),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text("BAIXO", color=ft.Colors.WHITE, size=12),
                            bgcolor=ft.Colors.RED,
                            padding=5,
                            border_radius=5
                        )
                    ),
                ]) for product in low_stock_products[:10]
            ]
        )
        
        dashboard_content = ft.Column([
            metrics_row,
            ft.Divider(),
            ft.Text("🚨 Produtos com Estoque Baixo", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=low_stock_table if low_stock_products else ft.Text("✅ Nenhum produto com estoque baixo!"),
                padding=10
            )
        ],scroll="auto")
        
        return ft.Container(content=dashboard_content, padding=20, expand=True)
    
    def create_metric_card(self, title: str, value: str, icon, color) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Icon(name=icon, size=40, color=color),
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_100),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_ACCENT)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=220,
            height=140,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY_900),
            border_radius=20,
            padding=15,
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(blur_radius=8, color=ft.Colors.CYAN_400, spread_radius=1, offset=ft.Offset(2, 2))
        )
    
    def build_products_tab(self) -> ft.Container:
        """Constrói a aba de produtos"""
        # Formulário de produto
        self.product_form = self.create_product_form()
        
        # Tabela de produtos
        self.products_table = self.create_products_table()
        
        products_content = ft.Column([
            ft.Text("📦 Gerenciamento de Produtos", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.product_form,
            ft.Divider(),
            ft.Text("📋 Lista de Produtos", size=18, weight=ft.FontWeight.BOLD),
            self.products_table
        ],scroll="auto")
        
        return ft.Container(content=products_content, padding=20, expand=True)
    
    def create_product_form(self) -> ft.Container:
        """Cria o formulário de produto"""
        # Campos do formulário
        self.nome_field = ft.TextField(label="Nome do Produto *", width=300)
        self.descricao_field = ft.TextField(label="Descrição", width=300, multiline=True)
        
        # Dropdowns
        categories = self.controller.get_categories()
        self.categoria_dropdown = ft.Dropdown(
            label="Categoria",
            width=200,
            options=[ft.dropdown.Option(cat['id'], cat['nome']) for cat in categories]
        )
        
        suppliers = self.controller.get_suppliers()
        self.fornecedor_dropdown = ft.Dropdown(
            label="Fornecedor",
            width=200,
            options=[ft.dropdown.Option(sup['id'], sup['nome']) for sup in suppliers]
        )
        
        # Campos numéricos
        self.preco_compra_field = ft.TextField(label="Preço Compra", width=150, value="0.00")
        self.preco_venda_field = ft.TextField(label="Preço Venda", width=150, value="0.00")
        self.estoque_atual_field = ft.TextField(label="Estoque Inicial", width=150, value="0",disabled=True)
        self.estoque_minimo_field = ft.TextField(label="Estoque Mínimo", width=150, value="0")
        self.estoque_maximo_field = ft.TextField(label="Estoque Máximo", width=150, value="100")
        self.unidade_field = ft.TextField(label="Unidade", width=100, value="UN")
        
        # Botões
        self.save_button = ft.ElevatedButton(
            "💾 Salvar Produto",
            on_click=self.save_product,
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE
        )
        
        self.clear_button = ft.ElevatedButton(
            "🗑️ Limpar",
            on_click=self.clear_form,
            bgcolor=ft.Colors.GREY,
            color=ft.Colors.WHITE
        )
        
        self.update_button = ft.ElevatedButton(
            "✏️ Atualizar",
            on_click=self.update_product,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE,
            visible=False
        )
        
        # Layout do formulário
        form_layout = ft.Column([
            ft.Row([self.nome_field, self.categoria_dropdown, self.fornecedor_dropdown]),
            ft.Row([self.descricao_field]),
            ft.Row([
                self.preco_compra_field, self.preco_venda_field, self.unidade_field,
                self.estoque_atual_field, self.estoque_minimo_field, self.estoque_maximo_field
            ]),
            ft.Row([self.save_button, self.update_button, self.clear_button])
        ])
        
        return ft.Container(
            content=form_layout,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY_900),
            padding=20,
            border_radius=10
        )
    
    def create_products_table(self) -> ft.Container:
        """Cria a tabela de produtos"""
        self.products_datatable = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nome", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Categoria", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estoque", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Preço Venda", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Ações", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )
        
        self.refresh_products_table()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton(
                        "🔄 Atualizar Lista",
                        on_click=lambda _: self.refresh_products_table()
                    )
                ]),
                self.products_datatable
            ]),
            height=400
        )
    
    def refresh_products_table(self):
        """Atualiza a tabela de produtos"""
        products = self.controller.get_products()
        self.products_datatable.rows.clear()
        
        for product in products:
            # Status do estoque
            if product['estoque_atual'] <= product['estoque_minimo']:
                status_color = ft.Colors.RED
                status_text = "BAIXO"
            elif product['estoque_atual'] >= product['estoque_maximo']:
                status_color = ft.Colors.ORANGE
                status_text = "ALTO"
            else:
                status_color = ft.Colors.GREEN
                status_text = "NORMAL"
            
            self.products_datatable.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(product['id']))),
                    ft.DataCell(ft.Text(product['nome'])),
                    ft.DataCell(ft.Text(product['categoria_nome'] or 'Sem categoria')),
                    ft.DataCell(ft.Text(f"{product['estoque_atual']} {product['unidade_medida']}")),
                    ft.DataCell(ft.Text(f"R$ {product['preco_venda']:.2f}")),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(status_text, color=ft.Colors.WHITE, size=10),
                            bgcolor=status_color,
                            padding=3,
                            border_radius=3
                        )
                    ),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda _, pid=product['id']: self.edit_product(pid)
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE,
                                tooltip="Excluir",
                                on_click=lambda _, pid=product['id']: self.delete_product_confirm(pid)
                            )
                        ])
                    ),
                ])
            )
        
        self.page.update()
    
    def save_product(self, e):
        """Salva um novo produto"""
        if not self.nome_field.value or not self.nome_field.value.strip():
            self.show_message("❌ Nome do produto é obrigatório!", ft.Colors.RED)
            return
        
        try:
            # Validações adicionais
            preco_compra = float(self.preco_compra_field.value or 0)
            preco_venda = float(self.preco_venda_field.value or 0)
            estoque_minimo = int(self.estoque_minimo_field.value or 0)
            estoque_maximo = int(self.estoque_maximo_field.value or 100)
            
            if preco_compra < 0:
                self.show_message("❌ Preço de compra não pode ser negativo!", ft.Colors.RED)
                return
                
            if preco_venda < 0:
                self.show_message("❌ Preço de venda não pode ser negativo!", ft.Colors.RED)
                return
                
            if estoque_minimo < 0:
                self.show_message("❌ Estoque mínimo não pode ser negativo!", ft.Colors.RED)
                return
                
            if estoque_maximo < estoque_minimo:
                self.show_message("❌ Estoque máximo deve ser maior que o mínimo!", ft.Colors.RED)
                return
            
            product_data = {
                'nome': self.nome_field.value.strip(),
                'descricao': self.descricao_field.value.strip() if self.descricao_field.value else '',
                'categoria_id': int(self.categoria_dropdown.value) if self.categoria_dropdown.value else None,
                'fornecedor_id': int(self.fornecedor_dropdown.value) if self.fornecedor_dropdown.value else None,
                'preco_compra': preco_compra,
                'preco_venda': preco_venda,
                'estoque_minimo': estoque_minimo,
                'estoque_maximo': estoque_maximo,
                'unidade_medida': self.unidade_field.value.strip() if self.unidade_field.value else 'UN'
            }
            
            if self.controller.create_product(product_data):
                self.show_message("✅ Produto cadastrado com sucesso!", ft.Colors.GREEN)
                self.clear_form(None)
                self.refresh_products_table()
                self.refresh_reports()
            else:
                self.show_message("❌ Erro ao cadastrar produto! Verifique se o nome não está duplicado.", ft.Colors.RED)
                
        except ValueError as ve:
            self.show_message(f"❌ Erro nos dados numéricos: Verifique os valores inseridos!", ft.Colors.RED)
        except Exception as ex:
            print(f"Erro detalhado: {ex}")  # Para debug
            self.show_message(f"❌ Erro inesperado ao salvar produto!", ft.Colors.RED)
        
    def edit_product(self, product_id: int):
        """Carrega um produto para edição"""
        products = self.controller.get_products(filter_active=False)
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            self.show_message("❌ Produto não encontrado!", ft.Colors.RED)
            return

        # Preencher formulário
        self.nome_field.value = product['nome']
        self.descricao_field.value = product['descricao'] or ''
        self.categoria_dropdown.value = str(product['categoria_id']) if product['categoria_id'] else None
        self.fornecedor_dropdown.value = str(product['fornecedor_id']) if product['fornecedor_id'] else None
        self.preco_compra_field.value = str(product['preco_compra'])
        self.preco_venda_field.value = str(product['preco_venda'])
        self.estoque_minimo_field.value = str(product['estoque_minimo'])
        self.estoque_maximo_field.value = str(product['estoque_maximo'])
        self.unidade_field.value = product['unidade_medida']

        # Atualiza estado interno para saber qual produto está sendo editado
        self.selected_product_id = product['id']

        # Mostrar botão de atualização e ocultar botão de salvar
        self.save_button.visible = False
        self.update_button.visible = True

        # Atualizar a interface
        self.page.update()

    def update_product(self, e):
        """Atualiza um produto existente"""
        if not self.selected_product_id:
            self.show_message("❌ Nenhum produto selecionado para atualização!", ft.Colors.RED)
            return
            
        if not self.nome_field.value.strip():
            self.show_message("❌ Nome do produto é obrigatório!", ft.Colors.RED)
            return
        
        try:
            product_data = {
                'nome': self.nome_field.value.strip(),
                'descricao': self.descricao_field.value.strip(),
                'categoria_id': int(self.categoria_dropdown.value) if self.categoria_dropdown.value else None,
                'fornecedor_id': int(self.fornecedor_dropdown.value) if self.fornecedor_dropdown.value else None,
                'preco_compra': float(self.preco_compra_field.value or 0),
                'preco_venda': float(self.preco_venda_field.value or 0),
                'estoque_minimo': int(self.estoque_minimo_field.value or 0),
                'estoque_maximo': int(self.estoque_maximo_field.value or 100),
                'unidade_medida': self.unidade_field.value.strip() or 'UN'
            }
            
            if self.controller.update_product(self.selected_product_id, product_data):
                self.show_message("✅ Produto atualizado com sucesso!", ft.Colors.GREEN)
                self.clear_form(None)
                self.refresh_products_table()
            else:
                self.show_message("❌ Erro ao atualizar produto!", ft.Colors.RED)
            self.refresh_reports()
                
        except ValueError as ve:
            self.show_message(f"❌ Erro nos dados: {ve}", ft.Colors.RED)
        except Exception as ex:
            self.show_message(f"❌ Erro inesperado: {ex}", ft.Colors.RED)
    
    def clear_form(self, e):
        """Limpa o formulário"""
        self.nome_field.value = ""
        self.descricao_field.value = ""
        self.categoria_dropdown.value = None
        self.fornecedor_dropdown.value = None
        self.preco_compra_field.value = "0.00"
        self.preco_venda_field.value = "0.00"
        self.estoque_atual_field.value = "0"
        self.estoque_minimo_field.value = "0"
        self.estoque_maximo_field.value = "100"
        self.unidade_field.value = "UN"
        
        # Resetar botões
        self.save_button.visible = True
        self.update_button.visible = False
        self.selected_product_id = None
        
        self.page.update()
    
    def delete_product_confirm(self, product_id: int):
        """Confirma a exclusão de um produto"""
        
        # Primeiro: verificar se o produto tem estoque > 0
        products = self.controller.get_products(filter_active=False)
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            self.show_message("❌ Produto não encontrado!", ft.Colors.RED)
            return
        
        if product['estoque_atual'] > 0:
            self.show_message(
                f"❌ Não é possível excluir o produto '{product['nome']}' pois possui estoque de {product['estoque_atual']} {product['unidade_medida']}!", 
                ft.Colors.RED
            )
            return
        
        # Funções do diálogo
        def delete_confirmed(e):
            if self.controller.delete_product(product_id):
                self.show_message("✅ Produto removido com sucesso!", ft.Colors.GREEN)
                self.refresh_products_table()
                self.refresh_reports()
            else:
                self.show_message("❌ Erro ao remover produto!", ft.Colors.RED)
            
            # Fechar diálogo corretamente
            self.dialog.open = False
            self.page.update()
        
        def cancel_delete(e):
            # Fechar diálogo corretamente
            if self.dialog:
                self.dialog.open = False
                self.dialog.update()
            self.page.update()
        
        # Criar diálogo
        confirmation_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Confirmar Exclusão", size=18, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Text(
                    f"Tem certeza que deseja remover o produto:\n\n'{product['nome']}'?\n\nEsta ação não pode ser desfeita.",
                    size=14
                ),
                width=300,
                padding=10
            ),
            actions=[
                ft.TextButton(
                    "❌ Cancelar", 
                    on_click=cancel_delete,
                    style=ft.ButtonStyle(color=ft.Colors.GREY)
                ),
                ft.TextButton(
                    "🗑️ Confirmar Exclusão", 
                    on_click=delete_confirmed,
                    style=ft.ButtonStyle(color=ft.Colors.RED)
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # Definir e abrir diálogo
        self.dialog = confirmation_dialog
        if not self.dialog.open:
            self.dialog.open = True
        self.page.add(self.dialog)
        self.page.update()
            
    def build_movements_tab(self) -> ft.Container:
        """Constrói a aba de movimentações"""
        # Formulário de movimentação
        self.movement_form = self.create_movement_form()
        
        # Tabela de movimentações
        self.movements_table = self.create_movements_table()
        
        movements_content = ft.Column([
            ft.Text("📊 Movimentações de Estoque", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            self.movement_form,
            ft.Divider(),
            ft.Text("📋 Histórico de Movimentações", size=18, weight=ft.FontWeight.BOLD),
            self.movements_table
        ], scroll="auto")
        
        return ft.Container(content=movements_content, padding=20, expand=True)
    
    def create_movement_form(self) -> ft.Container:
        """Cria o formulário de movimentação"""
        # Dropdown de produtos
        products = self.controller.get_products()
        self.produto_movimento_dropdown = ft.Dropdown(
            label="Produto *",
            width=300,
            options=[ft.dropdown.Option(prod['id'], f"{prod['nome']} (Estoque: {prod['estoque_atual']})") for prod in products]
        )
        
        # Tipo de movimentação
        self.tipo_movimento_dropdown = ft.Dropdown(
            label="Tipo de Movimentação *",
            width=200,
            options=[
                ft.dropdown.Option("ENTRADA", "Entrada"),
                ft.dropdown.Option("SAIDA", "Saída")
            ]
        )
        
        # Campos da movimentação
        self.quantidade_movimento_field = ft.TextField(label="Quantidade *", width=150, value="1")
        self.valor_unitario_movimento_field = ft.TextField(label="Valor Unitário", width=150, value="0.00")
        self.observacao_movimento_field = ft.TextField(
            label="Observação", 
            width=400, 
            multiline=True,
            max_lines=3
        )
        
        # Botões
        self.registrar_movimento_button = ft.ElevatedButton(
            "📝 Registrar Movimentação",
            on_click=self.register_movement_click,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )
        
        self.limpar_movimento_button = ft.ElevatedButton(
            "🗑️ Limpar",
            on_click=self.clear_movement_form,
            bgcolor=ft.Colors.GREY,
            color=ft.Colors.WHITE
        )
        
        # Layout do formulário
        form_layout = ft.Column([
            ft.Row([self.produto_movimento_dropdown, self.tipo_movimento_dropdown]),
            ft.Row([self.quantidade_movimento_field, self.valor_unitario_movimento_field]),
            ft.Row([self.observacao_movimento_field]),
            ft.Row([self.registrar_movimento_button, self.limpar_movimento_button])
        ])
        
        return ft.Container(
            content=form_layout,
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLUE_GREY_900),
            padding=20,
            border_radius=10
        )
    
    def create_movements_table(self) -> ft.Container:
        """Cria a tabela de movimentações"""
        self.movements_datatable = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Data", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Produto", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Quantidade", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Valor Unit.", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Valor Total", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Observação", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )
        
        self.refresh_movements_table()
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.ElevatedButton(
                        "🔄 Atualizar Lista",
                        on_click=lambda _: self.refresh_movements_table()
                    )
                ]),
                self.movements_datatable
            ]),
            height=400
        )
    
    def refresh_movements_table(self):
        """Atualiza a tabela de movimentações"""
        movements = self.controller.get_movements()
        self.movements_datatable.rows.clear()
        
        for movement in movements:
            # Formatar data
            data_movimento = datetime.strptime(movement['data_movimentacao'], '%Y-%m-%d %H:%M:%S')
            data_formatada = data_movimento.strftime('%d/%m/%Y %H:%M')
            
            # Cor do tipo
            tipo_color = ft.Colors.GREEN if movement['tipo'] == 'ENTRADA' else ft.Colors.RED
            
            self.movements_datatable.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(data_formatada, size=12)),
                    ft.DataCell(ft.Text(movement['produto_nome'], size=12)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(movement['tipo'], color=ft.Colors.WHITE, size=10),
                            bgcolor=tipo_color,
                            padding=3,
                            border_radius=3
                        )
                    ),
                    ft.DataCell(ft.Text(str(movement['quantidade']), size=12)),
                    ft.DataCell(ft.Text(f"R$ {movement['valor_unitario']:.2f}", size=12)),
                    ft.DataCell(ft.Text(f"R$ {movement['valor_total']:.2f}", size=12)),
                    ft.DataCell(ft.Text(movement['observacao'] or '', size=12)),
                ])
            )
        
        self.page.update()
    
    def register_movement_click(self, e):
        """Registra uma nova movimentação"""
        if not self.produto_movimento_dropdown.value:
            self.show_message("❌ Selecione um produto!", ft.Colors.RED)
            return
            
        if not self.tipo_movimento_dropdown.value:
            self.show_message("❌ Selecione o tipo de movimentação!", ft.Colors.RED)
            return
        
        try:
            quantidade = int(self.quantidade_movimento_field.value or 0)
            if quantidade <= 0:
                self.show_message("❌ Quantidade deve ser maior que zero!", ft.Colors.RED)
                return
                
            valor_unitario = float(self.valor_unitario_movimento_field.value or 0)
            if valor_unitario < 0:
                self.show_message("❌ Valor unitário não pode ser negativo!", ft.Colors.RED)
                return
            
            produto_id = int(self.produto_movimento_dropdown.value)
            tipo = self.tipo_movimento_dropdown.value
            observacao = self.observacao_movimento_field.value.strip() if self.observacao_movimento_field.value else ''
            
            # Verificar se há estoque suficiente para saída
            if tipo == 'SAIDA':
                products = self.controller.get_products()
                product = next((p for p in products if p['id'] == produto_id), None)
                if product and product['estoque_atual'] < quantidade:
                    self.show_message(
                        f"❌ Estoque insuficiente! Disponível: {product['estoque_atual']} {product['unidade_medida']}", 
                        ft.Colors.RED
                    )
                    return
            
            if self.controller.register_movement(produto_id, tipo, quantidade, valor_unitario, observacao):
                self.show_message("✅ Movimentação registrada com sucesso!", ft.Colors.GREEN)
                self.clear_movement_form(None)
                self.refresh_movements_table()
                self.refresh_products_table()
                self.refresh_reports()
                
                # Atualizar dropdown de produtos
                products = self.controller.get_products()
                self.produto_movimento_dropdown.options = [
                    ft.dropdown.Option(prod['id'], f"{prod['nome']} (Estoque: {prod['estoque_atual']})")
                    for prod in products
                ]
                self.page.update()
            else:
                self.show_message("❌ Erro ao registrar movimentação!", ft.Colors.RED)
                
        except ValueError as ve:
            self.show_message("❌ Erro nos dados: Verifique os valores numéricos!", ft.Colors.RED)
        except Exception as ex:
            print(f"Erro detalhado: {ex}")  # Para debug
            self.show_message("❌ Erro inesperado ao registrar movimentação!", ft.Colors.RED)
        
    def clear_movement_form(self, e):
        """Limpa o formulário de movimentação"""
        self.produto_movimento_dropdown.value = None
        self.tipo_movimento_dropdown.value = None
        self.quantidade_movimento_field.value = "1"
        self.valor_unitario_movimento_field.value = "0.00"
        self.observacao_movimento_field.value = ""
        self.page.update()
    
    def refresh_reports(self):
        """Atualiza os dados dos relatórios"""
        if hasattr(self, 'tabs') and len(self.tabs.tabs) > 3:
            self.tabs.tabs[3].content = self.build_reports_tab()
            self.page.update()
    
    def build_reports_tab(self) -> ft.Container:
        """Constrói a aba de relatórios"""
        # Relatório de produtos
        products = self.controller.get_products()
        
        # Estatísticas gerais
        total_produtos = len(products)
        produtos_baixo_estoque = len([p for p in products if p['estoque_atual'] <= p['estoque_minimo']])
        valor_total_estoque = sum(p['estoque_atual'] * p['preco_venda'] for p in products)
        
        # Relatório de movimentações
        movements = self.controller.get_movements()
        total_movimentacoes = len(movements)
        entradas = len([m for m in movements if m['tipo'] == 'ENTRADA'])
        saidas = len([m for m in movements if m['tipo'] == 'SAIDA'])
        
        # Cards de estatísticas
        stats_row1 = ft.Row([
            self.create_metric_card("Total Produtos", str(total_produtos), ft.Icons.INVENTORY, ft.Colors.BLUE),
            self.create_metric_card("Estoque Baixo", str(produtos_baixo_estoque), ft.Icons.WARNING, ft.Colors.ORANGE),
            self.create_metric_card("Valor Total", f"R$ {valor_total_estoque:,.2f}", ft.Icons.ATTACH_MONEY, ft.Colors.GREEN),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        
        stats_row2 = ft.Row([
            self.create_metric_card("Total Movimentações", str(total_movimentacoes), ft.Icons.SWAP_HORIZ, ft.Colors.PURPLE),
            self.create_metric_card("Entradas", str(entradas), ft.Icons.ARROW_DOWNWARD, ft.Colors.GREEN),
            self.create_metric_card("Saídas", str(saidas), ft.Icons.ARROW_UPWARD, ft.Colors.RED),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        
        # Tabela de produtos por categoria
        categories_report = self.create_categories_report()
        
        # Botões de exportação
        export_buttons = ft.Row([
            ft.ElevatedButton(
                "📄 Exportar Produtos (JSON)",
                on_click=self.export_products_json,
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE
            ),
            ft.ElevatedButton(
                "📄 Exportar Movimentações (JSON)",
                on_click=self.export_movements_json,
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE
            ),
        ])
        
        reports_content = ft.Column([
            ft.Text("📈 Relatórios e Estatísticas", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("📊 Estatísticas Gerais", size=18, weight=ft.FontWeight.BOLD),
            stats_row1,
            ft.Container(height=10),  # Espaçamento
            stats_row2,
            ft.Divider(),
            ft.Text("📋 Produtos por Categoria", size=18, weight=ft.FontWeight.BOLD),
            categories_report,
            ft.Divider(),
            ft.Text("💾 Exportação de Dados", size=18, weight=ft.FontWeight.BOLD),
            export_buttons
        ], scroll="auto")
        
        return ft.Container(content=reports_content, padding=20, expand=True)
    
    def create_categories_report(self) -> ft.Container:
        """Cria relatório de produtos por categoria"""
        categories = self.controller.get_categories()
        products = self.controller.get_products()
        
        categories_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Categoria", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Qtd Produtos", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Valor Total", weight=ft.FontWeight.BOLD)),
            ],
            rows=[]
        )
        
        for category in categories:
            category_products = [p for p in products if p['categoria_id'] == category['id']]
            qtd_produtos = len(category_products)
            valor_total = sum(p['estoque_atual'] * p['preco_venda'] for p in category_products)
            
            categories_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(category['nome'])),
                    ft.DataCell(ft.Text(str(qtd_produtos))),
                    ft.DataCell(ft.Text(f"R$ {valor_total:.2f}")),
                ])
            )
        
        # Produtos sem categoria
        sem_categoria = [p for p in products if not p['categoria_id']]
        if sem_categoria:
            qtd_sem_categoria = len(sem_categoria)
            valor_sem_categoria = sum(p['estoque_atual'] * p['preco_venda'] for p in sem_categoria)
            categories_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Sem Categoria")),
                    ft.DataCell(ft.Text(str(qtd_sem_categoria))),
                    ft.DataCell(ft.Text(f"R$ {valor_sem_categoria:.2f}")),
                ])
            )
        
        return ft.Container(content=categories_table, height=300)
    
    def export_products_json(self, e):
        """Exporta produtos para JSON"""
        try:
            products = self.controller.get_products()
            products_data = []
            
            for product in products:
                products_data.append({
                    'id': product['id'],
                    'nome': product['nome'],
                    'descricao': product['descricao'],
                    'categoria': product['categoria_nome'],
                    'fornecedor': product['fornecedor_nome'],
                    'preco_compra': product['preco_compra'],
                    'preco_venda': product['preco_venda'],
                    'estoque_atual': product['estoque_atual'],
                    'estoque_minimo': product['estoque_minimo'],
                    'estoque_maximo': product['estoque_maximo'],
                    'unidade_medida': product['unidade_medida'],
                    'status_estoque': product['status_estoque']
                })
            
            # Salvar arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/produtos_export_{timestamp}.json'
            
            os.makedirs('data', exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products_data, f, ensure_ascii=False, indent=2)
            
            self.show_message(f"✅ Produtos exportados para: {filename}", ft.Colors.GREEN)
            
        except Exception as ex:
            self.show_message(f"❌ Erro ao exportar: {ex}", ft.Colors.RED)
    
    def export_movements_json(self, e):
        """Exporta movimentações para JSON"""
        try:
            movements = self.controller.get_movements()
            movements_data = []
            
            for movement in movements:
                movements_data.append({
                    'id': movement['id'],
                    'produto': movement['produto_nome'],
                    'tipo': movement['tipo'],
                    'quantidade': movement['quantidade'],
                    'valor_unitario': movement['valor_unitario'],
                    'valor_total': movement['valor_total'],
                    'observacao': movement['observacao'],
                    'data_movimentacao': movement['data_movimentacao'],
                    'usuario': movement['usuario']
                })
            
            # Salvar arquivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/movimentacoes_export_{timestamp}.json'
            
            os.makedirs('data', exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(movements_data, f, ensure_ascii=False, indent=2)
            
            self.show_message(f"✅ Movimentações exportadas para: {filename}", ft.Colors.GREEN)
            
        except Exception as ex:
            self.show_message(f"❌ Erro ao exportar: {ex}", ft.Colors.RED)
    
    def close_dialog(self):
        """Fecha o AlertDialog atual"""
        if self.dialog:
            self.dialog.open = False
            self.dialog.update()
            self.page.update()
        
    def show_message(self, message: str, color=ft.Colors.BLUE):
        """Exibe as mensagens usando AlertDialog"""
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Mensagem", weight=ft.FontWeight.BOLD),
            content=ft.Text(message, color=color),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self.close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if not self.dialog.open:
            self.dialog.open = True
        self.page.add(self.dialog)
        self.page.update()
        
    def on_tab_change(self, e):
        """Callback para mudança de aba"""
        # Atualizar dados quando necessário
        if e.control.selected_index == 0:  # Dashboard
            # Reconstruir dashboard com dados atualizados
            self.tabs.tabs[0].content = self.build_dashboard()
        elif e.control.selected_index == 2:  # Movimentações
            # Atualizar dropdown de produtos
            products = self.controller.get_products()
            if hasattr(self, 'produto_movimento_dropdown'):
                self.produto_movimento_dropdown.options = [
                    ft.dropdown.Option(prod['id'], f"{prod['nome']} (Estoque: {prod['estoque_atual']})")
                    for prod in products
                ]
        elif e.control.selected_index == 3:  # Relatórios
            # Reconstruir relatórios com dados atualizados
            self.tabs.tabs[3].content = self.build_reports_tab()
        
        self.page.update()

def main(page: ft.Page):
    
    """Função principal da aplicação"""
    try:
        app = StockControlApp(page)
        print("🚀 Aplicação iniciada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        page.add(ft.Text(f"Erro ao iniciar aplicação: {e}", color=ft.Colors.RED))

if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=DeprecationWarning) #Apenas para ignorar as warnings de depreciação
    ft.app(target=main, view=ft.WEB_BROWSER, port=8080)