# FBK EXPLORER: SPECIFICHE DATI

## DIPENDENTI
* Divisione per anno
* Somme per tipologie/contratti sono da indicare in tutti i nodi/sottonodi
* *default* contiene le proprietà che nella versione precedente erano singole proprietà (totale etamedia, ...) e non fa distinzioni di stranieri e categorie protette
* l'ordine degli elementi nel JSON non ha impatto sul frontend/chart
---
### Sotto-struttura #values

```
{
  "totale": 56,
  "totale_donne": 22,
  "totale_uomini": 34,
  "etamedia": 48,
  "etamedia_donne": 42,
  "etamedia_uomini": 46
}
```
### Sotto-struttura #area-simple

``` 
{
  "ricerca": {
  "default": (( sottostruttura #values )),
  "stranieri": (( sottostruttura #values )),
  "categoria_protetta": (( sottostruttura #values ))
  },
  "amministrazione": {
  "default": (( sottostruttura #values )),
  "stranieri": (( sottostruttura #values )),
  "categoria_protetta": (( sottostruttura #values ))
  },
  "supporto_alla_ricerca": {
  "default": (( sottostruttura #values )),
  "stranieri": (( sottostruttura #values )),
  "categoria_protetta": (( sottostruttura #values ))
  }
}
```
## Sotto-struttura #area-extended

```
{
  "default": (( sottostruttura #values )),
  "stranieri": (( sottostruttura #values )),
  "categoria_protetta": (( sottostruttura #values )),
  "borsa_di_dottorato": {
  "default": (( sottostruttura #values )),
  "stranieri": (( sottostruttura #values )),
  "categoria_protetta": (( sottostruttura #values ))
  },
  "tempo_indeterminato": 
  {
    "default": (( sottostruttura #values )),
    "stranieri": (( sottostruttura #values )),
    "categoria_protetta": (( sottostruttura #values ))
  },
  "tempo_determinato": 
  {
    "default": (( sottostruttura #values )),
    "stranieri": (( sottostruttura #values )),
    "categoria_protetta": (( sottostruttura #values ))
  },
  "collaborazione_coordinata_jobs_act": 
  {
    "default": (( sottostruttura #values )),
    "stranieri": (( sottostruttura #values )),
    "categoria_protetta": (( sottostruttura #values ))
  }
}
```
## Sotto-struttura #contracts

```
{
  "borsa_di_dottorato": 
  {
    "default": (( sottostruttura #values )),
    "stranieri": (( sottostruttura #values )),
    "categoria_protetta": (( sottostruttura #values ))
  },
  "tempo_indeterminato": 
  {
    "default": (( sottostruttura #values )),
    "stranieri": (( sottostruttura #values )),
    "categoria_protetta": (( sottostruttura #values ))
  },
  "tempo_determinato": 
  {
    "default": (( sottostruttura #values )),
    "stranieri": (( sottostruttura #values )),
    "categoria_protetta": (( sottostruttura #values ))
  },
  "collaborazione_coordinata_jobs_act": 
  {
    "default": (( sottostruttura #values )),
    "stranieri": (( sottostruttura #values )),
    "categoria_protetta": (( sottostruttura #values ))
  }
}
```
## Schema completa del file (con riferimenti alla sotto-strutture)
```
{

"2014": { ... },

"2015": { ... },

"2016": { ... },

"2017": {
  "name": "FBK",
  "anno": 2017,
  "default": (( sottostruttura #values )),
  "stranieri": (( sottostruttura #values )),
  "categoria_protetta": (( sottostruttura #values )),
  "aree": (( sottostruttura #area-simple )),
  "contratti": (( sottostruttura #contracts )),
  "poli": 
  [
    {
      "name": "Nome Polo",
      "default": (( sottostruttura #values )),
      "stranieri": (( sottostruttura #values )),
      "categoria_protetta": (( sottostruttura #values )),
      "aree": (( sottostruttura #area-simple )),
      "contratti": (( sottostruttura #contracts )),
      "centri": 
      [
        {
          "name": "Nome Centro",
          "default": (( sottostruttura #values )),
          "stranieri": (( sottostruttura #values )),
          "categoria_protetta": (( sottostruttura #values )),
          "aree": 
            {
              "ricerca": (( sottostruttura #area-extended )),
              "amministrazione": (( sottostruttura #area-extended )),
              "supporto_alla_ricerca": (( sottostruttura #area-extended ))
            },
          "contratti": (( sottostruttura #contracts ))
         },
        ...
      ]
    },
    ...
   ]
  }
}
```
## ASSUNZIONI
* Lista degli anni non devono per forza corrispondere tra i vari centri
* Sul frontend verrà utilizzato l'ordine delle liste e rispettivi elementi da JSON
---
```
[
  {
    "title": "NOME CENTRO",
    "data": [
        { "year": 2007, "female": 10, "male": 23 },
        { "year": 2008, "female": 14, "male": 6 },
        { "year": 2009, "female": 4, "male": 5 },
        { "year": 2010, "female": 0, "male": 8 },
        { "year": 2011, "female": 7, "male": 12 },
        { "year": 2012, "female": 2, "male": 14 },
        { "year": 2013, "female": 6, "male": 9 },
        { "year": 2014, "female": 1, "male": 4 },
        { "year": 2015, "female": 23, "male": 7 },
        { "year": 2016, "female": 8, "male": 5 },
        { "year": 2017, "female": 2, "male": 12 }
    ]
  },
...
]
```
## ORGANIGRAMMA
### Divisione per anno

- Ogni anno contiene sections (liste con nomi/link) e overview (tree chart)
- Strutture per dettagli praticamente identitiche tra liste e chart
- ```gender``` può essere: ```male``` , ```female``` o non specificato (anche ```null``` eventualmente)
- Sul frontend verrà utilizzato l'ordine delle liste e rispettivi elementi da JSON
---
```
{
  "2015": {
    "sections": [ ... ],
    "overview": [ ... ]
  },
  "2016": {
    "sections": [
      {
      "title": "Nome Gruppo/Ente/Categoria",
      "elements": [
      {
        "name": "John Doe",
        "role": "President",
        "gender": "male",
        "image": "http://www.example.com/...",
        "permalink": "http://www.example.com/...",
        "details": 
         {
          "salary": {
          "label": "Compenso annuale",
          "value": "100.000 &euro;"
          }
       }
      },
        ...
      ]
    },
    ...
   ],
     "overview": [
      {
        "name": "Elemento Root",
        "parent": null
      },
      {
        "name": "Francesco Profumo",
        "role": "Presidente",
        "image": "http://www.example.com/...",
        "permalink": "http://www.example.com/...",
        "details": {
        "salary": {
        "label": "Compenso annuale",
        "value": 70.000 &euro;"
      }
    }
    },
    ...
    ]
  }
}
```
## BILANCIO
*  Divisione per anno
* Nomi dei ricavi e delle spesi tra gli elementi devono essere identici
* Ordinamento degli elementi nel JSON non ha impatto sul frontend/chart
---
```
{
  "2015": { ... },
  "2016": {
    "Nome Centro": {
    "polo": "Nome Polo",
    "incoming": {
      "progetti_europei": 10000,
      "altre_spese": 5200
    },
    "expenses": {
      "viaggi": 2400,
      "personale": 7200,
      "altre_spese": 5200
    }
   }
  },
  "2017": { ... }
}
```
## SEDI
* Divisione per anno
* Se ```image``` non viene specificato, viene utilizzata l'immagine di una sede generica
* ```address``` può contenere numero variabile di voci/linee
* Sul frontend verrà utilizzato l'ordine degli elementi nel JSON
---
```
{
  "2015": [
    ...
   ],
  "2016": [
    {
    "image": "./data/venues/sede-operativa.svg",
    "title": "Nome Sede",
    "address": [
      "Nome Edificio/Palazzo",
      "Via della Trasparenza, 123",
      "Trento"
    ],
      "square_footage": "http://www.example.com/...",
      "plan": "http://www.example.com/...",
      "location": "http://www.example.com/...",
      "rent": 10000,
      "revenue": 25000
    },
    ...
  ],
  "2017": [
  ...
  ]
}
```

