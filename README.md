### Скрипт асинхронной выгрузки данных из API и загрузки в базу данных с помощью Asyncio

Документация по API: [SWAPI](https://swapi.dev/documentation#people). <br>

Данные для выгрузки:<br>
* **id** - ID персонажа <br>
* **birth_year** <br>
* **eye_color** <br>
* **films** - строка с названиями фильмов через запятую <br>
* **gender** <br>
* **hair_color** <br>
* **height** <br>
* **homeworld** <br>
* **mass** <br>
* **name** <br>
* **skin_color** <br>
* **species** - строка с названиями типов через запятую <br>
* **starships** - строка с названиями кораблей через запятую <br>
* **vehicles** - строка с названиями транспорта через запятую   

<br>

Данные по каждому персонажу загружаются в базу данных.   

Выгрузка из API и загрузка в базу данных происходит **асинхронно**. <br>

#### Запуск:
```shell
docker-compose  --env-file .env.test up
```
