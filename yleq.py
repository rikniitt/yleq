#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import click
import sqlite3
import logging
from tabulate import tabulate
from datetime import datetime
from subprocess import call
from time import sleep


PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_FILE = PROJECT_DIR + "/yleq.log"
DB_FILE = PROJECT_DIR + "/yleq.db"


def get_logger():
    return logging.getLogger(__name__)


def setup_logging():
    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    filehandler = logging.FileHandler(LOG_FILE)
    filehandler.setLevel(logging.DEBUG)
    filehandler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s",
        datefmt='%Y-%d-%m %H:%M:%S'
    ))

    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(logging.INFO)
    streamhandler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(filehandler)
    logger.addHandler(streamhandler)


def log(message, lvl="INFO"):
    logger = get_logger()
    logger.log(getattr(logging, lvl), message)


def db_connect():
    return sqlite3.connect(DB_FILE)


@click.group()
def yleq():
    """yle-dl queue"""
    pass


@yleq.command("db-create")
def db_create():
    """create needed database tables"""
    open(DB_FILE, 'a').close()
    db = db_connect()
    cursor = db.cursor()

    sql = """
            CREATE TABLE IF NOT EXISTS yle_dl_queue (
                id INTEGER PRIMARY  KEY,
                url TEXT NOT NULL,
                status TEXT DEFAULT 'queued',  -- (queued, ready, failed)
                destdir TEXT DEFAULT '.',
                created_at TEXT,
                handled_at TEXT
            )
          """

    log("Creating tables")
    log(sql, "DEBUG")

    cursor.execute(sql)
    db.commit()


@yleq.command("show")
@click.option("--n", type=click.INT, default=-1)
def show(n):
    """show the next in queue"""
    db = db_connect()
    cursor = db.cursor()

    sql = """
            SELECT * FROM yle_dl_queue
             WHERE status = 'queued'
             ORDER BY created_at ASC
          """
    if n > 0:
        sql += "   LIMIT " + str(n)

    log(sql, "DEBUG")

    result = cursor.execute(sql)
    rows = [row[0:-1] for row in result]

    print tabulate(rows, headers=["#", "url", "status", "destdir", "created at"])


@yleq.command("enqueue")
@click.argument("url", type=click.STRING)
@click.option(
    "--destdir",
    default=".",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True
    )
)
def enqueue(url, destdir):
    """enqueue new download url"""
    log("Enqueueing " + url)
    log(" will be saved to " + destdir)

    db = db_connect()
    cursor = db.cursor()

    sql = """
            INSERT INTO yle_dl_queue
             (url, destdir, status, created_at)
             VALUES (?, ?, ?, ?)
          """
    values = (url, destdir, "queued", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    log(sql + " (" + " ".join(values) + ")", "DEBUG")

    cursor.execute(sql, values)
    db.commit()


@yleq.command("db-console")
def db_console():
    """open sqlite3 console"""
    cmd = ["sqlite3", "-column", "-header", DB_FILE]
    log("$ " + " ".join(cmd), "DEBUG")
    call(cmd)


@yleq.command("dequeue")
@click.option("--n", type=click.INT, default=-1)
@click.option("--d/--b", default=False)
def dequeue(n, d):
    """dequeue and handle the download urls"""
    while True:
        db = db_connect()
        cursor = db.cursor()

        sql = """
                SELECT id, url, destdir FROM yle_dl_queue
                 WHERE status = 'queued'
                 ORDER BY created_at ASC
              """
        if n > 0:
            sql += "LIMIT " + str(n)

        log(sql, "DEBUG")

        rows = [row for row in cursor.execute(sql)]
        if len(rows) == 0:
            log("Queue is empty")
        else:
            for row in rows:
                log("Starting to download " + row[1])
                log(str(row), "DEBUG")

                cmd = ["yle-dl", "--destdir", row[2], row[1]]
                log("$ " + " ".join(cmd), "DEBUG")
                exitcode = call(cmd)

                status = "ready" if exitcode == 0 else "failed"

                db = db_connect()
                cursor = db.cursor()

                sql = """
                        UPDATE yle_dl_queue
                           SET status = ?,
                           handled_at = ?
                         WHERE id = ?
                      """
                values = (status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), row[0])

                log(sql + " (" + " ".join([str(x) for x in values]) + ")", "DEBUG")

                cursor.execute(sql, values)
                db.commit()

        if d:
            log("Sleeping 5 secs", "DEBUG")
            sleep(5)
            continue
        else:
            break

    log("done")


if __name__ == "__main__":
    setup_logging()
    yleq()
