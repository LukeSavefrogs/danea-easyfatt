---
layout: default
title: Formattazione definita dall'utente
parent: Sviluppo
---

Il package `veryeasyfatt.formatter` contiene la classe `SimpleFormatter`, che permette di formattare una stringa in base ad un formato/template definito dall'utente con una sintassi molto semplice e intuitiva (`{var:s->substring(0, 5)}` invece di `{var:.5}`) seppur più verbosa.

## Sintassi

La sintassi è molto semplice: si utilizzano le parentesi graffe per indicare una variabile, e si utilizza il carattere `:` per indicare che si vuole applicare una formattazione alla variabile.
Dopodichè si usa `s->` per indicare che si vuole applicare una funzione alla variabile, e si inserisce il nome della funzione.

Le funzioni sono **separate da `->`** e **possono avere argomenti**, che vanno indicati tra parentesi tonde `()`; inoltre possono essere **concatenate** fino ad ottenere il risultato voluto.

```text
{variable_name:s->command1->command2(arguments)->command3}
```

{:.note-title}
> Esempio
>
> Nel caso in cui la variabile `variable_name` contenga la stringa `HeLLo woRld!` il risultato sarà `Hello, my beloved > world!`:
>
> ```text
> {variable_name:s->lowercase->replace(world, my beloved world)->capitalize}
> ```

## Funzioni disponibili

### `lowercase`

Converte la stringa in **minuscolo**.

{:.note-title}
> Esempio
>
> Nel caso in cui la variabile `variable_name` contenga la stringa `Hello World!` il risultato sarà `hello world!`:
>
> ```text
> {variable_name:s->lowercase}
> ```

### `uppercase`

Converte la stringa in **maiuscolo**.

{:.note-title}
> Esempio
>
> Nel caso in cui la variabile `variable_name` contenga la stringa `Hello World!` il risultato sarà `HELLO WORLD!`:
>
> ```text
> {variable_name:s->uppercase}
> ```

### `title`

Converte la stringa in **minuscolo**, con la **prima lettera** di ogni parola in *maiuscolo*.

{:.note-title}
> Esempio
>
> Nel caso in cui la variabile `variable_name` contenga la stringa `HelLo woRld!` il risultato sarà `Hello World!`:
>
> ```text
> {variable_name:s->title}
> ```

### `capitalize`

Converte la stringa in **minuscolo**, con solo la **prima lettera** in *maiuscolo*.

{:.note-title}
> Esempio
>
> Nel caso in cui la variabile `variable_name` contenga la stringa `hello world!` il risultato sarà `Hello world!`:
>
> ```text
> {variable_name:s->capitalize}
> ```

### `substring(start[, end])`

Restituisce una **sottostringa** della stringa, a partire da un indice (_in base `0`_) e con una lunghezza specificati.

{:.note-title}
> Esempio
>
> Nel caso in cui la variabile `variable_name` contenga la stringa `Hello World!` il risultato sarà `Hello`:
>
> ```text
> {variable_name:s->substring(0, 5)}
> ```

### `replace(search, replace)`

**Sostituisce** tutte le occorrenze di una string con un'altra stringa.

{:.note-title}
> Esempio
>
> Nel caso in cui la variabile `variable_name` contenga la stringa `Hello World!` il risultato sarà `Hello Italy!`:
>
> ```text
> {variable_name:s->replace(World, Italy)}
> ```

{:.warning-title}
> Attenzione
>
> In caso dovesse rendersi necessario sostituire caratteri speciali come `,`, `(`, `)` o `->` è possibile racchiudere la stringa tra apici (`"` o `'`) (_ad es. `{var:s->replace("(", "-")}`_).
>
> Per sostituire invece gli apici (`"` o `'`) usare la backslash (`\`) per indicare che il carattere successivo non è un carattere speciale, ma un carattere normale.
