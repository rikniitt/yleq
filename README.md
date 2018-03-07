yleq.py
=======

Simple python/sqlite yle-dl queue.

# Requirements

 * Python 2.7
   * click, sqlite, tabulate
 * SQLite 3
 * [yle-dl](https://aajanki.github.io/yle-dl/)

# Install

 * `python yleq.py db-create`

# Usage

```
bash$ python yleq.py
Usage: yleq.py [OPTIONS] COMMAND [ARGS]...

  yle-dl queue

Options:
  --help  Show this message and exit.

Commands:
  db-console  open sqlite3 console
  db-create   create needed database tables
  dequeue     dequeue and handle the download urls
  enqueue     enqueue new download url
  show        show the next in queue
bash$ python yleq.py enqueue https://areena.yle.fi/1-4234838
Enqueueing https://areena.yle.fi/1-4234838
 will be saved to /home/user
bash$ python yleq.py show
  #  url                              status    destdir      created at
---  -------------------------------  --------  -----------  -------------------
  1  https://areena.yle.fi/1-4234838  queued    /home/user   2018-03-07 20:00:00
bash$ python yleq.py dequeue
Starting to download https://areena.yle.fi/1-4234838
 ...
```

