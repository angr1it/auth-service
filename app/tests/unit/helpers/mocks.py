from unittest.mock import MagicMock


def _async_result_all(value):
    """Возвращает объект, похожий на AsyncResult,
    у которого есть .all()."""
    result = MagicMock()
    result.all.return_value = value
    return result


def _async_result_one_or_none(value):
    """Возвращает объект, похожий на AsyncResult,
    у которого есть .scalar_one_or_none()."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result
