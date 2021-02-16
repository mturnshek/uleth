## Uleth: CLI tool for retrieving forgotten Ethereum wallet passwords

#### Basic commands

Creates a new uleth keystore instance for a locked keystore. This will delete an existing entry with the same name. Example:

```
python3 uleth.py new asdf ../path/to/keystore
```

Begins a manual password loading session for the named keystore. Example:

```
python3 uleth.py entry asdf
```

Load a newline-separated password file for the named keystore.

```
python3 uleth.py load asdf ../path/to/newline-separated-passwords.txt
```

Begin attempting to unlock the keystore using loaded passwords.

```
python3 uleth.py run asdf
```

Removes all untried passwords from the named keystore.

```
python3 uleth.py clean asdf
```

Lists all passwords that have been attempted for the named keystore.

```
python3 uleth.py ls asdf
```

Provides statistics such as single-password check time, loaded passwords, attempted passwords for a keystore.

```
python3 uleth.py stats asdf
```
