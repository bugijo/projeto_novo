import pytest
from pathlib import Path
from core.gerenciador_preferencias import GerenciadorPreferencias

@pytest.fixture
def gerenciador(tmp_path):
    """Fixture que cria um gerenciador de preferências para testes"""
    # Configura diretório temporário
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # Patch do Path para usar diretório temporário
    original_path = Path
    Path = lambda *args: tmp_path / args[-1]
    
    gerenciador = GerenciadorPreferencias()
    
    # Restaura Path original
    Path = original_path
    
    return gerenciador

def test_inicializacao(gerenciador):
    """Testa a inicialização do gerenciador"""
    assert gerenciador.preferencias_usuario.tema == "dark"
    assert gerenciador.preferencias_usuario.idioma == "pt-BR"
    assert len(gerenciador.historico_interacoes) == 0

def test_registro_midia(gerenciador):
    """Testa o registro de interações com mídia"""
    # Registra série
    gerenciador.registrar_interacao("midia", {
        "tipo": "serie",
        "nome": "Breaking Bad",
        "genero": "Drama"
    })
    
    assert "Breaking Bad" in gerenciador.preferencias_midia.series_favoritas
    assert "Drama" in gerenciador.preferencias_midia.generos_preferidos
    assert len(gerenciador.historico_interacoes) == 1

def test_registro_musica(gerenciador):
    """Testa o registro de interações com música"""
    # Registra música
    gerenciador.registrar_interacao("musica", {
        "artista": "Metallica",
        "genero": "Metal",
        "playlist": "Rock",
        "musica": "Nothing Else Matters"
    })
    
    assert "Metallica" in gerenciador.preferencias_musica.artistas_favoritos
    assert "Metal" in gerenciador.preferencias_musica.generos_preferidos
    assert "Nothing Else Matters" in gerenciador.preferencias_musica.playlists["Rock"]

def test_recomendacoes(gerenciador):
    """Testa o sistema de recomendações"""
    # Registra algumas interações
    gerenciador.registrar_interacao("midia", {
        "tipo": "serie",
        "nome": "The Office",
        "genero": "Comédia"
    })
    
    gerenciador.registrar_interacao("musica", {
        "artista": "Queen",
        "genero": "Rock"
    })
    
    # Testa recomendações
    series = gerenciador.obter_recomendacoes("serie")
    assert "The Office" in series
    
    musicas = gerenciador.obter_recomendacoes("musica")
    assert any("Queen" in m for m in musicas)

def test_atualizacao_preferencias(gerenciador):
    """Testa a atualização de preferências do usuário"""
    assert gerenciador.atualizar_preferencia_usuario("tema", "light")
    assert gerenciador.preferencias_usuario.tema == "light"
    
    assert not gerenciador.atualizar_preferencia_usuario("configuracao_invalida", "valor")

def test_estatisticas(gerenciador):
    """Testa a geração de estatísticas"""
    # Registra algumas interações
    gerenciador.registrar_interacao("midia", {
        "tipo": "serie",
        "nome": "Stranger Things",
        "genero": "Ficção"
    })
    
    gerenciador.registrar_interacao("midia", {
        "tipo": "filme",
        "nome": "Matrix",
        "genero": "Ficção"
    })
    
    gerenciador.registrar_interacao("musica", {
        "artista": "Pink Floyd",
        "genero": "Rock Progressivo"
    })
    
    # Verifica estatísticas
    stats = gerenciador.obter_estatisticas()
    assert stats["total_series"] == 1
    assert stats["total_filmes"] == 1
    assert stats["total_artistas"] == 1
    assert "Ficção" in stats["generos_favoritos"]["midia"]
    assert "Rock Progressivo" in stats["generos_favoritos"]["musica"]
    assert stats["total_interacoes"] == 3

def test_persistencia(tmp_path):
    """Testa a persistência dos dados"""
    # Configura Path para usar diretório temporário
    original_path = Path
    Path = lambda *args: tmp_path / args[-1]
    
    # Cria primeiro gerenciador e registra dados
    gerenciador1 = GerenciadorPreferencias()
    gerenciador1.registrar_interacao("midia", {
        "tipo": "serie",
        "nome": "Black Mirror",
        "genero": "Ficção"
    })
    
    # Cria segundo gerenciador que deve carregar os dados salvos
    gerenciador2 = GerenciadorPreferencias()
    
    # Restaura Path original
    Path = original_path
    
    # Verifica se os dados persistiram
    assert "Black Mirror" in gerenciador2.preferencias_midia.series_favoritas
    assert "Ficção" in gerenciador2.preferencias_midia.generos_preferidos
    assert len(gerenciador2.historico_interacoes) == 1 