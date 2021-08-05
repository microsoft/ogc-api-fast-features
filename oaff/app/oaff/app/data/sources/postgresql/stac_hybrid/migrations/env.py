from logging.config import fileConfig
from os import environ
from typing import Final

from alembic import context
from sqlalchemy import engine_from_config, pool

from oaff.app.data.sources.postgresql import settings
from oaff.app.data.sources.postgresql.stac_hybrid.models import *  # noqa: F403, F401
from oaff.app.data.sources.postgresql.stac_hybrid.settings import OAFF_METADATA

EXCLUDE_TABLES: Final = ["spatial_ref_sys"]
SOURCE_NAME: Final = environ.get("ALEMBIC_SOURCE_NAME")
CONFIG_KEY_URL: Final = "sqlalchemy.url"

config = context.config
if config.get_main_option(CONFIG_KEY_URL) is None:
    """
    if URL is already set this migration is being called from the API
    if not set this migration is being called independently and expects
    an environment variable identifying the source name
    """
    config.set_main_option(CONFIG_KEY_URL, settings.url(SOURCE_NAME))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and name in EXCLUDE_TABLES:
        return False
    return not object.info.get("is_view", False)


def process_revision_directives(context, revision, directives):
    if config.cmd_opts.autogenerate:
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=OAFF_METADATA,
            include_object=include_object,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
