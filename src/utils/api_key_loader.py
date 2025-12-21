import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# SSM에서 가져온 키 캐싱 (Cold start 최적화)
_CACHED_KEYS = {}


def _get_from_ssm(param_name: str) -> str:
    """AWS Systems Manager Parameter Store에서 값 로드"""
    import boto3
    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]


def get_api_key(key_name: str) -> str:
    """
    API 키를 가져옵니다.

    우선순위:
    1. 캐시된 값
    2. SSM Parameter Store (Lambda 환경)
    3. 환경변수 직접 값 (로컬 환경)
    """
    # 캐시 확인
    if key_name in _CACHED_KEYS:
        return _CACHED_KEYS[key_name]

    # SSM Parameter Store 경로 확인 (예: GEMINI_API_KEY_PARAM)
    param_env = f"{key_name}_PARAM"
    param_path = os.getenv(param_env)

    if param_path:
        try:
            value = _get_from_ssm(param_path)
            _CACHED_KEYS[key_name] = value
            logger.info(f"Loaded {key_name} from SSM Parameter Store")
            return value
        except Exception as e:
            logger.warning(f"Failed to load {key_name} from SSM: {e}, trying env...")

    # 환경변수에서 직접 로드 (로컬 테스트용)
    value = os.getenv(key_name)
    if value:
        _CACHED_KEYS[key_name] = value
        logger.info(f"Loaded {key_name} from environment variable")
        return value

    raise ValueError(f"{key_name} not found. Set {param_env} or {key_name} environment variable.")