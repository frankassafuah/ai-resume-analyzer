"""Repository pattern base.

Repositories are the *only* layer that touches the ORM for a given model.
Services depend on repositories (not on querysets), which keeps business logic
free of persistence details and makes it trivial to fake data access in tests.
Use a repository where query logic is non-trivial or reused; for dead-simple
CRUD a service may call the model directly.
"""
from typing import Any

from django.db.models import Model, QuerySet

from apps.common.exceptions import NotFoundError


class BaseRepository[M: Model]:
    model: type[M]

    def __init__(self, model: type[M] | None = None) -> None:
        if model is not None:
            self.model = model

    # --- reads ---
    def get_queryset(self) -> QuerySet[M]:
        return self.model._default_manager.all()

    def all(self) -> QuerySet[M]:
        return self.get_queryset()

    def filter(self, **kwargs: Any) -> QuerySet[M]:
        return self.get_queryset().filter(**kwargs)

    def get_or_none(self, **kwargs: Any) -> M | None:
        return self.get_queryset().filter(**kwargs).first()

    def get(self, **kwargs: Any) -> M:
        instance = self.get_or_none(**kwargs)
        if instance is None:
            raise NotFoundError(f"{self.model.__name__} not found.")
        return instance

    def exists(self, **kwargs: Any) -> bool:
        return self.get_queryset().filter(**kwargs).exists()

    # --- writes ---
    def create(self, **kwargs: Any) -> M:
        return self.model._default_manager.create(**kwargs)

    def update(self, instance: M, **fields: Any) -> M:
        for key, value in fields.items():
            setattr(instance, key, value)
        instance.save(update_fields=[*fields.keys(), "updated_at"]
                      if hasattr(instance, "updated_at") else None)
        return instance

    def delete(self, instance: M) -> None:
        instance.delete()
