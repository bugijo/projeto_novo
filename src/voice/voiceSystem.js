const whisper = require('node-whisper');
const { CoquiTTS } = require('coqui-tts');
const path = require('path');
const fs = require('fs');

class VoiceSystem {
  constructor() {
    this.whisper = null;
    this.tts = null;
    this.isInitialized = false;
    this.isListening = false;
    this.voiceConfig = {
      language: 'pt-BR',
      model: 'base',
      speaker: 'pt_br_female'
    };
  }

  async initialize() {
    try {
      // Inicializar Whisper
      this.whisper = await whisper.load({
        modelName: this.voiceConfig.model,
        language: this.voiceConfig.language
      });

      // Inicializar Coqui TTS
      this.tts = new CoquiTTS();
      await this.tts.load(this.voiceConfig.speaker);

      this.isInitialized = true;
      console.log('Sistema de voz inicializado com sucesso');
    } catch (error) {
      console.error('Erro ao inicializar sistema de voz:', error);
      throw error;
    }
  }

  async startListening(callback) {
    if (!this.isInitialized) {
      throw new Error('Sistema de voz não inicializado');
    }

    this.isListening = true;
    
    try {
      while (this.isListening) {
        const audioData = await this.recordAudio();
        const text = await this.whisper.transcribe(audioData);
        
        if (text.trim()) {
          callback(text);
        }
      }
    } catch (error) {
      console.error('Erro ao processar áudio:', error);
      this.stopListening();
    }
  }

  stopListening() {
    this.isListening = false;
  }

  async speak(text) {
    if (!this.isInitialized) {
      throw new Error('Sistema de voz não inicializado');
    }

    try {
      const audioBuffer = await this.tts.synthesize(text);
      await this.playAudio(audioBuffer);
    } catch (error) {
      console.error('Erro ao sintetizar voz:', error);
      throw error;
    }
  }

  async recordAudio() {
    // Implementar gravação de áudio
    // Por enquanto, retorna um buffer vazio
    return Buffer.from([]);
  }

  async playAudio(audioBuffer) {
    // Implementar reprodução de áudio
    console.log('Reproduzindo áudio...');
  }

  setVoiceConfig(config) {
    this.voiceConfig = {
      ...this.voiceConfig,
      ...config
    };
  }
}

const voiceSystem = new VoiceSystem();

async function initializeVoice() {
  await voiceSystem.initialize();
}

module.exports = {
  initializeVoice,
  voiceSystem
}; 