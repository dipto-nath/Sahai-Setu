import logging
from typing import Dict, Optional
import asyncio
from transformers import MarianMTModel, MarianTokenizer

logger = logging.getLogger(__name__)

class TranslationService:
    """Service to dynamically load Helsinki-NLP MarianMT models and translate to English"""
    
    def __init__(self):
        self._models: Dict[str, MarianMTModel] = {}
        self._tokenizers: Dict[str, MarianTokenizer] = {}
        
        # Mapping from source lang code to huggingface model name
        self._model_map = {
            "hi": "Helsinki-NLP/opus-mt-hi-en",
            "bn": "Helsinki-NLP/opus-mt-bn-en"
        }
        
    def _load_model(self, source_lang: str):
        if source_lang not in self._model_map:
            raise ValueError(f"No translation model mapping found for language: {source_lang}")
            
        model_name = self._model_map[source_lang]
        if source_lang not in self._models:
            logger.info(f"Loading translation model for {source_lang}: {model_name}")
            try:
                self._tokenizers[source_lang] = MarianTokenizer.from_pretrained(model_name)
                self._models[source_lang] = MarianMTModel.from_pretrained(model_name)
                logger.info(f"Successfully loaded translation model for {source_lang}")
            except Exception as e:
                logger.error(f"Failed to load translation model {model_name}: {e}")
                raise e
                
    def _translate_sync(self, text: str, source_lang: str) -> str:
        self._load_model(source_lang)
        
        try:
            tokenizer = self._tokenizers[source_lang]
            model = self._models[source_lang]
            
            # Tokenize and translate
            inputs = tokenizer(text, return_tensors="pt", padding=True)
            translated_tokens = model.generate(**inputs)
            
            # Decode the translated tokens
            translated_text = tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
            return translated_text
        except Exception as e:
            logger.error(f"Translation failed for {source_lang}: {e}")
            return text  # Return original if translation fails
            
    async def translate(self, text: str, source_lang: str) -> str:
        """Translate text to English asynchronously to prevent blocking the event loop"""
        if source_lang == "en" or not text.strip():
            return text
            
        if source_lang not in self._model_map:
            logger.warning(f"Translation not supported for language: {source_lang}")
            return text
            
        # Run CPU-bound inference in a thread
        translated_text = await asyncio.to_thread(self._translate_sync, text, source_lang)
        return translated_text
