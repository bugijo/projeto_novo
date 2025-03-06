from flask import Flask, request, jsonify
from flask_cors import CORS
from comfy_manager import ComfyUIManager
from workflow_generator import WorkflowGenerator
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Inicializa os gerenciadores
manager = ComfyUIManager()
workflow_gen = WorkflowGenerator()

@app.route("/api/process", methods=["POST"])
def process_request():
    """Processa uma requisição em linguagem natural."""
    try:
        data = request.json
        prompt = data.get("prompt")
        
        if not prompt:
            return jsonify({"error": "Prompt não fornecido"}), 400
            
        # Processa a requisição
        result = manager.process_request(prompt)
        
        return jsonify({"result": result})
        
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/workflows", methods=["GET"])
def list_workflows():
    """Lista todos os workflows salvos."""
    try:
        workflows = []
        for file in manager.workflows_path.glob("*.json"):
            workflow = manager.load_workflow(file.stem)
            if workflow:
                workflows.append({
                    "name": file.stem,
                    "workflow": workflow
                })
        
        return jsonify({"workflows": workflows})
        
    except Exception as e:
        logger.error(f"Erro ao listar workflows: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/templates", methods=["GET"])
def list_templates():
    """Lista todos os templates disponíveis."""
    try:
        templates = {}
        for name, template in workflow_gen.templates.items():
            templates[name] = template
            
        return jsonify({"templates": templates})
        
    except Exception as e:
        logger.error(f"Erro ao listar templates: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/execute", methods=["POST"])
def execute_workflow():
    """Executa um workflow específico."""
    try:
        data = request.json
        workflow = data.get("workflow")
        
        if not workflow:
            return jsonify({"error": "Workflow não fornecido"}), 400
            
        # Executa o workflow
        result = manager.execute_workflow(workflow)
        
        return jsonify({"result": result})
        
    except Exception as e:
        logger.error(f"Erro ao executar workflow: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/save", methods=["POST"])
def save_workflow():
    """Salva um workflow como template."""
    try:
        data = request.json
        workflow = data.get("workflow")
        name = data.get("name")
        
        if not workflow or not name:
            return jsonify({"error": "Workflow ou nome não fornecido"}), 400
            
        # Salva o workflow
        workflow_gen.save_template(workflow, name)
        
        return jsonify({"message": f"Template {name} salvo com sucesso"})
        
    except Exception as e:
        logger.error(f"Erro ao salvar template: {str(e)}")
        return jsonify({"error": str(e)}), 500

def start_api():
    """Inicia o servidor API."""
    try:
        # Inicia o ComfyUI
        if not manager.start_server():
            logger.error("Falha ao iniciar ComfyUI")
            return False
            
        # Inicia a API
        app.run(host="0.0.0.0", port=5000)
        return True
        
    except Exception as e:
        logger.error(f"Erro ao iniciar API: {str(e)}")
        return False

if __name__ == "__main__":
    start_api() 