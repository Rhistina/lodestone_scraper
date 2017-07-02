# lodestone_scraper

### Description

A web scraper for the site http://na.finalfantasyxiv.com/lodestone/ using Requests and BeautifulSoup and written in Python 3.5.

Returns information on a player's character or an in-game free company.

### Usage
Look up player info by providing name and server
```bash
>python lodestone_scraper player -n Oren Iishi -s Gilgamesh
Look up free company info by provide name and server
```
```bash
>python lodestone_scraper fc -n Ascended -s Gilgamesh
```
Help on usage
```bash 
>python lodestone_scraper -h
usage: lodestone_scraper [-h] [-n NAME [NAME ...]] [-s SERVER] [-i ID]
                         {fc,player}

positional arguments:
  {fc,player}

optional arguments:
  -h, --help            show this help message and exit
  -n NAME [NAME ...], --name NAME [NAME ...]
                        Name of a player or free company
  -s SERVER, --server SERVER
                        Server the player or free company resides
  -i ID, --id ID        Lodestone ID of the player or free company
```  



### Authors
Rhistina Revilla (rhistina@gmail.com)

### Contributors
AbscissaX (https://github.com/AbscissaX/)
