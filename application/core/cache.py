"""
Cache key schema, TTL constants, and invalidation group definitions.
All cache keys live here so there is one place to audit/change them.
"""

import hashlib
import json
from typing import Optional


def _hash_dict(d: dict) -> str:
    """Stable short hash for a query-param dict used in cache keys."""
    canonical = json.dumps(d, sort_keys=True, default=str)
    return hashlib.md5(canonical.encode()).hexdigest()[:12]


class CacheTTL:
    AIRLINE_LIST     = 300    # 5 min
    VENDOR_LIST      = 300
    FUEL_PRICE_LIST  = 180    # 3 min — prices change more often
    DASHBOARD        = 120    # 2 min
    INVOICE_REPORT   = 120
    TRANSACTION_LIST = 60     # 1 min — high churn
    REFRESH_TOKEN    = 60 * 60 * 24 * 7   # 7 days


class CacheKey:
    AIRLINE_LIST        = "airlines:list"
    VENDOR_LIST         = "vendors:list"
    FUEL_PRICE_LIST     = "fuel_prices:list"
    TRANSACTION_LIST    = "transactions:list"

    @staticmethod
    def airline(airline_id: int) -> str:
        return f"airlines:{airline_id}"

    @staticmethod
    def vendor(vendor_id: int) -> str:
        return f"vendors:{vendor_id}"

    @staticmethod
    def fuel_price(price_id: int) -> str:
        return f"fuel_prices:{price_id}"

    @staticmethod
    def latest_price(vendor_id: int) -> str:
        return f"fuel_prices:latest:{vendor_id}"

    @staticmethod
    def price_history(vendor_id: int) -> str:
        return f"fuel_prices:history:{vendor_id}"

    @staticmethod
    def transaction(invoice_no: str) -> str:
        return f"transactions:{invoice_no}"

    @staticmethod
    def dashboard(filters: Optional[dict] = None) -> str:
        if not filters or all(v is None for v in filters.values()):
            return "report:dashboard:all"
        return f"report:dashboard:{_hash_dict(filters)}"

    @staticmethod
    def invoice_report(filters: Optional[dict] = None) -> str:
        if not filters or all(v is None for v in filters.values()):
            return "report:invoices:all"
        return f"report:invoices:{_hash_dict(filters)}"

    @staticmethod
    def refresh_token_jti(jti: str) -> str:
        return f"refresh_token:jti:{jti}"

    @staticmethod
    def user_refresh_tokens(username: str) -> str:
        return f"refresh_tokens:user:{username}"

    @staticmethod
    def rate_limit(kind: str, identifier: str) -> str:
        return f"rate_limit:{kind}:{identifier}"

    @staticmethod
    def user_notifications(user_id: int) -> str:
        return f"notifications:user:{user_id}"

    @staticmethod
    def user_notifications_read(user_id: int) -> str:
        return f"notifications:user:{user_id}:read"

    SYSTEM_NOTIFICATIONS_CHANNEL = "notifications:system"
    SYSTEM_NOTIFICATIONS_HISTORY = "notifications:system:history"


# Cache invalidation groups — delete all these keys when a domain entity changes.
INVALIDATE_ON_AIRLINE_CHANGE = [
    CacheKey.AIRLINE_LIST,
    "report:dashboard:*",
]

INVALIDATE_ON_VENDOR_CHANGE = [
    CacheKey.VENDOR_LIST,
    "report:dashboard:*",
]

INVALIDATE_ON_FUEL_PRICE_CHANGE = [
    CacheKey.FUEL_PRICE_LIST,
    "fuel_prices:latest:*",
    "fuel_prices:history:*",
    "report:dashboard:*",
]

INVALIDATE_ON_TRANSACTION_CHANGE = [
    CacheKey.TRANSACTION_LIST,
    "transactions:*",
    "report:dashboard:*",
    "report:invoices:*",
]
