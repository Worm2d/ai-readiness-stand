#!/usr/bin/env python3
"""Обновление существующих рисков из risks_rewritten.json.

Запуск из корня Django-проекта:
  python manage.py shell < update_risks.py             # проверка без записи
  APPLY=1 python manage.py shell < update_risks.py     # обновление БД

При необходимости:
  RISK_MODEL=app_label.Risk JSON_PATH=/path/file.json APPLY=1 \
    python manage.py shell < update_risks.py
"""

import json
import os
from pathlib import Path

from django.apps import apps
from django.db import transaction

JSON_PATH = Path(os.environ.get("JSON_PATH", "risks_rewritten.json"))
APPLY = os.environ.get("APPLY", "").strip().lower() in {"1", "true", "yes", "да"}
MODEL_LABEL = os.environ.get("RISK_MODEL", "").strip()
EXPECTED_IDS = set(range(35, 100))

SCALAR_FIELDS = (
    "title",
    "description",
    "mitigation",
    "severity",
    "public_case_title",
    "public_case_description",
    "public_case_source_url",
    "public_case_region",
    "is_active",
    "order",
    "categories",
)

REQUIRED_MODEL_FIELDS = {
    "title",
    "description",
    "mitigation",
    "severity",
    "public_case_description",
}


def load_payload(path):
    if not path.is_file():
        raise SystemExit(f"JSON-файл не найден: {path.resolve()}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Не удалось прочитать JSON: {exc}") from exc
    if not isinstance(payload, list):
        raise SystemExit("В корне JSON должен быть массив объектов.")

    ids = []
    for index, row in enumerate(payload, start=1):
        if not isinstance(row, dict) or not isinstance(row.get("id"), int):
            raise SystemExit(f"Запись №{index}: отсутствует целочисленный id.")
        ids.append(row["id"])
        for field in ("description", "mitigation", "public_case_description"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise SystemExit(f"ID {row['id']}: поле {field} не заполнено.")

    if len(ids) != len(set(ids)):
        raise SystemExit("В JSON есть повторяющиеся ID.")
    if set(ids) != EXPECTED_IDS:
        missing = sorted(EXPECTED_IDS - set(ids))
        extra = sorted(set(ids) - EXPECTED_IDS)
        raise SystemExit(f"Неверный набор ID. Отсутствуют: {missing}; лишние: {extra}")
    return payload


def concrete_field_names(model):
    return {
        field.name
        for field in model._meta.get_fields()
        if getattr(field, "concrete", False) and not field.many_to_many
    }


def find_risk_model():
    if MODEL_LABEL:
        try:
            model = apps.get_model(MODEL_LABEL)
        except (LookupError, ValueError) as exc:
            raise SystemExit(f"Модель {MODEL_LABEL!r} не найдена: {exc}") from exc
        if not REQUIRED_MODEL_FIELDS <= concrete_field_names(model):
            raise SystemExit(f"Модель {MODEL_LABEL!r} не похожа на модель риска.")
        return model

    candidates = [
        model
        for model in apps.get_models()
        if REQUIRED_MODEL_FIELDS <= concrete_field_names(model)
    ]
    if len(candidates) != 1:
        labels = [model._meta.label for model in candidates]
        raise SystemExit(
            "Не удалось однозначно определить модель риска. "
            f"Кандидаты: {labels or 'не найдены'}. "
            "Укажите RISK_MODEL=app_label.ModelName."
        )
    return candidates[0]


def category_relation(model):
    try:
        field = model._meta.get_field("categories")
    except Exception:
        return None
    return field if field.many_to_many else None


def category_lookup_name(category_model):
    names = concrete_field_names(category_model)
    for candidate in ("name", "title", "slug"):
        if candidate in names:
            return candidate
    raise SystemExit(
        f"У модели категорий {category_model._meta.label} нет поля name, title или slug."
    )


def main():
    payload = load_payload(JSON_PATH)
    model = find_risk_model()
    model_fields = concrete_field_names(model)
    update_fields = [field for field in SCALAR_FIELDS if field in model_fields]
    relation = category_relation(model)

    if not update_fields:
        raise SystemExit("Не найдено ни одного поля для обновления.")

    ids = [row["id"] for row in payload]
    existing = model.objects.in_bulk(ids)
    missing = sorted(set(ids) - set(existing))
    if missing:
        raise SystemExit(
            "Обновление отменено: в БД отсутствуют записи с ID "
            + ", ".join(map(str, missing))
            + ". Скрипт не создаёт новые записи."
        )

    changed = []
    unchanged = []
    preview = []
    for row in payload:
        obj = existing[row["id"]]
        fields_changed = [
            field for field in update_fields
            if field in row and getattr(obj, field) != row[field]
        ]
        if fields_changed:
            changed.append(row["id"])
            preview.append((row["id"], fields_changed))
        else:
            unchanged.append(row["id"])

    print(f"Модель: {model._meta.label}")
    print(f"JSON: {JSON_PATH.resolve()}")
    print(f"Найдено существующих записей: {len(existing)}")
    print(f"Изменятся: {len(changed)}; без изменений: {len(unchanged)}")
    for risk_id, fields in preview:
        print(f"  ID {risk_id}: {', '.join(fields)}")

    if not APPLY:
        print("\nПРОВЕРКА ЗАВЕРШЕНА. Данные в БД не менялись.")
        print("Для применения: APPLY=1 python manage.py shell < update_risks.py")
        return

    category_cache = {}
    with transaction.atomic():
        locked = {
            obj.pk: obj
            for obj in model.objects.select_for_update().filter(pk__in=ids)
        }
        if set(locked) != set(ids):
            raise RuntimeError("Состав записей изменился после проверки; транзакция отменена.")

        for row in payload:
            obj = locked[row["id"]]
            fields_to_save = []
            for field in update_fields:
                if field in row and getattr(obj, field) != row[field]:
                    setattr(obj, field, row[field])
                    fields_to_save.append(field)
            if fields_to_save:
                obj.save(update_fields=fields_to_save)

            if relation is not None and "categories" in row:
                category_model = relation.remote_field.model
                lookup_field = category_lookup_name(category_model)
                categories = []
                for value in row["categories"]:
                    cache_key = (category_model, lookup_field, value)
                    if cache_key not in category_cache:
                        try:
                            category_cache[cache_key] = category_model.objects.get(
                                **{lookup_field: value}
                            )
                        except category_model.DoesNotExist as exc:
                            raise RuntimeError(
                                f"ID {row['id']}: категория {value!r} не найдена. "
                                "Новые категории намеренно не создаются."
                            ) from exc
                    categories.append(category_cache[cache_key])
                getattr(obj, relation.name).set(categories)

    print(f"\nГОТОВО. Обновлено существующих рисков: {len(changed)}.")
    print("Новые записи не создавались; ID сохранены.")


main()
