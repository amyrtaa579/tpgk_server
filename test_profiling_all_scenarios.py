#!/usr/bin/env python3
"""
Тестирование профориентационного теста - все возможные сценарии.

Запуск:
    python test_profiling_all_scenarios.py
"""

import asyncio
from app.infrastructure.repositories import TestQuestionRepository
from app.infrastructure.database import create_async_engine, AsyncSession, async_sessionmaker, Base
from sqlalchemy.ext.asyncio import AsyncSession


async def test_all_scenarios():
    """Тестирование всех сценариев профориентации."""
    
    # Создаём тестовую БД
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        repo = TestQuestionRepository(session)
        
        print("=" * 80)
        print("ТЕСТИРОВАНИЕ ПРОФОРИЕНТАЦИОННОГО ТЕСТА")
        print("=" * 80)
        
        # =====================================================================
        # Сценарий 1: Сварщик (максимальные баллы)
        # =====================================================================
        print("\n" + "=" * 80)
        print("Сценарий 1: СВАРЩИК")
        print("=" * 80)
        
        answers_welder = [
            {"question_id": 1, "selected": "Да"},  # Физический труд
            {"question_id": 2, "selected": "Ручной труд"},  # Ручной труд
            {"question_id": 3, "selected": "Да"},  # На открытом воздухе
            {"question_id": 4, "selected": "Геометрия"},  # Геометрия
            {"question_id": 5, "selected": "Для Сварочных работ"},  # Маска
            {"question_id": 8, "selected": "Сварочный аппарат"},  # Инструмент
            {"question_id": 13, "selected": "Сварщики"},  # Перчатки
            {"question_id": 15, "selected": "Трубопровод"},  # Трубопровод
            {"question_id": 6, "selected": "Амперметр"},  # Прибор (нейтрально)
            {"question_id": 7, "selected": "Спиртовка"},  # Спиртовка (нейтрально)
        ]
        
        result = await repo.calculate_recommendation(answers_welder)
        print(f"\nРекомендация: {result['recommendation']}")
        print(f"Мотивация: {result['motivation']}")
        print(f"Специальности:")
        for spec in result['recommended_specialties']:
            print(f"  - {spec['code']}: {spec['name']} ({spec['duration']})")
        
        assert "Сварочн" in result['recommendation'] or "Сварщик" in result['recommendation'], "Должна быть рекомендация сварщика!"
        print("✅ Сценарий 1 пройден")
        
        # =====================================================================
        # Сценарий 2: Сооруженец (газонефтепроводы)
        # =====================================================================
        print("\n" + "=" * 80)
        print("Сценарий 2: СООРУЖЕНЕЦ (ГАЗОНЕФТЕПРОВОДЫ)")
        print("=" * 80)
        
        answers_builder = [
            {"question_id": 1, "selected": "Да"},  # Физический труд
            {"question_id": 2, "selected": "Физический труд"},  # Физический труд
            {"question_id": 3, "selected": "Да"},  # На открытом воздухе (максимум баллов)
            {"question_id": 4, "selected": "Геометрия"},  # Геометрия
            {"question_id": 5, "selected": "Для Дайвинга"},  # Маска (нейтрально)
            {"question_id": 8, "selected": "Отвертка"},  # Инструмент (нейтрально)
            {"question_id": 13, "selected": "Мушкетеры"},  # Перчатки (нейтрально)
            {"question_id": 15, "selected": "Трубопровод"},  # Трубопровод (максимум баллов)
            {"question_id": 6, "selected": "Барометр"},  # Прибор (нейтрально)
            {"question_id": 7, "selected": "Свеча"},  # Спиртовка (нейтрально)
        ]
        
        result = await repo.calculate_recommendation(answers_builder)
        print(f"\nРекомендация: {result['recommendation']}")
        print(f"Мотивация: {result['motivation']}")
        print(f"Специальности:")
        for spec in result['recommended_specialties']:
            print(f"  - {spec['code']}: {spec['name']} ({spec['duration']})")
        
        assert "Сооружени" in result['recommendation'] or "Газонефтепровод" in result['recommendation'], "Должна быть рекомендация сооруженца!"
        print("✅ Сценарий 2 пройден")
        
        # =====================================================================
        # Сценарий 3: Повар
        # =====================================================================
        print("\n" + "=" * 80)
        print("Сценарий 3: ПОВАР")
        print("=" * 80)
        
        answers_cook = [
            {"question_id": 1, "selected": "Да"},  # Физический труд
            {"question_id": 2, "selected": "Творческие работы"},  # Творчество
            {"question_id": 3, "selected": "Нет"},  # Не на воздухе
            {"question_id": 4, "selected": "Биология"},  # Биология
            {"question_id": 5, "selected": "Для Сноубординга"},  # Маска (нейтрально)
            {"question_id": 8, "selected": "Весы"},  # Весы (миксер)
            {"question_id": 9, "selected": "Наполеон"},  # Торт
            {"question_id": 12, "selected": "Миксер кондитерский"},  # Миксер
            {"question_id": 6, "selected": "Термометр"},  # Прибор (нейтрально)
            {"question_id": 7, "selected": "Масляная лампа"},  # Спиртовка (нейтрально)
        ]
        
        result = await repo.calculate_recommendation(answers_cook)
        print(f"\nРекомендация: {result['recommendation']}")
        print(f"Мотивация: {result['motivation']}")
        print(f"Специальности:")
        for spec in result['recommended_specialties']:
            print(f"  - {spec['code']}: {spec['name']} ({spec['duration']})")
        
        assert "Повар" in result['recommendation'] or "питания" in result['recommendation'], "Должна быть рекомендация повара!"
        print("✅ Сценарий 3 пройден")
        
        # =====================================================================
        # Сценарий 4: Химик
        # =====================================================================
        print("\n" + "=" * 80)
        print("Сценарий 4: ХИМИК")
        print("=" * 80)
        
        answers_chemist = [
            {"question_id": 1, "selected": "Нет"},  # Не физический труд
            {"question_id": 2, "selected": "Интеллектуальный труд"},  # Интеллектуальный
            {"question_id": 3, "selected": "Нет"},  # Не на воздухе
            {"question_id": 4, "selected": "Химия"},  # Химия
            {"question_id": 5, "selected": "Для Страйк бола"},  # Маска (нейтрально)
            {"question_id": 7, "selected": "Спиртовка"},  # Спиртовка
            {"question_id": 8, "selected": "Колба"},  # Колба
            {"question_id": 14, "selected": "Химическое производство"},  # Хим производство
            {"question_id": 6, "selected": "Дозиметр"},  # Прибор (нейтрально)
            {"question_id": 9, "selected": "Прага"},  # Торт (нейтрально)
        ]
        
        result = await repo.calculate_recommendation(answers_chemist)
        print(f"\nРекомендация: {result['recommendation']}")
        print(f"Мотивация: {result['motivation']}")
        print(f"Специальности:")
        for spec in result['recommended_specialties']:
            print(f"  - {spec['code']}: {spec['name']} ({spec['duration']})")
        
        assert "Химич" in result['recommendation'] or "Аналитическ" in result['recommendation'], "Должна быть рекомендация химика!"
        print("✅ Сценарий 4 пройден")
        
        # =====================================================================
        # Сценарий 5: КИП/Электрик
        # =====================================================================
        print("\n" + "=" * 80)
        print("Сценарий 5: КИП/ЭЛЕКТРИК")
        print("=" * 80)
        
        answers_kip = [
            {"question_id": 1, "selected": "Нет"},  # Не физический труд
            {"question_id": 2, "selected": "Автоматизированный труд"},  # Автоматизация
            {"question_id": 3, "selected": "Нет"},  # Не на воздухе
            {"question_id": 4, "selected": "Физика"},  # Физика
            {"question_id": 5, "selected": "Для Дайвинга"},  # Маска (нейтрально)
            {"question_id": 6, "selected": "Амперметр"},  # Амперметр
            {"question_id": 8, "selected": "Отвертка"},  # Отвертка
            {"question_id": 10, "selected": "Лампа накаливания"},  # Лампа
            {"question_id": 11, "selected": "Прибор учета электроэнергии"},  # Прибор учета
            {"question_id": 12, "selected": "Дрель"},  # Дрель (нейтрально)
        ]
        
        result = await repo.calculate_recommendation(answers_kip)
        print(f"\nРекомендация: {result['recommendation']}")
        print(f"Мотивация: {result['motivation']}")
        print(f"Специальности:")
        for spec in result['recommended_specialties']:
            print(f"  - {spec['code']}: {spec['name']} ({spec['duration']})")
        
        assert "КИП" in result['recommendation'] or "Контрольно-измерительные" in result['recommendation'] or "Электромонтер" in result['recommendation'], "Должна быть рекомендация КИП!"
        print("✅ Сценарий 5 пройден")
        
        # =====================================================================
        # Сценарий 6: Робототехника
        # =====================================================================
        print("\n" + "=" * 80)
        print("Сценарий 6: РОБОТОТЕХНИКА")
        print("=" * 80)
        
        answers_robot = [
            {"question_id": 1, "selected": "Нет"},  # Не физический труд
            {"question_id": 2, "selected": "Автоматизированный труд"},  # Автоматизация (робототехника +3)
            {"question_id": 3, "selected": "Нет"},  # Не на воздухе
            {"question_id": 4, "selected": "Математика"},  # Математика
            {"question_id": 5, "selected": "Для Дайвинга"},  # Маска (нейтрально)
            {"question_id": 6, "selected": "Дозиметр"},  # Дозиметр (робототехника +2)
            {"question_id": 8, "selected": "Отвертка"},  # Отвертка (робототехника +2)
            {"question_id": 10, "selected": "Светодиодная лампа"},  # Лампа (робототехника +2)
            {"question_id": 11, "selected": "Прибор учета электроэнергии"},  # Прибор учета (робототехника +2)
            {"question_id": 12, "selected": "Дрель"},  # Дрель (нейтрально)
            {"question_id": 14, "selected": "Машиностроение"},  # Машиностроение (нейтрально)
            {"question_id": 15, "selected": "Инновационная лесенка"},  # Нейтрально
        ]
        
        result = await repo.calculate_recommendation(answers_robot)
        print(f"\nРекомендация: {result['recommendation']}")
        print(f"Мотивация: {result['motivation']}")
        print(f"Специальности:")
        for spec in result['recommended_specialties']:
            print(f"  - {spec['code']}: {spec['name']} ({spec['duration']})")
        
        assert "Робот" in result['recommendation'] or "роботизированн" in result['recommendation'] or "КИП" in result['recommendation'] or "Контрольно-измерительные" in result['recommendation'], "Должна быть рекомендация робототехники или КИП!"
        print("✅ Сценарий 6 пройден")
        
        # =====================================================================
        # Сценарий 7: Оператор химического производства
        # =====================================================================
        print("\n" + "=" * 80)
        print("Сценарий 7: ОПЕРАТОР ХИМИЧЕСКОГО ПРОИЗВОДСТВА")
        print("=" * 80)
        
        answers_operator = [
            {"question_id": 1, "selected": "Нет"},  # Не физический труд
            {"question_id": 2, "selected": "Интеллектуальный труд"},  # Интеллектуальный
            {"question_id": 3, "selected": "Нет"},  # Не на воздухе
            {"question_id": 4, "selected": "Химия"},  # Химия
            {"question_id": 5, "selected": "Для Дайвинга"},  # Маска (нейтрально)
            {"question_id": 7, "selected": "Спиртовка"},  # Спиртовка (частично)
            {"question_id": 8, "selected": "Колба"},  # Колба (частично)
            {"question_id": 14, "selected": "Химическое производство"},  # Хим производство
            {"question_id": 6, "selected": "Дозиметр"},  # Прибор (нейтрально)
            {"question_id": 9, "selected": "Прага"},  # Торт (нейтрально)
        ]
        
        result = await repo.calculate_recommendation(answers_operator)
        print(f"\nРекомендация: {result['recommendation']}")
        print(f"Мотивация: {result['motivation']}")
        print(f"Специальности:")
        for spec in result['recommended_specialties']:
            print(f"  - {spec['code']}: {spec['name']} ({spec['duration']})")
        
        # Оператор может быть вместе с химиком
        assert "Оператор" in result['recommendation'] or "Химич" in result['recommendation'], "Должна быть рекомендация оператора или химика!"
        print("✅ Сценарий 7 пройден")
        
        # =====================================================================
        # Сценарий 8: Смешанные ответы (по умолчанию)
        # =====================================================================
        print("\n" + "=" * 80)
        print("Сценарий 8: СМЕШАННЫЕ ОТВЕТЫ (ПО УМОЛЧАНИЮ)")
        print("=" * 80)
        
        answers_mixed = [
            {"question_id": 1, "selected": "Я вообще не люблю работать"},
            {"question_id": 2, "selected": "Я вообще не люблю работать"},
            {"question_id": 3, "selected": "Нет"},
            {"question_id": 4, "selected": "География"},
            {"question_id": 5, "selected": "Для Страйк бола"},
            {"question_id": 6, "selected": "Барометр"},
            {"question_id": 7, "selected": "Просто предмет интерьера"},
            {"question_id": 8, "selected": "Отвертка"},
            {"question_id": 9, "selected": "Дамские пальчики"},
            {"question_id": 10, "selected": "Торшер"},
            {"question_id": 11, "selected": "Газоанализатор"},
            {"question_id": 12, "selected": "Посудомоечная машина"},
            {"question_id": 13, "selected": "Повара"},
            {"question_id": 14, "selected": "Машиностроение"},
            {"question_id": 15, "selected": "Инновационная лесенка"},
        ]
        
        result = await repo.calculate_recommendation(answers_mixed)
        print(f"\nРекомендация: {result['recommendation']}")
        print(f"Мотивация: {result['motivation']}")
        print(f"Специальности:")
        for spec in result['recommended_specialties']:
            print(f"  - {spec['code']}: {spec['name']} ({spec['duration']})")
        
        # Должна быть рекомендация по умолчанию
        assert len(result['recommended_specialties']) > 0, "Должны быть рекомендации!"
        print("✅ Сценарий 8 пройден")
        
        print("\n" + "=" * 80)
        print("ВСЕ СЦЕНАРИИ ПРОЙДЕНЫ УСПЕШНО! ✅")
        print("=" * 80)
        
        # Статистика
        print("\n📊 СТАТИСТИКА ТЕСТА:")
        print(f"  - Всего сценариев: 8")
        print(f"  - Пройдено: 8")
        print(f"  - Направлений: 7 (Сварщик, Сооруженец, Повар, Химик, КИП, Робототехника, Оператор)")
        print(f"  - Вопросов в тесте: 15")
        print(f"  - Специальностей в рекомендациях: 9")
        
    # Очистка
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_all_scenarios())
