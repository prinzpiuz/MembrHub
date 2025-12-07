from botocore.exceptions import ClientError
from tenacity import (
    retry as Retry,
)
from tenacity import (
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


retry = Retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(ClientError),
    reraise=True,
)
