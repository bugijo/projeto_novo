import asyncio
from core.gerenciador_sistema_avancado import GerenciadorSistemaAvancado
from core.monitor_seguranca import MonitorSeguranca
import json
import time

async def testar_sistema():
    print("\n=== INICIANDO TESTES COMPLETOS DO SISTEMA ===\n")
    
    # 1. Teste de APIs
    print("1. Verificando status das APIs...")
    gerenciador = GerenciadorSistemaAvancado()
    status_apis = gerenciador.verificar_apis()
    print(f"Status das APIs: {json.dumps(status_apis, indent=2)}")

    # 2. Teste de Hardware
    print("\n2. Coletando informações de hardware...")
    relatorio = gerenciador.gerar_relatorio()
    print(f"Informações do sistema: {json.dumps(relatorio, indent=2)}")

    # 3. Teste de Privilégios
    print("\n3. Verificando privilégios de administrador...")
    if not gerenciador.tem_admin:
        print("Solicitando privilégios de administrador...")
        admin_resultado = gerenciador.solicitar_admin()
        print(f"Resultado da solicitação: {'Sucesso' if admin_resultado else 'Falha'}")

    # 4. Teste de Monitoramento
    print("\n4. Iniciando monitor de segurança...")
    monitor = MonitorSeguranca()
    monitor.iniciar_monitoramento()
    
    print("Aguardando 10 segundos para coletar dados...")
    time.sleep(10)
    
    relatorio_seguranca = monitor.obter_relatorio()
    print(f"Relatório de segurança: {json.dumps(relatorio_seguranca, indent=2)}")
    
    # 5. Teste de Otimização
    print("\n5. Testando otimização do sistema...")
    perfis = ["gaming", "produtividade", "economia"]
    for perfil in perfis:
        print(f"\nTestando perfil: {perfil}")
        resultado = await gerenciador.otimizar_sistema(perfil)
        print(f"Resultado da otimização: {json.dumps(resultado, indent=2)}")
        time.sleep(2)  # Pausa entre otimizações

    # 6. Teste de Temperaturas
    print("\n6. Monitorando temperaturas...")
    temps = gerenciador._obter_temperaturas()
    print(f"Temperaturas atuais: {json.dumps(temps, indent=2)}")

    # 7. Teste de Energia
    print("\n7. Verificando status de energia...")
    energia = gerenciador._obter_status_energia()
    print(f"Status de energia: {json.dumps(energia, indent=2)}")

    # 8. Teste de Segurança
    print("\n8. Verificando configurações de segurança...")
    seguranca = {
        "firewall": gerenciador._verificar_firewall_ativo(),
        "antivirus": gerenciador._verificar_antivirus_ativo(),
        "atualizacoes": gerenciador._verificar_atualizacoes_pendentes()
    }
    print(f"Status de segurança: {json.dumps(seguranca, indent=2)}")

    # Finalizando testes
    print("\n=== TESTES CONCLUÍDOS ===")
    
    # Parando monitoramento
    monitor.parar_monitoramento()

if __name__ == "__main__":
    asyncio.run(testar_sistema()) 