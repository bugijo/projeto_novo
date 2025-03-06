import pytest
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt
import json
import os

# Importa os componentes principais
from core.programacao import AssistenteProgramacao, AnalisadorCodigo
from core.interface_programacao import InterfaceProgramacao, EditorCodigo, PainelSugestoes
from core.perfil_usuario import PerfilUsuario

# Arquivo de teste temporário
CODIGO_TESTE = """
import os
from typing import List, Dict

def funcao_complexa(param1, param2, param3, param4, param5, param6):
    '''Função com muitos parâmetros para teste'''
    resultado = param1 + param2
    for i in range(100):
        resultado += i
    return resultado

class ClasseTeste:
    def __init__(self):
        self.valor = 0
    
    def metodo_teste(self):
        return self.valor
"""

@pytest.fixture(scope="session")
def app():
    """Fixture para criar a aplicação Qt"""
    app = QApplication(sys.argv)
    yield app
    app.quit()

@pytest.fixture
def assistente(app, tmp_path):
    """Fixture para criar o assistente"""
    assistente = AssistenteProgramacao()
    QTest.qWait(200)  # Aguarda inicialização
    yield assistente
    assistente.finalizar()
    QTest.qWait(200)  # Aguarda finalização

@pytest.fixture
def interface(app, assistente):
    """Fixture para criar a interface"""
    interface = assistente.interface
    QTest.qWait(200)  # Aguarda inicialização
    yield interface
    interface.close()
    QTest.qWait(200)  # Aguarda finalização

@pytest.fixture
def arquivo_teste(tmp_path):
    """Fixture para criar um arquivo de teste"""
    arquivo = tmp_path / "teste.py"
    arquivo.write_text(CODIGO_TESTE, encoding='utf-8')
    return arquivo

@pytest.fixture
def perfil(tmp_path):
    """Fixture para criar um perfil de usuário para testes"""
    # Configura diretório temporário para dados
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    os.environ["DATA_DIR"] = str(data_dir)
    
    perfil = PerfilUsuario()
    yield perfil
    
    # Limpa recursos
    if perfil.driver:
        perfil.fechar_navegador()

def test_analisador_codigo(arquivo_teste):
    """Testa o analisador de código"""
    analisador = AnalisadorCodigo()
    resultado = analisador.analisar_arquivo(arquivo_teste)
    
    print("\nResultado da análise:", resultado)
    
    # Verifica imports
    assert len(resultado["imports"]) >= 2, f"Esperava pelo menos 2 imports, mas encontrou {len(resultado['imports'])}"
    print("\nImports encontrados:", resultado["imports"])
    assert any(imp["modulo"] == "os" for imp in resultado["imports"]), "Import 'os' não encontrado"
    
    # Verifica classes
    assert len(resultado["classes"]) == 1, f"Esperava 1 classe, mas encontrou {len(resultado['classes'])}"
    classe = resultado["classes"][0]
    assert classe["nome"] == "ClasseTeste", f"Nome da classe errado: {classe['nome']}"
    assert classe["metodos"] >= 1, f"Número de métodos errado: {classe['metodos']}"
    
    # Verifica funções
    assert len(resultado["funcoes"]) >= 1, f"Esperava pelo menos 1 função, mas encontrou {len(resultado['funcoes'])}"
    funcao = next(f for f in resultado["funcoes"] if f["nome"] == "funcao_complexa")
    assert funcao["nome"] == "funcao_complexa", f"Nome da função errado: {funcao['nome']}"
    assert funcao["argumentos"] == 6, f"Número de argumentos errado: {funcao['argumentos']}"
    
    # Verifica sugestões
    assert len(resultado["sugestoes"]) > 0, "Nenhuma sugestão encontrada"
    assert any("muitos argumentos" in sugestao for sugestao in resultado["sugestoes"]), "Sugestão sobre muitos argumentos não encontrada"

def test_interface_inicializacao(interface):
    """Testa a inicialização da interface"""
    # Verifica componentes principais
    assert interface.arvore_arquivos is not None
    assert interface.tabs_arquivos is not None
    assert interface.painel_sugestoes is not None
    
    # Verifica configurações iniciais
    assert interface.tabs_arquivos.count() == 0
    assert interface.windowTitle() == "Assistente de Programação"

def test_editor_codigo(app):
    """Testa o editor de código"""
    editor = EditorCodigo()
    
    # Testa configurações do editor
    assert editor.font().family() == "Consolas"
    assert editor.font().pointSize() == 11
    assert editor.lineWrapMode() == EditorCodigo.LineWrapMode.NoWrap
    
    # Testa highlight de sintaxe
    assert editor.highlighter is not None

def test_painel_sugestoes(app):
    """Testa o painel de sugestões"""
    painel = PainelSugestoes()
    
    # Testa componentes
    assert painel.lista_sugestoes is not None
    assert painel.lista_sugestoes.isReadOnly()

def esperar_evento(tempo_ms=200):
    """Aguarda o processamento de eventos do Qt"""
    QTest.qWait(tempo_ms)
    QApplication.processEvents()

def test_abrir_arquivo(app, interface, arquivo_teste):
    """Testa a abertura de arquivo"""
    try:
        interface.abrir_arquivo(str(arquivo_teste))
        esperar_evento(200)  # Aguarda processamento de eventos
        
        # Verifica se a aba foi criada
        assert interface.tabs_arquivos.count() == 1, "Aba não foi criada"
        assert interface.tabs_arquivos.tabText(0) == arquivo_teste.name, "Nome da aba incorreto"
        
        # Verifica se o conteúdo foi carregado
        editor = interface.tabs_arquivos.widget(0)
        assert editor is not None, "Editor não foi criado"
        assert CODIGO_TESTE in editor.toPlainText(), "Conteúdo não foi carregado"
    except Exception as e:
        print(f"Erro no teste: {e}")
        raise

def test_sugestoes_atualizadas(app, interface, arquivo_teste):
    """Testa a atualização de sugestões"""
    try:
        interface.abrir_arquivo(str(arquivo_teste))
        esperar_evento(200)  # Aguarda processamento de eventos
        
        interface.atualizar_sugestoes(str(arquivo_teste))
        esperar_evento(200)  # Aguarda processamento de eventos
        
        # Verifica se as sugestões foram atualizadas
        sugestoes = interface.painel_sugestoes.lista_sugestoes.toPlainText()
        assert len(sugestoes) > 0, "Nenhuma sugestão foi gerada"
        assert "IMPORTS" in sugestoes or "CLASSES" in sugestoes, "Conteúdo das sugestões incorreto"
    except Exception as e:
        print(f"Erro no teste: {e}")
        raise

def test_fechar_arquivo(app, interface, arquivo_teste):
    """Testa o fechamento de arquivo"""
    try:
        interface.abrir_arquivo(str(arquivo_teste))
        esperar_evento(200)  # Aguarda processamento de eventos
        assert interface.tabs_arquivos.count() == 1, "Arquivo não foi aberto"
        
        interface.fechar_arquivo(0)
        esperar_evento(200)  # Aguarda processamento de eventos
        assert interface.tabs_arquivos.count() == 0, "Arquivo não foi fechado"
    except Exception as e:
        print(f"Erro no teste: {e}")
        raise

def test_monitoramento_arquivos(app, assistente, arquivo_teste):
    """Testa o monitoramento de arquivos"""
    try:
        esperar_evento(500)  # Aguarda inicialização do observer
        
        # Verifica se o observer está rodando
        assert assistente.observer is not None, "Observer não foi inicializado"
        assert assistente.observer.is_alive(), "Observer não está rodando"
        
        # Simula modificação no arquivo
        arquivo_teste.write_text(CODIGO_TESTE + "\n# Comentário novo", encoding='utf-8')
        
        esperar_evento(500)  # Aguarda processamento do evento
        
        # Verifica se a análise foi atualizada
        assert not assistente.fila_analise.empty(), "Arquivo modificado não foi detectado"
    except Exception as e:
        print(f"Erro no teste: {e}")
        raise
    finally:
        esperar_evento(200)  # Aguarda finalização

def test_analise_codigo_complexo(assistente, arquivo_teste):
    """Testa análise de código complexo"""
    resultado = assistente.analisar_arquivo(arquivo_teste)
    
    # Verifica análise detalhada
    assert "funcoes" in resultado
    assert "classes" in resultado
    assert "imports" in resultado
    assert "sugestoes" in resultado
    
    # Verifica sugestões específicas
    sugestoes = assistente.sugerir_codigo(resultado)
    assert len(sugestoes) > 0

def test_integracao_completa(assistente, arquivo_teste):
    """Testa integração completa do sistema"""
    # Mostra interface
    assistente.mostrar_interface()
    
    # Abre arquivo
    assistente.interface.abrir_arquivo(str(arquivo_teste))
    esperar_evento(500)  # Aguarda processamento
    
    # Verifica componentes ativos
    assert assistente.interface.isVisible()
    assert assistente.interface.tabs_arquivos.count() == 1
    
    # Força análise e atualização de sugestões
    resultado = assistente.analisar_arquivo(str(arquivo_teste))
    assistente.interface.atualizar_sugestoes(str(arquivo_teste), resultado)
    esperar_evento(500)  # Aguarda atualização da interface
    
    # Verifica se as sugestões foram atualizadas
    texto_sugestoes = assistente.interface.painel_sugestoes.lista_sugestoes.toPlainText()
    assert len(texto_sugestoes) > 0, "Nenhuma sugestão foi exibida"

def test_perfil_usuario_inicializacao(perfil):
    """Testa a inicialização do perfil do usuário"""
    assert perfil.dados is not None
    assert "preferencias" in perfil.dados
    assert "hobbies" in perfil.dados
    assert len(perfil.historico_atividades) == 0

def test_registro_atividades(perfil):
    """Testa o registro de atividades do usuário"""
    # Registra uma série assistida
    perfil.registrar_atividade("midia", {
        "categoria": "serie",
        "nome": "Breaking Bad"
    })
    
    # Verifica se foi registrado
    assert "Breaking Bad" in perfil.dados["preferencias"]["series"]
    assert len(perfil.historico_atividades) == 1

def test_sugestao_midia(perfil):
    """Testa as sugestões de mídia"""
    # Registra algumas séries
    series = ["Breaking Bad", "Better Call Saul", "The Wire"]
    for serie in series:
        perfil.registrar_atividade("midia", {
            "categoria": "serie",
            "nome": serie
        })
    
    # Testa sugestões
    sugestoes = perfil.sugerir_midia("serie")
    assert len(sugestoes) > 0
    assert series[-1] in sugestoes  # deve sugerir a série mais recente

def test_automacao_basica(perfil):
    """Testa funções básicas de automação"""
    # Testa movimento do mouse (sem realmente mover)
    try:
        perfil.mover_mouse(100, 100, duracao=0.1)
        assert True  # Se não lançou exceção, está ok
    except Exception as e:
        pytest.fail(f"Erro ao mover mouse: {e}")

def test_integracao_assistente_perfil(assistente):
    """Testa a integração entre o assistente e o perfil"""
    # Verifica se o perfil foi inicializado
    assert assistente.perfil is not None
    
    # Testa comando de mídia
    assistente.executar_acao("assistir série")
    
    # Testa comando de automação
    try:
        assistente.executar_acao("abrir navegador")
        assert True
    except Exception as e:
        pytest.fail(f"Erro ao executar ação: {e}")

def test_persistencia_dados(tmp_path):
    """Testa se os dados do perfil são salvos corretamente"""
    # Configura diretório temporário
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    os.environ["DATA_DIR"] = str(data_dir)
    
    # Cria perfil e adiciona dados
    perfil = PerfilUsuario()
    perfil.registrar_atividade("midia", {
        "categoria": "filme",
        "nome": "Matrix"
    })
    perfil.salvar_dados()
    
    # Verifica se o arquivo foi criado
    arquivo_perfil = data_dir / "perfil_usuario.json"
    assert arquivo_perfil.exists()
    
    # Carrega os dados e verifica
    with open(arquivo_perfil, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    assert "Matrix" in dados["preferencias"]["filmes"]["assistidos"]

def test_preferencias_usuario(assistente):
    """Testa a integração das preferências do usuário"""
    # Testa tema padrão
    assert assistente.obter_tema_preferido() == "dark"
    
    # Testa mudança de tema
    assistente.definir_tema("light")
    assert assistente.obter_tema_preferido() == "light"
    
    # Testa registro de uso de app
    assistente.registrar_uso_app("vscode")
    assistente.registrar_uso_app("vscode")
    assistente.registrar_uso_app("chrome")
    
    # Testa registro de acesso a site
    assistente.registrar_acesso_site("github.com")
    assistente.registrar_acesso_site("github.com")
    assistente.registrar_acesso_site("stackoverflow.com")
    
    # Testa sugestões personalizadas
    sugestoes = assistente.obter_sugestoes_personalizadas()
    assert "apps" in sugestoes
    assert "sites" in sugestoes
    assert "vscode" in sugestoes["apps"]
    assert "chrome" in sugestoes["apps"]
    assert "github.com" in sugestoes["sites"]
    assert "stackoverflow.com" in sugestoes["sites"]
    
    # Testa atualização de preferências
    novas_prefs = {
        "series": ["Breaking Bad", "Better Call Saul"],
        "filmes": {
            "generos_favoritos": ["Ação", "Ficção Científica"]
        }
    }
    assistente.atualizar_preferencias(novas_prefs)
    
    # Verifica se as preferências foram salvas
    assert "Breaking Bad" in assistente.perfil.dados["preferencias"]["series"]
    assert "Ação" in assistente.perfil.dados["preferencias"]["filmes"]["generos_favoritos"]

def test_interface_preferencias(assistente, qtbot):
    """Testa a interface com as preferências do usuário"""
    # Obtém a interface
    interface = assistente.interface
    
    # Testa tema inicial
    assert interface.tema_atual == "dark"
    
    # Simula mudança de tema
    interface.mudar_tema("light")
    assert interface.tema_atual == "light"
    assert assistente.obter_tema_preferido() == "light"
    
    # Testa atualização de sugestões
    assistente.registrar_uso_app("vscode")
    assistente.registrar_acesso_site("github.com")
    
    # Simula clique no botão de atualizar sugestões
    painel_sugestoes = interface.painel_sugestoes
    qtbot.mouseClick(painel_sugestoes.findChild(QPushButton, ""), Qt.LeftButton)
    
    # Verifica se as sugestões foram atualizadas
    sugestoes = assistente.obter_sugestoes_personalizadas()
    assert "vscode" in sugestoes["apps"]
    assert "github.com" in sugestoes["sites"] 