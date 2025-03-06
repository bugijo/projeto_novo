from core.assistente_otimizado import AssistenteOtimizado
import time
import logging

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    # Cria instância do assistente
    assistente = AssistenteOtimizado()
    
    # Exemplo 1: Verificar status de segurança
    print("\nVerificando status de segurança...")
    resultado = assistente.processar_comando(
        "mostrar relatório de segurança"
    )
    print(f"Resultado:\n{resultado}")
    
    # Exemplo 2: Verificar desempenho do sistema
    print("\nVerificando desempenho do sistema...")
    resultado = assistente.processar_comando(
        "mostrar desempenho do sistema"
    )
    print(f"Resultado:\n{resultado}")
    
    # Exemplo 3: Verificar alertas
    print("\nVerificando alertas de segurança...")
    resultado = assistente.processar_comando(
        "mostrar alertas de segurança"
    )
    print(f"Resultado:\n{resultado}")
    
    # Exemplo 4: Comando de NLP
    print("\nExecutando comando de NLP...")
    resultado = assistente.processar_comando(
        "Qual é o significado desta frase: 'O código é a poesia do futuro'"
    )
    print(f"Resultado: {resultado}")
    
    # Exemplo 5: Comando de automação web
    print("\nExecutando comando de automação web...")
    resultado = assistente.processar_comando(
        "Abrir o site do Google e pesquisar sobre Python"
    )
    print(f"Resultado: {resultado}")
    
    # Exemplo 6: Status geral do assistente
    print("\nStatus do assistente:")
    status = assistente.status()
    print(f"Uso de memória: {status['memoria_uso']:.2%}")
    print(f"Memória disponível: {status['memoria_disponivel']:.2%}")
    print(f"Módulos ativos: {', '.join(status['modulos_ativos'])}")
    print("\nInformações de segurança:")
    print(f"- Alertas ativos: {status['seguranca']['alertas_ativos']}")
    print(f"- Processos suspeitos: {status['seguranca']['processos_suspeitos']}")
    print(f"- Conexões suspeitas: {status['seguranca']['conexoes_suspeitas']}")
    
    # Aguarda um pouco para coletar mais dados
    print("\nAguardando 30 segundos para coletar mais dados...")
    time.sleep(30)
    
    # Exemplo 7: Novo relatório após espera
    print("\nGerando novo relatório de segurança...")
    resultado = assistente.processar_comando(
        "mostrar relatório de segurança"
    )
    print(f"Resultado:\n{resultado}")
    
    # Exemplo 8: Limpar alertas
    print("\nLimpando alertas...")
    resultado = assistente.processar_comando(
        "limpar alertas de segurança"
    )
    print(f"Resultado: {resultado}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário")
    except Exception as e:
        logging.error(f"Erro não tratado: {e}", exc_info=True) 