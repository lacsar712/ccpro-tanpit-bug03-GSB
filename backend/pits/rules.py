"""鞣坑状态门槛。

- 放液（drained）：最近一次浸液酸碱度须在 3.5～5.0。
- 已放液坑：禁止再登记酸碱度（补酸碱只认坑本身，不看邻行）。
- 拨回注液（fill）：只改坑态，空带 / 旧 pH 带均不得拦截。
"""

from pits.models import Pit

MIN_PH = 3.5
MAX_PH = 5.0


class RuleError(ValueError):
    pass


def latest_ph(pit: Pit) -> float | None:
    sample = pit.samples.order_by("-taken_at", "-id").first()
    return None if sample is None else sample.ph


def assert_can_add_sample(pit: Pit) -> None:
    if pit.status == Pit.STATUS_DRAINED:
        raise RuleError("该坑已放液，不能再补酸碱")


def assert_can_set_status(pit: Pit, new_status: str) -> None:
    allowed = {Pit.STATUS_FILL, Pit.STATUS_TANNING, Pit.STATUS_DRAINED}
    if new_status not in allowed:
        raise RuleError(f"无效状态：{new_status}")
    if new_status == Pit.STATUS_DRAINED and pit.status != Pit.STATUS_DRAINED:
        ph = latest_ph(pit)
        if ph is None:
            raise RuleError("该坑尚无浸液酸碱记录，不能放液")
        if ph < MIN_PH or ph > MAX_PH:
            raise RuleError(f"最近酸碱度 {ph} 不在 {MIN_PH}～{MAX_PH}，不能放液")
