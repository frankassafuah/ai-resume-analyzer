"""Enable the pgvector extension from the very first migration (ADR-0004).

Vector-bearing tables and indexes are added later when embedding workflows
activate; here we only make the extension available.
"""
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies: list = []

    operations = [
        CreateExtension("vector"),
    ]
