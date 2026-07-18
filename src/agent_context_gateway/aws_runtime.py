from __future__ import annotations

import os
import re
import tempfile
from contextlib import contextmanager
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path, PurePosixPath
from typing import Iterator

from .cache import CacheEntry
from .models import ContextSlice, TaskRequest, utc_now


CONTEXT_ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")


def _boto3():
    try:
        import boto3
    except ImportError as exc:  # pragma: no cover - only reached in a misbuilt AWS package
        raise RuntimeError("Install AWS dependencies with: pip install -e '.[aws]'") from exc
    return boto3


def _dynamo_value(value):
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {key: _dynamo_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_dynamo_value(item) for item in value]
    return value


def validate_context_id(context_id: str) -> str:
    if not CONTEXT_ID_PATTERN.fullmatch(context_id):
        raise ValueError(
            "context_id must be 1-64 characters using letters, numbers, dot, underscore, or hyphen"
        )
    return context_id


class S3ContextStore:
    """Materialize a named context source from the deployment's private S3 bucket."""

    def __init__(self, bucket: str, *, client=None) -> None:
        self.bucket = bucket
        self.client = client or _boto3().client("s3")

    @classmethod
    def from_env(cls) -> "S3ContextStore":
        bucket = os.environ.get("ACG_CONTEXT_BUCKET")
        if not bucket:
            raise RuntimeError("ACG_CONTEXT_BUCKET is required in AWS mode")
        return cls(bucket)

    @contextmanager
    def materialize(self, context_id: str) -> Iterator[Path]:
        context_id = validate_context_id(context_id)
        prefix = f"sources/{context_id}/"
        objects: list[str] = []
        token = None
        while True:
            request = {"Bucket": self.bucket, "Prefix": prefix}
            if token:
                request["ContinuationToken"] = token
            response = self.client.list_objects_v2(**request)
            objects.extend(
                item["Key"]
                for item in response.get("Contents", [])
                if item.get("Key") and not item["Key"].endswith("/")
            )
            if not response.get("IsTruncated"):
                break
            token = response.get("NextContinuationToken")
        if not objects:
            raise FileNotFoundError(
                f"context_id '{context_id}' has no files under s3://{self.bucket}/{prefix}"
            )

        with tempfile.TemporaryDirectory(prefix=f"acg-{context_id}-") as temp_dir:
            root = Path(temp_dir).resolve()
            for key in objects:
                relative = PurePosixPath(key[len(prefix) :])
                if relative.is_absolute() or not relative.parts or ".." in relative.parts:
                    raise ValueError(f"unsafe S3 context key: {key}")
                destination = root.joinpath(*relative.parts).resolve()
                if root != destination and root not in destination.parents:
                    raise ValueError(f"unsafe S3 context key: {key}")
                destination.parent.mkdir(parents=True, exist_ok=True)
                self.client.download_file(self.bucket, key, str(destination))
            yield root


class DynamoContextSliceCache:
    def __init__(self, table_name: str, *, table=None) -> None:
        self.table = table or _boto3().resource("dynamodb").Table(table_name)

    @classmethod
    def from_env(cls) -> "DynamoContextSliceCache":
        table = os.environ.get("ACG_CONTEXT_CACHE_TABLE")
        if not table:
            raise RuntimeError("ACG_CONTEXT_CACHE_TABLE is required in AWS mode")
        return cls(table)

    @staticmethod
    def key_for(task: TaskRequest) -> str:
        from .models import stable_id

        return stable_id(
            "cache",
            task.normalized_request_id(),
            task.environment,
            task.approval_state,
        )

    def get(self, task: TaskRequest) -> CacheEntry | None:
        key = self.key_for(task)
        response = self.table.get_item(Key={"cache_key": key}, ConsistentRead=True)
        item = response.get("Item")
        if not item:
            return None
        self.table.update_item(
            Key={"cache_key": key},
            UpdateExpression="SET last_accessed_at = :now ADD hits :one",
            ExpressionAttributeValues={":now": utc_now(), ":one": 1},
        )
        return CacheEntry(
            key=key,
            slice_ids=list(item.get("slice_ids", [])),
            hits=int(item.get("hits", 0)) + 1,
        )

    def put(self, task: TaskRequest, slices: list[ContextSlice]) -> CacheEntry:
        entry = CacheEntry(key=self.key_for(task), slice_ids=[item.id for item in slices])
        self.table.put_item(
            Item={
                "cache_key": entry.key,
                "slice_ids": entry.slice_ids,
                "hits": 0,
                "updated_at": utc_now(),
                "last_accessed_at": utc_now(),
            }
        )
        return entry


class DynamoAuditStore:
    def __init__(self, table_name: str, *, table=None) -> None:
        self.table = table or _boto3().resource("dynamodb").Table(table_name)

    @classmethod
    def from_env(cls) -> "DynamoAuditStore":
        table = os.environ.get("ACG_AUDIT_EVENTS_TABLE")
        if not table:
            raise RuntimeError("ACG_AUDIT_EVENTS_TABLE is required in AWS mode")
        return cls(table)

    def put(self, record: dict) -> None:
        self.table.put_item(Item=_dynamo_value(record))


class DynamoSliceStore:
    def __init__(self, table_name: str, *, table=None) -> None:
        self.table = table or _boto3().resource("dynamodb").Table(table_name)

    @classmethod
    def from_env(cls) -> "DynamoSliceStore":
        table = os.environ.get("ACG_CONTEXT_SLICES_TABLE")
        if not table:
            raise RuntimeError("ACG_CONTEXT_SLICES_TABLE is required in AWS mode")
        return cls(table)

    def put_many(self, slices: list[ContextSlice]) -> None:
        with self.table.batch_writer(overwrite_by_pkeys=["slice_id"]) as batch:
            for slice_ in slices:
                item = asdict(slice_)
                item["slice_id"] = item.pop("id")
                item["stored_at"] = utc_now()
                batch.put_item(Item=_dynamo_value(item))
