import gradio as gr
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização do Flask
app = Flask(__name__)
CORS(app)

# Configuração dos modelos
MODELS = {
    'programacao': {
        'name': 'deepseek-coder/deepseek-coder-1.3b-instruct',
        'task': 'text-generation',
        'model': None,
        'tokenizer': None
    },
    'assistente': {
        'name': 'microsoft/phi-2',
        'task': 'text-generation',
        'model': None,
        'tokenizer': None
    }
}

def load_model(model_type):
    """Carrega um modelo específico se ainda não estiver carregado."""
    if MODELS[model_type]['model'] is None:
        try:
            logger.info(f"Carregando modelo {MODELS[model_type]['name']}...")
            MODELS[model_type]['tokenizer'] = AutoTokenizer.from_pretrained(MODELS[model_type]['name'])
            MODELS[model_type]['model'] = AutoModelForCausalLM.from_pretrained(
                MODELS[model_type]['name'],
                torch_dtype=torch.float16,
                device_map='auto'
            )
            logger.info(f"Modelo {MODELS[model_type]['name']} carregado com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar modelo {MODELS[model_type]['name']}: {str(e)}")
            return False
    return True

def generate_response(text, model_type='assistente'):
    """Gera uma resposta usando o modelo especificado."""
    if not load_model(model_type):
        return "Desculpe, não foi possível carregar o modelo necessário."
    
    try:
        inputs = MODELS[model_type]['tokenizer'](
            text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to('cuda' if torch.cuda.is_available() else 'cpu')
        
        outputs = MODELS[model_type]['model'].generate(
            **inputs,
            max_length=1024,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=MODELS[model_type]['tokenizer'].eos_token_id
        )
        
        response = MODELS[model_type]['tokenizer'].decode(outputs[0], skip_special_tokens=True)
        return response
    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {str(e)}")
        return f"Erro ao gerar resposta: {str(e)}"

# Interface Gradio
def gradio_interface(message, task_type="assistente"):
    return generate_response(message, task_type)

demo = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Mensagem"),
        gr.Radio(["assistente", "programacao"], label="Tipo de Tarefa", value="assistente")
    ],
    outputs=gr.Textbox(label="Resposta"),
    title="Assistente IA",
    description="Um assistente IA que pode ajudar com programação e outras tarefas."
)

# API Flask
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '').strip()
        task_type = data.get('type', 'assistente')
        
        if not message:
            return jsonify({'error': 'Mensagem vazia'})
        
        response = generate_response(message, task_type)
        return jsonify({'response': response})
    
    except Exception as e:
        logger.exception("Erro ao processar mensagem")
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    # Inicia a interface Gradio
    demo.launch(share=True)
    
    # Inicia o servidor Flask
    app.run(host='0.0.0.0', port=8000) 