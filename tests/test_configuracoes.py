import pytest
from pathlib import Path
import json
import shutil
from core.configuracoes import GerenciadorConfiguracoes

@pytest.fixture
def config_temp(tmp_path):
    """Fixture que cria um ambiente temporário para testes"""
    # Cria diretório de configuração temporário
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Copia arquivo de configuração para diretório temporário
    config_path = Path("config/programacao.json")
    if config_path.exists():
        shutil.copy(config_path, config_dir / "programacao.json")
    
    yield tmp_path
    
    # Limpa arquivos temporários
    shutil.rmtree(tmp_path)

@pytest.fixture
def gerenciador(config_temp):
    """Fixture que cria uma instância do gerenciador"""
    return GerenciadorConfiguracoes()

def test_carregar_configuracoes(gerenciador):
    """Testa o carregamento de configurações"""
    assert gerenciador.config is not None
    assert "preferencias" in gerenciador.config
    assert "tema" in gerenciador.config["preferencias"]
    
def test_obter_configuracao(gerenciador):
    """Testa a obtenção de configurações específicas"""
    # Testa configuração existente
    tema = gerenciador.obter_configuracao("preferencias.tema.padrao")
    assert tema == "dark"
    
    # Testa configuração inexistente com valor padrão
    valor = gerenciador.obter_configuracao("caminho.inexistente", "padrao")
    assert valor == "padrao"
    
def test_definir_configuracao(gerenciador):
    """Testa a definição de configurações"""
    # Define uma nova configuração
    gerenciador.definir_configuracao("preferencias.tema.padrao", "light")
    
    # Verifica se foi alterada
    tema = gerenciador.obter_configuracao("preferencias.tema.padrao")
    assert tema == "light"
    
    # Verifica se foi salva no arquivo
    config_path = Path("config/programacao.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        assert config["preferencias"]["tema"]["padrao"] == "light"
        
def test_restaurar_padrao(gerenciador):
    """Testa a restauração de configurações padrão"""
    # Altera algumas configurações
    gerenciador.definir_configuracao("preferencias.tema.padrao", "light")
    gerenciador.definir_configuracao("preferencias.interface.fonte.tamanho", 14)
    
    # Restaura configurações padrão
    gerenciador.restaurar_padrao()
    
    # Verifica se foram restauradas
    assert gerenciador.obter_configuracao("preferencias.tema.padrao") == "dark"
    assert gerenciador.obter_configuracao("preferencias.interface.fonte.tamanho") == 12
    
def test_observadores(gerenciador):
    """Testa o sistema de observadores"""
    alteracoes = []
    
    def observador(caminho, valor):
        alteracoes.append((caminho, valor))
    
    # Adiciona observador
    gerenciador.adicionar_observador(observador)
    
    # Faz algumas alterações
    gerenciador.definir_configuracao("preferencias.tema.padrao", "light")
    gerenciador.definir_configuracao("preferencias.interface.fonte.tamanho", 14)
    
    # Verifica se o observador foi notificado
    assert len(alteracoes) == 2
    assert alteracoes[0] == ("preferencias.tema.padrao", "light")
    assert alteracoes[1] == ("preferencias.interface.fonte.tamanho", 14)
    
    # Remove observador
    gerenciador.remover_observador(observador)
    
    # Faz mais uma alteração
    gerenciador.definir_configuracao("preferencias.tema.padrao", "dark")
    
    # Verifica se o observador não foi mais notificado
    assert len(alteracoes) == 2
    
def test_obter_tema(gerenciador):
    """Testa a obtenção de cores do tema"""
    cores = gerenciador.obter_tema()
    assert "fundo" in cores
    assert "texto" in cores
    assert "destaque" in cores
    
def test_obter_fonte(gerenciador):
    """Testa a obtenção de configurações de fonte"""
    fonte = gerenciador.obter_fonte()
    assert "familia" in fonte
    assert "tamanho" in fonte
    assert "estilo" in fonte
    
def test_obter_layout(gerenciador):
    """Testa a obtenção de configurações de layout"""
    layout = gerenciador.obter_layout()
    assert "mostrar_numeros_linha" in layout
    assert "quebrar_linha" in layout
    assert "destacar_linha_atual" in layout
    
def test_obter_config_editor(gerenciador):
    """Testa a obtenção de configurações do editor"""
    config = gerenciador.obter_config_editor()
    assert "auto_indentacao" in config
    assert "auto_completar" in config
    assert "destacar_sintaxe" in config
    
def test_obter_config_sugestoes(gerenciador):
    """Testa a obtenção de configurações de sugestões"""
    config = gerenciador.obter_config_sugestoes()
    assert "mostrar_automaticamente" in config
    assert "max_sugestoes" in config
    assert "ordenar_por" in config
    
def test_obter_config_analise(gerenciador):
    """Testa a obtenção de configurações de análise"""
    config = gerenciador.obter_config_analise()
    assert "tempo_real" in config
    assert "intervalo_analise" in config
    assert "nivel_detalhe" in config
    
def test_obter_config_notificacoes(gerenciador):
    """Testa a obtenção de configurações de notificações"""
    config = gerenciador.obter_config_notificacoes()
    assert "erros" in config
    assert "avisos" in config
    assert "sugestoes" in config
    
def test_obter_config_perfil(gerenciador):
    """Testa a obtenção de configurações do perfil"""
    config = gerenciador.obter_config_perfil()
    assert "salvar_historico" in config
    assert "max_historico" in config
    assert "sincronizar" in config 