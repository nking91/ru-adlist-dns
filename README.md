# ru-adlist-dns

Автообновляемый список доменов для AdGuard DNS, собранный на основе [RU AdList](https://github.com/easylist/ruadlist) и сжатый до 950 правил под лимит пользовательских списков (1000).

## Как это работает

1. GitHub Actions ежедневно в 03:00 UTC (06:00 МСК) скачивает актуальные версии adservers.txt, general_block.txt, thirdparty.txt и whitelist.txt из проекта RU AdList
2. Скрипт generate.py отбирает только правила, понятные AdGuard DNS (||domain^ и @@||domain^), отбрасывая косметические и неподдерживаемые правила
3. Приоритет заполнения лимита:
   - Исключения (whitelist) — идут первыми целиком, снимают ложные блокировки картинок/CDN
   - adservers.txt — самый выверенный источник рекламных доменов, заполняется следующим
   - general_block.txt и thirdparty.txt — добирают оставшееся место, если оно есть
4. Результат сохраняется в ru-adlist-dns.txt и коммитится в репозиторий автоматически

## Подключение в AdGuard DNS

Пользовательские списки блокировки → добавить URL:
https://raw.githubusercontent.com/nking91/ru-adlist-dns/main/ru-adlist-dns.txt
