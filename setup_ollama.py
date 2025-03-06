import os
import subprocess
import json

def create_modelfile(name, base_model):
    content = f"""FROM {base_model}
PARAMETER num_ctx 2048
PARAMETER num_thread 4"""
    
    with open(f"Modelfile_{name}", "w") as f:
        f.write(content)
    
    return f"Modelfile_{name}"

def setup_models():
    print("Configurando modelos quantizados do Ollama...")
    
    # Configurar LLaMA 2 quantizado
    modelfile = create_modelfile("llama2_q4", "llama2:7b-q4_0")
    try:
        subprocess.run(["ollama", "create", "llama2-q4", "-f", modelfile], check=True)
        print("Modelo llama2-q4 criado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar llama2-q4: {e}")
    
    # Configurar TinyLlama
    modelfile = create_modelfile("tinyllama", "tinyllama:latest")
    try:
        subprocess.run(["ollama", "create", "tinyllama-q4", "-f", modelfile], check=True)
        print("Modelo tinyllama-q4 criado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar tinyllama-q4: {e}")

if __name__ == "__main__":
    setup_models() 