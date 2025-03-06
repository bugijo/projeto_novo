import cv2
import numpy as np
from PIL import Image
import torch
from transformers import DetrImageProcessor, DetrForObjectDetection
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import pytesseract
from pathlib import Path
import mediapipe as mp

class VisaoComputacional:
    def __init__(self):
        # Inicializa os modelos de IA
        self.detector_objetos = self._inicializar_detector_objetos()
        self.descricao_imagem = self._inicializar_descricao_imagem()
        self.face_mesh = mp.solutions.face_mesh.FaceMesh()
        self.hands = mp.solutions.hands.Hands()
        self.pose = mp.solutions.pose.Pose()
        
        # Inicializa a câmera
        self.camera = None
        self.camera_ativa = False
        
    def _inicializar_detector_objetos(self):
        """Inicializa o modelo de detecção de objetos"""
        processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
        model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")
        return {"processor": processor, "model": model}
    
    def _inicializar_descricao_imagem(self):
        """Inicializa o modelo de descrição de imagens"""
        model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
        return {
            "model": model,
            "feature_extractor": feature_extractor,
            "tokenizer": tokenizer
        }

    def iniciar_camera(self, camera_id=0):
        """Inicia a câmera"""
        try:
            self.camera = cv2.VideoCapture(camera_id)
            self.camera_ativa = True
            return True
        except Exception as e:
            print(f"Erro ao iniciar câmera: {e}")
            return False

    def parar_camera(self):
        """Para a câmera"""
        if self.camera:
            self.camera.release()
            self.camera_ativa = False

    def capturar_frame(self):
        """Captura um frame da câmera"""
        if not self.camera_ativa:
            return None
        
        ret, frame = self.camera.read()
        if ret:
            return frame
        return None

    def detectar_objetos(self, imagem):
        """Detecta objetos em uma imagem"""
        try:
            # Converte a imagem para RGB se necessário
            if len(imagem.shape) == 2:
                imagem = cv2.cvtColor(imagem, cv2.COLOR_GRAY2RGB)
            elif imagem.shape[2] == 4:
                imagem = cv2.cvtColor(imagem, cv2.COLOR_BGRA2RGB)
            elif imagem.shape[2] == 3:
                imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)

            # Processa a imagem
            inputs = self.detector_objetos["processor"](images=imagem, return_tensors="pt")
            outputs = self.detector_objetos["model"](**inputs)

            # Converte as previsões
            target_sizes = torch.tensor([imagem.shape[:2]])
            results = self.detector_objetos["processor"].post_process_object_detection(
                outputs, target_sizes=target_sizes, threshold=0.9)[0]

            # Formata os resultados
            deteccoes = []
            for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
                deteccoes.append({
                    "objeto": self.detector_objetos["model"].config.id2label[label.item()],
                    "confianca": score.item(),
                    "box": box.tolist()
                })

            return deteccoes
        except Exception as e:
            print(f"Erro na detecção de objetos: {e}")
            return []

    def descrever_imagem(self, imagem):
        """Gera uma descrição em texto da imagem"""
        try:
            # Prepara a imagem
            if isinstance(imagem, np.ndarray):
                imagem = Image.fromarray(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))

            # Extrai características
            pixel_values = self.descricao_imagem["feature_extractor"](images=imagem, return_tensors="pt").pixel_values
            
            # Gera a descrição
            output_ids = self.descricao_imagem["model"].generate(
                pixel_values, max_length=50, num_beams=4, return_dict_in_generate=True
            ).sequences

            # Decodifica a descrição
            descricao = self.descricao_imagem["tokenizer"].batch_decode(output_ids, skip_special_tokens=True)[0]
            
            return descricao
        except Exception as e:
            print(f"Erro ao descrever imagem: {e}")
            return "Não foi possível gerar uma descrição da imagem."

    def reconhecer_texto(self, imagem):
        """Reconhece texto em uma imagem"""
        try:
            # Pré-processamento
            gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # OCR
            texto = pytesseract.image_to_string(thresh, lang='por')
            return texto.strip()
        except Exception as e:
            print(f"Erro no reconhecimento de texto: {e}")
            return ""

    def analisar_face(self, imagem):
        """Analisa características faciais"""
        try:
            resultados = self.face_mesh.process(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))
            if resultados.multi_face_landmarks:
                faces = []
                for face_landmarks in resultados.multi_face_landmarks:
                    # Extrai pontos principais
                    pontos = np.array([[p.x, p.y, p.z] for p in face_landmarks.landmark])
                    faces.append({
                        "pontos": pontos,
                        "orientacao": self._calcular_orientacao_face(pontos),
                        "expressao": self._analisar_expressao(pontos)
                    })
                return faces
            return []
        except Exception as e:
            print(f"Erro na análise facial: {e}")
            return []

    def detectar_maos(self, imagem):
        """Detecta e analisa posições das mãos"""
        try:
            resultados = self.hands.process(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))
            if resultados.multi_hand_landmarks:
                maos = []
                for hand_landmarks in resultados.multi_hand_landmarks:
                    pontos = np.array([[p.x, p.y, p.z] for p in hand_landmarks.landmark])
                    maos.append({
                        "pontos": pontos,
                        "gestos": self._reconhecer_gestos(pontos)
                    })
                return maos
            return []
        except Exception as e:
            print(f"Erro na detecção de mãos: {e}")
            return []

    def detectar_pose(self, imagem):
        """Detecta a pose do corpo"""
        try:
            resultados = self.pose.process(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))
            if resultados.pose_landmarks:
                pontos = np.array([[p.x, p.y, p.z] for p in resultados.pose_landmarks.landmark])
                return {
                    "pontos": pontos,
                    "postura": self._analisar_postura(pontos)
                }
            return None
        except Exception as e:
            print(f"Erro na detecção de pose: {e}")
            return None

    def _calcular_orientacao_face(self, pontos):
        """Calcula a orientação da face (para onde está olhando)"""
        # Implementação simplificada - pode ser melhorada
        centro = pontos.mean(axis=0)
        return {
            "rotacao_x": np.arctan2(centro[2], centro[1]),
            "rotacao_y": np.arctan2(centro[2], centro[0]),
            "rotacao_z": np.arctan2(centro[1], centro[0])
        }

    def _analisar_expressao(self, pontos):
        """Analisa a expressão facial"""
        # Implementação básica - pode ser expandida
        # Aqui você pode adicionar mais lógica para detectar sorrisos, tristeza, etc.
        return "neutra"

    def _reconhecer_gestos(self, pontos):
        """Reconhece gestos das mãos"""
        # Implementação básica - pode ser expandida
        # Aqui você pode adicionar mais lógica para reconhecer gestos específicos
        return ["desconhecido"]

    def _analisar_postura(self, pontos):
        """Analisa a postura corporal"""
        # Implementação básica - pode ser expandida
        # Aqui você pode adicionar mais lógica para detectar posturas específicas
        return "em pé"

    def salvar_imagem(self, imagem, caminho):
        """Salva uma imagem no disco"""
        try:
            cv2.imwrite(str(caminho), imagem)
            return True
        except Exception as e:
            print(f"Erro ao salvar imagem: {e}")
            return False

    def __del__(self):
        """Limpa recursos ao destruir o objeto"""
        self.parar_camera()
        cv2.destroyAllWindows() 