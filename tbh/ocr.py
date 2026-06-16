"""
OCR para leitura de texto do jogo usando EasyOCR (roda localmente, sem custo).
Detecta conclusão de estágio pelo texto "Estágio X-X concluído" que aparece na tela.
"""
import logging
import re
import numpy as np
from typing import Optional

logger = logging.getLogger("tbh.ocr")

# Palavras que indicam conclusão de estágio (português e inglês)
_COMPLETE_KEYWORDS = ["conclu", "completed", "cleared", "vitória", "victory"]


class GameOCR:
    """Lê texto do jogo via EasyOCR. Modelos rodam localmente (sem API paga)."""

    def __init__(self, languages: list[str] | None = None, gpu: bool = False):
        self._languages = languages or ["pt", "en"]
        self._gpu = gpu
        self._reader = None

    def preload(self) -> bool:
        """Carrega os modelos OCR antecipadamente (evita delay na primeira corrida)."""
        try:
            self._get_reader()
            return True
        except Exception as e:
            logger.warning(f"Não foi possível pré-carregar OCR: {e}")
            return False

    def read_all(self, frame: np.ndarray, min_confidence: float = 0.4) -> list[str]:
        """Extrai todo o texto visível no frame."""
        try:
            results = self._get_reader().readtext(frame, detail=1)
            return [text for _, text, conf in results if conf >= min_confidence]
        except Exception as e:
            logger.debug(f"OCR falhou: {e}")
            return []

    def is_stage_complete(self, frame: np.ndarray) -> bool:
        """Retorna True se o texto de conclusão de estágio estiver visível na tela."""
        try:
            texts = self.read_all(frame)
            joined = " ".join(texts).lower()
            return any(kw in joined for kw in _COMPLETE_KEYWORDS)
        except Exception:
            return False

    def extract_stage_id(self, frame: np.ndarray) -> Optional[str]:
        """
        Extrai o ID do estágio do texto de conclusão.
        Ex: 'Estágio 3-5 concluído. (563s)' → '3-5'
        """
        try:
            texts = self.read_all(frame)
            for text in texts:
                m = re.search(r'\b(\d+[-–]\d+)\b', text)
                if m:
                    return m.group(1).replace('–', '-')
        except Exception:
            pass
        return None

    # ── Internal ──────────────────────────────────────────────────────────────

    def _get_reader(self):
        if self._reader is None:
            logger.info("Carregando modelos EasyOCR (primeira vez ~30s, baixa uma vez)...")
            import easyocr
            self._reader = easyocr.Reader(self._languages, gpu=self._gpu, verbose=False)
            logger.info("EasyOCR carregado e pronto.")
        return self._reader
