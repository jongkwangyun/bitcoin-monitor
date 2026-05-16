"""재시도 로직이 내장된 공용 requests.Session.

일시적 HTTP 오류(429, 500, 502, 503, 504)에 대해
최대 3회 자동 재시도하며 지수 백오프(1s→2s→4s)를 적용한다.
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_RETRY_STRATEGY = Retry(
    total=3,
    backoff_factor=1,               # 1s → 2s → 4s
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"],
    raise_on_status=False,
)

_adapter = HTTPAdapter(max_retries=_RETRY_STRATEGY)


def get_session() -> requests.Session:
    """재시도 로직이 적용된 requests.Session을 반환한다."""
    s = requests.Session()
    s.mount("https://", _adapter)
    s.mount("http://", _adapter)
    return s
