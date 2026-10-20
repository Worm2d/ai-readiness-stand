#!/bin/bash
# Выгрузка всех рисков и рекомендаций по митигации из БД в JSON.
# Запускать из корня проекта: bash export_risks.sh
# (или просто вставить блок между EOF в консоль на сервере).

cd /opt/ai-readiness-stand || exit 1
source venv/bin/activate 2>/dev/null

python manage.py shell << 'PYEOF'
import json
from risks.models import Risk

def safe_get(obj, field):
    try:
        return getattr(obj, field)
    except Exception:
        return None

data = []
for risk in Risk.objects.all().order_by("order", "id").prefetch_related("categories"):
    data.append({
        "id": risk.id,
        "title": safe_get(risk, "title"),
        "description": safe_get(risk, "description"),
        "mitigation": safe_get(risk, "mitigation"),
        "severity": safe_get(risk, "severity"),
        "categories": list(risk.categories.values_list("name", flat=True)) if hasattr(risk, "categories") else [],
        "public_case_title": safe_get(risk, "public_case_title"),
        "public_case_description": safe_get(risk, "public_case_description"),
        "public_case_source_url": safe_get(risk, "public_case_source_url"),
        "public_case_region": safe_get(risk, "public_case_region"),
        "is_active": safe_get(risk, "is_active"),
        "order": safe_get(risk, "order"),
    })

with open("risks_export.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Экспортировано рисков: {len(data)}")
print(json.dumps(data, ensure_ascii=False, indent=2))
PYEOF

echo ""
echo "===== Готово. Файл сохранён как risks_export.json ====="
echo "Скопируйте вывод выше (JSON) и пришлите мне для правки."
