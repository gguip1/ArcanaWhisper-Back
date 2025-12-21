import json
import logging
import os

logger = logging.getLogger(__name__)

_CACHED_TAROT_CARDS = None


def _get_from_ssm(param_name: str) -> str:
    """AWS Systems Manager Parameter Store에서 값 로드"""
    import boto3
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]


def get_tarot_cards(file_path: str = None) -> list[dict]:
    """타로 카드 데이터를 SSM 또는 파일에서 로드합니다."""
    global _CACHED_TAROT_CARDS

    if _CACHED_TAROT_CARDS is not None:
        return _CACHED_TAROT_CARDS

    # 1. SSM Parameter Store에서 로드 (Lambda 환경)
    param_name = os.environ.get("TAROT_CARDS_PARAM")
    if param_name:
        try:
            cards_json = _get_from_ssm(param_name)
            _CACHED_TAROT_CARDS = json.loads(cards_json)
            logger.info(f"Loaded tarot cards from SSM: {param_name}")
            return _CACHED_TAROT_CARDS
        except Exception as e:
            logger.warning(f"Failed to load tarot cards from SSM: {e}, trying file...")

    # 2. 파일에서 로드 (로컬 테스트용)
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                _CACHED_TAROT_CARDS = json.load(file)
                logger.info(f"Loaded tarot cards from file: {file_path}")
                return _CACHED_TAROT_CARDS
        except FileNotFoundError:
            pass

    raise RuntimeError("Tarot cards not found. Set TAROT_CARDS_PARAM or provide valid file path.")
