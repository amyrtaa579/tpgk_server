"""
Скрипт для миграции answer_scores в test_questions.
Заменяет старые категории (welder, cook, kip и т.д.) на реальные коды специальностей.
"""
import asyncio
import asyncpg
import json

# Маппинг старых категорий на реальные коды специальностей
CATEGORY_TO_SPECIALTIES = {
    "welder": ["15.02.19", "15.01.05"],
    "builder": ["21.02.03"],
    "cook": ["19.02.10"],  # Технология продукции общественного питания (может не быть в БД)
    "chemist": ["18.02.12"],
    "kip": ["15.01.37", "13.01.10"],
    "robot": ["15.02.18"],
    "operator": ["18.01.35"],
}

# Существующие специальности в БД
EXISTING_SPECIALTIES = {
    "13.01.10", "15.01.05", "15.01.37", "15.02.18",
    "15.02.19", "18.01.35", "18.02.12", "21.02.03",
}


async def migrate():
    conn = await asyncpg.connect(
        user="anmicius",
        password="anmicius_secret_password",
        database="anmicius_db",
        host="localhost",
    )

    questions = await conn.fetch("SELECT id, answer_scores FROM test_questions")
    updated_count = 0

    for q in questions:
        qid = q["id"]
        scores = q["answer_scores"]

        if not scores:
            continue

        # answer_scores может быть строкой (JSON) или списком
        if isinstance(scores, str):
            scores = json.loads(scores)

        new_scores = []
        changed = False

        for entry in scores:
            specialties = entry.get("specialties", [])
            new_specialties = []

            for spec in specialties:
                if spec in CATEGORY_TO_SPECIALTIES:
                    # Заменяем категорию на реальные коды
                    mapped = CATEGORY_TO_SPECIALTIES[spec]
                    # Оставляем только те, что есть в БД (или добавляем все)
                    new_specialties.extend(mapped)
                    changed = True
                elif spec in EXISTING_SPECIALTIES or True:  # Оставляем все коды как есть
                    new_specialties.append(spec)

            # Убираем дубликаты, сохраняя порядок
            seen = set()
            unique_specialties = []
            for s in new_specialties:
                if s not in seen:
                    seen.add(s)
                    unique_specialties.append(s)

            new_entry = {"answer": entry.get("answer", ""), "specialties": unique_specialties}
            new_scores.append(new_entry)

        if changed:
            await conn.execute(
                "UPDATE test_questions SET answer_scores = $1 WHERE id = $2",
                json.dumps(new_scores),
                qid,
            )
            updated_count += 1
            print(f"Updated question {qid}: {json.dumps(new_scores, ensure_ascii=False)[:200]}")

    print(f"\nTotal updated: {updated_count}")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(migrate())
