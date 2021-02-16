## Uleth: CLI tool for retrieving forgotten Ethereum wallet passwords

### System Dependencies

`sudo apt install libssl-dev`

### Commands

#### new

Creates a new uleth keystore instance for a locked keystore. This will delete an existing entry with the same name

`python3 uleth.py new asdf ../path/to/keystore`

#### entry

Begins a manual password loading session for the named keystore.

`python3 uleth.py entry asdf`

#### load

Load a newline-separated password file for the named keystore.

`python3 uleth.py load asdf ../path/to/newline-separated-passwords.txt`

#### run

Begin attempting to unlock the keystore using loaded passwords.

`python3 uleth.py run asdf`

#### clean

Removes all untried passwords from the named keystore.

`python3 uleth.py clean asdf`

#### ls

Lists all passwords that have been attempted for the named keystore.

`python3 uleth.py ls asdf`

#### stats

Provides statistics such as single-password check time, loaded passwords, attempted passwords for a keystore.

`python3 uleth.py stats asdf`
