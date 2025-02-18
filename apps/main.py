import schedule
import time
from app import main

if __name__ == '__main__':
    main()
"""def job():
    main()

if __name__ == '__main__':
    # Планируем выполнение функции job каждую минуту
    schedule.every(1).minutes.do(job)

    # Бесконечный цикл для выполнения запланированных задач
    while True:
        schedule.run_pending()
        time.sleep(1)"""
