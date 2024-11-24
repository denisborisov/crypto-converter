# Crypto Converter

## A couple words about the project structure

the project structure is the following:
- `docs` is a directory containing the original task description received from Sparkland Trading
- `src` is a directory containing main Python code
- `test` is a directory with a pytest tests
<br />
<br />

## Before launching a project

#### Installing dependencies

Use the following command to install dependencies:

```shell
poetry install
```

or this one to update them:

```shell
poetry update
```

<br />

## Project launching

The `make` utility is used to run various commands in the project. All its arguments are written in the corresponding `Makefile` file. For example, to launch an application, simply run the following command in the terminal:

```shell
make up
```

If you do not want to use `make`, then you can just run the following command in the terminal:

```shell
docker compose up
```

This will launch containers with Redis and two services available by:
- http://0.0.0.0:8000/api/docs — Quote Consumer
- http://0.0.0.0:8001/api/docs — Currency Conversion API
<br />
<br />

## Testing

You can run all the tests of the project using this comand:

```shell
make test
```

## A few words about technologies used in these examples

Redis was chosen as a database solution, in that
- it has got a nice feature of TTL, so we can easy control records' lifetimes
- it should store around 2-3 Gb of data eventually, and this option is pretty well for in-memory DB
- it has got a nice feature of making it persistent, no no hard to durability here

Nevertheless, we could also choose PostgreSQL, for example, and this would work perfectly as well.

FastAPI was chosen as the target web framework, in that
- it is asynchronous
- it is modern, with a large active community

Python 3.13 was chosen because
- it it the latest version of Python
